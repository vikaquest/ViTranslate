"""Offline Argos model inference without importing the heavyweight NLP stack."""
import json
from pathlib import Path
import sys
import argparse
import ctranslate2
import sentencepiece

root = Path(__file__).resolve().parent
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
parser = argparse.ArgumentParser()
parser.add_argument("--from-code", choices=["ru", "en"], default="ru")
source_code = parser.parse_args().from_code
target_code = "en" if source_code == "ru" else "ru"
try:
    package = next(p.parent for p in (root / "models" / "packages").glob("*/metadata.json")
                   if (lambda m: m.get("from_code") == source_code and m.get("to_code") == target_code)
                   (json.loads(p.read_text(encoding="utf-8"))))
    metadata = json.loads((package / "metadata.json").read_text(encoding="utf-8"))
    # SentencePiece's native Windows file loader cannot open some Unicode paths.
    # Python handles these paths correctly; pass the model bytes to the tokenizer.
    tokenizer = sentencepiece.SentencePieceProcessor(model_proto=(package / "sentencepiece.model").read_bytes())
    engine = ctranslate2.Translator(str(package / "model"), device="cpu", compute_type="int8",
                                   inter_threads=1, intra_threads=2)
    print(json.dumps({"ready": True}), flush=True)
except Exception as exc:
    print(json.dumps({"ready": False, "error": type(exc).__name__}), flush=True)
    sys.exit(1)

for line in sys.stdin:
    try:
        request = json.loads(line)
        # This model treats bare lowercase fragments as dictionary compounds.
        # A sentence terminator preserves prepositions in phrases like на столе.
        text = request["text"].strip()
        if text and text[-1] not in ".!?…":
            text += "."
        tokens = tokenizer.encode(text, out_type=str)
        prefix = metadata.get("target_prefix", "")
        count = max(1, min(10, int(request.get("count", 3))))
        batch = engine.translate_batch([tokens], target_prefix=[[prefix]] if prefix else None,
                                       replace_unknowns=True, beam_size=max(4, count), num_hypotheses=count,
                                       length_penalty=0.2, return_scores=True)[0]
        variants = []
        for hypothesis in batch.hypotheses:
            result = tokenizer.decode_pieces(hypothesis).replace("▁", " ").replace("_", " ").strip()
            if prefix and result.startswith(prefix):
                result = result[len(prefix):].strip()
            if result and result not in variants:
                variants.append(result)
        print(json.dumps({"translation": variants[0] if variants else "", "variants": variants}, ensure_ascii=False), flush=True)
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__}), flush=True)
