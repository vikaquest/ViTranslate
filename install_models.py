"""Install the pinned official Argos packages; no third-party Python dependencies."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent


def download(url, path):
    # Small ranges also work when a proxy stalls a large full-file response.
    start = 0
    with path.open('wb') as output:
        while True:
            request = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (ViTranslate-open-worker)',
                'Range': f'bytes={start}-{start + 8 * 1024 * 1024 - 1}',
            })
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status == 200 and start == 0:
                    shutil.copyfileobj(response, output, length=64 * 1024)
                    return
                match = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', response.headers.get('Content-Range', ''))
                if response.status != 206 or not match or int(match[1]) != start:
                    raise RuntimeError('Unexpected model download range')
                end, total = int(match[2]), int(match[3])
                shutil.copyfileobj(response, output, length=64 * 1024)
                if output.tell() != end + 1:
                    raise RuntimeError('Incomplete model download')
            print(f'  {end + 1:,} / {total:,} bytes', flush=True)
            start = end + 1
            if start == total:
                return


def verify(package, entry):
    for name, expected in entry['sha256'].items():
        path = package / name
        if not path.is_file():
            return False
        with path.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != expected:
                return False
    return True


def extract(archive_path, destination):
    with zipfile.ZipFile(archive_path) as archive:
        for item in archive.infolist():
            path = (destination / item.filename).resolve()
            if not path.is_relative_to(destination.resolve()) or ':' in item.filename or '\\' in item.filename:
                raise ValueError('Unexpected path in model archive')
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Symbolic links are not accepted in model archives')
        archive.extractall(destination)


def install(entry, packages):
    destination = packages / entry['directory']
    if destination.exists():
        if verify(destination, entry):
            print(f"{entry['from_code']} -> {entry['to_code']}: already installed and verified", flush=True)
            return
        raise RuntimeError(f'Existing package does not match the lock file: {destination}. Move it aside and retry.')
    with tempfile.TemporaryDirectory(prefix='download-', dir=packages) as temporary:
        temporary = Path(temporary)
        archive_path = temporary / 'model.argosmodel'
        print(f"Downloading {entry['from_code']} -> {entry['to_code']} version {entry['package_version']}...", flush=True)
        download(entry['url'], archive_path)
        extracted = temporary / 'extracted'
        extracted.mkdir()
        extract(archive_path, extracted)
        package = extracted / entry['directory']
        if not verify(package, entry):
            raise RuntimeError('Model files differ from models.lock.json; nothing installed.')
        shutil.move(str(package), str(destination))
    print(f"{entry['from_code']} -> {entry['to_code']}: installed and verified", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-code', choices=['ru', 'en', 'both'], default='both')
    args = parser.parse_args()
    lock = json.loads((ROOT / 'models.lock.json').read_text(encoding='utf-8'))
    packages = ROOT / 'models' / 'packages'
    packages.mkdir(parents=True, exist_ok=True)
    for entry in lock['models']:
        if args.from_code in ('both', entry['from_code']):
            install(entry, packages)


if __name__ == '__main__':
    main()
