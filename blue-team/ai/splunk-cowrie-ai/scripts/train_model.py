from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from bridgehead_ai.training import fine_tune_distilbert, load_cowrie_logs, preview_eval_predictions


if __name__ == "__main__":
    log_files = [
        str(REPO_ROOT / "data" / "logs1.json"),
        str(REPO_ROOT / "data" / "logs2.json"),
        str(REPO_ROOT / "data" / "logs3.json"),
        str(REPO_ROOT / "data" / "fake_logs.json"),
    ]

    texts, labels = load_cowrie_logs(log_files)
    if not texts:
        raise SystemExit("No command data found. Add Cowrie JSONL logs under data/.")

    print(f"Extracted {len(texts)} sessions with commands.")

    model_output = str(REPO_ROOT / "models" / "saved_distilbert_cowrie")
    model, tokenizer, eval_dataset = fine_tune_distilbert(texts, labels, output_dir=model_output)

    print("\n--- Local evaluation preview ---")
    preview_eval_predictions(model, tokenizer, eval_dataset)
