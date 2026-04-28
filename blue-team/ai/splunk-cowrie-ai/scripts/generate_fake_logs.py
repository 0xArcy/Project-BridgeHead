from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from bridgehead_ai.data_generation import generate_fake_logs


if __name__ == "__main__":
    output_path = REPO_ROOT / "data" / "fake_logs.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_fake_logs(str(output_path), 100, 100, 100)
