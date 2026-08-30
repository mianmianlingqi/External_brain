# Agents propose from extracted text; the Brain does not store source files

Proposals come from text an Agent extracted, not from files the Brain holds. The Owner gives materials to an Agent; the Agent calls `propose_from_text` on exactly one Direction; the Owner accepts or rejects (ADR-0011). We rejected a Brain upload, storing original bytes or OCR dumps, a cross-Direction hopper, and treating a photo of a wrong answer as a Miss. The View stays read-only and does not receive files. This widens “pasted notes” in ADR-0010 and ADR-0011; it does not reverse accept-before-store.
