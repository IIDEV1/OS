"""Выполнить все ячейки и сохранить результаты в notebook."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parent
path = root / 'practice-6.ipynb'
notebook = nbformat.read(path, as_version=4)
NotebookClient(notebook, timeout=300, kernel_name='python3',
               resources={'metadata': {'path': str(root)}}).execute()
nbformat.write(notebook, path)
print('Все ячейки выполнены:', path.name)
