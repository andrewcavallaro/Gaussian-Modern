"""Create a GitHub-ready source/font ZIP with a SHA-256 manifest."""
from pathlib import Path
from hashlib import sha256
import zipfile
ROOT = Path(__file__).resolve().parent.parent
VERSION = '0.108'
EXCLUDE = {'.git', '__pycache__', '.rsync-tmp', '.venv', 'dist', 'work'}
files = sorted(p for p in ROOT.rglob('*') if p.is_file()
               and not any(part in EXCLUDE for part in p.relative_to(ROOT).parts)
               and p.suffix not in {'.pyc', '.pyo', '.aux', '.log', '.xdv', '.fls', '.fdb_latexmk'}
               and p.name not in {'SHA256SUMS.txt', '.DS_Store'})
manifest = ROOT / 'SHA256SUMS.txt'
manifest.write_text(''.join(sha256(p.read_bytes()).hexdigest() + '  ' +
                          p.relative_to(ROOT).as_posix() + '\n' for p in files))
dist = ROOT / 'dist'
dist.mkdir(exist_ok=True)
archive = dist / f'gaussian-modern-v{VERSION}.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=7) as z:
    for p in files + [manifest]:
        z.write(p, 'gaussian-modern/' + p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert 'gaussian-modern/.github/workflows/build.yml' in z.namelist()
    assert 'gaussian-modern/LICENSE' in z.namelist()
print(archive)
