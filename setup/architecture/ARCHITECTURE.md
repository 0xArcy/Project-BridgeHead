# Project BridgeHead Architecture

## Overview

Project BridgeHead is a segmented enterprise lab built on Virt-Manager and centered around a DMZ, an internal network, and a routed perimeter enforced by pfSense. The environment supports both red-team operations and blue-team monitoring, with Cowrie, Splunk, Wazuh, and a custom DistilBERT-based classifier integrated into the workflow.

## Network Segments

| Segment | Purpose | Systems |
|---|---|---|
| DMZ | Internet-exposed and semi-exposed services | `10.0.10.104`, `10.0.10.105`, `10.0.10.106` |
| Internal Network | Monitoring, management, and internal services | `10.0.20.101`, `10.0.20.103` |
| Perimeter | Routing and segmentation | pfSense connected to WAN, DMZ, and Internal Network |

## Node Layout

| Zone | Host | IP | Role |
|---|---|---|---|
| DMZ | Ubuntu 24.04 | `10.0.10.105` | Cowrie, HTTP website frontend, SSH, Splunk forwarder, Wazuh agent |
| DMZ | Windows 10 jump server | `10.0.10.106` | Jump box, AI DistilBERT host, Splunk forwarder, Wazuh agent, website database services |
| DMZ | Ubuntu Server | `10.0.10.104` | Backend server for the website |
| Internal | Ubuntu Server | `10.0.20.101` | Splunk Enterprise, Wazuh manager, `vsftpd 2.3.2` |
| Internal | Windows Server | `10.0.20.103` | Wazuh agent, Splunk forwarder |
| Perimeter | pfSense | N/A | WAN edge, DMZ/Internal routing, network control point |

## Logical Flow

1. WAN-facing traffic reaches pfSense first.
2. pfSense routes allowed traffic into the DMZ.
3. The frontend host at `10.0.10.105` handles web traffic and also exposes monitored SSH/Cowrie activity.
4. Website backend processing is handled by `10.0.10.104`.
5. The Windows 10 jump server at `10.0.10.106` supports administration and hosts the AI classification workflow tied to Splunk.
6. Internal telemetry is centralized through `10.0.20.101`, which runs Splunk Enterprise and Wazuh Manager.
7. Additional Windows internal telemetry is forwarded from `10.0.20.103`.

## Security Monitoring Stack

### DMZ Collection

- Cowrie honeypot activity is generated on `10.0.10.105`.
- Splunk forwarders are deployed on DMZ systems.
- Wazuh agents are deployed on the Ubuntu 24.04 frontend and the Windows 10 jump server.

### Internal Monitoring

- `10.0.20.101` is the main monitoring node.
- Splunk Enterprise centralizes collected logs.
- Wazuh Manager aggregates host-based telemetry and alerts.

### AI Integration

- DistilBERT-based attacker-behavior classification is hosted on `10.0.10.106`.
- The AI pipeline enriches Cowrie/Splunk events to help distinguish recon activity, malware-dropping behavior, and human-interactive sessions.

## Operational Purpose

This architecture supports the full BridgeHead workflow:

- attack simulation from exposed services in the DMZ
- defensive logging and alerting across DMZ and internal hosts
- investigation through Splunk and Wazuh
- AI-assisted classification of Cowrie honeypot interactions
- validation of segmentation between exposed and internal assets

## Notes

- The uploaded architecture diagram is treated as the current source of truth for host placement and roles.
- `10.0.10.106` serves multiple functions in the current lab, including jump-host operations and AI-assisted monitoring support.
- `10.0.20.101` is a high-value internal node because it combines monitoring and additional service exposure (`vsftpd 2.3.2`).
