import concurrent.futures
import fcntl
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import termios
import time
import unittest
from calculator import calculate, response

ROOT=Path(__file__).resolve().parent


def line_with_timeout(process, seconds=10):
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout,selectors.EVENT_READ)
        if not selector.select(seconds):
            raise TimeoutError('No output from subprocess')
        return process.stdout.readline().strip()


class IPCTests(unittest.TestCase):
    def start(self,*args):
        process=subprocess.Popen([sys.executable,*map(str,args)],cwd=ROOT,stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,text=True)
        def cleanup():
            if process.poll() is None:
                process.terminate()
                try: process.wait(timeout=8)
                except subprocess.TimeoutExpired: process.kill();process.wait()
            process.stdout.close();process.stderr.close()
        self.addCleanup(cleanup)
        self.assertTrue(line_with_timeout(process).startswith('READY'))
        return process

    def test_calculator(self):
        self.assertEqual(calculate('2 + 3 * (4 - 1)'),11)
        self.assertEqual(calculate('-4 / 2'),-2)
        for expr in ('1/0', '__import__("os").system("id")','2**100','True','1e309','[1]', '1'*257):
            self.assertFalse(response(expr)['ok'],expr)

    def test_fifo_sequential_and_cleanup(self):
        with tempfile.TemporaryDirectory(prefix='pr7-') as directory:
            server=self.start('service.py','fifo','server',directory,'--count','3')
            records=[]
            for expr,expected in [('2+3',5),('8/2',4),('9-7',2)]:
                start=time.perf_counter()
                result=subprocess.check_output([sys.executable,'service.py','fifo','client',directory,expr],cwd=ROOT,timeout=10,text=True)
                self.assertEqual(json.loads(result)['result'],expected)
                records.append({'expression':expr,'reply':json.loads(result),'roundtrip_including_client_start_seconds':time.perf_counter()-start,
                                'request_bytes':len((json.dumps(expr)+'\n').encode())})
            self.assertEqual(server.wait(timeout=10),0,server.stderr.read())
            self.assertEqual(list(Path(directory).iterdir()),[])
            (ROOT/'results/fifo_clients.json').write_text(json.dumps(records,indent=2))

    def test_unix_concurrent_and_cleanup(self):
        with tempfile.TemporaryDirectory(prefix='pr7-') as directory:
            path=Path(directory)/'calc.sock'
            server=self.start('service.py','unix','server',path,'--count','8')
            def client(i):
                start=time.perf_counter()
                result=subprocess.check_output([sys.executable,'service.py','unix','client',str(path),f'{i}*{i}'],cwd=ROOT,timeout=10,text=True)
                return {'expression':f'{i}*{i}','reply':json.loads(result),
                        'roundtrip_including_client_start_seconds':time.perf_counter()-start,
                        'request_bytes':len((json.dumps(f'{i}*{i}')+'\n').encode())}
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                records=list(pool.map(client,range(8)))
                self.assertEqual([r['reply']['result'] for r in records],[i*i for i in range(8)])
            self.assertEqual(server.wait(timeout=10),0,server.stderr.read())
            self.assertFalse(path.exists())
            (ROOT/'results/unix_clients.json').write_text(json.dumps(records,indent=2))

    def test_sigterm_cleans_endpoints(self):
        for transport in ('fifo','unix'):
            with tempfile.TemporaryDirectory(prefix='pr7-') as directory:
                path=Path(directory) if transport=='fifo' else Path(directory)/'calc.sock'
                server=self.start('service.py',transport,'server',path)
                server.terminate(); server.wait(timeout=10)
                self.assertEqual(list(Path(directory).iterdir()),[])

    def test_fifo_open_blocks(self):
        with tempfile.TemporaryDirectory(prefix='pr7-') as directory:
            path=Path(directory)/'channel'
            os.mkfifo(path)
            reader=subprocess.Popen(['cat',str(path)],stdout=subprocess.PIPE)
            try:
                time.sleep(0.1)
                self.assertIsNone(reader.poll())
                with path.open('w') as stream: stream.write('hello\n')
                output,_=reader.communicate(timeout=5)
                self.assertEqual(output,b'hello\n')
            finally:
                if reader.poll() is None: reader.kill();reader.wait()
                reader.stdout.close();path.unlink()

    def test_signal_handler(self):
        process=self.start('signal_demo.py')
        os.kill(process.pid,signal.SIGINT)
        self.assertIn('SIGINT',line_with_timeout(process))
        self.assertIsNone(process.poll())
        process.terminate()
        self.assertEqual(process.wait(timeout=5),0)

    def test_terminal_ctrl_c(self):
        master,slave=os.openpty()
        def setup_terminal():
            os.setsid()
            fcntl.ioctl(0,termios.TIOCSCTTY,0)
        process=subprocess.Popen([sys.executable,'signal_demo.py'],cwd=ROOT,stdin=slave,
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
                                 preexec_fn=setup_terminal)
        os.close(slave)
        try:
            self.assertTrue(line_with_timeout(process).startswith('READY'))
            os.write(master,b'\x03')  # Terminal driver generates SIGINT from Ctrl+C.
            self.assertIn('SIGINT',line_with_timeout(process))
            self.assertIsNone(process.poll())
        finally:
            process.terminate();process.wait(timeout=5)
            process.stdout.close();process.stderr.close();os.close(master)

    def test_pipe_and_pipeline(self):
        for file in ('pipe_demo.py','pipeline_demo.py'):
            result=subprocess.run([sys.executable,file],cwd=ROOT,capture_output=True,timeout=10,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(result.stdout)


if __name__=='__main__': unittest.main(verbosity=2)
