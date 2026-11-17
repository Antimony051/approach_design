# Laptop agent instructions: data processing subsystem lead

You are assisting the data processing subsystem lead from their laptop. The camera/LiDAR pipeline and GPU jobs run on the server.
Project files live on a remote Azure workstation. Your working folder is:

    /home/dev_admin/data_processing_subsystem

Connect as **dev_admin** over SSH on port **22**. This document establishes the
connection; explicitly read the remote AGENTS.md for project instructions.
Examples use Bash (Linux, macOS, WSL or Git Bash); adapt to the laptop's shell
if needed while preserving the cache location and remote paths.

## 1. Check the saved server IP first

Keep the current IP in this file **on the laptop**, outside the project:

    ~/.config/gpu-dev-workstation/server-ip.txt

Both subsystem guides use this same cache on a given laptop. Read it as plain
text; never source or execute it. At the start of each session:

```bash
IP_FILE="$HOME/.config/gpu-dev-workstation/server-ip.txt"
if [ -s "$IP_FILE" ]; then
  SERVER_IP=$(cat "$IP_FILE")
  printf 'Previously saved server IP: %s\n' "$SERVER_IP"
fi
```

If it contains a valid IP, try that address before asking for another:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new \
  "dev_admin@$SERVER_IP" 'test -d /home/dev_admin/data_processing_subsystem'
```

If there is no usable saved address, ask the human:

> Please ask the Project Manager for the workstation's current public IP address and send it to me.

Once supplied, validate it as a literal IPv4 or IPv6 address and save it promptly.
Replace the placeholder below with the supplied address. Save only the IP, never
passwords or keys. Overwrite the cache when the Project Manager supplies a new IP.

```bash
SERVER_IP='PASTE_THE_IP_HERE'
mkdir -p "$HOME/.config/gpu-dev-workstation"
printf '%s\n' "$SERVER_IP" > "$HOME/.config/gpu-dev-workstation/server-ip.txt"
chmod 600 "$HOME/.config/gpu-dev-workstation/server-ip.txt"
```

Retest the connection. On later sessions, reuse the saved IP if it works.
A timeout/refused connection may mean the VM is stopped or the IP changed; ask
the human to confirm the VM is running and get its current IP from the Project
Manager. A successful SSH login with a missing folder is a setup issue; keep
the IP and ask the human to have the Project Manager arrange the workspace.

`Permission denied (publickey)` is an access/key issue, not proof of a stale IP.
Ask the human to arrange SSH access with the Project Manager. Use an existing
authorized local key or SSH agent; use SSH's -i option if the human supplies a
specific key path. Private keys stay on the laptop. If SSH reports a changed
host key, have the human confirm the server identity with the Project Manager
before updating known_hosts. Keep host-key checks enabled.

## 2. Explicitly read the remote agent instructions

After connecting and **before editing files, installing dependencies or running
project code**, read the server's applicable AGENTS.md files. Your laptop agent
will not necessarily discover them automatically. Reload the saved IP in a new
shell and run this read-only command:

```bash
SERVER_IP=$(cat "$HOME/.config/gpu-dev-workstation/server-ip.txt")
ssh "dev_admin@$SERVER_IP" '
  set -eu
  cd /home/dev_admin/data_processing_subsystem
  test -f AGENTS.md || { echo "Remote AGENTS.md is missing; report this to the human." >&2; exit 1; }
  for instructions in /AGENTS.md /home/AGENTS.md /home/dev_admin/AGENTS.md AGENTS.md; do
    if [ -f "$instructions" ]; then
      printf "Reading remote instructions: %s\n" "$instructions"
      cat "$instructions"
    fi
  done
'
```

Follow all applicable remote instructions. Before editing a nested directory,
explicitly look for and read any additional AGENTS.md files along its path.
Relative documentation links in remote instructions resolve **on the server**,
relative to that file. If instructions are missing, report it so the Project
Manager can arrange installation; do not invent replacement rules.

## 3. Work on the server

Use SSH or a remote-development connection for inspection, edits, UV commands
and tests. Ordinary local tools act on the laptop; confirm which machine your
tools target. Each separate SSH command starts a new shell, so explicitly change
to the subsystem folder every time. For example:

```bash
ssh "dev_admin@$SERVER_IP" '
  set -eu
  cd /home/dev_admin/data_processing_subsystem
  export PATH="$HOME/.local/bin:$PATH"
  pwd
  uv --version
'
```

Use UV for Python package management and execution. Inspect the remote project
and its documented commands before choosing how to run it. Keep edits focused
and inspect current server files before updating them. If editing a local copy,
transfer only intended changes and run checks on the server; avoid replacing
whole directories or overwriting a friend's work. Coordinate changes to the
findings contract with the other subsystem lead.

Consult the remote GPU guidance before large runs; the GPU and machine are
shared. Use tmux for long-running jobs and capture logs so a laptop disconnect
does not lose the job/session. Coordinate resource-heavy work with the other lead.


## 4. Back up when asked

For a request such as "back up anything important to the bucket," explicitly read
this **server** document and follow its procedure:

    /home/dev_admin/data_processing_subsystem/docs/backup-instructions.md

Run its Azure CLI commands **on the server**, where managed identity is available.
Include important processing inputs, code and outputs as directed by that guide.
Verify the upload and report what was backed up and the exact blob location.
Preserve original local/server files. Read the same document for restores.
