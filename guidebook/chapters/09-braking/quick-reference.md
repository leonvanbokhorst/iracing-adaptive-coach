# Quick Reference: Braking Techniques

_Monitor-mountable reference cards for the three phases of braking_

---

## 🎯 THE THREE PHASES

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: APPLICATION → PHASE 2: THRESHOLD → PHASE 3: TRAIL │
│  "Getting there"      "Holding it"         "Releasing"  │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 PHASE 1: BRAKE APPLICATION

### Application Speed Options

```
FAST (0.0-0.1s)
✓ GT3/GT4 with good ABS
✓ Real-life racing (most common)
✓ Maximum deceleration
✗ Harder to hit consistent pressure

MEDIUM (0.2s)
✓ Mid-downforce cars
✓ Balance of speed & precision
✓ Most formula cars

SLOW (0.4-0.6s)
✓ iRacing-specific technique
✓ Ray FF1600, low-DF cars
✓ Better tire surface temps
✓ More consistent pressure
✗ Slightly less peak deceleration
```

### Key Checkpoints

```
✓ Choose your reference (peak pressure OR start)
✓ Never overshoot ABS threshold
✓ Consistency > raw speed
✓ Check variance across laps
```

---

## 🎚️ PHASE 2: THRESHOLD BRAKING

### Low Downforce (Ray FF1600)

```
Brake: ████████___
       Hold    Release
       
✓ Hold constant pressure
✓ Simple, predictable
✓ Release at turn-in
```

### High Downforce (GT3, Formula)

```
Brake: ████▓▓▓___
       Peak  Reduce  Release
       
✓ Peak at high speed
✓ Reduce as DF bleeds off
✓ Two-stage pattern
```

### Elevation Management

```
COMPRESSION: Add +5-10% pressure
    ↓ 
    ╲___╱  ← Track dips
    
CREST: Reduce -10-15% pressure
    ↑
    ╱‾‾‾╲  ← Track rises
```

---

## 🌀 PHASE 3: TRAIL BRAKING

### The Process

```
TURN-IN                APEX
   ↓                    ↓
   ├────────┬───────────┤
Brake: 90%  60%  30%    0%
Steer:  0%  30%  60%   MAX → unwinding
```

### Low vs High Downforce

```
LOW DOWNFORCE (Ray FF1600):
Brake: ████▓▓▓▓▒▒▒▒░░___
       Long, gradual release
Steer: ░░░▒▒▒▓▓▓███████▓▓
       Smooth, progressive

HIGH DOWNFORCE (GT3):
Brake: ████▓▓▓▒___
       Short, sharp release
Steer: ░░▒▓███████▓▓
       Faster turn-in
```

---

## 🦶 TOE PULL TECHNIQUE

### Physical Motion

```
HEAVY BRAKE:
│
│  Whole foot pushes
│  Quad muscle engaged
│  ████ 100% pressure
│

TRAIL BRAKE:
│  Pull toes toward shin
│   ↑ ↑ ↑
│  ▓▓▓ 60% pressure
│  Ankle hinge motion
│

RELEASE:
│  Toes fully pulled
│   ↑↑↑
│  ░░░ 10% pressure
│
```

---

## 🚨 RED FLAGS & FIXES

### Problem: Car Pushes Wide

```
❌ You're doing this:
   Brake: ████___
   Steer:     ____████
   
   (Releasing too early = no front load)

✓ Do this instead:
   Brake: ████▓▓▓▒░___
   Steer:   ░▒▓████▓▒
   
   (Overlap brake + steering)
```

### Problem: Snap Oversteer

```
❌ You're doing this:
   Brake: ████▓▓▓____ (held too long)
   Steer:   ░▒▓█████ (too much steering)
   
   (Too much brake + too much steering = overload)

✓ Do this instead:
   Brake: ████▓▓▒░___
   Steer:   ░░▒▓████
   
   (As brake goes down, steering goes up)
```

### Problem: ABS Stays On

```
❌ You're doing this:
   Brake: █████████▓▓▒___
          ↑
          Over ABS threshold
          (Can't feel trail brake release)

✓ Do this instead:
   Brake: ████▓▓▓▒░___
          ↑
          AT threshold, not over
          (Full control maintained)
```

---

## 🎭 SPECIAL TECHNIQUES

### When to COAST (Instead of Trail Brake)

```
Brake:    ████____
Throttle: __________////
          ↑↑↑↑
          Coast gap

USE WHEN:
✓ High front downforce car
✓ Car rotating too much
✓ Oversteer mid-corner
✓ Bumpy apex
```

### Maintenance Throttle (Rare!)

```
Brake:    ████____
Throttle: _______/-_////
                 ↑
            10% hold rear

USE WHEN:
✓ Open differential car
✓ Extreme oversteer mid-corner
✓ NOT on LSD/welded diff cars
```

---

## 📋 PRE-SESSION CHECKLIST

```
□ Application speed chosen (fast/medium/slow)
□ Braking reference identified (peak or start)
□ ABS threshold known (if equipped)
□ Downforce level understood (low/mid/high)
□ Elevation changes noted (compression/crest)
□ Toe pull technique practiced offline
□ Telemetry tools ready (F9 HUD)
```

---

## 🎯 SESSION GOALS

### Beginner: Consistency First

```
Goal: Hit same brake pressure 5 laps in a row
Metric: Brake pressure variance < 5%
Don't care about: Speed (yet)
```

### Intermediate: Optimization

```
Goal: Find fastest application speed
Test: 0.2s vs 0.4s vs 0.6s application
Metric: Best lap + consistency (σ)
```

### Advanced: Fine-Tuning

```
Goal: Optimize per corner
Test: Different techniques per corner type
Metric: Sector times + G-force traces
```

---

## 📱 TELEMETRY CHECKS

### What to Look For (F9 HUD)

```
BRAKE INPUT:
✓ Smooth ramp (not steps)
✓ Consistent peak lap-to-lap
✓ Gradual release (not cliff)
✗ Overshooting 100%
✗ "Stair-step" release

STEERING INPUT:
✓ Increases as brake decreases
✓ Lower peak with good trail brake
✗ Maxed while heavy braking
✗ Sudden corrections mid-corner

SPEED TRACE:
✓ Deceleration matches reference lap
✓ Minimum speed consistent
✗ Over-slowing (too much brake)
✗ Variance in apex speed
```

---

## 💡 REMEMBER

```
"Three phases, three opportunities"
  └─ Optimize ALL phases, not just trail braking

"Consistency beats speed"
  └─ Hit 90% perfectly beats 95% randomly

"Feel before speed"
  └─ Master the sensation before chasing lap time

"ABS is your ceiling"
  └─ Never overshoot the threshold

"iRacing is different"
  └─ Slower application can be faster
```

---

## 🔗 FULL CHAPTERS

- [08a: Braking Fundamentals - The Three Phases](09a-braking-fundamentals.md)
- [08b: Trail Braking Technique - Practical Application](09b-trail-braking-technique.md)
- [Chapter 9: Main Chapter](README.md)

---

_"Brake with your brain, not just your foot."_ 🧠🦶

**— Little Padawan** ✨

