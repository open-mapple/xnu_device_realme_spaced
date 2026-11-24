# Agent instructions

## iOSOnAnd tracker

This port is tracked at https://hackios.appaiproxy.com/device/realme-8i (slug `realme-8i`).
When a change makes an area work, or breaks one that worked, update the
tracker in the same session. Details and examples are in `TRACKER.md`.

- CLI: `node ~/.local/share/iosonand/cli.mjs` (from https://hackios.appaiproxy.com/cli.mjs) with `TRACKER_URL=https://hackios.appaiproxy.com`. Never download it into the repo.
- Read first: `status-get --device realme-8i`, and `areas` for the exact slug.
- Record: `status-set realme-8i <area> <works|in-progress|broken|unknown> --detail "<what the build, log or test showed>" --source <commit, CI run or log URL>`, then read it back.
- Auth comes from `TRACKER_TOKEN` or the CLI's saved login (`login`). Never
  write a key into a file in the repo, a commit or a `--detail`.
- Only record what was observed on the phone or in CI; unproven stays
  `unknown`. Do not lower someone else's state without evidence.
- Offline: `queue status-set ...` now, `flush` later.
