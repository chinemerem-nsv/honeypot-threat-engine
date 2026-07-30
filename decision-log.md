Decision Log

---

D-001

UTC Time: 2026-07-29 10:30:00 UTC

Decision: Adopt DuckDB as the core embedded SQL engine for log normalization and sessionization.

Evidence Used: Vectorized performance benchmarks, local file support, zero-external-service dependencies.

Alternatives Rejected: Pandas DataFrames, SQLite, PostgreSQL.

Assumption: The input JSONL dataset fits within local memory or disk-indexed streaming limits of DuckDB.

Owner: Pipeline Engineer

Review Trigger: Schema changes in raw honeypot event structures.

---

D-002

UTC Time: 2026-07-29 14:15:00 UTC

Decision: Exclude derived runtime deliverables (Parquet partitions, JSON clusters, STIX bundles) from Git version control.

Evidence Used: Git repository best practices, repository size efficiency, clean-build reproduction mandates.

Alternatives Rejected: Committing all 16 derived artifacts directly to the GitHub repository.

Assumption: Evaluators will execute the clean-build scripts from the README to reproduce deliverables from source.

Owner: Pipeline Engineer

Review Trigger: Changes in project grading or submission architecture guidelines.

---

D-003

UTC Time: 2026-07-29 09:45:00 UTC

Decision: Implement `.gitkeep` placeholder files inside `raw-export/` and `quarantine/` directory structures.

Evidence Used: Git behavior ignoring empty directory trees upon repository cloning.

Alternatives Rejected: Relying on manual directory creation or tracking empty folders without placeholders.

Assumption: Cloned directory paths must be pre-initialized for automated pipeline execution.

Owner: Pipeline Engineer

Review Trigger: Modifications to directory tree architecture.

---

D-004

UTC Time: 2026-07-29 16:00:00 UTC

Decision: Implement modular STIX 2.1 threat intelligence export via `export_stix.py`.

Evidence Used: Standardized threat interoperability and SOC framework requirements.

Alternatives Rejected: Custom JSON output formats without standard threat intelligence mapping.

Assumption: Downstream consumers require standardized indicators (STIX/TAXII compatible structures).

Owner: Pipeline Engineer

Review Trigger: Updates to threat taxonomy or schema requirements.

---

D-005

UTC Time: 2026-07-29 11:20:00 UTC

Decision: Enforce automated cryptographic sealing using SHA-256 hash ledgers and verification manifests.

Evidence Used: Chain-of-custody requirements, auditability during forensic defense.

Alternatives Rejected: Trusting unverified local file modifications.

Assumption: Evaluators will independently verify file integrity using the provided hash manifests.

Owner: Pipeline Engineer

Review Trigger: Changes to verification tooling or hashing algorithms.
