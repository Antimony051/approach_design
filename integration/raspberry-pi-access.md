# Connect to the project Raspberry Pi

Updated November 16, 2026 from the records in `picoscan150_hardware` (SRC-039–046) and the user's shared-key/login instructions (D-025/D-026). They record working Tailscale/OpenSSH access on November 16; this documentation update did not connect to or reconfigure the Pi. [Provenance and limits](../references/new-evidence/2026-11-16-raspberry-pi-access.md) preserve the source dates and observations.

## Recorded connection details

| Item | Recorded value / meaning |
| --- | --- |
| Hardware/system | Existing Raspberry Pi 4 Model B; Debian 11 Bullseye arm64; approximately 32 GB boot card |
| Linux hostname | `raspberrypi` |
| Tailscale device | `picoscan-pi` |
| Tailscale IPv4 | `100.72.89.22`; use the address shown in your own client if shared-device addressing differs |
| Full Tailscale DNS name | `picoscan-pi.tail53123d.ts.net` |
| Shell service | Regular OpenSSH on TCP 22; Tailscale SSH is disabled |
| SSH host identity | Ed25519 `SHA256:LydvSsaAsu9/3qfN5dFKHN8VTvqE5AYKEsS2UCf9LQk` |
| Team Linux login | **`pavewatch`**, using the **private SSH key provided by Shisir**; each recipient still uses their own Tailscale account/invitation |

The November 16 record reports Tailscale **1.104.7**, enabled at boot, registered and online without reported health warnings. The original laptop completed SSH through a Miami relay; that observation does not establish current connectivity, direct-peer transport, latency, or throughput for other clients.

## Team member quick start — shared key and pavewatch

The user confirmed that Shisir will supply the private SSH key and everyone
will connect as `pavewatch` per the latest username update (D-026). The current [shareable member guide](../references/new-evidence/2026-11-16-raspberry-pi-access/pavewatch-login/FRIEND_ACCESS.md)
uses this workflow; earlier per-member key/account instructions in SRC-039/040
are historical and superseded for team login.

## 1. Connect through Tailscale

1. Install [Tailscale](https://tailscale.com/download) for your operating system.
2. Sign in using your own Tailscale account and turn the connection on.
3. Accept the Pi-sharing invitation Shisir sends you. You should see **picoscan-pi** in your client.

Keep Tailscale connected whenever you use the Pi. The Pi must be powered and online. The Tailscale account is your own; the Linux login below is always `pavewatch`.

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

## 3. Connect as pavewatch

Run in PowerShell or a terminal:

```sh
ssh -o IdentitiesOnly=yes -i "$HOME/.ssh/picoscan_shared_key" pavewatch@100.72.89.22
```

If your Tailscale client shows a different address for the shared `picoscan-pi` device, substitute that address. If the private key has a passphrase, enter the supplied passphrase at the local key prompt.

On first connection, compare the Pi's Ed25519 fingerprint:

```text
SHA256:LydvSsaAsu9/3qfN5dFKHN8VTvqE5AYKEsS2UCf9LQk
```

Accept it when it matches. If it differs, confirm the Pi identity with Shisir before updating saved trust. After login, `whoami` should report `pavewatch` and `hostname` should report `raspberrypi`. Use `exit` to disconnect.

On the **original configured administrator laptop**, the previously recorded
shortcut uses its existing `~/.ssh/config` and key. Use
`ssh -l pavewatch picoscan-pi` to override an older configured username.
Teammates use the explicit command above; that laptop shortcut is not created
automatically on their computers.

## Onboard workspace — start here after login

The user supplied the following paths **inside the Raspberry Pi**. As
`pavewatch`, read the home-level instructions before operating the LiDAR:

```sh
cat ~/README.md
cat ~/AGENTS.md
cd /home/pavewatch/03-sensor-payload-acquisition
```

| Pi path | Contents |
| --- | --- |
| `/home/pavewatch/03-sensor-payload-acquisition/` | LiDAR workspace root |
| `/home/pavewatch/03-sensor-payload-acquisition/tools/` | LiDAR scripts |
| `/home/pavewatch/03-sensor-payload-acquisition/docs/` | Sensor documentation |
| `~/data/sessions/` = `/home/pavewatch/data/sessions/` | Recorded data; outside the subsystem workspace root |

`~` here is `/home/pavewatch` on the Pi, not the local workstation home.
These are user-provided workspace instructions; no remote files were inspected
or modified during this documentation update.

## Troubleshooting and account administration

| Symptom | Check |
| --- | --- |
| Timeout | Pi power/online state, both Tailscale connections, accepted share, recipient's displayed address, and access policy permitting TCP 22 |
| `Permission denied (publickey)` | Use `pavewatch` and the private key supplied by Shisir; verify its local filename/path and permissions; Tailscale sharing alone does not authenticate SSH |
| Agent refuses signing | The November 12 laptop encountered this; choose the intended working local key explicitly with `-i`/`IdentitiesOnly` rather than assuming a network failure |
| Name lookup fails | Use the recipient's numeric Tailscale address; `raspberrypi.local` did not resolve reliably in earlier checks |
| Different host fingerprint | Confirm Pi identity/reinstallation with the administrator before changing trust records |
| Disconnected service shell | Check access again; do not assume capture stopped or succeeded solely from the SSH connection state |

[The updated administrator guide](../references/new-evidence/2026-11-16-raspberry-pi-access/pavewatch-login/TAILSCALE.md) covers Tailscale sharing, the shared-key `pavewatch` login, policy checks and wired maintenance. It records `--accept-dns=false --accept-routes=false --ssh=false`: existing DNS is retained, subnet routes are not accepted, and ordinary OpenSSH provides the shell. The Pi is already registered; registration/install/setup steps are recovery references, not routine login steps. No invitations, accounts, policies or services were changed by adding this guide.

## Other network paths and historical addresses

| Path | Recorded endpoint | Scope |
| --- | --- | --- |
| Campus Wi-Fi | `172.18.2.95` on November 16 | DHCP can change it; Wi-Fi client isolation can prevent laptop-to-Pi access |
| Older apartment Wi-Fi | `100.70.49.73/25` on November 12 | Historical **LAN** address, not the current Pi Tailscale address despite the `100.*` prefix |
| Direct laptop-to-Pi Ethernet | IPv6 link-local `fe80::cb69:61b7:5997:6b6d` in the original laptop's notes | Requires a direct cable, the correct laptop interface zone and its preconfigured `picoscan-pi-direct` profile |
| Direct laptop-to-LiDAR Ethernet | Laptop `192.168.0.100/24`, sensor `192.168.0.1`, profile `picoscan150-direct` | November 11 laptop ping/HTTP evidence; a different connection from Pi maintenance access |

For **the original Linux administrator laptop**, the wired example below uses
the recorded network values with the username/key filename updated to the
current team instructions. This current-account combination was not retested:

```sh
nmcli connection up picoscan-pi-direct
ssh -o IdentitiesOnly=yes -o HostKeyAlias=100.70.49.73 \
    -i "$HOME/.ssh/picoscan_shared_key" \
    'pavewatch@fe80::cb69:61b7:5997:6b6d%enp109s0'
```

`enp109s0`, the profile, the private-key filename and the link-local address are recorded laptop/bench details, not universal settings. `HostKeyAlias=100.70.49.73` selects the administrator's previously trusted host-key entry; it does not route the connection to that old address. Other clients use the supplied shared key with `pavewatch`, their own actual interface/address, and the verified Pi host identity. The profile has autoconnect disabled and no default route; it preserves the laptop's separate internet path.

The `picoscan150-direct` profile instead addresses the **sensor** for SOPASair at `http://192.168.0.1/`. Do not substitute one profile for the other. A Pi-to-LiDAR static address/profile is not documented as applied in these records; inventory it before configuring the planned sensor Ethernet/PTP path.

## Integration boundaries and commissioning

Tailscale/OpenSSH is the recorder's **maintenance and development access** path (IF-22). It is separate from RC takeover, laptop-to-flight-controller MAVLink, payload Ethernet acquisition, PTP and validated post-flight export. The source records no advertised subnet route or exit-node role; a successful shell does not establish remote access to SOPASair or the LiDAR subnet. A shell session also does not prove sensor recording, camera support, timing accuracy or PC3 export throughput.

Prefer the documented Wi-Fi/Tailscale service path while the Pi Ethernet port is in use for LiDAR. Direct wired maintenance occupies that physical port; document any cable/topology changes and recheck sensor/PTP/clock validity afterward. Assess installed capture/timing under the actual network/service load rather than treating recorded SSH success as qualification.

The existing Pi/card is available in the source records, but RAM, wall-adapter rating, flight regulator compatibility, exact driver/library stack and camera/recording performance remain open. November 12 logs record unresolved filesystem findings and the user's choice to leave them unchanged. They also record the SSH correction from `ChallengeResponseAuthentication` to `KbdInteractiveAuthentication` in the per-user block for the installed OpenSSH 8.4 behavior. Later boot/SSH success does not establish that filesystem findings were repaired or survey storage passed.

Do not rerun initial account-creation/card setup or repair scripts as a login step. Those scripts were written for one inspected mounted Bullseye card, not arbitrary media or a newly selected OS. The original private backups, disk images, Wi-Fi credentials and keys remain at source and are not included here. Future setup/repair or OS changes need their own scoped instructions and validation; this guide changes documentation only.
