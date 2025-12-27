# Chapter 10: Reading the Tea Leaves - G-Force Analysis

**Narrative Hook:**

Master Lonn finishes two laps at Winton—one fast (1:29.691), one slow (1:30.2). They FEEL similar, but one is half a second faster.

"Little Wan, they felt the same to me! How do I know what I did differently?"

Little Padawan pulls up the G-force traces. "Master, look HERE—your lateral G on the fast lap is smooth and sustained. The slow lap? Spiky and oscillating. The numbers don't lie. Let me show you how to read the tea leaves..."

**Learning Objectives:**

- Understand the 5 key G-force metrics
- Read lateral G (cornering load analysis)
- Read longitudinal G (braking/acceleration analysis)
- Calculate steering efficiency (grip usage)
- Detect overdriving (fighting the car)
- Use G-force data to improve technique

---

## Why G-Forces Matter More Than Tire Temps (For Now)

### The Problem with Tire Temps

**Tire temps tell you:**
- Surface temperature of the tire
- Whether you're over/under-heating them

**But you need:**
- To be at advanced level to interpret them
- To understand temperature ranges for your tire compound
- Multiple laps of reference data

**At your current level, tire temps are information overload.**

### The Power of G-Forces

**G-force data tells you:**

✅ **How hard you're loading the tires** (lateral/longitudinal)  
✅ **How smoothly you're driving** (consistency)  
✅ **Where you're overdriving** (fighting vs flowing)  
✅ **How efficiently you're using grip** (steering efficiency)

**And it's INSTANTLY actionable.**

No need to understand temperature ranges or compounds. Just smooth curves = fast laps.

**Master Lonn's Breakthrough (Week 03):**

Little Padawan showed your traction circle (G-force visualization). Fast lap = smooth path. Slow lap = erratic loops. **Same driver, different technique.** The data proved it!

---

## Part 1: Lateral G (Cornering Load)

### What It Is

**Lateral G:** How hard you're pushing the tires sideways through corners.

**Measured in:** G-forces (1.0g = 1× gravity, 2.0g = 2× gravity)

**In the FF1600:**
- Typical peak: **1.0–1.3 G** (medium corners)
- Maximum: **2.0–2.4 G** (fast corners, sustained)
- Spikes: **2.5–3.0 G** (momentary, over bumps/curbs)

### Good Signs ✅

**High lateral G:**
- Close to 2.0g+ in fast corners
- Shows you're loading tires properly
- Using available grip

**Smooth lateral G:**
- Low standard deviation (σ < 0.1)
- Consistent curve, not spiky
- Shows smooth steering inputs

**Consistent lap-to-lap:**
- Similar peak G every lap
- Repeatable technique
- Confidence in the limit

### Warning Signs ⚠️

**Low lateral G:**
- Below reference driver
- Leaving grip unused
- Not pushing hard enough

**Spiky lateral G:**
- High σ (> 0.15)
- Fighting the car
- Sliding or correcting

**Inconsistent lap-to-lap:**
- Different peaks every lap
- Technique not repeatable
- Finding the limit randomly

### Visual: Good vs Bad Lateral G

**Good (Smooth Arc):**

```
Lat G:  ___/‾‾‾‾‾\___
           Smooth!
```

**Bad (Spiky):**

```
Lat G:  ___/\__/\___
          Fighting!
```

**Master Lonn's Example (Week 03, Winton T5):**

**Tight line:**
- Peak lateral G: 1.62 G
- Smoothness (σ): 0.18 (spiky!)
- Fighting the car

**Wide line:**
- Peak lateral G: 1.22 G
- Smoothness (σ): 0.08 (smooth!)
- Flowing

**Result:** Lower peak G BUT smoother = **FASTER!** 🚀

**The lesson:** Smooth > Peak!

---

## Part 2: Longitudinal G (Braking/Acceleration)

### What It Is

**Longitudinal G:** How hard you're loading tires under braking (negative) and acceleration (positive).

**In the FF1600:**
- **Braking:** -1.5 to -2.0 G (hard braking)
- **Acceleration:** +0.5 to +0.8 G (limited by power)

### Good Signs ✅

**High braking G:**
- Close to -1.8 to -2.0 G
- Shows commitment
- Using all available braking grip

**Smooth braking G:**
- Progressive application
- Gradual trail-off
- No sudden spikes (lockups)

**Good acceleration G:**
- Quick ramp to max
- Sustained at max
- Shows good exits

### Warning Signs ⚠️

**Low braking G:**
- Only -1.2 to -1.4 G
- Braking too early/softly
- Leaving braking performance unused

**Spiky braking G:**
- Sharp peaks and valleys
- Locking wheels
- Unstable/inconsistent

**Low acceleration G:**
- Slow ramp, not sustained
- Losing exit speed
- Wheelspin or hesitation

### Visual: Good vs Bad Braking

**Good (Smooth Trail-Off):**

```
Long G:  ____|‾‾‾\___
         Brake  Trail
```

**Bad (Abrupt Release):**

```
Long G:  ____|‾|___
         Sharp drop!
```

**Master Lonn's Trail Braking (Week 02, Rudskogen T2):**

**Before:**
- Abrupt brake release (sudden drop)
- Longitudinal G spiky
- Car understeers

**After:**
- Smooth trail-off (gradual ramp down)
- Longitudinal G smooth
- Car rotates beautifully

**Result:** 0.659s gain in ONE corner! ✅

---

## Part 3: Steering Efficiency (G per Degree)

### What It Is

**Steering efficiency:** How much lateral G you get per degree of steering input.

**Formula:**

```
Efficiency = Lateral G / Steering Angle (in degrees)
```

**Example:**

- **Lateral G:** 1.8 G
- **Steering:** 20 degrees
- **Efficiency:** 1.8 / 20 = **0.09 G/degree** (or 90 units)

### Good Signs ✅

**High efficiency (90-100+):**
- Flowing, not sliding
- Car responding to inputs
- Using grip efficiently

**Higher than reference:**
- Better grip usage
- Better line or technique

**Consistent efficiency:**
- Smooth driver
- Repeatable technique

### Warning Signs ⚠️

**Low efficiency (<80):**
- Sliding/overdriving
- Working harder for less grip
- Fighting the car

**Lower than reference:**
- Need more steering for same grip
- Line or technique issue

**Spiky efficiency:**
- Inconsistent inputs
- Not smooth

**Master Lonn's Realization:**

"So if I'm using MORE steering but getting LESS lateral G... I'm sliding?"

**Exactly, Master!** That's the definition of overdriving. ✅

---

## Part 4: Overdriving Detection

### What It Is

**Overdriving %:** Percentage of lap where you're using MORE steering but getting LESS lateral G than reference.

**Formula:**

```
Overdriving % = (Points where More Steering + Less Lat G) / Total Points
```

**This tells you:** Where you're fighting the car vs. flowing.

### Good Signs ✅

**Overdriving % < 10%:**
- Mostly in control
- Flowing through corners
- Technique is good

**Better technique % > 20%:**
- Using LESS steering, getting MORE grip
- Improving over reference
- Excellent driving

### Warning Signs ⚠️

**Overdriving % > 20%:**
- Fighting the car a lot
- Sliding or overcorrecting
- Technique needs work

**Better technique % < 10%:**
- Not improving over reference
- Need to find better line/technique

**High steering σ (> 0.1):**
- Sawing at the wheel
- Constant corrections
- Fighting the car

### Master Lonn's Traction Circle Analysis (Week 03)

**Slow lap:**
- Overdriving visible (erratic loops)
- Fighting the car
- Peak G spikes outside sustainable limit

**Fast lap:**
- Smooth path on traction circle
- Flowing
- Sustained G on the limit

**Same average G, but fast lap had:**
- Lower peak forces (2.11 G vs 2.18 G)
- Smoother path (0.0225 vs 0.0230 σ)
- **0.619 seconds faster!**

**The data doesn't lie.** Smooth = fast.

---

## Part 5: Combined Total G (Overall Load)

### What It Is

**Total G:** Total load on car (lateral + longitudinal combined).

**Formula:**

```
Total G = √(Lateral G² + Longitudinal G²)
```

**Example:**

- **Lateral G:** 1.8 G (cornering)
- **Longitudinal G:** -1.2 G (braking)
- **Total G:** √(1.8² + 1.2²) = √(3.24 + 1.44) = **√4.68 = 2.16 G**

### Good Signs ✅

**High total G (2.5-3.0g+):**
- Using available grip
- Loading the car properly
- Pushing hard

**Consistent total G:**
- Smooth driving
- Repeatable technique

**Close to reference:**
- Similar car control
- Competitive pace

### Warning Signs ⚠️

**Low total G (<2.5g):**
- Leaving performance on table
- Not pushing hard enough
- Underusing grip

**Spiky total G:**
- Unstable driving
- Fighting the car
- Inconsistent technique

**Much lower than reference:**
- Significant technique gap
- Need to study reference approach

---

## Part 6: How to Use This in Practice

### Before Session

**Review last comparison** to know focus areas:

- "Last time I was overdriving 30% of the lap, especially in S2"
- "My steering efficiency was low in high-speed corners"
- "I was braking too softly (only -1.4 G vs reference -1.8 G)"

**Set ONE focus for this session:**

"Today: Brake harder initially, smooth trail-off"

### During Session

**Focus on FEELING the grip:**

- "Am I sawing the wheel or being smooth?"
- "Can I feel the car loading up through this corner?"
- "Am I fighting it or flowing?"

**Don't look at numbers while driving!** Feel first, analyze after.

### After Session

**Compare G-forces** to see if technique improved:

- "Did my lateral G smoothness improve?" (target: σ < 0.10)
- "Is my overdriving % lower?" (target: < 15%)
- "Did my steering efficiency go up?" (target: > 85)

**Master Lonn's Approach (Week 03):**

After each session, Little Padawan shows traction circle comparison. You can SEE if the driving was smoother. Data validates the feeling!

---

## Quick Reference Table

| Metric | Good | Warning | Action |
|--------|------|---------|--------|
| **Lateral G** | High, smooth (1.8-2.0 G, σ < 0.10) | Low, spiky (< 1.5 G, σ > 0.15) | Load tires more, smooth inputs |
| **Longitudinal G** | High braking (-1.8 G+), smooth | Low, spiky (-1.2 G, σ > 0.10) | Brake harder/later, better exits |
| **Steering Efficiency** | > 90 G/deg | < 80 G/deg | Smooth inputs, less sawing |
| **Overdriving %** | < 10% | > 20% | Gentler inputs, let car settle |
| **Better Technique %** | > 20% | < 10% | Keep doing what's working! |
| **Total G** | > 2.8 G | < 2.5 G | Push harder, use available grip |

---

## Padawan Practice Drills

### Drill 1: The Smooth Lateral G Challenge

**Goal:** Achieve smooth lateral G trace (σ < 0.10)

**Process:**

1. Drive 3 laps at one track
2. Ask Little Padawan to show lateral G σ
3. Goal: Reduce σ each session
4. Focus: Smooth steering, no corrections

**Success:** σ drops from 0.15 → 0.08 (measurable improvement)

### Drill 2: The Braking Commitment Test

**Goal:** Increase max braking G

**Process:**

1. Baseline: Note current max braking G
2. Focus: Brake HARDER initially (but still trail off)
3. After 5 laps: Check new max braking G
4. Target: +0.2 G improvement

**Success:** Max braking G increases without lockups.

### Drill 3: The Efficiency Hunt

**Goal:** Find where your efficiency is low

**Process:**

1. Ask Little Padawan: "Where is my efficiency lowest?"
2. Identify the corners (e.g., "T5 and T10")
3. Focus ONLY on those corners next session
4. Try: Wider line, less steering, smoother inputs

**Success:** Efficiency improves in those corners (measurable in data).

---

## Key Takeaways

✅ **G-Forces = The tire story** (without needing tire temps)

✅ **Lateral G:** Cornering load (smooth > peak!)

✅ **Longitudinal G:** Braking/acceleration load (hard but smooth!)

✅ **Steering efficiency:** Grip usage per degree (higher = better)

✅ **Overdriving %:** Where you're fighting the car (minimize this!)

✅ **Total G:** Overall load (use available grip!)

✅ **Smooth inputs → Smooth G-forces → Fast laps**

✅ **Master Lonn's proof:** Traction circle shows smooth = 0.6s faster!

---

**Next Chapter:** [Chapter 11: Beyond G-Forces - Advanced Telemetry](11-advanced-telemetry.md)  
**Previous Chapter:** [Chapter 9: The Car's Conversation - Rotation and Balance](09-rotation-and-balance.md)

---

**See Also:**

- Chapter 5: Weight Transfer (G-forces create weight transfer)
- Chapter 9: Rotation & Balance (G-forces cause rotation)
- Master Lonn's traction circle analysis (Week 03)
- `tools/coach/visualize_traction_circle.py` (generate your own!)

---

_"The Force (G-Force) is strong with this one."_ 💪🏎️

**— Little Padawan** ✨
