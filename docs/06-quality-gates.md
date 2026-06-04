# Quality gates

| Gate | Pass condition |
| --- | --- |
| Source gate | Metadata is complete enough to cite and source type is clear |
| Source-note gate | Summary, evidence, limits, and possible use are recorded |
| Claim gate | Claim type, evidence status, confidence, and counterevidence are marked |
| Chapter-brief gate | Purpose, main claim, sequence, sources, and gaps are visible |
| Draft gate | Draft uses notes and marks unsupported claims |
| Citation gate | Citekeys exist and page needs are marked |
| Red-team gate | Weak assumptions, overclaims, and counterarguments are listed |
| Continuity gate | Terms, claims, and argument order stay consistent |
| Commit hygiene gate | `make precommit-run` catches file hygiene, placeholder, citation, and internal-link problems without running release-only checks |
| Export gate | `make release-audit` passes and unresolved placeholders are reviewed |

Do not advance a draft by hiding a failed gate. Record the failure and the next fix.
