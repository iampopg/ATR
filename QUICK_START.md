# Quick Start Guide

## What's New

✅ **Web UI** - Modern dashboard for monitoring and token management  
✅ **Windows Driver Concepts** - Reference code from NoMoreStealer for Month 4

## 1. Test the Web UI

```bash
# Install UI dependencies
cd ui
pip install -r requirements.txt

# Start the web server
python app.py

# Open browser
# http://localhost:5000
```

### Using the Dashboard

1. **Start Monitoring**
   - Enter directory path (e.g., `/home/popg/test`)
   - Click "Start Monitoring"

2. **Generate Token**
   - Enter password
   - Click "Generate Token"
   - Token displayed for 10 minutes

3. **View Statistics**
   - Blocked operations (red)
   - Allowed operations (green)
   - Real-time updates

4. **Monitor Events**
   - Recent file operations
   - Color-coded by type
   - Timestamps and paths

## 2. Review Windows Driver Concepts

```bash
cd resources/windows_driver_concepts
cat README.md
```

### Files Available

1. **minifilter_registration.cpp** - Driver setup and altitude
2. **file_name_information.cpp** - Path extraction
3. **process_verification.cpp** - Trust checking
4. **shared_memory_communication.cpp** - Kernel ↔ User-mode

### When to Use

- **Month 4** (Weeks 13-16): Windows driver development
- Reference when implementing kernel-level protection
- Copy patterns, adapt for token-based authentication

## 3. Test Existing Functionality

```bash
cd Research

# Run Week 4 protected monitor (CLI version)
python week4_protected_monitor.py /path/to/protect

# Run test suite
python week4_test_suite.py

# Simulate ransomware attack
python week4_ransomware_simulator.py /path/to/test
```

## Project Status

**Month 1 Complete** ✅
- Week 1: File monitoring
- Week 2: Token system (Argon2id + HKDF)
- Week 3: Entropy analysis
- Week 4: Token-protected filesystem

**New Additions** ✅
- Web UI with real-time monitoring
- Windows driver reference code
- Project structure documentation

**Next Steps** (Month 2)
- Enhanced detection engine
- UI improvements
- Performance optimization

## Architecture

```
┌─────────────────────────────────────────┐
│         Web UI (Flask + Socket.IO)      │
│  - Dashboard                            │
│  - Token management                     │
│  - Real-time events                     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Week 4 Protected Monitor (Python)    │
│  - Token validation                     │
│  - File operation blocking              │
│  - Entropy analysis                     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Watchdog Library (Cross-platform)  │
│  - File system events                   │
│  - CREATE, MODIFY, DELETE               │
└─────────────────────────────────────────┘
```

## Future Architecture (Month 4)

```
┌─────────────────────────────────────────┐
│         Web UI (Flask + Socket.IO)      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Shared Memory Communication          │
│  - 4KB section                          │
│  - Event notifications                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Windows Minifilter Driver (C++)      │
│  - IRP_MJ_CREATE, WRITE, SET_INFO       │
│  - Token validation in kernel           │
│  - Process verification                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Windows Filter Manager             │
└─────────────────────────────────────────┘
```

## Key Files

| File | Purpose |
|------|---------|
| `ui/app.py` | Web server |
| `ui/templates/dashboard.html` | UI interface |
| `Research/week4_protected_monitor.py` | Core protection |
| `resources/windows_driver_concepts/*.cpp` | Driver reference |
| `PROJECT_STRUCTURE.md` | Full documentation |

## Troubleshooting

**UI won't start:**
```bash
pip install flask flask-socketio python-socketio
```

**Port 5000 in use:**
Edit `ui/app.py`, change port to 5001

**Monitor not working:**
- Check path exists
- Verify permissions
- Review console logs

## Resources

- **NoMoreStealer**: `/repo/NoMoreStealers`
- **Documentation**: `/Research/*.md`
- **Test Suites**: `/Research/week*_test_suite.py`

## Contact

Project: Anti-Ransomware Protection System  
Location: Abuja, Nigeria 🇳🇬  
Started: January 27, 2026  
Status: Month 1 Complete, Month 2 Starting
