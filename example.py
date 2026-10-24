"""Run one phrase through the unchanged JSON-lines worker."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-code', choices=['ru', 'en'], default='ru')
    parser.add_argument('--count', type=int, choices=range(1, 11), default=1)
    parser.add_argument('--json', action='store_true', help='print the full JSON response')
    parser.add_argument('text', help='text to translate; quote phrases with spaces')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    result = subprocess.run(
        [sys.executable, '-u', str(root / 'worker.py'), '--from-code', args.from_code],
        input=json.dumps({'text': args.text, 'count': args.count}, ensure_ascii=False) + '\n',
        capture_output=True, text=True, encoding='utf-8', timeout=120,
    )
    lines = result.stdout.splitlines()
    ready = json.loads(lines[0]) if lines else {}
    if result.returncode or not ready.get('ready'):
        raise SystemExit('Worker could not start. Install requirements and models first.\n' + result.stderr + str(ready))
    response = json.loads(lines[1])
    if response.get('error'):
        raise SystemExit('Translation failed: ' + response['error'])
    print(json.dumps(response, ensure_ascii=False) if args.json else response.get('translation', ''))


if __name__ == '__main__':
    main()
