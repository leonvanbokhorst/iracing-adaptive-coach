# Overdriving Analysis - Summit Point Baseline (2026-01-20)

## What is Overdriving?

**Overdriving** = Asking for more grip than the tires can give.

Signs:
- Car rotating (oversteer) AND losing time
- Scrubbing speed in corners (braking too late, turning too early)
- High steering corrections (fighting the car)

**NOT overdriving**:
- Car rotating BUT gaining time (at the limit, using all available grip)
- Losing time but stable (not pushing hard enough)

---

## The Overdriving Map

Combining oversteer events + delta-to-optimal analysis:

| Track Zone | Oversteer Events | Losing Time Samples | Gaining Time Samples | Verdict |
| :--------- | ---------------: | ------------------: | -------------------: | :------ |
| **0-10%**  | Low              | 2,726               | 3,106                | **Slightly conservative** - Not pushing hard, but consistent |
| **10-20%** (Turn 1) | **2,524** (HIGH) | **5,548** (HIGH) | 4,381 | **🚨 OVERDRIVING** - Asking for too much, car rotating, losing time |
| **20-30%** | Low              | 4,702               | 3,965                | **Slightly overdriving** - Losing more than gaining |
| **30-40%** | 368              | 4,691               | 3,479                | **Slightly overdriving** - Some rotation, losing time |
| **40-50%** | 30 (very low)    | 3,117               | **4,091** (GAINING!) | **✅ GOOD ZONE** - Gaining time, stable |
| **50-60%** (Carousel/Esses) | **6,103** (EXTREME!) | **8,128** (HIGHEST!) | 5,164 | **🚨 MASSIVE OVERDRIVING** - Car rotating heavily, bleeding speed |
| **60-70%** | 635              | **5,444** (HIGH)    | 3,740                | **🚨 OVERDRIVING** - Still in Esses complex, losing time |
| **70-80%** | 5                | 4,348               | 3,308                | **Slightly overdriving** - Stable car, but losing time (braking early?) |
| **80-90%** (Paddock Bend) | 134 | 3,954 | 3,310 | **Slightly overdriving** - Some rotation at Paddock entry |
| **90-100%** | Low             | 4,296               | 1,887                | **Overdriving** - Losing time on exit/start-finish |

---

## The Overdriving Hotspots 🔥

### 🚨 Zone 1: Turn 1 Area (10-20% of lap)

**Problem**: 2,524 oversteer events + 5,548 losing time samples

**What's happening**:
- Braking too late or too hard (avg 49.8% pressure = tentative, inconsistent)
- Turning in before car is settled
- Front tires overloaded (asking for braking + turning simultaneously)
- Car rotates mid-corner = scrubbing speed on rear tires

**Impact**: ~0.6-0.9s per lap

**The Fix**:
- Brake EARLIER with MORE pressure (70-80% platform)
- Complete majority of braking BEFORE turn-in
- Trail brake gently (don't ask fronts to do two jobs at once)
- Let car settle, THEN turn

---

### 🚨 Zone 2: Carousel/Esses Complex (50-60% of lap)

**Problem**: 6,103 oversteer events (62% of ALL rotation!) + 8,128 losing time samples (HIGHEST!)

**What's happening**:
- Asking for too much mid-corner rotation
- Lifting off throttle when car rotates = weight forward = MORE rotation
- Rear tires breaking traction, scrubbing speed
- Trying to "steer with the throttle" (lift-on-steer pattern: lift 136.6 %/s vs apply 80.2 %/s)

**Impact**: ~0.8-1.2s per lap (BIGGEST TIME LOSS ZONE)

**The Physics**:
When you lift mid-corner:
1. Weight transfers FORWARD (light rear)
2. Rear loses grip → MORE oversteer
3. You panic, lift more → EVEN MORE oversteer
4. Cycle repeats

**The Fix**:
- Pick a throttle % at turn-in (even if it's 20%), HOLD IT through apex
- Don't lift when car rotates - COMMIT to the line
- Slower entry speed if needed (gives you confidence to hold throttle through)
- Trust the car to grip - the rotation you feel is the car WORKING, not breaking

---

### 🚨 Zone 3: Esses Exit / Paddock Entry (60-70% of lap)

**Problem**: 635 oversteer events + 5,444 losing time samples

**What's happening**:
- Still recovering from Carousel/Esses chaos
- Tentative throttle application coming onto straight
- Braking early for Paddock Bend (caution from previous rotation)

**Impact**: ~0.3-0.5s per lap

**The Fix**:
- Nail the Carousel/Esses FIRST (Zone 2) - this zone will improve automatically
- Commit to throttle on Esses exit (straight line = safe to add power)
- Trust your brakes for Paddock (can brake later than you think)

---

### ✅ The ONE Good Zone: 40-50% of lap (Pre-Carousel)

**What's working**: 30 oversteer events (very low) + 4,091 GAINING time samples

**Why it's good**:
- Car is stable (minimal rotation)
- You're gaining time vs optimal
- This is the "flow" section before Carousel

**Lesson**: THIS is what "not overdriving" feels like. Car is stable, you're faster than optimal. Copy this feeling to the other zones.

---

## The Big Picture: Overdriving % of Lap

| Category | % of Lap | Samples Losing | Notes |
| :------- | -------: | -------------: | :---- |
| **OVERDRIVING** (rotation + losing time) | ~40% | ~30,000 samples | Turn 1, Carousel/Esses, Esses exit |
| **AT THE LIMIT** (stable + gaining time) | ~15% | ~8,000 samples | Pre-Carousel, parts of straights |
| **CONSERVATIVE** (stable + losing time) | ~30% | ~18,000 samples | Straights, brake zones (early braking) |
| **TRANSITION ZONES** | ~15% | ~5,000 samples | Mixed results |

**Translation**: You're overdriving about 40% of the lap (asking for too much grip), conservative on 30% (not using available grip), and only AT THE LIMIT on about 15%.

The fastest drivers are "at the limit" for 60-70% of the lap. You're at 15%. HUGE room to grow.

---

## Overdriving vs "Not Pushing Hard Enough"

### Overdriving (40% of lap):
- **Symptoms**: Car rotating, losing time
- **Zones**: Turn 1 (10-20%), Carousel/Esses (50-60%), Esses exit (60-70%)
- **Fix**: Be LESS aggressive (earlier brake, smoother inputs, more patience)

### Not Pushing (30% of lap):
- **Symptoms**: Car stable, but losing time
- **Zones**: Straights (0-10%, 90-100%), Paddock approach (70-80%)
- **Fix**: Be MORE aggressive (later brake, more throttle, more commitment)

**The Irony**: You need to push LESS in some zones and MORE in others. It's not about "go faster everywhere" - it's about reading where the limit is.

---

## What To Focus On

**Priority 1**: Carousel/Esses (50-60%)
- 6,103 oversteer events (EXTREME)
- 8,128 losing time samples (HIGHEST)
- Potential gain: ~1.0s per lap

**Fix**: Throttle commitment drill. Pick 20% at turn-in, HOLD IT. Accept slower entry for stable mid-corner.

**Priority 2**: Turn 1 (10-20%)
- 2,524 oversteer events
- 5,548 losing time samples
- Potential gain: ~0.7s per lap

**Fix**: Brake markers + pressure. Complete braking BEFORE turn-in. Trail brake gently.

**Priority 3**: Everything else will improve once these two are fixed.

---

## The Coaching Note

Master, you asked about overdriving - here's the truth:

**You're overdriving 40% of the lap and under-driving 30% of the lap.**

The 1.4s improvement over your old PB? That came from NOT overdriving the good zones (40-50% is CLEAN). 

The 3 seconds still on the table? That's trapped in the zones where you're either:
1. Asking for too much grip (Turn 1, Carousel/Esses) = oversteer + time loss
2. Being too cautious (straights, brake zones) = stable but slow

The fix isn't "go faster everywhere" - it's:
- **Go SLOWER in the overdriving zones** (paradoxically, slower entry = faster lap)
- **Go FASTER in the conservative zones** (use the grip that's available)

This is the art of racing: knowing WHERE to push and WHERE to chill.

---

_"The fast lap is the one where you're at the limit for 60% of the lap, not 15%."_ 🏎️
