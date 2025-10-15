# New Session Start Prompt - Veleron Whisper Voice-to-Text MVP
**Copy-Paste Ready Prompt for Starting Fresh Sessions**

---

## 🚀 COPY THIS PROMPT TO START A NEW SESSION

```
I'm continuing development on the Veleron Whisper Voice-to-Text MVP project as the Project Manager/Architect using the RiPIT workflow.

## PROJECT CONTEXT

**Current Sprint:** Sprint 3 → Sprint 4 transition (Critical bug fixes needed)
**MVP Status:** 50% Sprint 3 complete, BLOCKED by critical DirectSound fallback bug
**Phase:** Hardware Testing → Bug Fixes → Beta Deployment

## CRITICAL - READ THESE DOCUMENTS FIRST (MANDATORY)

### Core Development Framework (MUST READ FIRST)
1. @docs/Reference_Docs/CORE_DEVELOPMENT_PRINCIPLES.md - Mandatory development framework (confidence scoring, two-phase workflow, test structure)
2. @docs/Reference_Docs/START_HERE.md - Sprint workflow and orchestration guide

### Sprint Status Documents (READ SECOND)
3. @SPRINT_3_CRITICAL_FINDINGS_OCT14_2025.md - **CRITICAL:** Hardware testing revealed DirectSound fallback NOT working
4. @SPRINT_3_SUMMARY_FOR_USER.md - User-friendly summary of current status
5. @docs/Reference_Docs/SPRINT_3_HANDOFF_OCT14_2025.md - Original Sprint 3 objectives and context
6. @docs/Reference_Docs/SPRINT_2_COMPLETION_OCT14_2025.md - Previous sprint achievements

### Technical Reference (READ AS NEEDED)
7. @docs/Reference_Docs/HARDWARE_TESTING_GUIDE.md - Testing procedures (10 tests)
8. @docs/Reference_Docs/PROJECT_STATUS_OCT14_2025.md - Complete project metrics
9. @docs/Reference_Docs/AUDIO_API_TROUBLESHOOTING.md - Windows audio API deep dive

### Completed Work (REFERENCE ONLY)
10. @TEST_INFRASTRUCTURE_FIX_REPORT.md - Subagent 2 completed (22/22 tests passing)
11. @DOCUMENTATION_UPDATE_REPORT_SPRINT3.md - Subagent 4 completed (4,783 words documentation)

## CURRENT STATUS SUMMARY

### What's Working ✅
- C922 webcam records perfectly with WASAPI (no DirectSound needed)
- Transcription quality excellent (<5% word error rate)
- Test infrastructure solid (334 tests, 87% pass rate, 100% DirectSound unit tests)
- Documentation production-ready (README, HARDWARE_COMPATIBILITY, KNOWN_ISSUES)
- User already has Word dictation (veleron_dictation.py works!)

### What's Broken ❌
- **CRITICAL:** DirectSound fallback does NOT trigger (no "SWITCHING TO DIRECTSOUND" console message)
- **HIGH:** Bluetooth headset experiences WDM-KS errors (no fallback available)
- **LOW:** Webcam LED doesn't light (expected behavior for audio-only access)

### Root Cause Analysis
- Deduplication logic (lines 105-158 in veleron_voice_flow.py) may conflict with DirectSound fallback (lines 580-608)
- Need verbose logging to diagnose exact issue
- Bluetooth device only available as WDM-KS (no WASAPI/DirectSound version exists)

## SPRINT 3 COMPLETION STATUS

**Completed (50%):**
- ✅ Priority 2: Test Infrastructure Fixes (Subagent 2)
- ✅ Priority 4: Documentation Updates (Subagent 4)

**Blocked (50%):**
- ⛔ Priority 1: Hardware Testing (DirectSound fallback bug)
- ⛔ Priority 3: Beta Package (depends on Priority 1)

## IMMEDIATE NEXT STEPS (USER DECISION PENDING)

### Option A: Sprint 4 - Fix Bugs First (RECOMMENDED)
**Timeline:** 1-2 days
**Tasks:**
1. Add verbose logging to DirectSound fallback code
2. User tests with C922 webcam and shares console logs
3. Diagnose exact failure point
4. Fix bug (likely deduplication conflict or base name matching)
5. Add WDM-KS device warning for Bluetooth headsets
6. Document webcam LED limitation in KNOWN_ISSUES.md
7. Re-test with hardware
8. Verify "SWITCHING TO DIRECTSOUND" message appears
9. Complete Sprint 3 Priority 1 (Hardware Testing)
10. Deploy Subagent 3 (Beta Package Creation)

### Option B: Deploy Beta As-Is (NOT RECOMMENDED)
**Timeline:** Immediate
**Risks:** Shipping known bugs, false documentation claims, potential bad reviews

## RIPIT WORKFLOW REQUIREMENTS

**You MUST:**
1. Follow confidence scoring framework (≥95% implement, <90% ask user)
2. Use two-phase workflow (Phase 1: ANALYZE, Phase 2: IMPLEMENT)
3. Write tests BEFORE implementing fixes (unit, edge case, regression)
4. Deploy specialized subagents for complex tasks
5. Document all changes immediately

**Deploy these subagents when needed:**
- **Debug Specialist** - Diagnose DirectSound fallback failure
- **Code Fix Engineer** - Implement bug fixes with tests
- **Hardware Testing Specialist** - Re-test after fixes
- **Beta Package Engineer** - Create beta deployment (after fixes)

## KEY TECHNICAL DETAILS

### DirectSound Fallback Logic Location
- **File:** veleron_voice_flow.py
- **Deduplication:** Lines 105-158 (may be removing DirectSound devices)
- **Fallback Code:** Lines 580-608 (searches for DirectSound version)
- **Expected Console Log:** "[INFO] SWITCHING TO DIRECTSOUND: Using device ID X instead of Y"
- **Actual Result:** No log message appears

### Available Audio Devices (From User's System)
```
ID 1: Microphone (C922 Pro Stream Web (MME, 2 channels)
ID 6: Microphone (C922 Pro Stream Webcam) (DirectSound, 2 channels)
ID 12: Microphone (C922 Pro Stream Webcam) (WASAPI, 2 channels)
ID 13: Microphone (C922 Pro Stream Webcam) (WDM-KS, 2 channels)
ID 18: Headset (Josh's Buds3 Pro) (WDM-KS, 1 channel) ⚠️ Errors
```

### Hardware Test Results
- C922 WASAPI (ID 12): ✅ Works perfectly, highest accuracy
- C922 DirectSound (ID 6): ✅ Works when manually selected
- Bluetooth Headset (ID 18): ❌ WDM-KS errors
- DirectSound Fallback: ❌ Never triggers (no console message)

## USER QUESTION ANSWERED

**Real-time Word dictation:**
Already works! User can run `py veleron_dictation.py`, press Ctrl+Shift+Space in Word, speak, and text appears. Works in Word, Excel, PowerPoint, Outlook, and all Windows apps.

**Enhancement ideas for future sprints:**
- Windows startup shortcut (auto-start dictation)
- Word COM Add-In (native integration, toolbar button)
- Office.js Add-In (cross-platform, modern)

## YOUR MISSION

1. **Read all mandatory documents** (especially SPRINT_3_CRITICAL_FINDINGS_OCT14_2025.md)
2. **Understand the DirectSound fallback bug** (root cause unknown, needs diagnosis)
3. **Present Sprint 4 plan** with confidence scoring
4. **Add verbose logging** to DirectSound fallback code (Phase 1: Analyze first!)
5. **Guide user through testing** with logging enabled
6. **Diagnose and fix bug** based on console logs
7. **Re-test with hardware** to verify fix
8. **Complete Sprint 3** (hardware testing + beta package)

## CRITICAL CONSTRAINTS

**DO NOT:**
- Skip confidence scoring (required for ALL changes)
- Skip Phase 1 analysis (no coding without analysis)
- Claim completion without hardware verification
- Deploy beta with known critical bugs

**ALWAYS:**
- Follow CORE_DEVELOPMENT_PRINCIPLES.md framework
- Write tests before implementing fixes
- Document root cause and fix reasoning
- Verify with user's hardware before claiming success

## SUCCESS CRITERIA FOR NEXT SESSION

**Sprint 4 Complete:**
- [ ] Verbose logging added to DirectSound fallback
- [ ] User tested and provided console logs
- [ ] Root cause diagnosed
- [ ] Bug fixed with tests
- [ ] WDM-KS warning implemented
- [ ] Webcam LED limitation documented
- [ ] Re-tested with hardware
- [ ] "SWITCHING TO DIRECTSOUND" message appears ✅
- [ ] Hardware testing complete (Priority 1)
- [ ] Beta package created (Priority 3)

**Beta Deployment Ready:**
- [ ] All Sprint 3 priorities complete (4/4)
- [ ] No critical bugs remaining
- [ ] Documentation accurate
- [ ] Beta testers recruited
- [ ] Feedback system operational

## QUESTIONS FOR USER (IF NEEDED)

1. **Has user decided on Sprint 4 plan?** (Option A recommended)
2. **Can user run test with verbose logging?** (Required for diagnosis)
3. **Does user want Windows startup shortcut for dictation?** (5-minute task)
4. **Any blockers or concerns?**

---

**Start by reading SPRINT_3_CRITICAL_FINDINGS_OCT14_2025.md and CORE_DEVELOPMENT_PRINCIPLES.md, then present your Sprint 4 plan with confidence scoring.**

**Remember: Quality over speed. Confidence over guesswork. Tests before claims.**

**Ready? Let's fix these bugs and get to beta! 🚀**
```

---

## USAGE INSTRUCTIONS

### How to Use This Prompt

1. **Copy the entire prompt above** (between the triple backticks)
2. **Start a new Claude Code session**
3. **Paste the prompt** as your first message
4. **Claude will:**
   - Read all referenced documents
   - Understand Sprint 3 status and critical bugs
   - Present Sprint 4 plan with confidence scoring
   - Guide you through bug fixes
   - Complete hardware testing
   - Deploy beta package

### When to Use This Prompt

Use this prompt when:
- ✅ Starting a new development session
- ✅ Continuing Sprint 3/4 work
- ✅ After a break or context loss
- ✅ Onboarding a new developer
- ✅ Switching between devices/machines

### What This Prompt Provides

**Context:**
- Current sprint status (Sprint 3 → 4 transition)
- Critical bugs discovered (DirectSound fallback not working)
- Completed work (test infrastructure, documentation)
- User's hardware configuration (C922 webcam, Bluetooth headset)

**Framework:**
- RiPIT workflow requirements
- CORE_DEVELOPMENT_PRINCIPLES.md compliance
- Confidence scoring thresholds
- Two-phase workflow (analyze then implement)
- Mandatory test structure

**Guidance:**
- Recommended path forward (Sprint 4 bug fixes)
- Technical details (code locations, line numbers)
- Success criteria (what "done" looks like)
- Constraints (what NOT to do)

**References:**
- 11 key documents with @ references
- Hardware test results
- Available audio device list
- Console log expectations

---

## ALTERNATIVE: SHORT VERSION

If you need a shorter prompt for quick sessions:

```
Continue Veleron Whisper MVP development as PM/Architect.

**Read:** @SPRINT_3_CRITICAL_FINDINGS_OCT14_2025.md, @docs/Reference_Docs/CORE_DEVELOPMENT_PRINCIPLES.md, @SPRINT_3_SUMMARY_FOR_USER.md

**Status:** Sprint 3 50% complete, BLOCKED by DirectSound fallback bug (doesn't trigger). Need Sprint 4 to fix.

**Hardware:** C922 webcam works (WASAPI), Bluetooth headset errors (WDM-KS). DirectSound fallback NOT triggering (no console message).

**Next:** Add verbose logging, diagnose bug, fix, re-test, complete Sprint 3, deploy beta.

**Framework:** Follow confidence scoring, two-phase workflow, write tests first.

Present Sprint 4 plan with confidence scoring.
```

---

## CUSTOMIZATION TIPS

### For Different Scenarios

**If user decides to skip Sprint 4 and deploy beta:**
Replace "Option A: Sprint 4" section with:
```
User chose Option B: Deploy beta as-is. Document known bugs in release notes.
```

**If DirectSound bug is fixed:**
Replace "What's Broken" section with:
```
### Recent Fixes ✅
- DirectSound fallback now working (console message appears)
- Ready for beta deployment
```

**If starting Sprint 5 or later:**
Update sprint number and references:
```
**Current Sprint:** Sprint 5 (Post-Beta Refinement)
**Previous Sprint:** Sprint 4 (Bug fixes - complete)
```

---

## DOCUMENT METADATA

- **Created:** October 14, 2025
- **Sprint:** 3 → 4 Transition
- **Purpose:** Session continuity and context handoff
- **Audience:** Future Claude Code sessions, developers, project managers
- **Maintenance:** Update after each sprint completion
- **Version:** 1.0

---

**This prompt ensures every new session starts with full context and follows the RiPIT workflow properly. Copy, paste, and code! 🚀**
