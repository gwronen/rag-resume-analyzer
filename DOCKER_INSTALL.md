# Docker Installation Guide for Windows

## Step 1: Download Docker Desktop

1. Go to: https://www.docker.com/products/docker-desktop
2. Click "Download for Windows"
3. This will download `Docker Desktop Installer.exe`

## Step 2: Install Docker Desktop

1. Run the downloaded installer (`Docker Desktop Installer.exe`)
2. Follow the installation wizard
3. **Important**: When prompted, check "Use WSL 2 instead of Hyper-V" (recommended for Windows)
4. Complete the installation
5. **Restart your computer** if prompted

## Step 3: Start Docker Desktop

1. After restart, launch Docker Desktop from the Start menu
2. Accept the service agreement
3. Docker Desktop will start (you'll see a whale icon in your system tray)
4. Wait for Docker to fully start (the whale icon will stop animating)

## Step 4: Verify Installation

Open a new terminal/PowerShell and run:
```bash
docker --version
```

You should see something like: `Docker version 24.x.x, build ...`

Also verify docker-compose:
```bash
docker-compose --version
```

## Step 5: Once Docker is Running

Come back here and we'll run:
```bash
docker-compose up -d
```

This will start Prometheus and Grafana automatically!

---

## Troubleshooting

**"WSL 2 installation is incomplete"**
- Install WSL 2: https://docs.microsoft.com/en-us/windows/wsl/install
- Or use Hyper-V instead during Docker installation

**Docker Desktop won't start**
- Check Windows features: Enable "Virtual Machine Platform" and "Windows Subsystem for Linux"
- Restart your computer
- Check Docker Desktop logs for errors

**Port conflicts**
- If port 3000 or 9090 are already in use, we can change them in docker-compose.yml


