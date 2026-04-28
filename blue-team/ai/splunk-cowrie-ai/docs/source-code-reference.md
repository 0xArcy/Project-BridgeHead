# Source Code Reference

This document explains every code file in the `splunk-cowrie-ai` module.

## `src/bridgehead_ai/settings.py`

Responsibility:
- Centralized environment loading and Splunk config modeling.

Key elements:
- `SplunkConfig` dataclass stores REST and HEC settings.
- `missing_required()` validates mandatory connection fields.
- `load_splunk_config()` loads `.env` variables through `python-dotenv`.

Why it matters:
- Keeps configuration logic out of runtime and training paths.

## `src/bridgehead_ai/data_generation.py`

Responsibility:
- Generates synthetic Cowrie-style JSONL logs for bootstrapping and testing.

Key elements:
- `generate_fake_logs(...)` emits session lifecycle events:
  - `cowrie.session.connect`
  - `cowrie.login.success`
  - `cowrie.command.input`
  - `cowrie.session.closed`
- Behavior pools are split across recon, dropper, and interactive patterns.

Why it matters:
- Supports demonstration/training when real honeypot volume is limited.

## `src/bridgehead_ai/training.py`

Responsibility:
- Build training examples from Cowrie logs and fine-tune DistilBERT.

Key elements:
- `_infer_label_from_session_text(text)`:
  heuristic bootstrap label assignment.
- `load_cowrie_logs(file_paths)`:
  reads JSONL, groups commands by session, and produces `(texts, labels)`.
- `fine_tune_distilbert(...)`:
  tokenizes dataset, performs train/eval split, trains `DistilBertForSequenceClassification`, saves artifacts.
- `preview_eval_predictions(...)`:
  prints sample predictions with confidence.

Implementation notes:
- Requires at least 5 sessions for stable train/eval split.
- Uses `evaluation_strategy="epoch"` and `save_strategy="epoch"`.

## `src/bridgehead_ai/splunk_client.py`

Responsibility:
- Splunk I/O helpers.

Key elements:
- `stream_splunk_search_results(config)`:
  connects to Splunk real-time export endpoint and yields parsed `result` objects.
- `send_to_splunk(data, config)`:
  sends enriched events to Splunk HEC.

Why it matters:
- Isolates external API behavior from model inference logic.

## `src/bridgehead_ai/realtime_inference.py`

Responsibility:
- Continuous model inference loop over Splunk stream.

Key elements:
- `_score_command(...)`:
  runs tokenizer + model inference and returns `(label, confidence)`.
- `run_continuous_reader(model_path, config)`:
  loads model/tokenizer, streams events, filters for `cowrie.command.input`, enriches and sends AI results to HEC.

Operational behavior:
- Handles transient Splunk connectivity errors with retry/backoff loop.

## `scripts/generate_fake_logs.py`

Responsibility:
- CLI entrypoint for fake log generation.

Behavior:
- Writes output to `data/fake_logs.json`.

## `scripts/train_model.py`

Responsibility:
- CLI entrypoint for model training.

Behavior:
- Reads JSONL logs from `data/`.
- Saves model artifacts to `models/saved_distilbert_cowrie`.
- Prints sample evaluation predictions.

## `scripts/run_splunk_reader.py`

Responsibility:
- CLI entrypoint for real-time inference service.

Behavior:
- Loads `.env` configuration.
- Fails fast if required Splunk config fields are missing.
- Starts continuous inference loop.

## `src/bridgehead_ai/__init__.py`

Responsibility:
- Package metadata and explicit module exports through `__all__`.

## `requirements.txt`

Dependencies:
- `transformers`, `datasets`, `torch`, `numpy`, `accelerate`
- `requests`, `python-dotenv`, `urllib3`

## Suggested Next Engineering Steps

1. Replace heuristic labels with human-reviewed labels for higher fidelity.
2. Add unit tests for parser, labeler, and Splunk client behavior.
3. Add Docker packaging and systemd service templates for deployment.
4. Add model evaluation metrics beyond accuracy (precision/recall/F1 per class).
