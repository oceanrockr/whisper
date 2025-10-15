# 🚀 START HERE - Sprint 3 Kickoff Guide
**Critical Reading List for New Development Session**

**Last Updated:** October 14, 2025
**Purpose:** Definitive guide for starting Sprint 3
**Status:** Use ONLY these files from Reference_Docs folder

---

## ⚠️ IMPORTANT: Use ONLY Reference_Docs Folder

**Correct Location:** `docs/Reference_Docs/`

This folder contains the **definitive, final versions** of all reference documents. Do not use files from other locations as they may be outdated or duplicates.

---

## 📋 Definitive File List (Reference_Docs Folder ONLY)

### Files in Reference_Docs (8 total):

1. ✅ **CORE_DEVELOPMENT_PRINCIPLES.md** (26 KB)
2. ✅ **SPRINT_3_HANDOFF_OCT14_2025.md** (65 KB)
3. ✅ **HARDWARE_TESTING_GUIDE.md** (23 KB)
4. ✅ **PROJECT_STATUS_OCT14_2025.md** (18 KB)
5. ✅ **SPRINT_2_COMPLETION_OCT14_2025.md** (26 KB)
6. ✅ **AUDIO_API_TROUBLESHOOTING.md** (71 KB)
7. ✅ **DAILY_DEV_NOTES.md** (134 KB)
8. ✅ **README.md** (17 KB) - Index and navigation

**Total:** 8 files, 396 KB

---

## 🎯 CRITICAL: Read These 3 Files FIRST (30 minutes)

**Read in this exact order:**

### 1. CORE_DEVELOPMENT_PRINCIPLES.md (MANDATORY - 10 minutes)
**Location:** `docs/Reference_Docs/CORE_DEVELOPMENT_PRINCIPLES.md`

**Why Critical:**
- MANDATORY framework for ALL development work
- Defines confidence scoring (required before any change)
- Defines two-phase workflow (analyze → implement)
- Defines mandatory test structure (unit + edge + regression)
- Contains critical rules (never/always lists)

**What to Learn:**
- How to calculate confidence (5 factors)
- When to implement vs when to ask (≥95%, 90-94%, <90%)
- Two-phase workflow steps
- Test structure requirements

**Read These Sections:**
- Core Principles (4 principles)
- Confidence Scoring (examples included)
- Two-Phase Workflow (templates included)
- Mandatory Test Structure
- Critical Rules (never/always)

---

### 2. SPRINT_3_HANDOFF_OCT14_2025.md (CRITICAL - 15 minutes)
**Location:** `docs/Reference_Docs/SPRINT_3_HANDOFF_OCT14_2025.md`

**Why Critical:**
- Complete handoff for Sprint 3 (your current sprint)
- Contains all context from previous sprints
- Defines Sprint 3 objectives and priorities
- Includes RiPIT workflow deployment instructions
- Has ready-to-use startup prompt (Section 18)

**What to Learn:**
- Sprint 3 objectives (4 priorities)
- Current state assessment (100% MVP complete)
- Hardware testing requirements
- RiPIT subagent deployment (4 subagents)
- Timeline and milestones
- Known issues and workarounds

**Read These Sections:**
- Section 2: Executive Summary
- Section 3: Sprint 3 Objectives (Priority 1-4)
- Section 4: Current State Assessment
- Section 5: Hardware Testing Guide Reference
- Section 9: RiPIT Workflow Deployment Instructions
- Section 18: New Session Startup Prompt (copy/paste this)

---

### 3. HARDWARE_TESTING_GUIDE.md (IMPORTANT - 5 minutes skim)
**Location:** `docs/Reference_Docs/HARDWARE_TESTING_GUIDE.md`

**Why Important:**
- Step-by-step testing procedures
- Your first task in Sprint 3 (Priority 1)
- 10 comprehensive hardware tests documented
- Success criteria clearly defined

**What to Learn:**
- Testing checklist (10 tests)
- Test 1-3: USB webcam tests (primary test cases)
- Expected console output ("SWITCHING TO DIRECTSOUND")
- Success criteria (DirectSound logs, no WDM-KS errors)
- Troubleshooting guide

**Read These Sections:**
- Overview
- Testing Checklist (10 tests)
- Test 1: veleron_voice_flow.py with USB webcam
- Test 2: veleron_dictation.py with USB webcam
- Test 3: veleron_dictation_v2.py with USB webcam
- Success Criteria
- Common Issues and Solutions

---

## 📚 Reference Files (Read As Needed)

**Don't read these immediately - reference when needed:**

### 4. PROJECT_STATUS_OCT14_2025.md
**Location:** `docs/Reference_Docs/PROJECT_STATUS_OCT14_2025.md`

**When to Read:**
- Need quick project overview
- Want to understand application status
- Need security audit results
- Want to see test coverage metrics

**Key Sections:**
- Executive Summary (100% MVP complete)
- Application Status (all 5 apps)
- Security Status (all vulnerabilities fixed)
- Testing Infrastructure (334 tests)

---

### 5. SPRINT_2_COMPLETION_OCT14_2025.md
**Location:** `docs/Reference_Docs/SPRINT_2_COMPLETION_OCT14_2025.md`

**When to Read:**
- Need DirectSound implementation details
- Want to understand what was done yesterday
- Need technical reference for DirectSound code
- Want to see lessons learned

**Key Sections:**
- Section 1: DirectSound in veleron_dictation.py
- Section 2: DirectSound in veleron_dictation_v2.py
- Section 3: Unit Test Suite (22 tests)
- Section 12: Lessons Learned

---

### 6. AUDIO_API_TROUBLESHOOTING.md
**Location:** `docs/Reference_Docs/AUDIO_API_TROUBLESHOOTING.md`

**When to Read:**
- Troubleshooting audio device issues
- Understanding Windows audio API architecture
- Debugging WDM-KS errors
- Need technical deep-dive on DirectSound

**Key Sections:**
- Section 1: Windows Audio API Overview
- Section 2: DirectSound Fallback Solution
- Section 3: WDM-KS Error Explanation
- Section 5: Debugging Procedures

---

### 7. DAILY_DEV_NOTES.md
**Location:** `docs/Reference_Docs/DAILY_DEV_NOTES.md`

**When to Read:**
- Want to see development history
- Need context on technical decisions
- Want to understand project evolution
- Looking for historical reference

**Key Sections:**
- October 13, 2025: Sprint 1 (Security + WDM-KS)
- October 14, 2025: Sprint 2 (DirectSound + Testing)

---

### 8. README.md (This Folder's Index)
**Location:** `docs/Reference_Docs/README.md`

**When to Read:**
- Need to navigate the reference docs
- Want quick finding information guide
- Need to understand document relationships
- Want usage scenarios and checklists

---

## ✅ Quick Start Checklist

**Before starting Sprint 3, complete this checklist:**

- [ ] **Read CORE_DEVELOPMENT_PRINCIPLES.md completely** (10 min)
  - [ ] Understand confidence scoring (5 factors)
  - [ ] Understand two-phase workflow
  - [ ] Understand mandatory test structure
  - [ ] Review critical rules (never/always)

- [ ] **Read SPRINT_3_HANDOFF_OCT14_2025.md completely** (15 min)
  - [ ] Note Sprint 3 objectives (4 priorities)
  - [ ] Understand current state (100% MVP)
  - [ ] Review RiPIT deployment (Section 9)
  - [ ] Copy startup prompt (Section 18)

- [ ] **Skim HARDWARE_TESTING_GUIDE.md** (5 min)
  - [ ] Review testing checklist (10 tests)
  - [ ] Understand Test 1-3 procedures
  - [ ] Note success criteria

- [ ] **Verify hardware availability**
  - [ ] C922 webcam (or any USB webcam) available?
  - [ ] Bluetooth headset available?
  - [ ] Built-in microphone working?

- [ ] **Verify tools installed**
  - [ ] pytest installed: `py -m pytest --version`
  - [ ] pytest-cov installed: `py -m pytest --cov --version`
  - [ ] Python 3.13.7 working: `py --version`

- [ ] **Ready to start Sprint 3!**

---

## 🚀 Starting Sprint 3 - Use This Prompt

**Once you've completed the checklist above, start your new session with this exact prompt:**

```markdown
I'm continuing Sprint 3 of the Veleron Whisper Voice-to-Text MVP project.

**Context:**
- Sprint 2 completed successfully (100% MVP complete)
- DirectSound fallback implemented in all 3 recording apps
- 334 tests created (87% pass rate)
- Ready for hardware testing and beta deployment

**Sprint 3 Objectives (in priority order):**
1. PRIORITY 1: Hardware testing with USB devices (C922 webcam, Bluetooth/USB headsets)
2. PRIORITY 2: Fix 2 integration test errors in test_audio_device_fallback.py
3. PRIORITY 3: Create beta testing package and feedback system
4. PRIORITY 4: Update documentation (README, compatibility list, known issues)

**I have read:**
✅ docs/Reference_Docs/CORE_DEVELOPMENT_PRINCIPLES.md (confidence scoring, two-phase workflow, test structure)
✅ docs/Reference_Docs/SPRINT_3_HANDOFF_OCT14_2025.md (complete handoff, RiPIT deployment)
✅ docs/Reference_Docs/HARDWARE_TESTING_GUIDE.md (10 hardware tests documented)

**Please:**
1. Confirm you've read these reference docs
2. Begin Sprint 3 by deploying RiPIT workflow subagents per SPRINT_3_HANDOFF Section 9
3. Start with PRIORITY 1: Hardware testing following HARDWARE_TESTING_GUIDE procedures

**Critical framework to follow:**
- Use confidence scoring framework (≥95% implement, <90% ask)
- Follow two-phase workflow (analyze then implement)
- Write tests before implementing fixes
- Deploy subagents for parallel execution

**Hardware available for testing:**
[Tell the agent which hardware you have: C922 webcam? Bluetooth headset? USB headset? Built-in mic only?]

Let's start with hardware testing first per HARDWARE_TESTING_GUIDE.md Test 1-3.
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ DON'T:
1. ❌ Read files from other folders (use Reference_Docs ONLY)
2. ❌ Skip CORE_DEVELOPMENT_PRINCIPLES.md (it's MANDATORY)
3. ❌ Skip confidence scoring (required for ALL changes)
4. ❌ Start coding without reading the handoff
5. ❌ Mix files from different dates (use Oct 14 versions ONLY)

### ✅ DO:
1. ✅ Use Reference_Docs folder exclusively
2. ✅ Read the 3 critical files first (30 minutes)
3. ✅ Follow confidence scoring framework
4. ✅ Use two-phase workflow for all changes
5. ✅ Deploy RiPIT subagents as documented

---

## 📁 Folder Structure Clarification

```
c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper\
│
├── docs\
│   ├── Reference_Docs\          ← USE THESE FILES (definitive versions)
│   │   ├── CORE_DEVELOPMENT_PRINCIPLES.md ✅
│   │   ├── SPRINT_3_HANDOFF_OCT14_2025.md ✅
│   │   ├── HARDWARE_TESTING_GUIDE.md ✅
│   │   ├── PROJECT_STATUS_OCT14_2025.md ✅
│   │   ├── SPRINT_2_COMPLETION_OCT14_2025.md ✅
│   │   ├── AUDIO_API_TROUBLESHOOTING.md ✅
│   │   ├── DAILY_DEV_NOTES.md ✅
│   │   └── README.md ✅
│   │
│   ├── [other .md files]        ← May be duplicates, use Reference_Docs instead
│   └── ...
│
├── PROJECT_STATUS_OCT14_2025.md ← Duplicate (use Reference_Docs version)
└── ...
```

**Golden Rule:** If the file exists in `docs/Reference_Docs/`, use that version. It's the definitive copy.

---

## 🎯 Summary: Your 30-Minute Kickoff

**Total Time:** 30 minutes

**Minute 0-10:**
- Read: `docs/Reference_Docs/CORE_DEVELOPMENT_PRINCIPLES.md`
- Focus: Confidence scoring, two-phase workflow, test structure

**Minute 10-25:**
- Read: `docs/Reference_Docs/SPRINT_3_HANDOFF_OCT14_2025.md`
- Focus: Sections 2, 3, 4, 5, 9, 18

**Minute 25-30:**
- Skim: `docs/Reference_Docs/HARDWARE_TESTING_GUIDE.md`
- Focus: Testing checklist, Test 1-3, success criteria

**Minute 30:**
- Copy the startup prompt from this document
- Start new session with the prompt
- Begin Sprint 3!

---

## ✅ You're Ready When:

- [ ] You've read CORE_DEVELOPMENT_PRINCIPLES.md
- [ ] You've read SPRINT_3_HANDOFF_OCT14_2025.md
- [ ] You've skimmed HARDWARE_TESTING_GUIDE.md
- [ ] You understand confidence scoring (5 factors)
- [ ] You understand two-phase workflow
- [ ] You know Sprint 3 priorities (1-4)
- [ ] You have the startup prompt ready
- [ ] You know which hardware you have available

**When all checked: You're ready to start Sprint 3!** 🚀

---

**Document Version:** 1.0
**Created:** October 14, 2025
**Purpose:** Definitive kickoff guide for Sprint 3
**Status:** Current

**🎯 Start Here → Read 3 Files → Copy Prompt → Begin Sprint 3! 🎯**
