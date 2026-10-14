# data_private

This folder is for unpublished measurements from the fab.

- **Release from the custodian.** Data arrive here only after the custodian (the fab) releases them, and, for holdout data, only after the matching prediction has been registered and timestamped.
- **AI consent.** Do not add data here until the fab has agreed that AI tools (Claude, Codex, Astra) may read them (task HUM-001).
- **Raw files.**
  - Keep raw files exactly as received, in `raw/<date>_<description>/`.
  - Add a `MANIFEST.md` that gives the sender, the date, the SHA-256 of each file, the devices and the measurement conditions.
- **Derived files.** Derived files go in `derived/`, made by scripts. Never edit anything in `raw/`.
- **Size.** Files over 50 MB need Git LFS or a pointer to where they are stored. Do not commit them directly.
