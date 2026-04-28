# BridgeHead AI: Cowrie + Splunk Threat Classification

This module trains and runs a DistilBERT-based classifier that labels Cowrie SSH command behavior and sends AI enrichments back into Splunk.

## Classification Labels

- `recon_bot`: scripted reconnaissance behavior
- `malware_dropper`: payload retrieval/execution behavior
- `human_interactive`: hands-on-keyboard interactive behavior

## Project Structure

```text
splunk-cowrie-ai/
├── data/                       # Input logs (JSONL)
├── docs/
│   ├── architecture.md
│   ├── code-walkthrough.md
│   └── source-code-reference.md
├── scripts/
│   ├── generate_fake_logs.py
│   ├── train_model.py
│   └── run_splunk_reader.py
├── src/bridgehead_ai/
│   ├── __init__.py
│   ├── data_generation.py
│   ├── training.py
│   ├── settings.py
│   ├── splunk_client.py
│   └── realtime_inference.py
├── .env.example
└── requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run Flow

1. Generate synthetic Cowrie logs (optional):
```bash
python scripts/generate_fake_logs.py
```

2. Train the model:
```bash
python scripts/train_model.py
```

3. Run real-time Splunk inference:
```bash
python scripts/run_splunk_reader.py
```

## Environment Variables

Configured via `.env`:
- `SPLUNK_REST_URL`
- `SPLUNK_USERNAME`
- `SPLUNK_PASSWORD`
- `SPLUNK_SEARCH_QUERY`
- `SPLUNK_HEC_URL`
- `SPLUNK_HEC_TOKEN`
- `SPLUNK_INDEX` (default `main`)

`run_splunk_reader.py` validates required fields before startup.

## Security Notes

- Current requests use `verify=False` for lab/self-signed cert compatibility.
- For production, enable TLS certificate verification and enforce least-privilege Splunk accounts.
- Rotate HEC tokens and credentials before any non-lab deployment.

## Documentation

- `docs/architecture.md`: pipeline architecture and threat-model context
- `docs/code-walkthrough.md`: concise module walkthrough
- `docs/source-code-reference.md`: file-by-file technical reference
