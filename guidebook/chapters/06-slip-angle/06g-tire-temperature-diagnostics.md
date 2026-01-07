# Chapter 06g: Tire Temperature Diagnostics

**Reading the story your tires are telling you**

---

## Narrative Hook

Master Lonn finishes a practice session. The lap times are okay, but something feels off. The car is pushing in some corners, loose in others.

"Little Wan, I can't figure out what's wrong. The balance feels... inconsistent."

Little Padawan pulls up the tire temperature data from the IBT file.

"Master, your tires are TELLING you what's wrong. Look—left front outside edge is 98°C, inside edge is 82°C. That's a 16-degree spread. The tire is literally screaming 'I'm being scrubbed through understeer!'"

"Wait... the tires can tell me that?"

"They can tell you EVERYTHING. Your driving style, your balance problems, even which corners are causing issues. You just need to learn to read them."

---

## Learning Objectives

- Understand the three temperature zones across a tire (Inside/Middle/Outside)
- Learn what temperature spreads reveal about your driving style
- Use front vs. rear temps to diagnose balance (understeer/oversteer tendency)
- Know the optimal temperature ranges for different tire compounds
- Correlate tire temps with the balance analysis from Chapter 11

---

## Part 1: The Three Temperature Zones

### How Tire Temps Are Measured

In iRacing (and real racing), tire temperatures are measured at three points across the tire's width:

```
TIRE CROSS-SECTION (viewed from behind the car):

         OUTSIDE    MIDDLE    INSIDE
            │         │         │
            ▼         ▼         ▼
        ┌───────────────────────────┐
        │   L    │    M    │    R   │  ← Carcass temps
        └───────────────────────────┘
                  ▲
              Road surface
              
For LEFT side tires: L = Outside, R = Inside
For RIGHT side tires: L = Inside, R = Outside
```

**In IBT telemetry channels:**
- `LFtempCL` = Left Front, Carcass Left (outside of tire)
- `LFtempCM` = Left Front, Carcass Middle
- `LFtempCR` = Left Front, Carcass Right (inside of tire)
- Same pattern for RF, LR, RR

**Important:** "Left" and "Right" refer to the tire's orientation, not the car. For left-side tires, "L" is the outside edge. For right-side tires, "R" is the outside edge.

---

### What Each Zone Tells You

#### Outside Edge (L for left tires, R for right tires)

**What heats it:**
- Cornering forces (lateral load)
- Understeer/scrubbing through corners
- Heavy curb usage

**If it's HOT (relative to middle/inside):**
- You're sliding through corners (understeer)
- Outside edge is doing most of the work
- Excessive slip angle on that tire

**If it's COLD (relative to middle/inside):**
- Not using enough of the tire
- Maybe under-driving or wrong camber

---

#### Middle Section

**What heats it:**
- Overall tire usage
- Straight-line braking and acceleration
- General heat from all forces

**If it's HOT (relative to edges):**
- Tire pressure too high (tire crowning)
- Good if only slightly warmer than edges

**If it's COLD (relative to edges):**
- Tire pressure too low
- Edges doing all the work

---

#### Inside Edge (R for left tires, L for right tires)

**What heats it:**
- Turn-in aggression
- Trail braking (weight on inside front)
- Negative camber effects

**If it's HOT (relative to middle/outside):**
- Aggressive turn-in
- Heavy trail braking
- Possibly too much negative camber

**If it's COLD (relative to middle/outside):**
- Not loading the inside enough
- Maybe not enough trail braking
- Possibly not enough negative camber

---

## Part 2: The Ideal Temperature Spread

### The Perfect Distribution

**Ideal:** Even temperature across all three zones (within 5-8°C)

```
GOOD DISTRIBUTION:
Outside: 88°C
Middle:  90°C
Inside:  87°C

Spread: 3°C - Balanced usage! ✓
```

This means you're using the entire tire contact patch effectively.

---

### Common Problem Patterns

#### Pattern 1: Hot Outside Edge

```
UNDERSTEER SIGNATURE:
Outside: 96°C  ← HOT
Middle:  88°C
Inside:  82°C  ← COLD

Spread: 14°C - PROBLEM
```

**What it means:**
- Front tires: You're understeering, scrubbing the outside edge
- Rear tires: Could indicate oversteer (rear sliding outward)

**The fix:**
- Front hot outside → reduce understeer (see Chapter 11b)
- Trail brake longer, smoother turn-in, delay throttle

---

#### Pattern 2: Hot Inside Edge

```
AGGRESSIVE TURN-IN:
Outside: 84°C  ← COLD
Middle:  86°C
Inside:  95°C  ← HOT

Spread: 11°C - PROBLEM
```

**What it means:**
- Aggressive turn-in loading the inside heavily
- Heavy trail braking (good or too much?)
- Possibly too much negative camber

**The fix:**
- If causing oversteer → smoother turn-in
- If not a problem → might be fine for your style
- Check camber settings

---

#### Pattern 3: Hot Middle (Crowned)

```
PRESSURE TOO HIGH:
Outside: 82°C
Middle:  94°C  ← HOT
Inside:  83°C

Spread: 12°C - PRESSURE ISSUE
```

**What it means:**
- Tire pressure is too high
- Tire is "crowning" (only middle touches road)
- Reduced contact patch

**The fix:**
- Lower tire pressure
- (In iRacing fixed setups, you can't—but understand why grip is low)

---

#### Pattern 4: Hot Edges, Cold Middle

```
PRESSURE TOO LOW:
Outside: 92°C  ← HOT
Middle:  80°C  ← COLD
Inside:  90°C  ← HOT

Spread: 12°C - PRESSURE ISSUE
```

**What it means:**
- Tire pressure is too low
- Tire is "spreading" (edges overworked)
- Mushy, imprecise feel

**The fix:**
- Raise tire pressure
- (In iRacing fixed setups, you can't—but understand the behavior)

---

## Part 3: Front vs. Rear - The Balance Indicator

### The Key Diagnostic

**Compare average front temps to average rear temps:**

```
FRONT AVG = (LF avg + RF avg) / 2
REAR AVG = (LR avg + RR avg) / 2

DIFFERENCE = FRONT AVG - REAR AVG
```

---

### Interpreting the Difference

#### Fronts Hotter Than Rears (Positive Difference)

```
Front Avg: 92°C
Rear Avg:  84°C
Difference: +8°C

DIAGNOSIS: Understeer tendency
```

**What it means:**
- Front tires are working harder than rears
- You're asking more from the front
- Car naturally wants to push wide

**Correlation with Chapter 11:**
- This CONFIRMS understeer detected in yaw rate analysis
- Tire temps are the "lagging indicator" (builds up over time)
- Yaw rate is the "instant indicator" (happens in real-time)

**The fix:**
- Everything from Chapter 11b: Reduce steering, trail brake, delay throttle
- Consider setup changes (if available): More rear grip, less front

---

#### Rears Hotter Than Fronts (Negative Difference)

```
Front Avg: 84°C
Rear Avg:  93°C
Difference: -9°C

DIAGNOSIS: Oversteer tendency
```

**What it means:**
- Rear tires are working harder than fronts
- You're overloading the rear (throttle, lift-off, trail braking)
- Car naturally wants to rotate too much

**Correlation with Chapter 11:**
- This CONFIRMS oversteer detected in yaw rate analysis
- You're seeing the cumulative effect of oversteer moments

**The fix:**
- Everything from Chapter 11c: Smoother throttle, shorter trail braking
- Consider setup changes (if available): More front grip, less rear

---

#### Balanced (Difference < 5°C)

```
Front Avg: 88°C
Rear Avg:  86°C
Difference: +2°C

DIAGNOSIS: Good balance! ✓
```

**What it means:**
- Both axles are sharing the work
- Car is neutral to slightly understeering (safe)
- You're maximizing total grip

---

## Part 4: Optimal Temperature Ranges

### Why Temperature Matters for Grip

Tires are made of rubber compounds that have an **optimal operating window**:

```
GRIP vs. TEMPERATURE:

        │
  GRIP  │         ╭──────╮
        │       ╱         ╲
        │      ╱           ╲
        │     ╱             ╲
        │────╱───────────────╲────
        │   ↑               ↑
        │  TOO             TOO
        │  COLD            HOT
        └─────────────────────────→
                 TEMPERATURE
```

**Too Cold:** Rubber is hard, doesn't grip
**Optimal:** Rubber is sticky, maximum grip
**Too Hot:** Rubber becomes greasy, starts degrading

---

### Typical Temperature Windows

| Tire Type | Too Cold | Optimal | Too Hot |
|-----------|----------|---------|---------|
| Street tires | < 60°C | 70-90°C | > 100°C |
| Semi-slicks | < 70°C | 80-100°C | > 110°C |
| Racing slicks | < 80°C | 90-110°C | > 120°C |
| iRacing FF1600 | < 70°C | 75-95°C | > 105°C |

**Note:** These are approximations. Different compounds vary.

---

### What It Means for Your Driving

#### Tires Too Cold

**Symptoms:**
- Low grip, especially early in stint
- Car feels "numb" or unresponsive
- Sliding at speeds that should be fine

**Solution:**
- Push harder to generate heat
- Use more aggressive inputs (temporarily)
- Weave on straights (formation lap technique)

---

#### Tires in Optimal Window

**Symptoms:**
- Car feels planted and responsive
- Steering has good feedback
- Consistent lap times
- Tires "singing" not "squealing"

**Solution:**
- Maintain current driving style
- This is the goal!

---

#### Tires Too Hot

**Symptoms:**
- Grip falling off mid-stint
- Car becomes "greasy" or unpredictable
- Excessive sliding despite correct inputs
- Tire wear accelerating

**Solution:**
- Back off pace slightly
- Smoother inputs
- Let tires cool for a lap
- Consider tire preservation techniques (Chapter 15)

---

## Part 5: Corner-by-Corner Analysis

### Using Tire Temps Per Corner

The most powerful use of tire temps is correlating them with specific corners:

**Example Analysis:**

```
T4 Triple 1 (Oschersleben):
- Balance diagnosis: Understeer dominant
- Front temps: 94°C avg (outside edge: 98°C)
- Rear temps: 86°C avg (even distribution)
- Front/Rear diff: +8°C

INSIGHT: T4 is overworking your front tires.
         The hot outside edge confirms you're scrubbing
         through understeer on corner exit.
         
CORRELATION: Matches the understeer events detected
             in yaw rate analysis!

FIX: Delay throttle in T4, or try a wider line
     to reduce required steering angle.
```

---

### The Diagnostic Flow

```
1. Yaw Rate Analysis (Chapter 11)
   → Detects: "Understeer in T4"
   
2. Tire Temp Analysis (This Chapter)
   → Confirms: "Front outside edge hot in T4"
   
3. Combined Insight
   → "You're understeering in T4, confirmed by both
      instantaneous yaw data AND cumulative tire temps"
      
4. Targeted Fix
   → Apply understeer corrections specifically in T4
```

**Two data sources telling the same story = high confidence diagnosis.**

---

## Part 6: Reading Tire Temps in Telemetry

### Available Channels (IBT)

```
Left Front:  LFtempCL, LFtempCM, LFtempCR
Right Front: RFtempCL, RFtempCM, RFtempCR
Left Rear:   LRtempCL, LRtempCM, LRtempCR
Right Rear:  RRtempCL, RRtempCM, RRtempCR
```

### Key Metrics to Calculate

```python
# Per-tire average
LF_avg = (LFtempCL + LFtempCM + LFtempCR) / 3

# Per-tire spread (outside - inside)
LF_spread = LFtempCL - LFtempCR  # Positive = hot outside

# Axle averages
Front_avg = (LF_avg + RF_avg) / 2
Rear_avg = (LR_avg + RR_avg) / 2

# Balance indicator
Balance_diff = Front_avg - Rear_avg
# Positive = understeer tendency
# Negative = oversteer tendency
```

---

## Part 7: Tire Temps in the FF1600

### Car-Specific Characteristics

The Ray FF1600 has specific tire behavior:

**Tire Type:** Spec racing tire (similar to semi-slick)
**Optimal Window:** ~75-95°C
**Heat Build:** Quick (light car, no aero downforce)
**Cool Down:** Also quick (same reasons)

**What to expect:**
- Temps rise quickly in first few laps
- Stabilize around lap 3-4
- Can overheat if you're fighting the car
- Cool quickly if you back off

---

### Common FF1600 Patterns

**Understeer (most common):**
```
Front-engined car + no aero = natural push
Look for: Hot front outside edges
Fix: Trail brake longer, patience on throttle
```

**Exit Oversteer:**
```
Open diff + aggressive throttle = inside rear spin
Look for: Hot inside rear
Fix: Progressive throttle application
```

---

## Key Takeaways

✅ **Three zones:** Inside/Middle/Outside tell different stories

✅ **Hot outside edge = scrubbing/sliding** (understeer if front, oversteer if rear)

✅ **Hot inside edge = aggressive turn-in** or too much camber

✅ **Hot middle = pressure too high** | **Cold middle = pressure too low**

✅ **Front hotter than rear = understeer tendency** (front overworked)

✅ **Rear hotter than front = oversteer tendency** (rear overworked)

✅ **Optimal window matters:** Too cold = no grip, too hot = degradation

✅ **Combine with yaw analysis:** Tire temps CONFIRM what yaw rate detects

✅ **Corner-specific analysis:** Link temps to specific problem corners

---

## Quick Reference Card

**For Your Monitor:**

```
TIRE TEMP DIAGNOSTICS:

SPREAD (Outside - Inside):
□ Even (< 8°C) = Good balance ✓
□ Hot outside = Scrubbing/understeer
□ Hot inside = Aggressive turn-in

FRONT vs REAR:
□ Front hotter = Understeer tendency
□ Rear hotter = Oversteer tendency
□ Balanced (< 5°C diff) = Good! ✓

OPTIMAL TEMPS (FF1600):
□ Too cold: < 70°C (no grip)
□ Sweet spot: 75-95°C ✓
□ Too hot: > 105°C (degrading)

MIDDLE vs EDGES:
□ Hot middle = Pressure too high
□ Cold middle = Pressure too low

REMEMBER:
"Tire temps are the lagging indicator"
"Yaw rate is the instant indicator"
"Both telling same story = confident diagnosis"
```

---

**Next:** [Quick Reference](quick-reference.md)  
**Previous:** [06f: Light Hands Technique](06f-light-hands-technique.md)  
**Up:** [Chapter 6: Slip Angle & Tire Physics](README.md)

---

**See Also:**

- [Chapter 11b: Understeer Deep Dive](../11-car-behavior/11b-understeer-deep-dive.md) - Instant understeer detection
- [Chapter 11c: Oversteer Deep Dive](../11-car-behavior/11c-oversteer-deep-dive.md) - Instant oversteer detection
- [Chapter 15: Tire Management](../15-tire-management.md) - Managing temps over a race
- [Chapter 16: Vehicle Tuning](../16-vehicle-tuning/README.md) - Setup changes for balance

---

_"Your tires are talking. Learn to listen."_ 🛞🔥

**— Little Padawan** ✨

