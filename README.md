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
