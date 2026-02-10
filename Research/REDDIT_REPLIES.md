# Suggested Replies to Reddit Comments

## Reply to TruReyito (15 upvotes - Top comment)

**Their point:** Detection ≠ protection. Need pre-built defensive architecture.

**Your reply:**
```
Great point about "assume breach" - that's exactly the mindset I'm exploring. 

You're right that detection alone isn't protection. What I'm curious about is 
the gap between detection and response. Most EDR detects suspicious behavior 
and alerts/kills the process, but by then files might already be encrypted.

I'm thinking about pre-built controls that don't rely on detection at all - 
like requiring cryptographic authentication for ANY file write operation, 
regardless of which process requests it. So even if ransomware executes and 
isn't detected, it still can't modify files without valid tokens.

Basically: "You can run on my system, but you can't touch my files without 
this physical key." Similar to how full-disk encryption protects against 
physical theft.

Does that approach make sense or am I missing something fundamental?
```

---

## Reply to Sqooky (8 upvotes - Red Team perspective)

**Their point:** AV/EDR already does this. Attackers bypass it. Cat and mouse game.

**Your reply:**
```
Really appreciate the Red Team perspective! You're absolutely right about the 
cat-and-mouse game.

The MFT parsing and direct disk write scenario is interesting - that's the 
kind of bypass I'm trying to understand. If ransomware has admin privileges 
and writes directly to disk, traditional file permissions won't help.

What about kernel-level hooks that intercept at the filesystem driver level? 
Or would that just be another layer to bypass?

I'm thinking the only real "last line" might be cryptographic - where files 
are encrypted at rest and the decryption key is on a physical device 
(like YubiKey). Even with admin access, you can't decrypt without the 
physical token.

But that has usability issues... curious if you've seen anything like that 
in the wild?
```

---

## Reply to 2timetime (2 upvotes - EDR example)

**Their point:** EDR (Defender) blocked Akira v2 ransomware.

**Your reply:**
```
That's great to hear! Do you know what specifically triggered the block? 
Was it behavioral detection (mass file changes) or signature-based?

I'm curious about the edge cases where EDR might miss it - like if 
ransomware encrypts slowly (1 file per minute) to avoid behavioral triggers.
```

---

## Reply to Gorstak-Zadar (2 upvotes - Windows features)

**Their point:** UAC + Defender Protected Folders + disable EFS.

**Your reply:**
```
Good point about Defender's Protected Folders feature - that's closer to 
what I'm thinking about.

Question: If ransomware is running with user privileges (not admin), can 
Protected Folders actually block it? Or does the user's own process have 
implicit access to their files?

Also curious about the EFS registry value - does disabling EFS prevent 
ransomware from using other encryption methods (like AES)?
```

---

## Reply to cbowers (3 upvotes - ESET layers)

**Their point:** Multiple layers working together. ESET has ransomware remediation.

**Your reply:**
```
Love the "all lines of defense" mindset. The ESET ransomware remediation 
link is helpful - looks like they use behavioral detection + automatic 
rollback.

The HIPS rules blocking unexpected child processes is interesting. Do you 
find that catches most ransomware, or do some still slip through by 
mimicking legitimate process behavior?

Also curious about the supply chain angle - if malware gets injected into 
a trusted application (like a compromised update), would HIPS still catch it?
```

---

## Reply to Admirable_Group_6661 (2 upvotes - IR focus)

**Their point:** Focus on IR process, containment, burn and rebuild.

**Your reply:**
```
Solid IR perspective. You're right that process matters more than tech in 
the response phase.

My question is more about the prevention/containment boundary. If we assume 
the malware has already executed (prevention failed), what technical controls 
can limit damage BEFORE the IR team even knows there's an incident?

Like automated containment that doesn't require human detection/response. 
Is that realistic or am I overthinking it?
```

---

## Reply to caribbeanjon (1 upvote - Snapshots)

**Their point:** Changing permissions too slow. Use snapshots for recovery.

**Your reply:**
```
Good point about permission changes being too slow. I wasn't thinking about 
changing permissions reactively - more like having them locked by default 
and requiring explicit authentication to unlock.

So instead of:
1. Detect ransomware → 2. Lock files (too late)

It would be:
1. Files always locked → 2. Require token to unlock → 3. Ransomware can't 
get token

But yeah, snapshots are definitely the fastest recovery method if prevention 
fails.
```

---

## Reply to Wolpertingar (2 upvotes - FSRM solution)

**Their point:** Used FSRM to detect encrypted file extensions, auto-deny user access.

**Your reply:**
```
That's a clever approach! Detecting by file extension and auto-denying the 
user is basically automated containment.

Did you find it caught ransomware fast enough to prevent significant damage? 
Or would some files already be encrypted by the time the script triggered?

Also curious about the false positives - what legitimate files triggered it?
```

---

## General Follow-up Post (After replies)

**Post this as a comment on your own thread:**
```
Thanks everyone for the detailed responses! Really helpful to hear from 
people dealing with this in production.

Key takeaways I'm getting:
1. Modern EDR already does behavioral detection + auto-response
2. "Assume breach" means having controls pre-built, not reactive
3. Admin-level malware can bypass most file-level protections
4. Snapshots/backups are the most reliable recovery method

The gap I'm still curious about: What if we treat file access like network 
access? Where even legitimate processes need to authenticate before writing.

Like how VPNs require a token even if you're on the corporate network. 
Could that work for filesystems, or is it fundamentally different?

Appreciate all the insights - this is exactly the kind of feedback I was 
looking for!
```

---

## Key Strategy:

✅ **Be humble** - "What am I missing?"
✅ **Ask follow-up questions** - Shows genuine interest
✅ **Acknowledge their expertise** - "Great point", "Really helpful"
✅ **Don't push your solution yet** - Just explore the problem space
✅ **Build relationships** - These could be future collaborators

**Don't mention you're building a product until you have 50+ karma and established credibility!**
