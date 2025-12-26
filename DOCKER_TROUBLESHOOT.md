# Docker Desktop Troubleshooting

## Error: "Docker Desktop is unable to start"

### Common Solutions:

### 1. Enable WSL 2 (Most Common Fix)

Open PowerShell as Administrator and run:
```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

Then:
- Restart your computer
- Download WSL2 kernel update: https://aka.ms/wsl2kernel
- Install it
- Set WSL 2 as default: `wsl --set-default-version 2`

### 2. Check Windows Features

1. Open "Turn Windows features on or off"
2. Enable:
   - ☑ Virtual Machine Platform
   - ☑ Windows Subsystem for Linux
   - ☑ Hyper-V (if available)

### 3. Restart Docker Desktop

1. Right-click Docker Desktop in system tray → Quit Docker Desktop
2. Restart Docker Desktop as Administrator
3. Wait 1-2 minutes for it to fully start

### 4. Check Docker Desktop Settings

1. Open Docker Desktop
2. Go to Settings → General
3. Check "Use WSL 2 based engine"
4. Apply & Restart

### 5. Alternative: Use Docker with Hyper-V

If WSL 2 doesn't work:
1. Docker Desktop Settings → General
2. Uncheck "Use WSL 2 based engine"
3. Use Hyper-V instead
4. Apply & Restart

## Still Not Working?

Try these diagnostic commands (run as Administrator):
```powershell
# Check WSL status
wsl --status

# Check Docker info
docker info

# Check if virtualization is enabled
systeminfo | findstr /C:"Hyper-V"
```

## Alternative: Manual Installation

If Docker Desktop continues to have issues, we can set up Prometheus and Grafana manually without Docker. Let me know if you'd prefer that approach!

