---
name: iosonand-tracker
description: Update the iOSOnAnd tracker (hackios.appaiproxy.com, device realme-8i) with evidence. Use when a change to this port makes a phone feature work (boot, touch, gpu, wifi, audio, ...) or breaks one, or when asked to sync, update or push progress to the tracker.
---

# Update the iOSOnAnd tracker for realme 8i

Device slug: `realme-8i`. Page: https://hackios.appaiproxy.com/device/realme-8i.
Full guide: `TRACKER.md` at the repo root.

Below, `T` stands for `node ~/.local/share/iosonand/cli.mjs`, run with `TRACKER_URL=https://hackios.appaiproxy.com` set.

1. **CLI.** If `~/.local/share/iosonand/cli.mjs` is missing, fetch it from the tracker (never into the repo):
   `mkdir -p ~/.local/share/iosonand && curl -fsSLo ~/.local/share/iosonand/cli.mjs https://hackios.appaiproxy.com/cli.mjs`.
   Run `T check`.
2. **Auth.** `T whoami` must show a login that maintains `realme-8i`. The
   token comes from `TRACKER_TOKEN` or the CLI's saved login. If neither
   exists, ask the user to run `T login` (GitHub via `gh`) or to set
   `TRACKER_TOKEN`. Never open, print, create or commit a file that holds a key.
3. **Current state.** `T status-get --device realme-8i`.
4. **Map the change to areas.** `T areas` for the exact slugs. Pick the state
   from the evidence: `works` shown working on the phone; `in-progress`
   partly working, or built but not yet run; `broken` shown failing or a
   regression; `unknown` nothing proven. Do not upgrade on a guess, and do
   not lower someone else's state without evidence.
5. **Record.** One call per area:
   `T status-set realme-8i <area> <state> --detail "<what the build, log or test showed>" --source <commit, CI run, log or PR URL>`,
   then read it back with `T status-get --device realme-8i --area <area>`.
   If the tracker is unreachable: `T queue status-set ...`, then `T flush` later.
6. **Media (optional).** `T update realme-8i <file> ... --text "what changed" --area <area>`.
   Crop out IMEI, serial numbers and personal data first.
7. **Report back.** Each area changed (old state to new), the detail and
   source used, anything queued, and any 401/403 with the CLI's hint.
