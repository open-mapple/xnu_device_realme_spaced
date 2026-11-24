# iOSOnAnd tracker

[iOSOnAnd](https://hackios.appaiproxy.com) is a community tracker of which Android phones run iOS
ports and what works on each. Every area of a phone (boot, wifi, gpu, touch,
audio, ...) has a state, a one-line detail and a source link.

This port's page: https://hackios.appaiproxy.com/device/realme-8i (realme 8i, Helio G96 (MT6781); device slug `realme-8i`).

It is part of Open Mapple, whose page lists every phone and repo built on it: https://hackios.appaiproxy.com/?tab=repos&family=Open%20Mapple.

The tracker is updated with its command-line client, `cli.mjs` (Node 18
or newer, no dependencies), served by the tracker at https://hackios.appaiproxy.com/cli.mjs. This
file covers setup and the commands this repo uses. `node ~/.local/share/iosonand/cli.mjs --help` lists all
of them.

## One-time setup

Keep the CLI outside the repo:

```sh
mkdir -p ~/.local/share/iosonand
curl -fsSLo ~/.local/share/iosonand/cli.mjs https://hackios.appaiproxy.com/cli.mjs
```

Point it at the live tracker (without this it talks to `http://localhost:3000`).
Add this to your shell profile:

```sh
export TRACKER_URL=https://hackios.appaiproxy.com
```

Check that it works: `node ~/.local/share/iosonand/cli.mjs check`.

## Signing in

Either of these works. Neither puts anything in the repo.

1. GitHub sign-in through `gh` (needs `gh auth login` done once):
   `node ~/.local/share/iosonand/cli.mjs login`, then `node ~/.local/share/iosonand/cli.mjs whoami`, which should list `realme-8i`
   among the devices you maintain. The token is saved in
   `~/.config/iosonand/tokens.json`.
2. An API key from https://hackios.appaiproxy.com/profile/keys with the scopes you need
   (`status:write` for states, `media:write` for photos, `fork:write` for
   repo records). Put it in `TRACKER_TOKEN`, in your shell profile or in a
   `.env` file at the repo root, which `.gitignore` excludes. The CLI does
   not read `.env` itself: load it with `set -a; . ./.env; set +a`.

`node ~/.local/share/iosonand/cli.mjs tokens` shows which token is in use, masked. Writes to `realme-8i`
need an account that maintains it; on a 403, claim the repo with
`node ~/.local/share/iosonand/cli.mjs repo-claim open-mapple/xnu_device_realme_spaced --device realme-8i`.

## Reading the current state

No sign-in needed:

```sh
node ~/.local/share/iosonand/cli.mjs status-get --device realme-8i
node ~/.local/share/iosonand/cli.mjs status-get --device realme-8i --area wifi
node ~/.local/share/iosonand/cli.mjs areas
```

| Area | Slug |
|---|---|
| Audio output | `audio` |
| Battery reporting | `battery` |
| Bluetooth | `bluetooth` |
| Boot to Home Screen | `boot` |
| Auto-brightness | `brightness` |
| Phone calls | `calls` |
| Camera capture | `camera` |
| Face ID | `face-id` |
| GPU compositing | `gpu` |
| Haptics | `haptics` |
| Keyboard input | `keyboard` |
| macOS | `macos` |
| Cellular modem | `modem` |
| Passcode | `passcode` |
| Sensors (general) | `sensors` |
| SMS | `sms` |
| SpringBoard stability | `stability` |
| Thermals under load | `thermal` |
| Touch + buttons | `touch` |
| Video encode (HEVC) | `video-encode` |
| Wallet | `wallet` |
| Wi-Fi | `wifi` |

## Recording a change

The states are `works`, `in-progress`, `broken` and `unknown`. Every write
needs `--detail` (what the build, log or test showed) and `--source` (a
commit, CI run, log or PR URL):

```sh
node ~/.local/share/iosonand/cli.mjs status-set realme-8i boot works \
  --detail "Boots to the lock screen; swipe unlock reaches the home screen" \
  --source https://github.com/open-mapple/xnu_device_realme_spaced/commit/<sha>
node ~/.local/share/iosonand/cli.mjs status-set realme-8i wifi in-progress \
  --detail "Firmware loads and scans; the interface does not come up (boot log)" \
  --source https://github.com/open-mapple/xnu_device_realme_spaced/commit/<sha>
```

Replace the text and `<sha>` with the real ones, then read it back with
`status-get --device realme-8i --area <slug>`.

## Photos and clips

```sh
node ~/.local/share/iosonand/cli.mjs update realme-8i home-screen.jpg clip.mp4 --text "What changed" --area touch
```

Crop or blur anything that shows an IMEI, serial number or personal data
first.

## Working offline

`node ~/.local/share/iosonand/cli.mjs queue status-set realme-8i ...` appends the command to
`./TRACKER_QUEUE.md` (git-ignored); `node ~/.local/share/iosonand/cli.mjs flush` sends the queue later.
Do not put `--token` on a queued command.

## Honesty rules

- Record only what a build, log, test or capture shows, and cite it in
  `--source`.
- What has not been shown on the phone stays `unknown`; code that builds but
  has not run on the phone is at most `in-progress`.
- Never lower someone else's state without evidence that it no longer holds.
- Keys and tokens never go in git, a commit or a `--detail` text.
