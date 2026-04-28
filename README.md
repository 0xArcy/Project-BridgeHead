# Project BridgeHead

Project BridgeHead is a full lab-based cyber operation where we simulated an enterprise on a mini PC using Virt-Manager, attacked it as a red team, defended and hardened it as a blue team, and built an AI-assisted detection workflow using Cowrie + Splunk.

This repository is intentionally organized for public portfolio review.

## Lab Summary

- Environment: 6 VM enterprise simulation
- Platform: Virt-Manager / libvirt on mini PC
- Core scenario: vulnerable banking application compromised from public edge to internal systems
- Defensive response: endpoint hardening + architecture migration + monitoring
- AI component: DistilBERT pipeline classifying SSH honeypot behavior in real time

## Exact Repository Structure

Only three primary project directories are used:

```text
.
├── setup/
├── red-team/
└── blue-team/
```

Everything in the repo sits under one of those three categories.

## Where To Start Reading

If you are opening this repository for the first time:

1. Read this file fully.
2. Open `red-team/reports/executive-report.md`.
3. Open `setup/architecture/ARCHITECTURE.md`.
4. Open `blue-team/ai/splunk-cowrie-ai/README.md`.
5. Dive into raw evidence and notebooks.

## Setup Folder (Environment + Architecture)

`setup/` contains artifacts that describe how the environment was designed, deployed, and migrated.

### `setup/architecture/`

- `ARCHITECTURE.md`
- `Architecture.pdf`

### `setup/target-environment/`

This contains the vulnerable app analysis and migration docs:

- `KILL_CHAIN.md`
- `VULNERABILITIES.md`
- `SECURITY_MIGRATION_REPORT.md`
- `FILE_UPLOAD_REMEDIATION_OWASP_CVE.md`
- `BRAND_PACK.md`

## Red Team Folder (Attack, Recon, Pentest, Nessus)

`red-team/` contains offensive testing data and final offensive reporting.

### `red-team/scans/nessus/`

This is where Nessus lives:

- `nessus-10.0.10.102.pdf`
- `nessus-10.0.10.105.pdf`
- `nessus-10.0.10.106.pdf`

### `red-team/evidence/`

Curated screenshots from exploitation and post-exploitation context:

- `exposed-sensitive-env-file.png`
- `exposed-sensitive-information.png`
- `frontend-proxy-service-token.png`

### `red-team/notes/ctb-export/`

Raw CherryTree export of the operation notebook.

Start at:
- `red-team/notes/ctb-export/index.html`

Contains:
- phase-by-phase HTML notes
- embedded screenshots in `red-team/notes/ctb-export/images/`

### `red-team/reports/`

Main report set (markdown only, no duplicate PDF copies):

- `executive-report.md`
- `pentest-report.md`
- `rules-of-engagement.md`
- `owasp-report.md`
- `technical-appendix.md`

## Blue Team Folder (Defense + Monitoring + AI)

`blue-team/` contains defensive hardening artifacts and AI monitoring integration.

### `blue-team/endpoint-hardening/windows-endpoint/`

Windows hardening evidence:

- Defender status/config/events (`.png` + `.txt`)
- Firewall rule sets (`.png` + `.txt`)
- UAC settings evidence

### `blue-team/monitoring/splunk/`

Splunk monitoring evidence:

- `splunk-dashboard-overview.png`
- `splunk-ioc-ubuntu-dmz.png`
- `Splunk_Cowrie-2026-04-09.pdf`

### `blue-team/ai/splunk-cowrie-ai/`

This is the AI implementation folder.

Key paths:

- `src/bridgehead_ai/training.py`
- `src/bridgehead_ai/realtime_inference.py`
- `src/bridgehead_ai/splunk_client.py`
- `src/bridgehead_ai/settings.py`
- `scripts/train_model.py`
- `scripts/run_splunk_reader.py`

What it does:

- ingests Cowrie command events
- trains DistilBERT classifier for behavior classes
- streams Splunk events for realtime scoring
- writes AI enrichment events back into Splunk HEC

Classification labels:

- `recon_bot`
- `malware_dropper`
- `human_interactive`

## Why Markdown-Only Reports

You requested cleaner organization and no duplicated `same-name.md` + `same-name.pdf` clutter.

This repo now keeps report content in markdown only for:

- direct GitHub readability
- easier diff/review in commits
- lower visual clutter for portfolio visitors

## Fast Navigation Cheatsheet

- Want architecture setup? `setup/architecture/ARCHITECTURE.md`
- Want vulnerabilities/migration? `setup/target-environment/`
- Want Nessus? `red-team/scans/nessus/`
- Want raw attack notebook? `red-team/notes/ctb-export/index.html`
- Want pentest narrative? `red-team/reports/pentest-report.md`
- Want blue-team AI code? `blue-team/ai/splunk-cowrie-ai/src/bridgehead_ai/`
- Want Splunk monitoring evidence? `blue-team/monitoring/splunk/`

## Notes

- All credentials shown are lab-only and intentionally insecure for simulation.
- The CherryTree export is preserved in raw form for timeline integrity.
- This repo is now structured for portfolio consumption first, and deep technical review second.
