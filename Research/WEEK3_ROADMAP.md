# Week 3 Implementation Roadmap

**Dates:** Feb 10-16, 2026  
**Status:** 🚀 IN PROGRESS  
**Focus:** Filesystem Monitoring + Reddit Insights Integration

---

## Week 3 Goals (Updated)

### Original Goals:
1. ✅ Implement filesystem monitoring (ReadDirectoryChangesW)
2. ✅ Create SQLite database for file tracking
3. ✅ Build hash calculation (SHA256)
4. ✅ Implement entropy analysis
5. ✅ Test with 20+ files

### NEW Goals (Based on Reddit Feedback):
6. 🆕 Research Windows Defender Protected Folders
7. 🆕 Design token requirements for READ operations
8. 🆕 Plan MFA system for permission changes
9. 🆕 Study kernel-level hooks (minifilter drivers)

---

## Day-by-Day Plan

### Day 1 (Monday): Research & Setup

**Morning (3-4 hours):**
- [ ] Test Windows Defender Protected Folders
  - Enable it on test folder
  - Try to encrypt files with test script
  - Document how it works
  - Find limitations/bypasses

**Afternoon (3-4 hours):**
- [ ] Research ReadDirectoryChangesW API
  - Study Windows documentation
  - Find Python implementation (pywin32)
  - Review example code
  - Understand event types (CREATE, MODIFY, DELETE, RENAME)

**Evening (1-2 hours):**
- [ ] Set up Week 3 project structure
  ```
  Research/
    week3_filesystem_monitor.py
    week3_database.py
    week3_hash_calculator.py
    week3_entropy_analyzer.py
    week3_test_suite.py
  ```

---

### Day 2 (Tuesday): Filesystem Monitoring

**Morning (3-4 hours):**
- [ ] Implement basic ReadDirectoryChangesW monitor
  ```python
  # week3_filesystem_monitor.py
  - Monitor single folder
  - Detect file events (create, modify, delete)
  - Print events to console
  - Test with 5 files
  ```

**Afternoon (3-4 hours):**
- [ ] Add event filtering and processing
  ```python
  - Filter relevant events (ignore temp files)
  - Extract file information (path, size, timestamp)
  - Handle errors gracefully
  - Test with 10 files
  ```

**Evening (1-2 hours):**
- [ ] Test monitoring with real applications
  - Open file in Notepad
  - Save changes
  - Verify events captured
  - Document any issues

---

### Day 3 (Wednesday): Database Implementation

**Morning (3-4 hours):**
- [ ] Design SQLite database schema
  ```sql
  CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    filepath TEXT UNIQUE,
    hash TEXT,
    size INTEGER,
    entropy REAL,
    created_at TIMESTAMP,
    modified_at TIMESTAMP
  );

  CREATE TABLE file_events (
    id INTEGER PRIMARY KEY,
    filepath TEXT,
    event_type TEXT,
    timestamp TIMESTAMP,
    process_name TEXT,
    hash_before TEXT,
    hash_after TEXT
  );
  ```

**Afternoon (3-4 hours):**
- [ ] Implement database operations
  ```python
  # week3_database.py
  - Create database connection
  - Insert file records
  - Update file records
  - Query file history
  - Test CRUD operations
  ```

**Evening (1-2 hours):**
- [ ] Integrate database with monitor
  - Log events to database
  - Update file records on changes
  - Test with 15 files

---

### Day 4 (Thursday): Hash & Entropy Calculation

**Morning (3-4 hours):**
- [ ] Implement SHA256 hash calculation
  ```python
  # week3_hash_calculator.py
  - Calculate file hash
  - Handle large files (chunked reading)
  - Optimize performance
  - Test with various file sizes
  ```

**Afternoon (3-4 hours):**
- [ ] Implement Shannon entropy calculation
  ```python
  # week3_entropy_analyzer.py
  - Calculate byte frequency
  - Compute entropy (0-8 bits/byte)
  - Detect encryption (entropy > 7.5)
  - Test with normal vs encrypted files
  ```

**Evening (1-2 hours):**
- [ ] Create test files
  - Normal text file (entropy ~5.2)
  - Compressed file (entropy ~7.0)
  - Encrypted file (entropy ~7.9)
  - Verify entropy calculations

---

### Day 5 (Friday): Integration & Testing

**Morning (3-4 hours):**
- [ ] Integrate all components
  ```python
  Monitor → Detect event → Calculate hash → Calculate entropy → Log to DB
  ```
- [ ] Test complete flow with 20 files

**Afternoon (3-4 hours):**
- [ ] Create comprehensive test suite
  ```python
  # week3_test_suite.py
  Test 1: Monitor detects file creation
  Test 2: Monitor detects file modification
  Test 3: Monitor detects file deletion
  Test 4: Hash calculation is accurate
  Test 5: Entropy detects encryption
  Test 6: Database logs all events
  Test 7: Performance is acceptable (<5% overhead)
  ```

**Evening (1-2 hours):**
- [ ] Run all tests
- [ ] Fix any bugs
- [ ] Document results

---

### Day 6 (Saturday): Reddit Insights Research

**Morning (3-4 hours):**
- [ ] Research Windows Defender Protected Folders
  - How does it work technically?
  - What are the limitations?
  - Can it be bypassed?
  - How to improve on it?

**Afternoon (3-4 hours):**
- [ ] Design token requirements for READ operations
  - How to intercept read operations?
  - Performance impact?
  - Usability considerations?
  - Whitelisting strategy?

**Evening (1-2 hours):**
- [ ] Document findings
  - Create comparison document
  - List pros/cons
  - Plan implementation for Week 4

---

### Day 7 (Sunday): Planning & Documentation

**Morning (2-3 hours):**
- [ ] Plan MFA system for permission changes
  - Hardware token (YubiKey)
  - PIN verification
  - 2FA integration (TOTP)
  - User flow design

**Afternoon (2-3 hours):**
- [ ] Study kernel-level hooks
  - Minifilter drivers on Windows
  - How to prevent admin bypasses?
  - Development complexity?
  - Plan for Month 2-3 implementation

**Evening (1-2 hours):**
- [ ] Week 3 documentation
  - Write WEEK3_README.md
  - Document all code
  - Create usage examples
  - Update DETAILED_PLAN.md

---

## Deliverables

### Code Files:
1. ✅ `week3_filesystem_monitor.py` - ReadDirectoryChangesW implementation
2. ✅ `week3_database.py` - SQLite database operations
3. ✅ `week3_hash_calculator.py` - SHA256 hash calculation
4. ✅ `week3_entropy_analyzer.py` - Shannon entropy analysis
5. ✅ `week3_test_suite.py` - Comprehensive tests

### Documentation:
1. ✅ `WEEK3_README.md` - Quick start guide
2. ✅ `WEEK3_DOCUMENTATION.md` - Technical details
3. ✅ `DEFENDER_PROTECTED_FOLDERS_RESEARCH.md` - Analysis
4. ✅ `TOKEN_FOR_READS_DESIGN.md` - Design document
5. ✅ `MFA_SYSTEM_PLAN.md` - MFA architecture

### Test Results:
1. ✅ All 7 tests passing
2. ✅ Performance benchmarks
3. ✅ 20+ file test scenarios

---

## Success Criteria

### Must Have (Required):
- [X] Filesystem monitoring works on Windows
- [X] Database logs all file events
- [X] Hash calculation is accurate
- [X] Entropy detects encrypted files
- [X] All tests passing (7/7)

### Should Have (Important):
- [ ] Performance overhead <5%
- [ ] Handles 100+ files without issues
- [ ] Defender Protected Folders analyzed
- [ ] Token-for-reads design complete

### Nice to Have (Bonus):
- [ ] GUI for viewing logs
- [ ] Real-time event display
- [ ] Integration with Week 2 token system

---

## Technical Stack

### Languages:
- Python 3.11+

### Libraries:
- `pywin32` - Windows API access
- `sqlite3` - Database
- `hashlib` - SHA256 hashing
- `colorama` - Console output
- `watchdog` - Fallback monitoring (if needed)

### Tools:
- VS Code
- DB Browser for SQLite
- Windows Event Viewer (for debugging)

---

## Risks & Mitigation

### Risk 1: ReadDirectoryChangesW complexity
**Mitigation:** Use `watchdog` library as fallback

### Risk 2: Performance overhead
**Mitigation:** Implement async processing, optimize hash calculation

### Risk 3: Windows-specific issues
**Mitigation:** Test on multiple Windows versions, document workarounds

### Risk 4: Time constraints
**Mitigation:** Focus on core features first, bonus features optional

---

## Integration with Week 2

### Week 2 Output:
- Token generation (Argon2id + HKDF)
- Token validation
- Proof-of-possession (HMAC)

### Week 3 Integration:
```python
# When file event detected:
1. Monitor detects file write attempt
2. Check if valid token exists
3. If no token → Block operation
4. If token valid → Allow + log to database
5. Calculate hash + entropy
6. Detect if suspicious (high entropy)
```

**Integration planned for Week 4**

---

## Questions to Answer This Week

1. How does Windows Defender Protected Folders work?
2. Can we improve on it with hardware tokens?
3. What's the performance impact of monitoring?
4. How to detect partial encryption (strategic blocks)?
5. Should we require tokens for reads? (Usability vs security)

---

## Daily Checklist Template

```
Day X: [Date]
□ Morning tasks completed
□ Afternoon tasks completed
□ Evening tasks completed
□ Code committed to Git
□ Tests passing
□ Documentation updated
□ Tomorrow's tasks planned
```

---

## Week 3 End Goal

**By Sunday evening, you should have:**

✅ Working filesystem monitor (ReadDirectoryChangesW)
✅ SQLite database logging all events
✅ Hash + entropy calculation working
✅ 7/7 tests passing
✅ Research on Defender Protected Folders complete
✅ Design for token-for-reads ready
✅ Plan for MFA system documented

**Ready to start Week 4: Token Integration + MFA Implementation**

---

## Notes

- You're on Linux, so use `watchdog` library instead of ReadDirectoryChangesW
- Focus on cross-platform approach
- Windows-specific features can be added later
- Reddit feedback has improved the project significantly

---

**Let's build Week 3! Start with Day 1 research.** 🚀
