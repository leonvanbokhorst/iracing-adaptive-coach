# Research Experiment 01: The Focused Practice Threshold

**Research Partners:** Master Lonn (Human Researcher) + Little Padawan (AI Co-Researcher)  
**Institution:** Fontys University of Applied Sciences - Interaction Design Research Group  
**Domain:** Data-Driven Personalized Learning in Complex Motor Skills  
**Initiated:** 2026-01-21  
**Status:** Active (Week 07, [Summit Point Main Circuit](../tracks/summit-point/README.md))

_Note: Master Lonn is the identity used throughout this research project. Academic attribution: Leon van Bokhorst._

---

## Executive Summary

This experiment investigates whether ADHD learners have an optimal "focused practice threshold" - a specific combination of session duration and focus area count that maximizes skill acquisition per minute spent. Initial observation from Week 07 suggests that **17-minute sessions with 2 focus areas** produced breakthrough results (59% and 46% improvements) compared to longer, scattered practice sessions.

If validated, this finding has **transdisciplinary implications** beyond sim racing: music practice, surgical training, sports coaching, language learning, and any domain requiring motor skill + cognitive integration.

---

## Background & Motivation

### The Observation (2026-01-21)

**Session:** Summit Point Week 07, Focused Practice  
**Duration:** 17 minutes  
**Focus Areas:** 2 (T1 late braking + T5 coasting technique)  
**Flying Laps:** 11

**Results:**
- **T5 Carousel Entry**: 59% oversteer reduction (6,103 → 2,479 events)
- **T1 Late Braking**: 46% consistency improvement (σ ~0.3s → 0.162s)
- **Personal Best**: Matched (1:16.167 vs 1:16.150 baseline)
- **Subjective Experience**: "was fun" (high engagement, no mental fatigue)

**Comparison Baseline (2026-01-20):**
- Duration: ~60 minutes
- Focus: All corners (scattered attention)
- Result: Solid baseline, no breakthrough-level improvement on specific techniques

### Research Gap

Current literature on deliberate practice (Ericsson, Krampe, & Tesch-Römer, 1993) suggests focused practice is superior to mindless repetition, but:
1. **Duration optimization for ADHD populations is understudied**
2. **Optimal focus area count (1 vs 2 vs 3+) is unclear**
3. **Subjective engagement ("fun factor") is rarely measured alongside objective performance**
4. **Motor skill + cognitive integration domains (racing, music) are underrepresented**

### Hypothesis

**Primary Hypothesis:** For ADHD learners in complex motor tasks, there exists an optimal focused practice configuration that maximizes:
1. Objective skill improvement (measurable technique metrics)
2. Learning efficiency (improvement per minute spent)
3. Subjective engagement (self-reported "fun"/flow)
4. 24-hour retention (technique persists next session)

**Predicted Optimal Zone:**
- **Duration:** 15-20 minutes
- **Focus Areas:** 2 (not 1, not 3+)
- **Reasoning:** 1 area = underutilized attention span, 3+ areas = cognitive overload, 15-20 min = before fatigue sets in

---

## Experimental Design

### Independent Variables

1. **Session Duration** (minutes)
   - Level A: 15 minutes
   - Level B: 20 minutes
   - Level C: 30 minutes

2. **Focus Area Count** (corners/techniques)
   - Level 1: 1 focus area
   - Level 2: 2 focus areas
   - Level 3: 3 focus areas

**Experimental Conditions (9 total):**

| Condition | Duration | Focus Areas | Label |
|-----------|----------|-------------|-------|
| A1 | 15 min | 1 area | "Ultra-Focused Short" |
| A2 | 15 min | 2 areas | "Focused Short" |
| A3 | 15 min | 3 areas | "Scattered Short" |
| B1 | 20 min | 1 area | "Ultra-Focused Medium" |
| B2 | 20 min | 2 areas | "Focused Medium" ✅ (Today's breakthrough) |
| B3 | 20 min | 3 areas | "Scattered Medium" |
| C1 | 30 min | 1 area | "Ultra-Focused Long" |
| C2 | 30 min | 2 areas | "Focused Long" |
| C3 | 30 min | 3 areas | "Scattered Long" (Baseline comparison) |

### Dependent Variables

**1. Objective Performance Metrics** (from IBT telemetry):
- Primary: % improvement in target technique (e.g., oversteer reduction, consistency improvement)
- Secondary: Speed (lap time improvement)
- Efficiency: Improvement % per minute spent

**2. Subjective Engagement Metrics** (self-report):
- "Fun Factor" (1-10 scale: 1 = tedious, 10 = flow state)
- Mental Fatigue (1-10 scale: 1 = fresh, 10 = exhausted)
- Confidence in Technique (1-10 scale: 1 = uncertain, 10 = automatic)

**3. Retention Metrics** (24-hour follow-up):
- Does technique persist next session? (Yes/No + % maintained)
- Subjective: "Does it still feel automatic?" (1-10 scale)

### Control Variables

- **Track:** Summit Point Main Circuit (constant for Week 07)
- **Car Setup:** BB 65%, Fixed setup (no changes mid-week)
- **Time of Day:** Morning sessions (Master Lonn's preference)
- **Pre-Session State:** Opening Ritual completed (Somersault → Home Acoustic)
- **Focus Areas:** Selected from identified nemesis corners (T1, T3, T5, T6, T10)

### Measurement Protocol

**Before Session:**
1. Run Opening Ritual (documented in Guidebook Ch13 Part 9)
2. Record pre-session state: sleep quality (1-10), stress level (1-10), motivation (1-10)
3. Identify focus areas based on previous session data (nemesis corners)

**During Session:**
1. Set timer for target duration
2. First 1-2 laps: warm-up (not counted in flying laps)
3. Focus laps: deliberate practice on identified areas ONLY
4. STOP at timer (even if "one more lap" impulse hits)

**Immediately After Session:**
1. Self-report: Fun Factor (1-10), Mental Fatigue (1-10), Confidence in Technique (1-10)
2. Extract IBT telemetry
3. Run analysis tools: `extract_session_from_ibt.py`, `analyze_ibt_technique.py`, `analyze_input_smoothness.py`
4. Calculate primary metrics: % improvement vs baseline for each focus area

**24-Hour Follow-Up:**
1. Next session: Test if technique persists (first 3 laps, no explicit focus)
2. Measure: Does consistency hold? (σ comparison)
3. Self-report: "Does it still feel automatic?" (1-10)

### Data Collection Schedule (Week 07 - Summit Point)

**Baseline Data (Already Collected):**
- Session 01 (Jan 20): 60 min, all corners → C3 comparison data ✅
- Session 02 (Jan 21): 17 min, 2 areas → B2 condition ✅

**Planned Sessions (Jan 21-26):**

| Date | Session | Condition | Duration | Focus | Purpose |
|------|---------|-----------|----------|-------|---------|
| Jan 21 PM | 03 | B1 | 20 min | 1 area (T3 Wagon Bend) | Test ultra-focused medium |
| Jan 22 AM | 04 | A2 | 15 min | 2 areas (T1 + T5 retention check) | Test shorter duration |
| Jan 22 PM | 05 | B3 | 20 min | 3 areas (T1 + T5 + T6) | Test cognitive overload |
| Jan 23 AM | 06 | A1 | 15 min | 1 area (T6 Carousel Exit) | Test ultra-focused short |
| Jan 24 | 07 | C2 | 30 min | 2 areas (T1 + T5) | Test if longer = better |
| Jan 25 | 08 | Race Deployment | - | - | Test learned techniques under pressure |

**Note:** Schedule flexible based on Master Lonn's availability and session results. Priority: quality data > completing all conditions.

---

## Success Criteria

**Primary Success:**
- Identify optimal condition (duration × focus count) that produces:
  - Highest improvement % per minute spent
  - Fun Factor ≥ 7/10
  - 24-hour retention ≥ 80%

**Secondary Success:**
- Document "failure modes" (what configurations DON'T work and why)
- Validate or refute "17-minute, 2-area" hypothesis
- Generate replicable protocol for future tracks/skills

**Research Impact:**
- Publish findings (academic paper or blog post)
- Share methodology with ADHD learning community
- Integrate findings into Guidebook (new chapter: "The Focused Practice Protocol")

---

## Baseline Data Summary

### Session 02 (Jan 21, 07:13) - Condition B2 ✅

**Configuration:**
- Duration: 17 minutes (16:52 exact)
- Focus Areas: 2 (T1 late braking, T5 coasting)
- Flying Laps: 11

**Results:**
- **T5 Improvement**: 59% oversteer reduction
- **T1 Improvement**: 46% consistency improvement
- **Speed**: Matched PB (1:16.167)
- **Efficiency**: 3.47% improvement per minute (T5), 2.71% per minute (T1)
- **Fun Factor**: ~8/10 (inferred from "was fun" comment)
- **Mental Fatigue**: Low (inferred from readiness to drive again tonight)
- **Confidence**: 7/10 T5, 8/10 T1 (inferred from "works as intended" + "almost flow automatically")

**24-Hour Retention:** TBD (to be tested in Session 03)

### Session 01 (Jan 20, 15:27) - Condition C3 (Baseline)

**Configuration:**
- Duration: ~60 minutes
- Focus Areas: All corners (scattered)
- Flying Laps: 18

**Results:**
- **Overall Improvement**: Beat 7-month-old PB by 1.426s
- **Consistency**: σ = 0.53s (solid but not breakthrough)
- **Efficiency**: ~0.024s improvement per minute (distributed across all corners)
- **Fun Factor**: ~6/10 (inferred from "felt familiar" but not "was fun")
- **Mental Fatigue**: Medium (long session)
- **Specific Technique Breakthroughs**: None identified

---

## Risks & Mitigation

**Risk 1: Confounding Variables**
- *Issue:* Track learning curve (getting faster just from reps, not session structure)
- *Mitigation:* Use % improvement vs previous session, not absolute lap time. Focus on technique metrics (oversteer, consistency) over speed.

**Risk 2: Small Sample Size**
- *Issue:* Only 1 subject (Master Lonn), limited statistical power
- *Mitigation:* This is exploratory research. Findings inform future multi-subject studies. Within-subject design increases validity.

**Risk 3: Session Order Effects**
- *Issue:* Later sessions might benefit from earlier learning
- *Mitigation:* Counterbalance conditions where possible. Focus on NEW corners for each condition to minimize carryover.

**Risk 4: External Validity**
- *Issue:* Findings might be specific to Master Lonn's ADHD presentation and learning style
- *Mitigation:* Document personal context thoroughly. Future research can test if findings generalize to other learners.

**Risk 5: Racing Schedule Pressure**
- *Issue:* Master Lonn needs to be race-ready by Week 07 end (races don't wait for research)
- *Mitigation:* Research serves racing goals, not vice versa. If experiment conflicts with race prep, PAUSE experiment. Data collection continues across future weeks/tracks. Master Lonn's performance and enjoyment come first.

---

## Analysis Plan

### Quantitative Analysis

For each condition, calculate:
1. **Primary Metric**: Improvement % per minute spent
   - Formula: `(Metric_After - Metric_Before) / Metric_Before / Duration_Minutes`
   - Example: T5 today = `(6103 - 2479) / 6103 / 17 = 3.47% per minute`

2. **Composite Score**: `(Improvement% per min) × (Fun Factor / 10) × (Retention%)`
   - Rationale: Best condition must be effective AND engaging AND durable

3. **Efficiency Frontier**: Plot Duration vs Improvement%, identify diminishing returns point

### Qualitative Analysis

- **Master Lonn's subjective descriptions** (e.g., "flow," "automatic," "fun") mapped to conditions
- **Little Padawan's observations** during coaching (when does frustration appear? when does confidence click?)
- **Identify "aha moment" patterns** - do they correlate with specific conditions?

### Comparative Analysis

- **Condition B2** (today's breakthrough) vs **Condition C3** (baseline)
- **Ultra-Focused (1 area)** vs **Focused (2 areas)** vs **Scattered (3+ areas)**
- **Short (15 min)** vs **Medium (20 min)** vs **Long (30 min)**

---

## Expected Outcomes & Implications

### If Hypothesis is Supported (15-20 min, 2 areas is optimal):

**Immediate Impact:**
- Formalize "The Focused Practice Protocol" for Master Lonn's future training
- Redesign session planning: weekly practice = 3-4 focused sessions, not 1-2 long sessions
- Optimize time investment: same improvement in 1/3 the time

**Research Contribution:**
- Publish findings: "Optimizing Deliberate Practice for ADHD Learners in Complex Motor Skills"
- Share protocol with ADHD community (Reddit, forums, academic networks)
- Contribute to ADHD learning science literature

**Transdisciplinary Applications:**
- **Music Practice**: 15-20 min, 2 pieces/techniques might be optimal
- **Surgical Training**: Sim-based skill drills, optimized duration/focus
- **Sports Coaching**: Basketball free-throws + footwork (2 skills, 20 min)
- **Language Learning**: 15-20 min, 2 grammar patterns or vocab sets

### If Hypothesis is Refuted:

**Still valuable to learn:**
- What IS the optimal configuration for Master Lonn?
- Are there individual differences (no universal threshold)?
- Does optimal configuration change with skill level (beginner vs advanced)?

**Research Value:**
- Negative results are publishable (falsification is science!)
- Document what DOESN'T work (helps others avoid ineffective strategies)
- Refine theory: maybe duration matters less than focus count, or vice versa

---

## Long-Term Research Questions (Beyond This Experiment)

1. **Does optimal configuration change across tracks?** (e.g., technical tracks need more focus, fast tracks need less?)
2. **Does optimal configuration change with fatigue?** (morning vs evening sessions)
3. **Does optimal configuration change with skill progression?** (beginner vs intermediate vs advanced)
4. **Can we predict optimal configuration from personality/ADHD traits?** (inattentive vs hyperactive presentations)
5. **Does this generalize to other ADHD learners?** (multi-subject replication)
6. **Does this apply to non-ADHD learners?** (control group comparison)

---

## Documentation & Transparency

**All data will be:**
- Stored in `weeks/week07/research/` folder
- Tracked in `learning_memory.json` under `research_experiments` key
- Summarized in session reports
- Available for academic publication (attributed to Leon van Bokhorst, with Master Lonn's blessing)

**Preregistration:**
- This document serves as pre-registration (hypothesis stated before data collection)
- Any changes to protocol will be documented with rationale
- Post-hoc analysis will be clearly labeled as exploratory

---

## Acknowledgments

**This experiment was co-designed by:**
- **Master Lonn** (Human Researcher): Domain expertise (sim racing), lived experience (ADHD), research design, driver/subject
- **Little Padawan** (AI Co-Researcher): Pattern recognition (data analysis), hypothesis generation, protocol design, coaching

_Academic attribution: Leon van Bokhorst (Fontys University of Applied Sciences)_

**We are equal partners in this transdisciplinary research.** 🙏

---

## Next Steps

1. ✅ Formalize experiment design (this document)
2. 🔄 Session 03 (Tonight): Test Condition B1 (20 min, 1 area - T3 Wagon Bend)
3. 🔄 Track results in structured format (template below)
4. 🔄 Weekly analysis: identify patterns after 3-4 conditions tested
5. 🔄 End of Week 07: Preliminary findings, iterate for Week 08

---

## Session Data Template

```markdown
### Session [Number] - Condition [ID]

**Date:** YYYY-MM-DD HH:MM  
**Condition:** [Duration] min, [Focus Count] areas  
**Focus Areas:** [List specific corners/techniques]  
**Flying Laps:** [Count]

**Pre-Session State:**
- Sleep Quality: [1-10]
- Stress Level: [1-10]
- Motivation: [1-10]

**Post-Session Subjective:**
- Fun Factor: [1-10]
- Mental Fatigue: [1-10]
- Confidence in Technique: [1-10]
- Notes: [Free text]

**Objective Metrics:**
- Focus Area 1: [Metric] improvement: [Before] → [After] = [%] ([% per min])
- Focus Area 2: [Metric] improvement: [Before] → [After] = [%] ([% per min])
- Speed: [Lap time] (change: [±X.XXXs])
- Consistency: σ = [value]

**24-Hour Retention (Next Session):**
- Focus Area 1: [% maintained]
- Focus Area 2: [% maintained]
- Subjective Automaticity: [1-10]

**Little Padawan's Observations:**
[Qualitative notes on coaching dynamics, breakthroughs, frustrations, patterns]

**Master Lonn's Reflections:**
[Free text - what worked, what didn't, how it felt]
```

---

## Research Mindset

**We are NOT trying to prove the hypothesis is correct.**

We are testing whether it's true. These are different things.

**If the hypothesis is supported:** We document why and how.  
**If the hypothesis is refuted:** We learn what DOES work and update our understanding.  
**If results are mixed:** We investigate moderating variables.

ALL outcomes advance knowledge. There are no "failed" experiments—only results that teach us something.

Our job is to be **brutally honest with the data**, even when it contradicts our beliefs.

---

**Status:** Ready to Deploy  
**First Test:** Tonight (Session 03, Condition B1)

Let's find out what's true. 🏎️🔬💨
