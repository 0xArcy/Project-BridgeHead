# Project BridgeHead AI Architecture

## Scope of This Repository (Current)
This repository currently contains the AI component of Project BridgeHead:
- Cowrie SSH honeypot command ingestion
- DistilBERT fine-tuning for threat-tier classification
- Continuous Splunk streaming inference and HEC feedback loop

The broader lab setup (6 VMs on Virt-manager, attack/defense operations, Wazuh workflows) can be added into this repository later as additional directories and documentation.

## Threat Labels
The model predicts one of three labels:
- `recon_bot` (0): scripted recon behavior
- `malware_dropper` (1): payload download/execute behavior
- `human_interactive` (2): hands-on-keyboard operator behavior

## Data Flow
1. Cowrie logs are collected as JSONL events.
2. Training pipeline groups commands by `session` and applies heuristic bootstrapping labels.
3. DistilBERT (`distilbert-base-uncased`) is fine-tuned for 3-class sequence classification.
4. A real-time Splunk export search streams events to the inference process.
5. Each `cowrie.command.input` event is scored and AI insights are sent back to Splunk HEC.

## Code Structure
- `src/bridgehead_ai/data_generation.py`: synthetic Cowrie log generation.
- `src/bridgehead_ai/training.py`: parsing, heuristic labels, fine-tuning, and evaluation preview.
- `src/bridgehead_ai/splunk_client.py`: Splunk REST stream and HEC sender helpers.
- `src/bridgehead_ai/realtime_inference.py`: continuous scoring loop.
- `src/bridgehead_ai/settings.py`: `.env` loading and Splunk config object.
- `scripts/train_model.py`: train entry point.
- `scripts/generate_fake_logs.py`: data generation entry point.
- `scripts/run_splunk_reader.py`: continuous inference entry point.

## Security Notes
- SSL verification is currently disabled for Splunk API calls (`verify=False`) for lab compatibility.
- For production, use trusted certificates and set `verify=True`.
- Use least-privilege Splunk credentials and rotate HEC tokens.

## Extension Plan for Full BridgeHead Repo
Recommended top-level additions when you drop the remaining content:
- `infra/`: VM topology, network diagrams, provisioning scripts.
- `detections/`: Sigma/Splunk detection rules and hunts.
- `wazuh/`: Wazuh agent/server configs and correlation notes.
- `red-team/reports/`: attack timeline and formal findings.
- `setup/`: architecture, migration, and governance context.
