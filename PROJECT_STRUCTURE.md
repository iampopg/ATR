# Project Structure Summary

## New Additions

### 1. Web UI (`/ui`)
Modern web-based dashboard for monitoring and token management.

**Files:**
- `app.py` - Flask server with WebSocket support
- `templates/dashboard.html` - Responsive dashboard UI
- `requirements.txt` - Flask, Flask-SocketIO dependencies
- `README.md` - UI documentation

**Features:**
- Real-time monitoring via WebSocket
- Token generation and management
- Statistics dashboard (blocked/allowed operations)
- Event log with color coding
- Responsive design

**Usage:**
```bash
cd ui
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

### 2. Windows Driver Concepts (`/resources/windows_driver_concepts`)
Reference implementations from NoMoreStealer for Month 4 development.

**Files:**
1. `minifilter_registration.cpp` - Driver registration and altitude selection
2. `file_name_information.cpp` - File path extraction and matching
3. `process_verification.cpp` - Process trust and signature checking
4. `shared_memory_communication.cpp` - Kernel-to-user-mode events
5. `README.md` - Integration guide

**Key Concepts Extracted:**
- Minifilter registration with Filter Manager
- `FltGetFileNameInformation()` usage patterns
- `PsIsProtectedProcessLight()` for process verification
- Shared memory communication (4KB section)
- Altitude selection (371000 - FSFilter Activity Monitor)

**Purpose:**
Reference for implementing Windows kernel driver in Month 4 (Weeks 13-16).

## Project Structure

```
anti-ransomW/
├── Research/                    # Month 1 implementation
│   ├── week2_*.py              # Token system (Argon2id + HKDF)
│   ├── week3_*.py              # Filesystem monitoring
│   ├── week4_*.py              # Token-protected filesystem
│   └── requirements.txt        # Python dependencies
│
├── ui/                         # NEW: Web dashboard
│   ├── app.py                  # Flask server
│   ├── templates/
│   │   └── dashboard.html      # UI interface
│   ├── requirements.txt        # UI dependencies
│   └── README.md               # UI documentation
│
├── resources/                  # NEW: Reference materials
│   └── windows_driver_concepts/
│       ├── minifilter_registration.cpp
│       ├── file_name_information.cpp
│       ├── process_verification.cpp
│       ├── shared_memory_communication.cpp
│       └── README.md
│
├── repo/                       # External projects
│   └── NoMoreStealers/         # Reference implementation
│
├── README.md                   # Project overview
├── .gitignore                  # Git ignore rules
└── DETAILED_PLAN.md           # 26-week roadmap
```

## Technology Stack

### Current (Month 1-3)
- **Language**: Python 3.13
- **Token System**: Argon2id + HKDF + HMAC-SHA256
- **Monitoring**: Watchdog library (cross-platform)
- **Database**: SQLite3
- **UI**: Flask + Socket.IO + HTML/CSS/JS

### Future (Month 4+)
- **Driver**: C++ Windows Kernel Driver
- **Filter**: Minifilter (Filter Manager)
- **Communication**: Shared memory (kernel ↔ user-mode)
- **Build**: Visual Studio + WDK

## Development Timeline

- **Month 1** (Weeks 1-4): Core token system and monitoring ✅
- **Month 2** (Weeks 5-8): Enhanced detection and UI ← **Current**
- **Month 3** (Weeks 9-12): Hardware token integration
- **Month 4** (Weeks 13-16): Windows driver development
- **Month 5** (Weeks 17-20): Performance optimization
- **Month 6** (Weeks 21-26): Testing and documentation

## Next Steps

### Immediate (Week 5)
1. Test web UI with Week 4 protected monitor
2. Add entropy visualization to dashboard
3. Implement alert notifications

### Short-term (Month 2)
1. Enhanced detection engine
2. Behavioral analysis
3. Performance optimization
4. User authentication for UI

### Long-term (Month 3-4)
1. Hardware token prototyping
2. Windows kernel driver development
3. Integration with driver concepts from resources/

## Key Differentiators

Your project vs NoMoreStealer:

| Feature | NoMoreStealer | Your Project |
|---------|---------------|--------------|
| **Target** | Info stealers | Ransomware |
| **Auth** | Process allowlist | Token-based |
| **Detection** | Path matching | Entropy analysis |
| **Monitoring** | CREATE only | CREATE + WRITE + SET_INFO |
| **Protection** | Specific paths | Entire directories |
| **UI** | Wails (Go) | Flask (Python) |

## Resources

- **NoMoreStealer**: `/repo/NoMoreStealers`
- **Driver Concepts**: `/resources/windows_driver_concepts`
- **Documentation**: `/Research/*.md`
- **UI**: `/ui`

## Testing

```bash
# Test Week 4 monitor
cd Research
python week4_test_suite.py

# Test UI
cd ui
python app.py

# Simulate ransomware
cd Research
python week4_ransomware_simulator.py /path/to/test
```

## Notes

- All Month 1 test suites passing (5/5, 7/7, 10/10)
- UI integrates with existing Week 4 implementation
- Driver concepts ready for Month 4 development
- Zero spending maintained (using open-source tools)
- Developed in Abuja, Nigeria 🇳🇬
