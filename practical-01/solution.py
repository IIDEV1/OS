import os, platform, shutil, subprocess
from pathlib import Path
print('OS:', platform.platform())
print('Python:', platform.python_version())
print('User:', os.environ.get('USER') or os.environ.get('USERNAME'))
print('Home:', Path.home())
print('Root disk:', shutil.disk_usage(Path.home()))
if shutil.which('id'):
    print(subprocess.run(['id'], text=True, capture_output=True).stdout.strip())
