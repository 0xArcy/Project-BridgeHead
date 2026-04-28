# Rules of Engagement Report

## 1.1 Executive Summary

This document records the Rules of Engagement position reflected in the assessment notes and aligns those boundaries with the final interpretation of the test results. The most important point is that the productive compromise path stayed inside the authorized web-testing scope. The assessment was driven through the public application on 10.0.10.105, while SSH activity on TCP/2222 was treated as constrained and unsuitable for brute-force testing.

That distinction matters because it keeps the final report accurate. The strongest evidence supports a web-application compromise followed by credential exposure and backend access. It does not support a claim that SSH brute-force or decoy interaction was the core intrusion route.

> Headline judgment: the assessment result is stronger, not weaker, because the confirmed compromise was achieved without stepping outside the approved web-testing path.

## 1.2 At-a-Glance Position

| Topic | Rules of Engagement Position |
| --- | --- |
| Primary authorized path | Public web application testing on TCP/80 |
| Constrained path | SSH service on TCP/2222 |
| Brute-force status | Not authorized for SSH |
| Productive compromise route | Web application upload flaw on 10.0.10.105 |
| Follow-on activity | Limited validation of credential exposure, backend access, and internal enumeration |
| Evidence handling | Findings treated as confirmed only where notes, screenshots, or imported reports support them |
| Reporting standard | Evidence-led, conservative interpretation, no inflation of unconfirmed paths |

## 1.3 Engagement Objective

The recorded objective was to assess whether the exposed application path could be used to compromise the environment and whether that compromise could affect connected internal systems. The notes show that the assessment was organized as a staged chain across the public host, backend host, and Windows data tier, rather than as isolated one-off tests.

## 1.4 Scope

The evidence set supports the following scope interpretation.

| Asset | Role in Assessment | Scope Reading |
| --- | --- | --- |
| 10.0.10.105 | Public-facing web application tier | Primary in-scope target |
| 10.0.10.102 | Internal backend host | In-scope for validation after authorized foothold |
| 10.0.10.106 | Internal Windows host | In-scope for follow-on reconnaissance and hardening review |
| TCP/80 on 10.0.10.105 | Web application surface | Authorized primary attack surface |
| TCP/2222 on 10.0.10.105 | SSH-like monitored service | Constrained surface, not a brute-force target |

## 1.5 Authorized Methods

The assessment record supports the use of standard penetration testing methods within the approved path.

- network and service discovery
- web application enumeration and manual review
- vulnerability validation against the public application
- controlled exploitation to confirm impact
- limited post-compromise validation sufficient to confirm credential exposure and backend access
- internal host reconnaissance required to understand business impact
- monitoring and log review to correlate attacker activity with defensive visibility

## 1.6 Restricted Methods and Boundaries

### Scope Control That Matters Most

The notes include an explicit threat-model statement that should be carried forward into the final engagement record.

```text
Primary Vector: Modern Bank web application (Port 80)
Secondary Vector: SSH service on Port 2222
Automated credential brute-forcing on SSH strictly prohibited
```

This is the most important Rules of Engagement control in the evidence. It means the report should not imply that aggressive SSH password attacks were permitted or required to prove impact.

The evidence also supports the following practical boundaries:

- no destructive action was required to prove the central findings
- the retained notes focus on access validation and limited enumeration rather than service disruption
- attempted SQL injection and directory traversal checks were documented, but they were not overstated as confirmed compromise routes
- decoy telemetry was observed and reported, but not misrepresented as proof of successful intrusion

## 1.7 Engagement Conduct Assessment

The assessment record is consistent with a controlled engagement.

| Conduct Area | Assessment |
| --- | --- |
| Scope discipline | The workflow stayed focused on the public web path first and internal validation second |
| Escalation logic | Internal testing followed confirmed compromise evidence rather than speculative scanning |
| Evidence standard | The reporting approach distinguishes confirmed results from attempted-only vectors |
| Decoy awareness | TCP/2222 activity was recognized as monitored or deceptive and not used to overstate the intrusion story |
| Business-risk focus | The notes stayed centered on the path that produced real access and meaningful impact |

## 1.8 Impact on Report Interpretation

Rules of Engagement affects how the results should be read by management and reviewers.

1. The main issue is the web application compromise path, because that was both authorized and successful.
2. TCP/2222 telemetry is useful supporting evidence for detection maturity, but not the headline breach mechanism.
3. Attempted vectors such as SQL injection and directory traversal should remain in the record as tested paths, not inflated findings.
4. Backend access is still a valid conclusion because it followed the authorized initial foothold and was supported by captured evidence.

## 1.9 Tooling Within Scope

The following tools and platforms appear in the evidence record and are consistent with the engagement boundaries.

| Tool or Platform | Role |
| --- | --- |
| Nmap | Service and exposure discovery |
| Nikto | Web hardening review |
| OWASP ZAP | HTTP-layer inspection and application review |
| Caido | Proxy-assisted exploitation workflow |
| curl | Direct request validation |
| PHP payload testing | Minimal upload-based impact validation |
| Metasploit and Meterpreter | Limited follow-on validation after access confirmation |
| Nessus | Supplemental host hardening assessment |
| Splunk and Cowrie | Monitoring correlation and decoy telemetry review |

## 1.10 Assurance Notes

The Rules of Engagement position strengthens the credibility of the final deliverable. The notes show that the tester did not need uncontrolled or prohibited activity to produce a meaningful result. The compromise path was available through the intended application surface, and the supporting telemetry was interpreted conservatively rather than opportunistically.

> Assurance reading: this is a disciplined engagement record, not an overstated attack story.

## 1.11 Conclusion

The engagement boundaries were clear enough to support a defensible conclusion: the legacy web application path was the authorized and productive route into the environment, while the SSH decoy path remained secondary and constrained. That is the correct frame for both management reporting and remediation planning.

## References

- [technical-appendix.md](technical-appendix.md)
- [executive-report.md](executive-report.md)
- [KILL_CHAIN.md](../../setup/target-environment/KILL_CHAIN.md)
- [Splunk_Cowrie-2026-04-09.pdf](../../blue-team/monitoring/splunk/Splunk_Cowrie-2026-04-09.pdf)