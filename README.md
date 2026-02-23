# Anti-Ransomware Protection System

Token-based file protection system that prevents ransomware attacks through cryptographic access control.

## Project Structure

```
anti-ransomW/
├── docs/                    # Documentation
├── Research/                # Month 1 implementation (Python)
├── resources/               # Windows driver reference code
├── ui/                      # Web-based configuration UI
└── repo/                    # External reference projects
```

## Quick Start

```bash
# Install dependencies
cd Research
pip install -r requirements.txt

# Run protected monitor
python week4_protected_monitor.py /path/to/protect

# Start web UI
cd ../ui
pip install -r requirements.txt
python app.py
```

## Status

**Month 1 Complete** ✅
- Token system (Argon2id + HKDF)
- Filesystem monitoring with entropy analysis
- Token-protected filesystem
- All test suites passing (5/5, 7/7, 10/10)

## Documentation

See `/docs` for detailed documentation:
- [Quick Start Guide](docs/QUICK_START.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [NoMoreStealer Analysis](docs/NOMORESTEALER_ANALYSIS.md)
- [Development Plan](docs/DETAILED_PLAN.md)

## Technology

- **Language**: Python 3.13 (current), C++ (Month 4)
- **Security**: Argon2id, HKDF, HMAC-SHA256
- **Monitoring**: Watchdog (Python), Minifilter (Windows)
- **UI**: Flask + Socket.IO

## License

Personal project - License TBD
