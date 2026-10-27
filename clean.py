from pathlib import Path
for root in [Path(r'C:\Users\user\Documents\Codex\2026-10-12\new-chat\work\OS'),Path(r'C:\Users\user\Documents\Codex\2026-10-12\new-chat\work\ML')]:
 for p in root.rglob('__pycache__'):
  import shutil; shutil.rmtree(p)
 for p in root.rglob('*.pyc'): p.unlink()
for p in [Path(r'C:\Users\user\Documents\Codex\2026-10-12\new-chat\work\OS/practical-04/numbers.txt')]:
 if p.exists(): p.unlink()

