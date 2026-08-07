# Emergency Hard-Deactivate — Final Plan

**Moved (2026-07-06):** the final, signed-off consolidated build plan lives in [`AdminEverything.md`](AdminEverything.md) — that file is the single source of truth for this feature.

This file previously held a terminal copy-paste of the draft (including a duplicated boxed §9/§10 rendering artifact and the pre-signoff §4.2 wording). Both sign-off edits are applied in `AdminEverything.md`:

1. Duplicated boxed block removed (it was a paste artifact, not doc content).
2. §4.2 marker wording softened to "load-bearing for the official app flow, not a tamper-proof cryptographic boundary" — a marked machine may not self-recover offline *through the official app*; file-tampering attackers are the same class as custom unwrap tooling, already covered by the §1 honest limit.

Earlier drafts (`AdminEverything-Update.md`, `AdminEverything-GPT.md`) are superseded; the decision log in `AdminEverything.md` §2 records what was adopted and rejected from each.
