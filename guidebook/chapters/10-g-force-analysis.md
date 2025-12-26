# G-Force Analysis Guide: The Tire Story Without Tire Temps

**Why G-Forces Matter More Than Tire Temps (For Now)**

At your current level, G-force data tells you 90% of what tire temps would tell you, but in a MORE actionable way.

---

## What Each Metric Means

### 1. Lateral G (Cornering Load)

**What it is:** How hard you're pushing the tires sideways through corners.

**Good Signs:**

- ✅ High lateral G (close to 2.0g+ in FF1600)
- ✅ Smooth lateral G (low standard deviation)
- ✅ Consistent lateral G lap-to-lap

**Warning Signs:**

- ⚠️ Low lateral G in fast corners = leaving grip unused
- ⚠️ Spiky lateral G = sliding/overdriving
- ⚠️ Lower lateral G than reference = not loading tires enough

**What Little Padawan Will Say:**

- "Your max lateral G is 2.1g but reference is 2.4g - you're leaving 0.3g on the table!"
- "Your lateral G smoothness is 0.15 vs reference 0.08 - you're fighting the car more."

---

### 2. Longitudinal G (Braking/Acceleration)

**What it is:** How hard you're loading tires under braking and acceleration.

**Good Signs:**

- ✅ High braking G (shows commitment)
- ✅ Smooth braking G (not locking up)
- ✅ Good acceleration G (good exits)

**Warning Signs:**

- ⚠️ Low braking G = braking too early/softly
- ⚠️ Spiky braking G = unstable/locking
- ⚠️ Low accel G = losing exit speed

**What Little Padawan Will Say:**

- "Your max braking G is -1.5g but reference is -1.8g - you're leaving braking performance unused!"
- "Your braking is smooth (σ = 0.05) - that's good technique!"

---

### 3. Steering Efficiency (G per Degree)

**What it is:** How much lateral G you get per degree of steering input.

**Formula:** `Lateral G / Steering Angle = Efficiency`

**Good Signs:**

- ✅ High efficiency (90-100+ g/deg) = flowing, not sliding
- ✅ Higher than reference = better grip usage
- ✅ Consistent efficiency = smooth driver

**Warning Signs:**

- ⚠️ Low efficiency (< 80 g/deg) = sliding/overdriving
- ⚠️ Lower than reference = working harder for less grip
- ⚠️ Spiky efficiency = inconsistent inputs

**What Little Padawan Will Say:**

- "Your steering efficiency is 85 g/deg vs reference 95 g/deg - you're working the wheel 10% harder for the same grip!"
- "That means you're sliding or being too aggressive with inputs."

---

### 4. Overdriving Detection

**What it is:** % of lap where you're using MORE steering but getting LESS lateral G than reference.

**Formula:** `(More Steering + Less Lat G) / Total Lap = Overdriving %`

**Good Signs:**

- ✅ Overdriving % < 10% = mostly in control
- ✅ Better technique % > 20% = improving over reference
- ✅ Low steering smoothness (σ) = not sawing

**Warning Signs:**

- ⚠️ Overdriving % > 20% = fighting the car a lot
- ⚠️ Better technique % < 10% = not improving technique
- ⚠️ High steering smoothness (σ > 0.1) = sawing the wheel

**What Little Padawan Will Say:**

- "You're overdriving 25% of the lap - that's where you're losing time!"
- "At 40% lap distance, you're using 5 degrees more steering but getting 0.3g LESS grip. That's sliding, Master."
- "Good news: 30% of the lap you're using LESS steering and getting MORE grip. Build on that!"

---

### 5. Combined Total G (Overall Load)

**What it is:** Total load on car (lateral + longitudinal combined).

**Formula:** `sqrt(Lat G² + Long G²)`

**Good Signs:**

- ✅ High total G (2.5-3.0g+) = using available grip
- ✅ Consistent total G = smooth driving
- ✅ Close to reference = similar car control

**Warning Signs:**

- ⚠️ Low total G = leaving performance on table
- ⚠️ Spiky total G = unstable driving
- ⚠️ Much lower than reference = not pushing hard enough

**What Little Padawan Will Say:**

- "Your max total G is 2.8g vs reference 3.1g - you're not loading the car as hard."
- "That 0.3g difference is costing you time around the lap."

---

## How to Use This in Practice

### Before Session

Review last comparison to know focus areas:

- "Last time I was overdriving 30% of the lap, especially in S2"
- "My steering efficiency was low in high-speed corners"

### During Session

Focus on FEELING the grip:

- "Am I sawing the wheel or being smooth?"
- "Can I feel the car loading up through this corner?"
- "Am I fighting it or flowing?"

### After Session

Compare G-forces to see if technique improved:

- "Did my lateral G smoothness improve?"
- "Is my overdriving % lower?"
- "Did my steering efficiency go up?"

---

## Quick Reference Table

| Metric                  | Good               | Warning    | Action                           |
| ----------------------- | ------------------ | ---------- | -------------------------------- |
| **Lateral G**           | High, smooth       | Low, spiky | Load tires more, smooth inputs   |
| **Longitudinal G**      | High braking/accel | Low, spiky | Brake harder/later, better exits |
| **Steering Efficiency** | > 90 g/deg         | < 80 g/deg | Smooth inputs, less sawing       |
| **Overdriving %**       | < 10%              | > 20%      | Gentler inputs, let car settle   |
| **Better Technique %**  | > 20%              | < 10%      | Keep doing what's working!       |
| **Total G**             | > 2.8g             | < 2.5g     | Push harder, use available grip  |

---

## The Bottom Line

**G-Forces ARE the tire story:**

- **High lateral G** = tires are loaded and gripping
- **Low lateral G** = tires are underused or sliding
- **Steering efficiency** = how well you're managing grip
- **Overdriving %** = where you're fighting the car
- **Better technique %** = where you're flowing

You don't need tire temps to know if you're overdriving or underusing grip. The G-forces tell you in real-time, lap by lap.

**Focus on:** Smooth inputs → High G-forces → Better lap times

---

_"The Force (G-Force) is strong with this one."_ 🏎️💨
