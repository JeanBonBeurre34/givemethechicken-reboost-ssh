
# GiveMeTheChicken SSH Honeypot

GiveMeTheChicken is a lightweight Python-based SSH honeypot designed to:
- Accept SSH connections
- Spoof an OpenSSH banner for Nmap detection
- Provide a fake shell with a simulated file system
- Log attacker commands
- Run stably without PTY to avoid cursor/terminal issues

This honeypot is ideal for:
- Learning attacker behavior
- Running deception environments
- Collecting threat intelligence
- Training cybersecurity teams

---

## 🚀 Features

### ✔ SSH Banner Spoofing
The honeypot returns a customizable SSH version string:
```
SSH-2.0-OpenSSH_9.8p1 Debian-1
```
Nmap will detect it exactly as OpenSSH.

### ✔ Stable RAW Shell (No PTY)
- No cursor drift  
- No weird rendering  
- Fully predictable  
- Logs every command  

### ✔ Fake File System
Supports:
- `ls`
- `mkdir`
- `touch`
- `cat`
- `echo "text" > file`
- `cd`

Attacker sees a simple filesystem but nothing touches the real OS.

### ✔ Logging
All commands and connection details are logged to:
```
server.log
```
---
Or the stdout of your docker container so you directly access it from:
```
docker logs REPLACE_WITH_YOURCONTAINERID
```
## 🐍 Installation

### Clone the repository
```
git clone https://github.com/JeanBonBeurre34/givemethechicken
cd givemethechicken
```

---

## 🐳 Docker Deployment

### Example Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY givemethechicken.py /app/

RUN pip install --no-cache-dir paramiko

EXPOSE 22

CMD ["python", "givemethechicken.py"]
```

### Build & Run
```
docker build -t givemethechicken .
docker run -p 22:22 --name chicken givemethechicken
```

---

## 🔍 Nmap Detection

Running:
```
nmap -sV localhost -p 22
```

Will show:
```
22/tcp open ssh OpenSSH 9.8p1 (protocol 2.0)
```

---

## 🔒 Security Notes
- This is **not** a real SSH server.
- Do **not** use in production networks unless isolated.
- Always run inside Docker or a sandbox environment.

---

## 📜 License
MIT License — free for all educational and research use.

---

## 💬 Contact
Author: JeanBonBeurre34  
GitHub: https://github.com/JeanBonBeurre34
