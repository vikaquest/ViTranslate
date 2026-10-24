"""Check both real installed models and the JSON-lines protocol, without GUI/input hooks."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding='utf-8')
for language, text in [('ru', 'Привет, мой друг!'), ('en', 'I wanna play with you.')]:
    requests = [json.dumps({'text': text, 'count': 3}), '{invalid json', json.dumps({'text': text, 'count': 1})]
    result = subprocess.run([sys.executable, '-u', str(root / 'worker.py'), '--from-code', language],
                            input='\n'.join(requests) + '\n', capture_output=True, text=True, encoding='utf-8', timeout=120)
    assert result.returncode == 0, result.stderr
    ready, translated, invalid, subsequent = map(json.loads, result.stdout.splitlines())
    assert ready['ready']
    assert translated['translation'] and 1 <= len(translated['variants']) <= 3
    assert invalid.get('error') and subsequent['translation']
    print(f"PASS {language}: {translated['translation']}")
print('PASS both directions, variants, UTF-8, error response, and continuing after an invalid request')
