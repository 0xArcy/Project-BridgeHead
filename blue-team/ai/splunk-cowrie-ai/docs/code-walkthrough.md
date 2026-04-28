# Code Walkthrough (AI Component)

## src/bridgehead_ai/settings.py
- Defines `SplunkConfig` dataclass for all Splunk-related variables.
- `load_splunk_config()` reads values from `.env` using `python-dotenv`.
- Keeps connection details centralized to avoid repeated `os.getenv()` calls.

## src/bridgehead_ai/data_generation.py
- `generate_fake_logs(...)` builds synthetic Cowrie JSONL events for three behavior classes.
- Session-level event ordering mirrors Cowrie flow:
  `session.connect` -> `login.success` -> multiple `command.input` -> `session.closed`.
- Used to bootstrap model training when real logs are sparse.

## src/bridgehead_ai/training.py
- `load_cowrie_logs(file_paths)`:
  - Reads JSONL files.
  - Groups commands by `session`.
  - Creates one training text per session.
- `_infer_label_from_session_text(text)`:
  - Applies rule-based bootstrap labels for initial supervised learning.
- `fine_tune_distilbert(texts, labels, output_dir)`:
  - Loads tokenizer/model (`distilbert-base-uncased`).
  - Creates HF dataset and train/test split.
  - Tokenizes text and trains via `Trainer`.
  - Saves model/tokenizer to the model directory.
- `preview_eval_predictions(...)`:
  - Runs a quick sample of predictions on eval data with confidence scores.

## src/bridgehead_ai/splunk_client.py
- `stream_splunk_search_results(config)`:
  - Connects to Splunk export endpoint in real-time mode.
  - Yields parsed `result` objects for downstream processing.
- `send_to_splunk(data, config)`:
  - Wraps AI output in Splunk HEC payload format and posts it.

## src/bridgehead_ai/realtime_inference.py
- `run_continuous_reader(model_path, config)`:
  - Loads fine-tuned model/tokenizer.
  - Streams new events from Splunk.
  - Filters to `cowrie.command.input` events.
  - Scores command text and sends enriched AI insight events back to HEC.
- Includes retry behavior for transient Splunk connection failures.

## scripts/generate_fake_logs.py
- CLI wrapper that writes synthetic data to `data/fake_logs.json`.

## scripts/train_model.py
- CLI wrapper for training workflow.
- Expects training data in `data/*.json` and writes model artifacts to `models/saved_distilbert_cowrie`.

## scripts/run_splunk_reader.py
- CLI wrapper for real-time inference.
- Loads `.env` values, then starts the continuous reader.

## Operational Notes
- All scripts are run from repository root.
- Generated logs and model artifacts are intentionally ignored by git.
- This modular layout makes it easier to plug in future Wazuh and full BridgeHead infrastructure components.
