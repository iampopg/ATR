# Lessons Learned from Reddit - Anti-Ransomware Research

**Date:** February 2026  
**Source:** r/cybersecurity post - "Can files be protected AFTER ransomware starts running?"  
**Engagement:** 16 upvotes, 10 detailed responses from security professionals

---

## Executive Summary

Posted question about post-infection ransomware protection on Reddit. Received critical feedback from SOC analysts, Red Team professionals, and security architects that fundamentally changed our understanding of modern ransomware and project direction.

**Key Discovery:** Modern ransomware uses remote encryption, not local encryption. Our token-based approach protects against yesterday's threats, not today's.

---

## Lesson 1: Windows Already Has This Feature

**Source:** Gorstak-Zadar (2 upvotes)

### What We Learned:
- **Windows Defender Protected Folders** already exists
- Allows you to designate folders that can't be encrypted by anything
- UAC at max requires confirmation for all file operations
- Registry value can disable EFS (but breaks BitLocker)

### Impact on Project:
✅ **Validates our approach** - Microsoft thinks this is worth building
⚠️ **We're not first** - Need to understand why it's not enough
🔍 **Research needed** - How does it work? What are limitations? Can it be bypassed?

### Action Items:
- [ ] Test Defender Protected Folders immediately
- [ ] Document how it works technically
- [ ] Find its weaknesses/bypass methods
- [ ] Position our tool as "Protected Folders + hardware tokens + kernel-level"

### Quote:
> "Defender has protected folders feature, meaning you can assign folders you don't want encrypted by anything."

---

## Lesson 2: Admin-Level Malware Bypasses File Locks

**Source:** Sqooky - Red Team (8 upvotes)

### What We Learned:
- Modern AV/EDR already uses canary files + behavioral detection
- **Admin-level ransomware can bypass file permissions by:**
  - Manually parsing MFT (Master File Table)
  - Writing data directly to disk (bypassing NTFS)
- EDR vendors use techniques to prevent their software from being killed
- Ransomware can implement same techniques
- It's a cat-and-mouse game

### Impact on Project:
❌ **File locks alone won't work** against sophisticated attacks
⚠️ **Admin access is our biggest challenge**
🔍 **Need kernel-level or hardware solution**

### Technical Details:
```
Attack Vector: Direct Disk Write
1. Ransomware gets admin privileges
2. Parses MFT directly (bypasses filesystem)
3. Writes encrypted data to raw disk sectors
4. File permissions are irrelevant
Result: File locks bypassed
```

### Action Items:
- [ ] Research MFT parsing techniques
- [ ] Study direct disk write methods
- [ ] Investigate kernel-level hooks (minifilter drivers)
- [ ] Consider hardware-based protection (TPM, secure boot)
- [ ] Accept that no solution is 100% - aim for 70-80% protection

### Quote:
> "What if you manually parse the MFT, and writing data directly to disk? For most impact ransomware should be running as administrator. At that point, what's a file lock going to do if it's circumventing NTFS permissions?"

---

## Lesson 3: Detection ≠ Protection (Pre-Built Architecture Required)

**Source:** TruReyito (15 upvotes - Top comment)

### What We Learned:
- Modern security strategy = **"assume breach"**
- Detection is NOT protection (by the time you detect, files are encrypted)
- Need **pre-built defensive architecture**, not reactive responses
- Can't detect malware and THEN lock files (too late)
- Canary files are for detection, not protection
- Wherever ransomware executes is "likely already a casualty"

### Impact on Project:
✅ **Validates our token approach** - it's pre-built, not reactive
✅ **Confirms the gap** - detection happens too late
🎯 **Frame our tool correctly** - "zero-trust file access" not "ransomware detection"

### Philosophy Shift:
```
OLD THINKING:
1. Detect ransomware
2. Lock files
3. Kill process
Problem: Steps 1-2 take time, files already encrypted

NEW THINKING (Our Approach):
1. Files locked by default
2. Require token for ANY write
3. Ransomware can't get token
Result: Protection is pre-built
```

### Action Items:
- [ ] Frame marketing as "assume breach" mindset
- [ ] Emphasize pre-built architecture
- [ ] Don't rely on detection/behavioral analysis
- [ ] Position as "zero-trust file access control"

### Quote:
> "You aren't going to detect malware and then initiate mass file write lock downs... You architect the defensive players into the system... so that if ransomware deploys your 'detections' give you the time to limit the spread."

---

## Lesson 4: Real Companies Use Similar Techniques

**Source:** Wolpertingar (2 upvotes)

### What We Learned:
- Company used **FSRM (File Server Resource Manager)** to detect encrypted file extensions
- PowerShell script auto-denies user access when .locky, .enc files detected
- Had false positives but worked as "last line of defense"
- Modern EDR should do this better (not relying on extensions)

### Impact on Project:
✅ **Proof of concept works** in production environments
⚠️ **Extension-based detection is weak** (easy to bypass)
🔍 **Entropy analysis is better** than extension matching

### Real-World Implementation:
```
FSRM Detection Flow:
1. Monitor file creation events
2. Check file extension (.locky, .enc, .encrypted)
3. If match → PowerShell script triggers
4. Script adds user to deny group
5. User loses access to share
Result: Contained but files already encrypted
```

### Why Our Approach is Better:
- ❌ FSRM: Reactive (detects after encryption starts)
- ✅ Our tool: Proactive (blocks before encryption)
- ❌ FSRM: Extension-based (easy to bypass)
- ✅ Our tool: Token-based (can't bypass without token)

### Action Items:
- [ ] Research FSRM for Windows implementation ideas
- [ ] Don't rely on file extensions
- [ ] Use entropy analysis + behavioral patterns
- [ ] Study their false positive cases

### Quote:
> "We used FSRM to check the files for common encryption file name extensions... If somebody created such a file, a powershell script put the user in a deny group"

---

## Lesson 5: EDR Already Does Behavioral Detection

**Source:** 2timetime (2 upvotes)

### What We Learned:
- Windows Defender successfully blocked Akira v2 ransomware
- EDR uses behavioral detection to catch ransomware
- It works but isn't 100% effective

### Impact on Project:
✅ **EDR exists but has gaps** - room for additional layers
🤔 **Need to understand what EDR misses**
🎯 **Position as complementary**, not replacement

### Action Items:
- [ ] Research Akira v2 ransomware family
- [ ] Understand what triggers EDR detection
- [ ] Find edge cases EDR misses (slow encryption, etc.)
- [ ] Position tool as "additional layer beyond EDR"

---

## Lesson 6: Multi-Layer Defense is Standard

**Source:** cbowers (3 upvotes)

### What We Learned:
- Don't think "last line of defense" - think "all lines of defense"
- ESET uses multiple layers:
  - Network layer (connection termination)
  - HIPS rules (block unexpected child processes)
  - Ransomware-specific components
  - Supply chain management
  - UEFI/firmware monitoring (Eclypsium)
- No single layer is invincible

### Impact on Project:
✅ **Our tool is ONE layer** in multi-layer defense
✅ **Should integrate with existing security stack**
⚠️ **Don't claim to be complete solution**

### Defense Layers:
```
Layer 1: Network (block C2 connections)
Layer 2: Endpoint (EDR behavioral detection)
Layer 3: Process (HIPS rules)
Layer 4: Filesystem (Our token system) ← NEW LAYER
Layer 5: Backup (Snapshots/immutable backups)
Layer 6: Recovery (IR playbook)
```

### Action Items:
- [ ] Research ESET HIPS implementation
- [ ] Study supply chain attack vectors
- [ ] Design integration points with EDR
- [ ] Position as "Layer 4" not "complete solution"

### Quote:
> "I don't really think of 'last line of defence' I think of all lines of defence... it's all of them working in concert"

---

## Lesson 7: Performance Matters (Pre-Built vs Reactive)

**Source:** caribbeanjon (1 upvote)

### What We Learned:
- Changing file permissions reactively is too slow
- Better to remount filesystem read-only
- Snapshots are fastest recovery method
- Reactive protection is ineffective

### Impact on Project:
✅ **Our pre-built locks avoid this problem**
✅ **Validates architecture decision**
🎯 **Emphasize performance in marketing**

### Performance Comparison:
```
REACTIVE APPROACH (Slow):
1. Detect ransomware (1-5 seconds)
2. Change permissions on 10,000 files (30+ seconds)
3. Files already encrypted
Result: Too slow

OUR APPROACH (Fast):
1. Permissions already locked (0 seconds)
2. Token required for write (0.1 seconds)
3. Ransomware blocked immediately
Result: Effective
```

### Action Items:
- [ ] Benchmark token validation speed (<0.1s)
- [ ] Measure overall system overhead (<5%)
- [ ] Emphasize "pre-built" in documentation
- [ ] Compare performance vs reactive solutions

---

## Lesson 8: IR Process Matters More Than Tech

**Source:** Admirable_Group_6661 - Security Architect (2 upvotes)

### What We Learned:
- Complete control requires: preventive + detective + corrective controls
- Focus on containment, not fixing
- Burn and rebuild is safest approach
- Without backups, you're "cooked"
- MTD (Maximum Tolerable Downtime) will likely be exceeded
- Process matters more than technology

### Impact on Project:
⚠️ **Technology alone isn't enough**
✅ **Our tool is preventive control**
🔍 **Need to integrate with IR processes**

### Control Types:
```
PREVENTIVE (Our Tool):
- Block unauthorized file writes
- Require token authentication
- Pre-built file locks

DETECTIVE (EDR):
- Behavioral analysis
- Anomaly detection
- Alert on suspicious activity

CORRECTIVE (IR/Backup):
- Incident response playbook
- Restore from backups
- Burn and rebuild
```

### Action Items:
- [ ] Document how tool fits into IR process
- [ ] Create integration guide for SOC teams
- [ ] Emphasize backup importance
- [ ] Don't oversell technology capabilities

### Quote:
> "Notice it's a lot of focus on processes as oppose to tech..."

---

## Lesson 9: 🚨 CRITICAL - Remote Ransomware Changes Everything

**Source:** Anonymous SOC Analyst (1 upvote) - MOST IMPORTANT RESPONSE

### What We Learned:

#### Old Ransomware (What we're protecting against):
- Runs locally on infected machine
- CPU intensive (noisy)
- Takes time
- Leaves signatures
- Full file encryption (high entropy = detectable)

#### NEW Ransomware (Modern threat):
- **Files copied OUT of network**
- **Encrypted REMOTELY** (not on victim machine)
- **Partial encryption** - only strategic blocks (low entropy change)
- **Copied back** via normal SMB traffic
- **Double extortion** - data breach + encryption

### Impact on Project:
❌ **CRITICAL FLAW IDENTIFIED** - Our system doesn't protect against this
🚨 **Major pivot required** - Need to address exfiltration, not just encryption
⚠️ **We're solving yesterday's problem** - Modern ransomware is different

### Attack Flow (Modern):
```
Phase 1: EXFILTRATION (Our system doesn't block)
1. Malware reads files (no token needed for reads)
2. Copies to attacker server via SMB
3. Data breach occurs

Phase 2: REMOTE ENCRYPTION (Outside our control)
4. Attacker encrypts files on their server
5. Uses partial encryption (strategic blocks)
6. Low entropy change = hard to detect

Phase 3: REPLACEMENT (Our system might not block)
7. Encrypted files copied back via SMB
8. Looks like normal network file operation
9. SMB might be whitelisted
10. Files replaced with encrypted versions
```

### Why Our Current Approach Fails:
```
Our System Sees:
- "SMB process reading files" → ✅ Allowed (reads don't need tokens)
- "Network file transfer" → ✅ Allowed (legitimate protocol)
- "SMB process writing files" → ✅ Might allow (SMB is whitelisted)

Result: Ransomware bypasses our protection entirely
```

### Technical Details:

**Partial Encryption Technique:**
- Don't encrypt entire file (obvious from entropy)
- Encrypt strategic blocks (file headers, key data structures)
- File becomes corrupted/unusable
- Entropy analysis doesn't detect it
- Much faster than full encryption

**Why It's Effective:**
- Looks like normal file operations
- No CPU spike on victim machine
- No obvious entropy change
- Uses legitimate protocols (SMB)
- Hard to distinguish from normal activity

### What This Means:

**Our token system protects:**
- ✅ Local file encryption
- ✅ Process-based attacks
- ✅ Mass file modifications

**Our token system DOESN'T protect:**
- ❌ Files being copied out (exfiltration)
- ❌ Remote encryption
- ❌ SMB-based file replacement
- ❌ Data breach/double extortion
- ❌ Partial encryption attacks

### Potential Solutions:

**Option 1: Require Tokens for Reads (Nuclear)**
```
Pros:
- Prevents exfiltration
- Complete file access control

Cons:
- Terrible user experience
- Token required for every file open
- Users would hate it
- Productivity impact
```

**Option 2: Network Monitoring Layer**
```
Pros:
- Detect files being copied out
- Monitor SMB traffic patterns
- Alert on suspicious transfers

Cons:
- Requires network-level integration
- Complex to implement
- Performance overhead
```

**Option 3: File Integrity Monitoring**
```
Pros:
- Track file hashes
- Detect when file replaced
- Alert on "went out, came back different"

Cons:
- Database of all file hashes
- Storage overhead
- Performance impact
```

**Option 4: Hybrid Approach (Recommended)**
```
Layer 1: Token for local writes (current system)
Layer 2: Monitor network file operations
Layer 3: Detect exfiltration patterns
Layer 4: Block file replacement if hash changed
Layer 5: Alert on suspicious SMB activity
```

### Critical Questions:

1. **Should we require tokens for reads?**
   - Prevents exfiltration but kills usability
   - Maybe only for sensitive folders?

2. **How to detect copy-out/copy-back pattern?**
   - Track file hashes before/after network transfer?
   - Monitor SMB traffic for same filename?

3. **Can we detect partial encryption?**
   - Entropy analysis won't work
   - Need different detection method
   - File structure analysis?

4. **How to handle legitimate SMB operations?**
   - Can't block all network file access
   - Need to distinguish legitimate vs malicious
   - Whitelist trusted servers?

### Action Items:
- [ ] Research remote ransomware families (LockBit, BlackCat, ALPHV)
- [ ] Study exfiltration detection techniques
- [ ] Understand partial encryption methods
- [ ] Rethink architecture to include network layer
- [ ] Consider if token-based approach still makes sense
- [ ] Research DLP (Data Loss Prevention) solutions
- [ ] Study SMB traffic analysis
- [ ] Investigate file integrity monitoring systems

### Updated Threat Model:

**OLD (What we planned for):**
```
Threat: Local file encryption
Protection: Token-based write control
Result: Effective
```

**NEW (What we must address):**
```
Threat: Remote encryption + exfiltration
Protection: ??? (Need to figure out)
Result: Current approach insufficient
```

### Project Pivot Required:

**Before This Insight:**
- Focus: Prevent local file encryption
- Solution: Token-based write control
- Target: Traditional ransomware

**After This Insight:**
- Focus: Prevent exfiltration + remote encryption
- Solution: Multi-layer (local + network)
- Target: Modern ransomware

### Silver Lining:

This makes our project MORE valuable because:
- ✅ Addressing cutting-edge threat
- ✅ Gap that even EDR struggles with
- ✅ Network + local = comprehensive
- ✅ Hardware tokens could prevent exfiltration (require token to read)
- ✅ More interesting research problem

### Quote:
> "Now remote ransomware is a thing. Files are copied out of the network and encrypted remotely. And they don't encrypt the whole file (that looks obviously from an entropy perspective), but select strategic blocks the file to encrypt which corrupt it or make it unusable. Then they copy the files back. All you see is some SMB like process copying files across the network..."

---

## Overall Lessons Summary

### What We Got Right:
1. ✅ Token-based approach is valid (Microsoft uses it)
2. ✅ Pre-built architecture is correct (not reactive)
3. ✅ Multi-layer defense is necessary
4. ✅ There's a gap in current solutions

### What We Got Wrong:
1. ❌ Assumed ransomware encrypts locally (it doesn't anymore)
2. ❌ Focused only on write operations (reads matter too)
3. ❌ Ignored network layer (critical for modern threats)
4. ❌ Underestimated admin-level bypass techniques

### Critical Gaps Identified:
1. 🚨 Remote encryption (files encrypted off-system)
2. 🚨 Exfiltration (data breach before encryption)
3. 🚨 Partial encryption (entropy analysis won't detect)
4. 🚨 SMB-based attacks (looks like legitimate traffic)
5. 🚨 Admin-level bypasses (direct disk writes)

### Project Direction Changes:

**Original Plan:**
- Week 3: Local filesystem monitoring
- Week 4: Token enforcement for writes
- Focus: Prevent local encryption

**Updated Plan:**
- Week 3: Local + network monitoring
- Week 4: Token enforcement + exfiltration detection
- Week 5: File integrity monitoring
- Week 6: SMB traffic analysis
- Focus: Prevent exfiltration + remote encryption

### Technology Stack Updates:

**Original:**
- Filesystem hooks (ReadDirectoryChangesW)
- Token validation
- Entropy analysis

**Updated:**
- Filesystem hooks (local)
- Network monitoring (SMB traffic)
- Token validation (reads + writes?)
- File integrity monitoring (hashes)
- Exfiltration detection
- Partial encryption detection

### Market Positioning Changes:

**Before:**
"Token-based ransomware protection"

**After:**
"Zero-trust file access control with exfiltration prevention"

### Success Metrics Updated:

**Original:**
- Block 80% of local ransomware
- <5% performance overhead
- 10-minute token validity

**Updated:**
- Block 70% of modern ransomware (including remote)
- Detect 90% of exfiltration attempts
- <5% performance overhead (local + network)
- Prevent data breach + encryption

---

## Key Takeaways for Development

### Immediate Actions (This Week):
1. [ ] Test Windows Defender Protected Folders
2. [ ] Research remote ransomware families
3. [ ] Study exfiltration detection methods
4. [ ] Understand partial encryption techniques
5. [ ] Investigate SMB traffic monitoring

### Architecture Changes (Week 3-4):
1. [ ] Add network monitoring layer
2. [ ] Implement file integrity checking
3. [ ] Consider token requirements for reads
4. [ ] Design exfiltration detection
5. [ ] Plan SMB traffic analysis

### Research Needed:
1. [ ] How does Defender Protected Folders work?
2. [ ] What are MFT parsing techniques?
3. [ ] How to detect partial encryption?
4. [ ] What are modern ransomware families doing?
5. [ ] How do DLP solutions work?

### Questions to Answer:
1. Should we require tokens for reads? (Usability vs security)
2. Can we detect copy-out/copy-back patterns?
3. How to handle legitimate SMB operations?
4. Is our approach still viable for modern threats?
5. Should we pivot to exfiltration prevention?

---

## Validation of Approach

### What Reddit Confirmed:
✅ There IS a gap in current solutions
✅ Pre-built architecture is the right approach
✅ Token-based control is valid (Microsoft uses it)
✅ Multi-layer defense is necessary
✅ Real companies use similar techniques

### What Reddit Challenged:
⚠️ Local-only protection is insufficient
⚠️ Modern ransomware is more sophisticated
⚠️ Admin-level bypasses are real
⚠️ Exfiltration is as important as encryption
⚠️ Network layer is critical

### Overall Assessment:
**Our core idea is sound, but scope must expand significantly.**

---

## Next Steps

### Week 3 (Updated):
- Implement local filesystem monitoring (original plan)
- Add network file operation monitoring (NEW)
- Research remote ransomware techniques (NEW)
- Test Defender Protected Folders (NEW)

### Week 4 (Updated):
- Token enforcement for writes (original plan)
- Consider token requirements for reads (NEW)
- Implement basic exfiltration detection (NEW)
- Design file integrity monitoring (NEW)

### Week 5-6 (NEW):
- SMB traffic analysis
- Partial encryption detection
- Integration with existing EDR
- Performance optimization (local + network)

### Long-term (Months 2-3):
- Hardware token integration
- Kernel-level hooks (minifilter drivers)
- Admin-level bypass prevention
- Enterprise deployment features

---

## Conclusion

Reddit discussion was INVALUABLE. Discovered:
1. Windows already has similar feature (Defender Protected Folders)
2. Modern ransomware uses remote encryption (game changer)
3. Admin-level bypasses are real threat
4. Our approach is valid but scope must expand
5. Network layer is critical for modern threats

**Project is still viable but requires significant pivot to address modern ransomware techniques.**

**Most important lesson: We were solving yesterday's problem. Now we know what today's problem looks like.**

---

## Metrics

- **Post Engagement:** 16 upvotes, 10 detailed responses
- **Professional Input:** SOC analysts, Red Team, Security Architects
- **Critical Insights:** 9 major lessons learned
- **Project Impact:** Major architecture pivot required
- **Value:** Saved months of development in wrong direction

**Reddit validation: EXTREMELY VALUABLE** ⭐⭐⭐⭐⭐

---

**Document Status:** Living document - will update as we learn more
**Last Updated:** February 2026
**Next Review:** After Week 3 implementation
