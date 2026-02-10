# Anti-Ransomware Protection System - Personal Development Plan

**Initiated on Jan 27th, 2026**

As the creator of the Anti-Ransomware Protection System project, initiated today on January 27, 2026, in Abuja, FCT, NG, I'm building this innovative zero-trust file protection system as a **personal project first**. This plan prioritizes building a functional software prototype for my own use, followed by finding malware experts to collaborate with (like co-persons), and only after 6 months will I consider any spending or business outreach.

The plan is divided into **monthly phases** (from January 27, 2026, to July 27, 2026), with **weekly milestones** for easy tracking and execution. It's designed to be realistic, low-cost, and milestone-driven—assuming I'm working solo initially. Total timeline: 26 weeks. Key assumptions:

- I'll dedicate 20-30 hours/week.
- **No spending for 6 months** - only free tools and my time.
- Success metric for software: A working MVP that demonstrates token-based access and ransomware detection.
- If software succeeds (e.g., passes internal tests), then consider hardware exploration.
- Malware expertise: Find experts to work with like co-persons, not hire them.

By the end of 6 months, I'll have:

- A polished software prototype built for myself.
- 1-2 malware experts working with me as collaborators.
- A decision point: continue as personal tool or explore broader applications.
- A hardware prototype plan, if viable.
- Documented progress for my own reference.

---

## Month 1: Foundation & Software Prototype Kickoff (Jan 27 - Feb 27, 2026)

**Focus:** Establish project fundamentals and begin core software development (drawing from PROJECT.md and ARCHITECTURE.md). No external involvement yet—focus on building.

### Week 1 (Jan 27 - Feb 2): Project Setup

- Define scope: Lock in requirements (e.g., Windows-focused prototype with JWT tokens, ReadDirectoryChangesW hooks, SQLite logs).
- Set up dev environment: Install Python 3.8+, PyJWT, cryptography libs, pywin32; set up Git repo.
- Research quick wins: Explore Windows API for file monitoring (ReadDirectoryChangesW, minifilter drivers via free resources).
- **Achievement:** Project charter document and basic code skeleton.
- **Must Achieve This Week:**
  - [X] Complete development environment setup
  - [X] Create Git repository with initial project structure
  - [X] Write project requirements document (2-3 pages)
  - [X] Research and document 3 Windows API approaches for file monitoring
  - [X] Create basic Python project structure with main modules

### Week 2 (Feb 3-9): Master Key & Token Implementation

- Develop master key derivation (Argon2id or simulated YubiKey).
- Create dynamic token generation/validation (HKDF, HMAC proofs).
- Test basic CLI for token requests.
- **Achievement:** Working token system (e.g., local generate/validate functionality).
- **Must Achieve This Week:**
  - [X] Implement Argon2id password-based key derivation
  - [X] Create HKDF token generation function
  - [X] Build HMAC proof validation system
  - [X] Write CLI script that generates and validates tokens
  - [X] Test token system with 10 different scenarios
  - [X] Document token format and validation process

### Week 3 (Feb 10-16): Filesystem Monitoring Basics

- Implement ReadDirectoryChangesW hooks for protected folders.
- Add baseline database (SQLite) for file states (hashes, entropy).
- Test interception for read/write operations using Windows API.
- **Achievement:** Prototype monitors a test folder and logs changes.
- **Must Achieve This Week:**
  - [X] Implement ReadDirectoryChangesW monitoring for one folder
  - [X] Create SQLite database schema for file tracking
  - [X] Build file hash calculation function (SHA256)
  - [X] Implement entropy calculation for files
  - [X] Test monitoring by creating/modifying 20 test files
  - [X] Log all file changes to database with timestamps

**UPDATED BASED ON REDDIT FEEDBACK:**
- **Additional Requirements:**
  - [X] Research token requirements for READ operations (prevent exfiltration)
  - [ ] Design MFA system for permission changes
  - [ ] Study Windows Defender Protected Folders implementation
  - [ ] Plan kernel-level hooks for admin bypass prevention

### Week 4 (Feb 17-27): Initial Integration & Testing

- Integrate tokens with hooks: Enforce tokens for writes.
- Add basic ransomware detection rules (e.g., alerts for mass modifications).
- Conduct internal tests (simulate attacks on my machine).
- **Achievement:** MVP v0.1—Functional protection on local Windows. Note bugs/fixes.
- **Must Achieve This Week:**
  - [X] Connect token validation to file monitoring
  - [X] Block write operations without valid tokens
  - [X] Implement basic ransomware detection (>5 files in 10 seconds)
  - [X] Create test script that simulates ransomware behavior
  - [X] Successfully block simulated attack 8/10 times
  - [ ] Document 5+ bugs found and their fixes
  - [ ] Create MVP v0.1 release with basic functionality

**Month 1 End Goal:** A basic software prototype ready for personal testing. No hardware considerations yet.

---

## Month 2: Software Refinement & Internal Validation (Feb 28 - Mar 27, 2026)

**Focus:** Refine the software, incorporate features, and test thoroughly on my own. No outreach—solidify the build first.

### Week 5 (Feb 28 - Mar 5): Enhance Detection Engine

- Add entropy analysis and risk scoring.
- Implement auto-lockdown (e.g., permission changes on alerts).
- **Achievement:** Detection rules activate during simulated ransomware scenarios.
- **Must Achieve This Week:**
  - [ ] Implement Shannon entropy calculation for files
  - [ ] Create risk scoring algorithm (0-10 scale)
  - [ ] Build auto-lockdown mechanism (change file permissions)
  - [ ] Test entropy detection with encrypted vs normal files
  - [ ] Achieve 90%+ accuracy in detecting file encryption
  - [ ] Create 3 different attack simulation scenarios

### Week 6 (Mar 6-12): UI/CLI Improvements

- Develop a simple GUI (e.g., via Tkinter or Qt) for token requests and logs.
- Include process whitelisting database.
- **Achievement:** Intuitive interface for folder protection and audit viewing.
- **Must Achieve This Week:**
  - [ ] Create basic GUI with Tkinter (3 main screens)
  - [ ] Build token request dialog with PIN entry
  - [ ] Implement audit log viewer with filtering
  - [ ] Create process whitelist management interface
  - [ ] Add 10 common Windows applications to whitelist
  - [ ] Test GUI with family member or friend for usability

### Week 7 (Mar 13-19): Performance Optimizations

- Add token caching and async logging.
- Measure overhead (aim for <5%).
- Resolve any performance bottlenecks.
- **Achievement:** Optimized prototype with personal test reports.
- **Must Achieve This Week:**
  - [ ] Implement token caching system (10-minute sessions)
  - [ ] Add asynchronous logging to prevent blocking
  - [ ] Benchmark file operation overhead (before/after)
  - [ ] Achieve <5% performance impact on file operations
  - [ ] Optimize database queries for faster lookups
  - [ ] Create performance test report with metrics

### Week 8 (Mar 20-27): Full Internal Testing & Documentation

- Simulate varied attacks (e.g., rapid file alterations) and confirm defenses.
- Draft a user manual and demo script for self-reference.
- **Achievement:** MVP v1.0—Stable software prepared for collaborative input. If effective (e.g., 80% attack block rate), approve hardware exploration.
- **Must Achieve This Week:**
  - [ ] Test against 5 different ransomware simulation patterns
  - [ ] Achieve 80%+ attack blocking success rate
  - [ ] Write comprehensive user manual (10+ pages)
  - [ ] Create demo script showing all features
  - [ ] Record 5-minute demo video of system working
  - [ ] Fix all critical bugs found during testing
  - [ ] Release MVP v1.0 with full documentation

**Month 2 End Goal:** A robust, testable software MVP. Evaluate progress; prepare for expert connections if ready.

---

## Month 3: Expert Connection & Software Enhancements (Mar 28 - Apr 27, 2026)

**Focus:** With software built, connect with 1-2 malware experts (e.g., through LinkedIn, Nigerian tech forums like Andela or TechCabal) as collaborators for insights.

### Week 9 (Mar 28 - Apr 3): Identify & Contact Experts

- Search for malware experts: Aim for 5-10 candidates (e.g., Nigerian/global cybersecurity specialists with ransomware knowledge).
- Reach out: Via email/LinkedIn, share project overview and MVP demo link—seek collaboration, not employment.
- **Achievement:** 3-5 responses; arrange informal discussions.
- **Must Achieve This Week:**
  - [ ] Research and identify 10 potential expert collaborators
  - [ ] Create professional project overview (2-page summary)
  - [ ] Send personalized outreach messages to 10 experts
  - [ ] Receive responses from at least 3 experts
  - [ ] Schedule video calls with 3-5 interested experts
  - [ ] Prepare demo presentation for expert meetings

### Week 10 (Apr 4-10): Establish Collaborations

- Discuss and select 1-2 experts as co-persons/collaborators.
- Share MVP code for their review—no financial commitments.
- **Achievement:** Informal collaboration pacts; first feedback exchange.
- **Must Achieve This Week:**
  - [ ] Conduct 3-5 expert interviews/discussions
  - [ ] Select 1-2 experts for ongoing collaboration
  - [ ] Share complete source code with selected collaborators
  - [ ] Establish communication channels (Discord/Slack)
  - [ ] Receive initial feedback from collaborators
  - [ ] Create collaboration agreement (informal document)

### Week 11 (Apr 11-17): Incorporate Expert Feedback

- Apply suggested enhancements (e.g., refined entropy rules, vulnerability patches).
- Test jointly via shared sessions.
- **Achievement:** MVP v1.1 with collaborative improvements.
- **Must Achieve This Week:**
  - [ ] Implement 5+ expert-suggested improvements
  - [ ] Fix 3+ security vulnerabilities identified by experts
  - [ ] Conduct joint testing session with collaborators
  - [ ] Update entropy detection based on expert input
  - [ ] Improve token validation security
  - [ ] Release MVP v1.1 with expert enhancements

### Week 12 (Apr 18-27): Joint Testing & Refinement

- Perform advanced simulations (e.g., sandboxed real ransomware samples).
- Record updates.
- **Achievement:** Polished software; experts as active collaborators.
- **Must Achieve This Week:**
  - [ ] Set up safe testing environment for real malware samples
  - [ ] Test against 3 real ransomware samples (safely)
  - [ ] Achieve 85%+ protection rate against real threats
  - [ ] Document all test results and improvements
  - [ ] Establish regular collaboration schedule with experts
  - [ ] Create joint roadmap for future improvements

**Month 3 End Goal:** 1-2 malware experts as partners; software advanced to v1.1.

---

## Month 4: Software Enhancement & Documentation (Apr 28 - May 27, 2026)

**Focus:** Further refine software through expert collaboration. Remain in personal project mode—no outreach.

### Week 13 (Apr 28 - May 4): Advanced Features

- Add sophisticated detection algorithms with expert guidance.
- Enhance entropy analysis depth.
- **Achievement:** Improved detection precision.
- **Must Achieve This Week:**
  - [ ] Implement machine learning-based anomaly detection
  - [ ] Add behavioral analysis for process monitoring
  - [ ] Improve entropy analysis with sliding window technique
  - [ ] Create advanced threat scoring algorithm
  - [ ] Test new features against 10 attack scenarios
  - [ ] Achieve 90%+ detection accuracy

### Week 14 (May 5-11): Cross-Platform Testing

- Test across Windows versions (10, 11).
- Log and address compatibility notes.
- **Achievement:** Verified broader Windows support.
- **Must Achieve This Week:**
  - [ ] Test on Windows 10 (3 different builds)
  - [ ] Test on Windows 11 (2 different builds)
  - [ ] Document compatibility issues and solutions
  - [ ] Fix 5+ compatibility problems found
  - [ ] Create compatibility matrix document
  - [ ] Ensure 95%+ functionality across all tested versions

### Week 15 (May 12-18): Security Hardening

- Collaborate on spotting and fixing vulnerabilities.
- Layer in extra security protocols.
- **Achievement:** Strengthened, resilient system.
- **Must Achieve This Week:**
  - [ ] Conduct security audit with expert collaborators
  - [ ] Fix 10+ security vulnerabilities identified
  - [ ] Implement additional encryption for sensitive data
  - [ ] Add tamper detection mechanisms
  - [ ] Create secure communication protocols
  - [ ] Pass security review from expert collaborators

### Week 16 (May 19-27): Documentation & Demo

- Compile detailed personal documentation.
- Create a demo video demonstrating features.
- **Achievement:** Fully documented setup; software v1.2.
- **Must Achieve This Week:**
  - [ ] Write comprehensive technical documentation (20+ pages)
  - [ ] Create user installation guide with screenshots
  - [ ] Record professional demo video (10+ minutes)
  - [ ] Document all APIs and configuration options
  - [ ] Create troubleshooting guide with common issues
  - [ ] Release software v1.2 with full documentation

**Month 4 End Goal:** Advanced software via collaboration; solid personal records.

---

## Month 5: Advanced Testing & Evaluation (May 28 - Jun 27, 2026)

**Focus:** Rigorous self-testing of the system. Assess if it meets personal needs or warrants further steps.

### Week 17 (May 28 - Jun 3): Stress Testing

- Execute tests under diverse attack conditions.
- Evaluate system under heavy load.
- **Achievement:** Detailed test outcomes.
- **Must Achieve This Week:**
  - [ ] Test with 1000+ files being monitored simultaneously
  - [ ] Simulate high-frequency file operations (100/second)
  - [ ] Test system stability over 72-hour period
  - [ ] Measure memory and CPU usage under load
  - [ ] Test recovery from system crashes/restarts
  - [ ] Document performance limits and bottlenecks

### Week 18 (Jun 4-10): Real-World Simulation

- Configure a lifelike test setup with my files.
- Mimic everyday usage.
- **Achievement:** Practical performance insights.
- **Must Achieve This Week:**
  - [ ] Set up protection on actual personal documents
  - [ ] Use system for 1 week of normal computer activities
  - [ ] Test with real applications (Office, browsers, etc.)
  - [ ] Measure user experience impact and friction
  - [ ] Document usability issues and improvements
  - [ ] Achieve <2% impact on daily workflow

### Week 19 (Jun 11-17): Expert Review

- Invite collaborators for in-depth security assessment.
- Pinpoint any overlooked issues.
- **Achievement:** Completed security review.
- **Must Achieve This Week:**
  - [ ] Conduct formal security review with expert collaborators
  - [ ] Test against latest ransomware techniques
  - [ ] Identify and fix 5+ remaining vulnerabilities
  - [ ] Get written security assessment from experts
  - [ ] Implement final security recommendations
  - [ ] Achieve expert approval for security posture

### Week 20 (Jun 18-27): Decision Point & Hardware Research

- Review: Sufficient for personal use, or explore more?
- If promising: Study hardware integration options.
- **Achievement:** Project assessment; hardware concept outline.
- **Must Achieve This Week:**
  - [ ] Complete comprehensive project evaluation
  - [ ] Decide: personal tool vs. broader application
  - [ ] Research hardware token integration options
  - [ ] Create cost analysis for hardware development
  - [ ] Document lessons learned and future possibilities
  - [ ] Make go/no-go decision for hardware phase

**Month 5 End Goal:** Comprehensive evaluation; informed decision on progression.

---

## Month 6: Hardware Exploration & Project Consolidation (Jun 28 - Jul 27, 2026)

**Focus:** If software excels, conceptualize hardware for token security. Conclude with overall review.

### Week 21 (Jun 28 - Jul 4): Hardware Planning

- Collaborate on specs (e.g., TPM-based USB token).
- Research components (no buys yet).
- **Achievement:** Hardware design sketch and analysis.
- **Must Achieve This Week:**
  - [ ] Design hardware token specifications
  - [ ] Research required components and suppliers
  - [ ] Create cost estimate for hardware prototype
  - [ ] Design integration protocol with software
  - [ ] Create hardware development timeline
  - [ ] Get expert input on hardware feasibility

### Week 22 (Jul 5-11): Integration Design

- Outline software-hardware fusion.
- Detail challenge-response flows.
- **Achievement:** Theoretical integration framework.
- **Must Achieve This Week:**
  - [ ] Design complete hardware-software protocol
  - [ ] Create detailed challenge-response flow diagrams
  - [ ] Specify hardware communication interface
  - [ ] Design secure key storage mechanism
  - [ ] Create integration testing plan
  - [ ] Document hardware security requirements

### Week 23 (Jul 12-18): Final Software Polish

- Make last refinements and fixes.
- Fine-tune for optimal personal use.
- **Achievement:** Finalized version.
- **Must Achieve This Week:**
  - [ ] Fix all remaining bugs and issues
  - [ ] Optimize performance for daily use
  - [ ] Create final user interface improvements
  - [ ] Complete all documentation updates
  - [ ] Create final software release (v2.0)
  - [ ] Prepare software for potential hardware integration

### Week 24-26 (Jul 19-27): Project Review & Future Planning

- Assemble 6-month summary: Key achievements, metrics (e.g., 85% protection rate).
- Decide: Stay personal, or initiate spending/outreach?
- **Achievement:** Full project wrap-up; next-phase strategy.
- **Must Achieve This Week:**
  - [ ] Write comprehensive 6-month project report
  - [ ] Document all achievements and metrics
  - [ ] Create final demo showcasing all capabilities
  - [ ] Evaluate total time and effort invested
  - [ ] Make final decision on project future
  - [ ] Create roadmap for next phase (if applicable)
  - [ ] Archive all project materials and code

**Month 6 End Goal:** Completed software system; decision on expansion beyond personal scope.

---

## Personal Notes & Flexibility

This plan is adaptable—tweak as needed. Track progress in a free tool like Trello. If challenges arise (e.g., collaborator connections), turn to online forums.

**Key Reminders:**

- This is a **personal project first** - build for myself
- **No spending until after 6 months** of development
- Focus on software prototype before any hardware considerations
- Malware experts will be **like co-persons** - collaborators, not employees
- Only after 6 months will I consider if this should become more than personal
- Document everything for future reference

Let's build this Anti-Ransomware project successfully!
