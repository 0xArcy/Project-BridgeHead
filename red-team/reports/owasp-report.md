# OWASP Top 10 Mapping Report

## 1.1 Executive Summary

This report maps the confirmed assessment results for the Modern Bank environment to the OWASP Top 10 2021 framework. The strongest conclusion is that the legacy environment was not affected by a single isolated weakness. The confirmed compromise path crossed several OWASP categories at once: insecure design in the upload workflow, injection-style code execution through attacker-controlled file content, weak access and trust boundaries after compromise, and broader misconfiguration across the exposed and internal tiers.

The secure runtime and remediation material now present in the workspace addresses the right areas. The purpose of this document is to show where the environment failed under OWASP language, what that meant operationally, and which controls should be treated as closure criteria.

> Headline judgment: the breach path is best understood as a stacked OWASP failure, not a single bug.

## 1.2 At-a-Glance Mapping

| OWASP 2021 Category | Assessment Position | Severity | Why It Matters |
| --- | --- | --- | --- |
| A01 Broken Access Control | Confirmed | High | A public compromise exposed internal access paths that should not have been reachable from the web tier |
| A02 Cryptographic Failures | Confirmed in legacy design | High | The migration record shows the legacy stack relied on cleartext inter-tier communication and weak secret handling |
| A03 Injection | Confirmed | Critical | The upload workflow allowed attacker-controlled content to become executable on the server |
| A04 Insecure Design | Confirmed | Critical | The original upload and trust model relied on unsafe assumptions rather than layered controls |
| A05 Security Misconfiguration | Confirmed | Medium | Missing headers, exposed content, weak service settings, and SMB signing gaps lowered attack cost |
| A07 Identification and Authentication Failures | Confirmed | High | Recovered credentials enabled authenticated backend access |
| A08 Software and Data Integrity Failures | Confirmed | High | Raw user-controlled file content was trusted and stored unsafely |
| A09 Security Logging and Monitoring Failures | Partially mitigated | Medium | Decoy telemetry existed, but it did not prevent the productive compromise path |

## 1.3 Confirmed Attack Chain in OWASP Terms

### Category Stack

The legacy path can be summarized in one line: an externally reachable application accepted untrusted file content, allowed execution on the public tier, exposed valid internal credentials, and permitted movement into the backend environment.

From an OWASP perspective, that chain is best understood as a stacked failure:

1. A04 Insecure Design created the unsafe upload model.
2. A03 Injection and A08 Software and Data Integrity Failures turned that model into executable abuse.
3. A07 Identification and Authentication Failures and A01 Broken Access Control allowed the foothold to expand.
4. A05 Security Misconfiguration increased reconnaissance value and reduced attacker effort.
5. A09 Security Logging and Monitoring Failures was not a total failure, but monitoring remained secondary to prevention and containment.

## 1.4 Detailed Category Assessment

### A01 Broken Access Control

The assessment confirmed that compromise of the public application tier exposed access paths that should have remained isolated from external influence. Once the web server was under attacker control, internal service details and credentials were available and accepted by 10.0.10.102.

Management reading: the boundary between the public application and the internal tier was too weak. A compromise at the edge should not have translated so quickly into authenticated internal reach.

Closure expectation:

- remove legacy trust paths from reachable deployment
- restrict backend reachability to approved frontend paths only
- validate identity and authorization at each internal boundary

### A02 Cryptographic Failures

The migration hardening report states that the legacy three-tier design communicated in cleartext and handled credentials weakly. That legacy position is directly relevant because it shows that encryption and secret protection were not foundational controls in the original design.

Management reading: even without the upload flaw, weak transport and poor secret handling would have increased breach impact and reduced containment confidence.

Closure expectation:

- TLS enforced at the edge, backend, and database tiers
- secure cookie handling and secret rotation
- no plaintext credential storage or distribution practice

### A03 Injection

This was the primary exploitation class. The avatar upload workflow accepted attacker-controlled content that was then used to achieve server-side execution on 10.0.10.105. This is the most severe issue in the report and the main reason the overall rating is Critical.

Management reading: a normal web feature could be converted into code execution by an external user.

Closure expectation:

- strict server-side validation
- content normalization and rewrite for accepted image types
- storage outside web root
- controlled authenticated retrieval instead of direct serving

### A04 Insecure Design

The core failure was architectural, not cosmetic. The original upload process relied on unsafe assumptions about file type, storage location, and execution risk. The evidence shows the design did not require multiple independent controls before user content reached a sensitive execution context.

Management reading: the old workflow was unsafe by design, not merely under-patched.

Closure expectation:

- redesign the upload path as a layered trust decision
- isolate storage from executable content paths
- verify design controls before deployment, not after exploitation

### A05 Security Misconfiguration

Nmap, Nikto, and Nessus evidence added several misconfiguration indicators around the environment: missing browser hardening headers, accessible configuration-related content, weak SSH options, SMB signing not required on the Windows tier, and information disclosure through ICMP timestamps.

Management reading: these issues were not the decisive breach mechanism, but they reduced attacker effort and signaled inconsistent baseline control.

Closure expectation:

- enforce web security headers and directory restrictions
- harden SSH exposure on Internet-reachable hosts
- require SMB signing on 10.0.10.106
- remove unnecessary information leakage where practical

### A07 Identification and Authentication Failures

The assessment confirmed that credentials exposed on the compromised application tier were usable against 10.0.10.102. That means internal authentication material was both exposed and over-trusted.

Management reading: the environment did not sufficiently limit the value of compromised credentials.

Closure expectation:

- rotate all exposed secrets and tokens
- constrain service identities to least privilege
- separate user, service, and administrative trust paths

### A08 Software and Data Integrity Failures

The upload workflow trusted raw user-supplied bytes too early in the process. That is an integrity-control failure as much as an input-validation failure. The remediation report correctly shifts the model toward parsing, rewriting, private storage, and controlled retrieval.

Management reading: untrusted content was allowed too close to sensitive execution and storage paths.

Closure expectation:

- accept only known-safe file types
- decode and rewrite accepted images
- isolate upload storage and prevent direct execution

### A09 Security Logging and Monitoring Failures

This category is mixed rather than purely negative. Splunk and Cowrie captured TCP/2222 activity and produced useful telemetry, including classifier output around attacker behavior. That was valuable detection coverage. The problem is that the productive compromise path did not depend on that monitored route.

Management reading: monitoring existed, but it did not compensate for the exposed application path.

Closure expectation:

- preserve deception and centralized logging
- increase coverage of web-application exploitation and credential abuse events
- treat monitoring as confirmation and triage support, not as a substitute for preventive control

## 1.5 Priority Remediation Order

| Priority | Theme | Required Change |
| --- | --- | --- |
| 1 | Eliminate A03 and A04 exposure | Remove the legacy upload path or replace it with the remediated design |
| 2 | Break A07 expansion risk | Rotate credentials, tokens, and secrets exposed on the web tier |
| 3 | Enforce A01 boundaries | Restrict backend access and validate service trust paths |
| 4 | Close A02 legacy risk | Complete TLS and secure-cookie implementation across all tiers |
| 5 | Reduce A05 noise | Harden SSH, SMB, headers, and information disclosure settings |
| 6 | Improve A09 assurance | Expand logging around web abuse and internal trust-boundary failures |

## 1.6 Target-State Alignment

### Closure Standard

The secure runtime architecture, migration hardening report, and upload-remediation document align well to the OWASP issues above. In particular, they introduce layered upload validation, content rewriting, private file storage, authenticated retrieval, TLS-protected inter-tier communication, stronger authentication handling, and clearer segmentation between frontend, backend, and database roles.

That alignment is important, but it is not itself closure. Closure requires deployed implementation, secret rotation, and retesting against the original compromise chain.

> Management reading: the OWASP gaps are understood and the control design is directionally correct; the open question is execution quality, not diagnosis.

## 1.7 Conclusion

The OWASP view of this assessment is clear. The confirmed attack path was driven by insecure design and exploitability in a public-facing workflow, then amplified by weak internal trust boundaries and inconsistent configuration. The remediation direction is correct. The remaining task is to convert that design into verified operational control.

## References

- [technical-appendix.md](technical-appendix.md)
- [executive-report.md](executive-report.md)
- [FILE_UPLOAD_REMEDIATION_OWASP_CVE.md](../../setup/target-environment/FILE_UPLOAD_REMEDIATION_OWASP_CVE.md)
- [SECURITY_MIGRATION_REPORT.md](../../setup/target-environment/SECURITY_MIGRATION_REPORT.md)
- [ARCHITECTURE.md](../../setup/architecture/ARCHITECTURE.md)
- [VULNERABILITIES.md](../../setup/target-environment/VULNERABILITIES.md)
- [Splunk_Cowrie-2026-04-09.pdf](../../blue-team/monitoring/splunk/Splunk_Cowrie-2026-04-09.pdf)
- [nessus-10.0.10.105.pdf](../scans/nessus/nessus-10.0.10.105.pdf)
- [nessus-10.0.10.102.pdf](../scans/nessus/nessus-10.0.10.102.pdf)
- [nessus-10.0.10.106.pdf](../scans/nessus/nessus-10.0.10.106.pdf)