# Connect to the project Raspberry Pi

Updated November 16, 2026: the team uses the **shared `antimony` Linux account** and the **private SSH key provided by Shisir**. Team members do not need to generate another key pair or request a separate Pi username for this workflow.

## 1. Connect through Tailscale

1. Install [Tailscale](https://tailscale.com/download) for your operating system.
2. Sign in using your own Tailscale account and turn the connection on.
3. Accept the Pi-sharing invitation Shisir sends you. You should see **picoscan-pi** in your client.

Keep Tailscale connected whenever you use the Pi. The Pi must be powered and online. The Tailscale account is your own; the Linux login below is always `antimony`.

## 2. Save the provided private key

Obtain the private SSH key from Shisir and save it on your computer as:

```text
$HOME/.ssh/picoscan_shared_key
```

Use the private-key file itself, not a `.pub` file. The filename above is the local name used by these instructions; rename the provided file accordingly. Keep it outside the project repository and logs. No key contents belong in these instructions.

Windows PowerShell, to create the destination folder:

```powershell
New-Item -ItemType Directory -Force "$HOME/.ssh" | Out-Null
```

Place the supplied file in that folder as `picoscan_shared_key`. If Windows OpenSSH reports an unprotected key file, restrict that file's permissions to your Windows account before retrying.

macOS/Linux terminal, after saving the supplied file:

```sh
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
chmod 600 "$HOME/.ssh/picoscan_shared_key"
```

## 3. Connect as antimony

Run in PowerShell or a terminal:

```sh
ssh -o IdentitiesOnly=yes -i "$HOME/.ssh/picoscan_shared_key" antimony@100.72.89.22
```

If your Tailscale client shows a different address for the shared `picoscan-pi` device, substitute that address. If the private key has a passphrase, enter the supplied passphrase at the local key prompt.

On first connection, compare the Pi's Ed25519 fingerprint:

```text
SHA256:LydvSsaAsu9/3qfN5dFKHN8VTvqE5AYKEsS2UCf9LQk
```

Accept it when it matches. If it differs, confirm the Pi identity with Shisir before updating saved trust. After login, `whoami` should report `antimony` and `hostname` should report `raspberrypi`. Use `exit` to disconnect.

## Connection details and troubleshooting

- Tailscale device: **picoscan-pi**
- Recorded Tailscale IPv4: **100.72.89.22**
- Full Tailscale DNS name: **picoscan-pi.tail53123d.ts.net**
- Linux username: **antimony**
- SSH: ordinary OpenSSH, **TCP22**, over Tailscale

A Tailscale invitation permits network access subject to the sharing policy; SSH uses the provided key for the existing `antimony` account. No per-member Pi-account creation is required for this shared-login procedure.

- **Timeout:** check Tailscale, the accepted invitation, the Pi's online state and your client's displayed address. Shisir can check policy access to TCP22 if needed.
- **Permission denied / publickey:** use `antimony`, confirm the supplied private-key file/path and select it explicitly with `-i` and `IdentitiesOnly`.
- **Key permissions error:** on macOS/Linux apply `chmod 600` above; on Windows restrict the file to your account.
- **Name lookup fails:** use the numeric address shown by your Tailscale client.

Reference: [Tailscale device sharing](https://tailscale.com/docs/features/sharing). The key/account workflow above follows the user's November16 instruction; no keys or invitations are distributed by this documentation update.
