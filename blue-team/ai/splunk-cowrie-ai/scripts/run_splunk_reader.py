from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from bridgehead_ai.realtime_inference import run_continuous_reader
from bridgehead_ai.settings import load_splunk_config


if __name__ == "__main__":
    config = load_splunk_config()
    missing = config.missing_required()
    if missing:
        missing_str = ", ".join(missing)
        raise SystemExit(
            "Missing required Splunk configuration fields in .env: "
            f"{missing_str}"
        )
    model_path = str(REPO_ROOT / "models" / "saved_distilbert_cowrie")
    run_continuous_reader(model_path=model_path, config=config)
