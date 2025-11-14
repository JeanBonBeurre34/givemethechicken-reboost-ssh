#!/usr/bin/env python3
import socket
import threading
import logging
import paramiko
import os

# =========================================================
# LOGGING
# =========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("server.log"), logging.StreamHandler()]
)

# =========================================================
# FAKE FILESYSTEM
# =========================================================
class FakeFileSystem:
    def __init__(self):
        self.files = {"root": {}}
        self.current_path = ["root"]

    def current_dir(self):
        cur = self.files
        for d in self.current_path:
            cur = cur[d]
        return cur

    def ls(self, all=False):
        cur = self.current_dir()
        items = []
        for name, value in cur.items():
            if name.startswith(".") and not all:
                continue
            items.append(name + "/" if isinstance(value, dict) else name)
        return "\n".join(items)

    def touch(self, name):
        self.current_dir()[name] = ""

    def echo(self, text, name):
        self.current_dir()[name] = text
        return f"Content written to {name}"

    def cat(self, name):
        return self.current_dir().get(name, "File not found")

    def mkdir(self, name):
        cur = self.current_dir()
        if name not in cur:
            cur[name] = {}
            return f"Directory '{name}' created"
        return "Directory already exists"

    def cd(self, name):
        if name == "..":
            if len(self.current_path) > 1:
                self.current_path.pop()
            return ""
        cur = self.current_dir()
        if name in cur and isinstance(cur[name], dict):
            self.current_path.append(name)
            return ""
        return "Directory not found"

    def handle(self, cmd):
        logging.info(f"[CMD] {cmd}")

        if cmd.startswith("echo") and ">" in cmd:
            left, right = cmd.split(">", 1)
            txt = left.replace("echo", "").strip().strip('"')
            return self.echo(txt, right.strip())

        args = cmd.split()
        if not args:
            return None

        c = args[0]

        if c == "exit":
            return "exit"
        if c == "ls":
            return self.ls(len(args) > 1 and args[1] == "-la")
        if c == "touch" and len(args) > 1:
            self.touch(args[1])
            return f"Created file {args[1]}"
        if c == "mkdir" and len(args) > 1:
            return self.mkdir(args[1])
        if c == "cd" and len(args) > 1:
            return self.cd(args[1])
        if c == "cat" and len(args) > 1:
            return self.cat(args[1])

        return "Invalid command"


# =========================================================
# RAW NON-PTY SHELL (STABLE)
# =========================================================
def raw_shell(chan, fs: FakeFileSystem):
    chan.send(b"/$ ")

    try:
        while True:
            data = chan.recv(1024)
            if not data:
                break

            cmd = data.decode(errors="ignore").strip()
            if not cmd:
                chan.send(b"/$ ")
                continue

            result = fs.handle(cmd)
            if result == "exit":
                return

            if result:
                chan.send(result.encode() + b"\n")

            chan.send(b"/$ ")

    except Exception as e:
        logging.error(f"[SHELL ERROR] {e}")
    finally:
        try:
            chan.close()
        except:
            pass


# =========================================================
# SSH SERVER
# =========================================================
KEY_FILE = "server_host.key"

def ensure_key():
    if not os.path.exists(KEY_FILE):
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(KEY_FILE)
    return paramiko.RSAKey(filename=KEY_FILE)

HOST_KEY = ensure_key()


class SSHServer(paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        return (
            paramiko.OPEN_SUCCEEDED
            if kind == "session"
            else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
        )

    def check_auth_password(self, user, pwd):
        logging.info(f"[AUTH] {user}:{pwd}")
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_none(self, user):
        logging.info(f"[AUTH] {user} (none)")
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password,none"

    def check_channel_pty_request(self, *args, **kwargs):
        # Reject PTY for full stability (no cursor movement issues)
        return False

    def check_channel_shell_request(self, *args, **kwargs):
        return True


def handle_client(sock, addr):
    logging.info(f"[SSH] Connection from {addr}")

    t = paramiko.Transport(sock)

    # ---- SPOOF SSH BANNER HERE ----
    t.local_version = "SSH-2.0-OpenSSH_9.8p1 Debian-1"

    t.add_server_key(HOST_KEY)

    try:
        t.start_server(server=SSHServer())
    except Exception:
        return

    chan = t.accept(30)
    if not chan:
        return

    fs = FakeFileSystem()
    raw_shell(chan, fs)

    chan.close()
    t.close()


def start():
    srv = socket.socket()
    srv.bind(("0.0.0.0", 22))
    srv.listen(100)

    logging.info("[+] SSH honeypot running on port 22")

    while True:
        client, addr = srv.accept()
        threading.Thread(
            target=handle_client,
            args=(client, addr),
            daemon=True
        ).start()


if __name__ == "__main__":
    start()

