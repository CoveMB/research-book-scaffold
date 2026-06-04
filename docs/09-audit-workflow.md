# Audit workflow

Store audit notes in `notes/08-audits/`.

| Audit | Checks |
| --- | --- |
| Claim audit | Claims have evidence status, confidence, and safer wording |
| Citation audit | Citekeys exist and match the claim being supported |
| Source-quality audit | Source type, limits, bias risk, and fit are clear |
| External-reference audit | External URLs, DOIs, and optional archive coverage have been checked with warnings separated from likely failures |
| Counterargument audit | Strong objections and rival readings are recorded |
| Bias and assumption audit | Hidden assumptions and framing risks are marked |
| Continuity audit | Terms, claims, and sequence stay consistent |
| Final manuscript audit | Placeholders, citations, claims, and exports are ready |

Each audit includes scope, findings, severity, required fixes, decision, and follow-up.

Use `make check-external-references` only when a network-dependent reference check is useful for the audit scope. It is not part of the fast audit or release audit because network failures, rate limits, paywalls, and resolver outages can create noisy results.
