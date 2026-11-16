# Connect to the project Raspberry Pi

You will need Tailscale on your computer, a Pi-sharing invitation from Shisir,
and an SSH account on the Pi. Shisir will confirm your Pi username after your
public SSH key has been added.

## 1. Install Tailscale and accept your invitation

1. Install [Tailscale](https://tailscale.com/download) for your operating system.
2. Open Tailscale, sign in using your own account, and turn the connection on.
3. Open the Pi-sharing invitation Shisir sends you and accept it with that
   account. You should then see **picoscan-pi** in Tailscale.

Keep Tailscale connected whenever you use the Pi. You can connect from a
different Wi-Fi network or from home.

## 2. Create an SSH key and send the public key

Run the commands for your operating system. If you already created the named
key below, use its existing `.pub` file rather than generating it again.

### Windows: PowerShell

```powershell
New-Item -ItemType Directory -Force "$HOME/.ssh" | Out-Null
ssh-keygen -t ed25519 -f "$HOME/.ssh/picoscan_ed25519"
Get-Content "$HOME/.ssh/picoscan_ed25519.pub"
```

### macOS or Linux: Terminal

```bash
mkdir -p "$HOME/.ssh"
ssh-keygen -t ed25519 -f "$HOME/.ssh/picoscan_ed25519"
cat "$HOME/.ssh/picoscan_ed25519.pub"
```

`ssh-keygen` will let you choose a passphrase for your key. Send Shisir the
complete public-key line printed by the final command, along with your desired
Pi username. The line starts with `ssh-ed25519`. Send only the `.pub` output;
the file without `.pub` is your private key and stays on your computer.

Wait for confirmation that your Pi account and key are ready before continuing.

## 3. Connect to the Pi

In PowerShell or Terminal, replace `YOUR_PI_USERNAME` with the Pi username
Shisir confirms:

```sh
ssh -o IdentitiesOnly=yes -i "$HOME/.ssh/picoscan_ed25519" YOUR_PI_USERNAME@100.72.89.22
```

Your Pi username is a Linux account name, rather than your Tailscale email
address. If you set a passphrase on your SSH key, enter that passphrase when
prompted.

On the first connection, SSH asks you to confirm the Pi's identity. Its
Ed25519 fingerprint should be:

```text
SHA256:LydvSsaAsu9/3qfN5dFKHN8VTvqE5AYKEsS2UCf9LQk
```

If that fingerprint matches, type `yes`. Once connected, you will see a Linux
shell prompt. Run `hostname` to confirm the computer reports `raspberrypi`.
Use `exit` to disconnect.

## Connection details and troubleshooting

- Device name: **picoscan-pi**
- Tailscale IPv4: **100.72.89.22**
- Full Tailscale DNS name: **picoscan-pi.tail53123d.ts.net**
- SSH port: **22**

Tailscale can occasionally assign a shared machine a different address in the
recipient's network. If your Tailscale client shows a different address for
`picoscan-pi`, use the address shown in your client.

- **Connection times out:** confirm Tailscale is connected, the sharing
  invitation has been accepted, and the Pi is online. Send Shisir the error
  if it still fails so the device-sharing access policy can be checked.
- **Permission denied / publickey:** confirm your Pi username and that the
  public key you sent matches `picoscan_ed25519` on this computer.
- **Hostname does not resolve:** use the numeric Tailscale IP above, or the
  address shown in your client.

Reference: [Tailscale device sharing](https://tailscale.com/docs/features/sharing).
