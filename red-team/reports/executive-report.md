# Executive Report

## 1.1 Decision Snapshot

This assessment confirmed a practical external-to-internal compromise path in the Modern Bank legacy environment. A public-facing upload workflow on 10.0.10.105 allowed server-side code execution, exposed valid internal credentials, and enabled authenticated access to the backend host at 10.0.10.102. Follow-on review also identified host-hardening gaps on 10.0.10.105 and 10.0.10.106.

The key management point is simple: the legacy stack did not fail at one control. It failed across application design, credential handling, and internal trust boundaries. The secure architecture and migration material now present in the workspace is materially stronger, but it should be treated as a target state until implementation, secret rotation, and retesting are complete.

> Headline judgment: the legacy environment allowed a public web weakness to become an internal access event with limited resistance.

## 1.2 At-a-Glance Summary

| Area | Executive Position |
| --- | --- |
| Overall rating | Critical |
| Primary entry point | Public web application on 10.0.10.105 |
| Confirmed business issue | External user reached code execution and then internal authenticated access |
| Most important weakness | Unrestricted file upload leading to remote code execution |
| Internal impact | Credentials recovered on the web tier were accepted by 10.0.10.102 |
| Detection position | TCP/2222 generated useful decoy telemetry, but it was not the productive intrusion route |
| Required response | Remove legacy exposure, rotate secrets, validate secure-state migration, and retest |

## 1.3 What Happened

The evidence supports a clean attack narrative.

1. External reconnaissance identified the public application and its supporting services on 10.0.10.105.
2. The avatar upload workflow accepted attacker-controlled content and allowed execution on the web tier.
3. The compromised application exposed credentials and internal service details.
4. Those credentials were then used successfully against 10.0.10.102.
5. Internal visibility expanded toward 10.0.10.106.

The SSH service on TCP/2222 generated logs and classifier output through Cowrie and Splunk, but the evidence shows that this path was monitored noise rather than the route that produced the confirmed backend compromise.

## 1.4 Why This Matters

### Business Position

In a banking environment, this weakness class is high consequence even before fraud or destructive activity is observed. A public foothold that leads to internal authenticated access can affect service trust, incident-response cost, regulatory reporting, and management's ability to prove containment. The concern is not only initial compromise. It is the collapse of separation between the exposed tier and the internal tier.

## 1.5 Material Findings

| ID | Finding | Affected Assets | Severity | CVSS v3.1 | Executive Meaning |
| --- | --- | --- | --- | --- | --- |
| EX-01 | Insecure file upload enabled remote code execution | 10.0.10.105 | Critical | 9.8 | A public user could convert normal application access into server compromise |
| EX-02 | Exposed credentials enabled backend access | 10.0.10.105, 10.0.10.102 | Critical | 9.1 | Initial compromise immediately crossed into the internal tier |
| EX-03 | Weak web hardening lowered attack cost | 10.0.10.105 | Medium | 5.3 | Missing headers and exposed content reduced attacker effort |
| EX-04 | SMB signing not required | 10.0.10.106 | Medium | 5.3 | The Windows tier remained more exposed to relay-style abuse than it should be |
| EX-05 | SSH hardening gaps | 10.0.10.105 | Low | 3.7 / 3.7 / 2.6 | Internet-reachable service posture remained weaker than necessary |
| EX-06 | ICMP timestamp disclosure | 10.0.10.102, 10.0.10.106 | Low | 2.1 | Low direct impact, but useful to attackers during profiling |

## 1.6 Control Failure Pattern

The compromise worked because several controls failed together.

| Control Layer | Legacy Outcome | Management Reading |
| --- | --- | --- |
| Input handling | Upload validation was not sufficient to prevent executable content | The public application could be weaponized |
| Secrets handling | Credentials and internal details were exposed after foothold | The web tier became a launch point into the estate |
| Internal trust boundary | Recovered credentials were accepted by the backend host | Public compromise was not contained |
| Host hardening | Additional SSH, SMB, and information-leak weaknesses remained | Baseline security discipline was inconsistent |
| Monitoring | Cowrie and Splunk captured decoy traffic | Detection existed, but prevention and segmentation were not strong enough |

## 1.7 Current State Versus Target State

### Target-State Direction

The workspace now includes a secure runtime architecture, a migration hardening report, and a detailed upload remediation plan. Together they define the correct direction of travel:

- JavaScript frontend behind an Nginx TLS edge
- Node.js or Express backend over HTTPS
- MongoDB with TLS and authentication
- stronger secrets handling and service-to-service trust
- upload isolation, image normalization, and controlled file serving

This target state addresses the main failure pattern seen during the assessment. The remaining issue is delivery discipline. Until the legacy path is removed from reachable deployment, exposed credentials are rotated, and the hardened design is retested against the original attack chain, the risk should not be considered closed.

> Management reading: the design response is credible, but the risk remains open until the legacy path is removed, secrets are rotated, and the original chain fails on retest.

## 1.8 Rules of Engagement Note

The assessment record contains explicit Rules of Engagement guidance that matters to management interpretation. The authorized primary path was the web application on TCP/80. SSH activity on TCP/2222 was constrained and not a brute-force target. That boundary matters because it confirms the core business issue was the exposed application, not the monitored decoy service.

## 1.9 Immediate Actions

### First 30 Days

| Priority | Action | Outcome Sought |
| --- | --- | --- |
| 1 | Remove or isolate the vulnerable legacy upload path from any reachable deployment | Close the confirmed initial access route |
| 2 | Rotate all credentials and trust tokens exposed on 10.0.10.105 | Break the confirmed pivot path into 10.0.10.102 |
| 3 | Validate the secure runtime implementation in the live environment | Confirm the target-state design exists in practice, not only on paper |
| 4 | Enforce SMB signing and complete Windows host hardening on 10.0.10.106 | Reduce downstream abuse risk inside the estate |
| 5 | Preserve decoy monitoring, but strengthen preventive controls and segmentation | Improve both detection and containment |
| 6 | Retest the upload workflow, credential model, and service trust boundaries | Obtain assurance that the original chain no longer works |

## 1.10 Management Conclusion

The assessment found a credible compromise path from the public edge into the internal environment. That is the headline issue. The positive counterpoint is that the remediation material now available in the workspace is aligned to the real failure pattern and, if implemented correctly, would materially improve resilience. The next decision is operational rather than analytical: complete the migration, rotate secrets, remove legacy exposure, and verify closure through targeted retesting.

## 1.11 Supporting Evidence

The technical detail, command output, screenshots, Nessus references, monitoring evidence, and integrated operator notes are preserved in the companion appendix and supporting reports.

## References

- [technical-appendix.md](technical-appendix.md)
- [owasp-report.md](owasp-report.md)
- [rules-of-engagement.md](rules-of-engagement.md)
- [ARCHITECTURE.md](../../setup/architecture/ARCHITECTURE.md)
- [SECURITY_MIGRATION_REPORT.md](../../setup/target-environment/SECURITY_MIGRATION_REPORT.md)
- [FILE_UPLOAD_REMEDIATION_OWASP_CVE.md](../../setup/target-environment/FILE_UPLOAD_REMEDIATION_OWASP_CVE.md)
- [nessus-10.0.10.105.pdf](../scans/nessus/nessus-10.0.10.105.pdf)
- [nessus-10.0.10.102.pdf](../scans/nessus/nessus-10.0.10.102.pdf)
- [nessus-10.0.10.106.pdf](../scans/nessus/nessus-10.0.10.106.pdf)
- [Splunk_Cowrie-2026-04-09.pdf](../../blue-team/monitoring/splunk/Splunk_Cowrie-2026-04-09.pdf)