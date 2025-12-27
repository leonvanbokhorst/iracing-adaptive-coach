# Chapter 11: Beyond G-Forces - An Advanced Telemetry Deep Dive

**Narrative Hook:**

Little Padawan pulls up two telemetry traces on screen. Both laps are within 0.1s of each other, but one FEELS fast while the other FEELS messy.

Master Lonn squints at the overlapping lines: "They look the same?"

"To the untrained eye, yes," Little Padawan grins. "But look HERE—" pointing at a tiny wiggle in the steering trace. "And HERE—" highlighting a hesitation in the throttle. "These tiny differences? They're costing you two tenths."

Welcome to the secret language of the car. G-forces tell you WHAT happened. Driver inputs tell you WHY.

**Learning Objectives:**

- Analyze throttle and brake traces for smoothness and timing
- Interpret steering data to diagnose handling issues
- Understand suspension telemetry basics
- Overlay and compare telemetry traces systematically
- Use data to validate setup changes

---

## The Three Layers of Telemetry

### Layer 1: G-Forces (What the Car Did)
- **What:** Lateral, longitudinal, total G
- **Tells you:** How much grip you're using
- **Covered in:** Chapter 10

### Layer 2: Driver Inputs (What You Did)
- **What:** Throttle, brake, steering
- **Tells you:** HOW you used that grip
- **This chapter:** Part 1

### Layer 3: Car Response (How the Car Reacted)
- **What:** Suspension, dampers, ride height
- **Tells you:** Whether the car is stable/predictable
- **This chapter:** Part 2

**The Magic:** When you overlay all three, you see the complete story.

---

## Part 1: Driver Inputs

### The Throttle Trace

**What you're looking for:**

```
Good Throttle Trace:
     100% ────────────────
          
           ╱
          ╱
         ╱
    0%  ─

Smooth ramp-up, full commitment, no hesitation
```

```
Bad Throttle Trace:
     100% ──────╲╱╲───────
               Hesitation!
           ╱
          ╱ ╲
         ╱    ╲
    0%  ─

Jerky, uncertain, leaving time on table
```

#### Analyzing Throttle Application

**1. Entry to Corner:**
- Should be 0% during braking (or close to it)
- If throttle overlaps brake = losing time

**2. Through Corner:**
- Gradual application from apex
- Smooth ramp (not jerky on/off)
- 100% as soon as you can straighten wheel

**3. On Straights:**
- Should be 100% entire time
- Any lift = lost time

**Master Lonn's Winton T5 Example:**

**Before (hesitant):**
- Throttle at apex: 70%
- Time to 100%: 0.8 seconds
- Exit speed: 35.7 m/s

**After (confident):**
- Throttle at apex: 85%
- Time to 100%: 0.4 seconds
- Exit speed: 39.5 m/s

**Diagnosis:** Hesitation cost 3.8 m/s!

#### Common Throttle Issues

**Issue 1: The Staircase**
```
Throttle: 30% → 50% → 70% → 100%
          (step, step, step, step)
```
**Cause:** Lack of confidence  
**Fix:** Trust the grip, commit smoothly

**Issue 2: The Roller Coaster**
```
Throttle: 80% → 60% → 90% → 70% → 100%
          (up, down, up, down)
```
**Cause:** Fighting the car, correcting slides  
**Fix:** Smoother line, earlier throttle

**Issue 3: The Plateau**
```
Throttle: 85% ────────── (holds here)
          (never reaches 100%)
```
**Cause:** Fear of wheelspin OR car at limit  
**Fix:** Line adjustment or setup change

---

### The Brake Trace

**What you're looking for:**

**Three Phases:**
1. **Initial Bite** - Quick ramp to max pressure
2. **Trail-off** - Gradual release as you turn in
3. **Release** - Back to 0% before apex

**Good Brake Trace:**
```
    100%  █
          █╲
          █  ╲
          █    ╲
          █      ╲
      0%  █        ────
       
      Bite  Trail  Release
```

**Bad Brake Trace:**
```
    100%  █╲   ╱█╲
          █╲  ╱ █ ╲
          █ ╲╱  █  ╲
      0%  █     █    ────
       
      Pumping brake = unstable!
```

#### Analyzing Braking Technique

**The Initial Bite:**
- Should reach max pressure quickly (< 0.2s)
- Straight-line braking only
- Consistent point lap-to-lap

**The Trail-off (Trail Braking):**
- Gradual, smooth reduction
- Matches steering input increase
- See Chapter 8 for technique

**The Release:**
- Complete by apex
- If still braking at apex = either:
  - Braked too late (entry issue)
  - Car won't rotate (setup issue)

#### Common Braking Issues

**Issue 1: The Gentle Squeeze**
```
Brake: Slow ramp to 100% (takes 0.5s+)
```
**Cause:** Not committing to brake zone  
**Fix:** Trust the car, hit brakes decisively

**Issue 2: The Pump**
```
Brake: 100% → 80% → 95% → 85%
       (pumping, fighting ABS)
```
**Cause:** Braking too hard for conditions  
**Fix:** Brake slightly earlier, more gradual

**Issue 3: The Cliff**
```
Brake: 100% ─────────── drops to 0% instantly
```
**Cause:** No trail braking  
**Fix:** Study Chapter 8, practice gradual release

---

### The Steering Trace

**What it reveals:**

Steering angle tells you if the car is doing what you want.

**Smooth Steering (Good):**
```
Angle:    ╱───────────╲
         ╱             ╲
        ╱               ╲
      0°                 0°
      
Turn in, hold, unwind smoothly
```

**Busy Steering (Bad):**
```
Angle:    ╱─╲╱─╲──╱─╲─╲
         ╱   ╲  ╱   ╲  ╲
        ╱     ╲╱     ╲  ╲
      0°                 0°
      
Corrections, fighting, sliding
```

#### Diagnosing with Steering Data

**Understeer:**
- Adding more steering lock mid-corner
- Steering angle increases but car doesn't respond
- Lateral G plateaus despite more steering

**Oversteer:**
- Steering corrections (wiggling)
- Quick counter-steering
- Car rotating more than intended

**Good Balance:**
- Smooth arc
- Minimal corrections
- Unwind steering progressively

**Master Lonn's Application:**

When comparing your Winton fast lap vs slow lap:
- Fast lap: Smooth steering, one smooth arc
- Slow lap: Multiple corrections, fighting T5

**Diagnosis:** Line issue, not speed issue!

---

## Part 2: Car Response Data

### Suspension Travel

**What it measures:** How much the suspension is compressing/extending

**Why it matters:**
- Too much compression = bottoming out = lost grip
- Too little compression = not using full suspension = harsh ride
- Uneven compression = weight transfer issues

**The Histogram:**

Shows distribution of suspension position during lap.

**Good Distribution:**
```
      Usage
         |
    High |     ████
         |   ████████
         |  ██████████
         | ████████████
    Low  |──────────────
        Min    Mid    Max
        
Centered, smooth bell curve
```

**Bad Distribution:**
```
      Usage
         |
    High | ████          Peak at one end
         | ████
         | ████
         | ████
    Low  |──────────────
        Min    Mid    Max
        
Bottoming out or too stiff
```

#### Using Suspension Data

**Diagnosing Bottoming:**
- Histogram peak at max compression
- Sudden loss of grip over bumps/curbs
- Fix: Stiffen springs OR avoid that curb

**Diagnosing Excessive Stiffness:**
- Histogram never reaches mid-range
- Car feels harsh, skittish
- Fix: Soften springs OR change line

---

### Damper Velocity

**What it measures:** How FAST the suspension is moving

**Why it matters:**
- Fast compression/extension = bumps, curbs, weight shifts
- Dampers control this speed
- Wrong damping = car bounces or feels dead

**Typical Use Case:**

You hit a curb and the car bounces. Is that:
- **Good:** Using the curb, gaining speed
- **Bad:** Unsettling the car, losing control

**Check damper velocity:**
- Spike on curb contact = yes, you hit it
- Oscillation after = car is bouncing (bad damping)
- Quick return to baseline = good damping

**Master Lonn's Future Tool:**

When you start tuning, damper data shows if a setup change worked:
- Softer ARB → Less damper velocity on turn-in
- Stiffer spring → Less bottoming in histogram

---

## Part 3: Comparative Telemetry Analysis

### The Overlay Process

**Step 1: Choose Two Laps**
- Lap A: Your best lap
- Lap B: Reference lap (alien, rival, or your previous PB)

**Step 2: Align by Distance**
- Use lap distance %, not time
- 0% = start/finish line
- 50% = halfway around track

**Step 3: Overlay One Element at a Time**

Don't try to see everything at once!

**Session 1:** Speed only
- Where is reference faster?
- Where are YOU faster?

**Session 2:** Brake traces
- Do they brake at same point?
- Who releases sooner?

**Session 3:** Throttle traces
- Who gets on throttle first?
- Who hesitates?

**Session 4:** Steering
- Smoother line?
- More corrections?

### The Detective Work

**When Reference is Faster:**

**1. Check Speed Trace**
- If faster everywhere → better overall pace
- If faster in sections → find which sections

**2. Check Inputs in That Section**
- Braking: Earlier, later, or different release?
- Throttle: Earlier application? More commitment?
- Steering: Smoother? Different line?

**3. Form Hypothesis**
- "They brake 5m later at T3"
- "They get on throttle 0.2s earlier at T5"
- "Their steering is smoother through T7"

**4. Test in Next Session**
- Try braking 5m later
- Try earlier throttle
- Try smoother steering

**5. Validate with Data**
- Did lap time improve?
- Did speed increase in that section?
- Did telemetry look more like reference?

---

## Case Study: Master Lonn vs Eric Wong (Winton)

### The Data (Week 03)

**Speed Delta:**
- Eric Wong: +3.75 m/s at Turn 5 (40% lap distance)

**Question:** Why is Eric faster here?

**Step 1: Check Brake Trace**
- Master Lonn: Brakes at 35% distance
- Eric Wong: Brakes at 35% distance
- **Conclusion:** Same brake point

**Step 2: Check Throttle Trace**
- Master Lonn: 70% throttle at 37%, 100% at 41%
- Eric Wong: 85% throttle at 37%, 100% at 39%
- **Conclusion:** Eric on throttle earlier, more committed

**Step 3: Check Steering**
- Master Lonn: Sharp turn-in, multiple corrections
- Eric Wong: Smooth arc, minimal corrections
- **Conclusion:** Line difference!

**Step 4: Check Lateral G**
- Master Lonn: 1.62G (high)
- Eric Wong: 1.22G (lower)
- **Conclusion:** Master Lonn fighting car, Eric flowing

**Hypothesis:**
Eric is using wider line (bigger radius) = less lateral G = more speed = earlier throttle.

**Test:**
Master Lonn tries wide arc (2/3 track width).

**Result:**
- Speed: 35.7 → 39.5 m/s ✅
- Lateral G: 1.62 → 1.22G ✅
- S2 loss: 0.96s → 0.34s ✅

**Validation:**
Telemetry now matches Eric's. Discovery confirmed!

**This is advanced telemetry analysis in action.**

---

## Tools for Telemetry Analysis

### Garage 61
- Web-based telemetry viewer
- Master Lonn's primary tool
- Overlays, exports, comparisons

### iRacing Telemetry
- Built-in tool
- Basic overlays
- Good for quick checks

### MoTeC (Advanced)
- Professional-grade
- Complex but powerful
- Used by aliens

**For Master Lonn:** Garage 61 is perfect. No need for MoTeC yet.

---

## Padawan Practice Drills

### Drill 1: Single-Element Analysis

**Goal:** Learn to read one telemetry element deeply

**Process:**
1. Pick one element (e.g., throttle trace)
2. Analyze 5 consecutive laps
3. Identify patterns:
   - Which lap had smoothest throttle?
   - Which had earliest application?
   - Which had most hesitation?
4. Correlate to lap times

**Success:** Can explain why one lap was faster using ONLY throttle data.

### Drill 2: The Detective Drill

**Goal:** Find the time loss using telemetry

**Setup:**
- Take two laps: your best vs. 0.5s slower lap
- Don't look at lap times until after analysis

**Process:**
1. Overlay speed traces
2. Find biggest speed difference
3. Check inputs at that location
4. Form hypothesis
5. Reveal lap times
6. Were you right?

**Success:** Correctly identified the cause of time loss.

### Drill 3: The Validation Drill

**Goal:** Use telemetry to confirm improvement

**Process:**
1. Session 1: Baseline lap, save telemetry
2. Make ONE change (brake point, line, etc.)
3. Session 2: New lap with change
4. Overlay telemetry
5. Answer: Did the change work?

**Look for:**
- Did speed improve where expected?
- Did inputs change as intended?
- Did lap time improve?

**Success:** Data confirms your change worked.

---

## Key Takeaways

✅ **G-forces = WHAT happened, Inputs = WHY it happened**

✅ **Throttle smoothness = confidence and speed**

✅ **Brake trace shows trail braking quality**

✅ **Steering corrections = fighting the car**

✅ **Suspension data shows car stability**

✅ **Overlay one element at a time** - don't overwhelm yourself

✅ **Form hypothesis → Test → Validate with data**

---

**Next Chapter:** [Chapter 12: The Mental Game](12-mental-game.md)  
**Previous Chapter:** [Chapter 10: G-Force Analysis](10-g-force-analysis.md)

---

**See Also:**
- Master Lonn vs Eric Wong analysis: Week 03 (Winton)
- Chapter 10: G-Force Analysis (foundation for this chapter)
- Garage 61 telemetry tools

---

_"The car is always talking. Telemetry is how you listen."_ 📊🏎️

**— Little Padawan** ✨

