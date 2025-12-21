# compare-telemetry-vs-reference

Compare a session's fastest lap telemetry against a reference lap (e.g., PB from same series) and provide coaching insights on where time is gained/lost.

---

## What This Command Does

1. **Runs telemetry comparison tool** on two CSV files (current lap vs reference lap)
2. **Generates visual track speed delta map** showing where you're faster/slower
3. **Analyzes the data** to find speed, braking, throttle, and G-force differences
4. **Creates coaching narrative** with actionable advice on how to tackle differences
5. **Updates session report** with visual map + narrative + comparison data
6. **Provides specific focus areas** for next session based on findings

---

## Prerequisites

Before running this command, ensure:

1. ✅ Current session has been analyzed (session report exists in `weeks/weekXX/`)
2. ✅ Current session's fastest lap telemetry is in `data/processed/`
3. ✅ Reference lap telemetry is uploaded to `data/compare/`
4. ✅ Both laps are from the **same series/setup** (fair comparison)

---

## Usage

**Step 1**: Tell Little Padawan:

```
/compare-telemetry-vs-reference
```

**Step 2**: Provide when asked:

- Path to **current lap telemetry** (usually in `data/processed/`)
- Path to **reference lap telemetry** (in `data/compare/`)
- Reference lap time (e.g., "1:28.969")
- Reference lap context (e.g., "2024 PB - same series, 6 months ago")

**Step 3**: Little Padawan will:

- Run the telemetry comparison tool (JSON data)
- Generate visual track speed delta map (PNG image)
- Analyze the data and create coaching narrative
- Update the session report with:
  - Visual track map embedded
  - Little Padawan's narrative on what the data means
  - Actionable advice on how to tackle the differences
  - Specific focus areas for next session
- Save all comparison data for reference

---

## Example Flow

**You**: `/compare-telemetry-vs-reference`

**Little Padawan**: "Alright Master, let's compare your lap against a reference! 🔍

I need:

1. Current lap telemetry path
2. Reference lap telemetry path
3. Reference lap time
4. Reference lap context"

**You**:

```
Current: data/processed/2025-12-20-15-22-rudskogen-practice-ray-ff1600-01-29-691.csv
Reference: data/compare/2024-rudskogen-same-series-pb-01-28-969.csv
Ref time: 1:28.969
Context: 2024 PB - same series, 6 months ago
```

**Little Padawan**:

- Runs telemetry comparison (speed, braking, throttle, G-forces)
- Generates visual track speed delta map
- Creates coaching narrative based on the data
- Updates `weeks/week02/2025-12-20-15-22-rudskogen-practice.md` with:
  - Embedded track speed delta map image
  - Coaching narrative explaining what to look at
  - Actionable advice on tackling the differences
  - Specific focus areas ranked by opportunity
- Saves raw data to `weeks/week02/comparison/` folder
- Tells you exactly where the time gap is and HOW to close it

---

## What You'll Learn

### Speed Delta Map

- Where on track you're faster/slower (km/h difference)
- Maximum speed gains/losses and at what % of lap
- Average speed comparison

### Braking Analysis

- Are you braking earlier/later than reference?
- Brake pressure differences
- Time spent braking (% of lap)
- Braking zones comparison

### Throttle Application

- Full throttle time comparison
- Average throttle application
- Where you're getting on/off power differently

### Cornering G-Forces (ENHANCED)

**Lateral G (Cornering Load):**

- Max lateral G comparison (peak cornering force)
- Average lateral G (overall tire loading)
- Lateral G smoothness (lower = smoother, higher = spiky/overdriving)
- Where max lateral G gain/loss occurs (% of lap)

**Longitudinal G (Braking/Acceleration):**

- Max braking G (how hard you're braking)
- Max acceleration G (how hard you're accelerating)
- Longitudinal G smoothness (harsh vs smooth inputs)

**Combined Load:**

- Max total G-force (lat + long combined)
- Average total G-force (overall grip usage)

**Overdriving Detection:**

- Steering efficiency (lateral G per degree of steering)
- Steering smoothness (sawing vs smooth)
- Overdriving % (using MORE steering, getting LESS grip = sliding)
- Better technique % (using LESS steering, getting MORE grip = flow)

### Distance Breakdown

- Speed/brake/throttle at every 10% of lap
- **Lateral G at every 10% of lap** (cornering load by location)
- **Longitudinal G at every 10% of lap** (braking/accel by location)
- **Steering angle at every 10% of lap** (input by location)
- Pinpoint which corners are different

### How to Read G-Force Data (The Tire Story)

**What High Lateral G Means:**

- ✅ Good: High lateral G + smooth = loading tires correctly
- ❌ Problem: Low lateral G + high speed corner = leaving grip on table
- ❌ Problem: Spiky lateral G = sliding/overdriving

**What Steering Efficiency Means:**

- **Higher efficiency** = More grip per steering input (good!)
- **Lower efficiency** = Sliding/overdriving (using more steering, getting less grip)

**Overdriving Indicators:**

- High steering angle + low lateral G = **sliding**
- High steering smoothness (std dev) = **sawing the wheel**
- Overdriving % > 20% = **fighting the car**

**Flow State Indicators:**

- High lateral G + smooth steering = **perfect grip usage**
- Better technique % > 30% = **you've improved!**
- Higher steering efficiency = **more grip per input**

---

## Output Files

**Primary**: Updated session report with new section:

```markdown
## 🔬 Telemetry Comparison vs Reference Lap

**Gap**: [time difference]
**Reference**: [context, e.g., "2024 PB - same series (1:28.969) - 6 months ago"]
**Comparison Files**:

- Visual Map: [link to PNG]
- Raw Data: [link to JSON]
- Track Data: [link to map data JSON]

### 🗺️ Visual Speed Delta Map

![Track Speed Delta Map](comparison/track-speed-delta-map.png)

**How to Read This Map:**

- 🟢 **Green sections**: You're FASTER than reference
- 🟡 **Yellow sections**: About the same speed
- 🔴 **Red sections**: You're SLOWER than reference (opportunities!)
- **Red X markers**: Biggest time loss zones
- **Orange X markers**: Secondary loss zones
- **Green Star markers**: Where you're beating the reference!

### 🔥 Little Padawan's Analysis: [Catchy Title]

[Engaging narrative about what the data reveals - not just facts, but MEANING]

#### 📊 The Reality Check

[High-level overview of the comparison - e.g., "68.4% slower, but 31.6% faster"]

#### 🔴 PROBLEM ZONE #1: [Zone Name]

[Detailed explanation of the biggest loss area]

- **What it is**: [Corner/section identification]
- **The Issue**: [What's happening]
- **My Hunch**: [Little Padawan's interpretation]
- **How to Fix**: [Specific actionable advice]

#### 🔴 PROBLEM ZONE #2: [Zone Name]

[Second biggest opportunity]

#### ⭐ WINNING ZONE: [Zone Name]

[Where you're faster - reinforce what's working!]

### 🎯 The Gap Breakdown

[Table showing where time is lost/gained]

### 💡 What To Do Next Session

[Ranked, specific, actionable tasks]

1. **[Task 1]** - [Why + How]
2. **[Task 2]** - [Why + How]
3. **[Task 3]** - [Why + How]

### 🏁 The Bottom Line

[Motivating summary - "Fix X and Y, beat your PB"]
```

**Secondary Files** (saved to `weeks/weekXX/comparison/`):

- `[date]-track-speed-delta-map.png` - Visual track map
- `[date]-telemetry-comparison.json` - Raw comparison data
- `[date]-track-speed-delta-map-data.json` - Map data points

---

## Important Notes

### Data Unit Conversions (Automatic) ✅

The tool automatically handles Garage 61 export quirks:

- **LatAccel** and **LongAccel** are exported in **m/s²** (not G)
- Tool auto-converts to G (divides by 9.81) when values exceed 5.0
- Removes wrap-around data points (where lap distance goes backwards)
- You don't need to pre-process the data!

### Fair Comparisons Only ⚠️

- Compare laps from **same series/setup** only
- Different setups = different car behavior = unfair comparison
- Open setup vs fixed setup = apples vs oranges
- **Different steering ratios** (e.g., 900° vs 1040°) will affect steering angle comparisons

### Context Matters 📝

- Track conditions (wet vs dry)
- Time of year (tire compound changes)
- Setup version (if setup was updated)
- Steering ratio (affects steering angle data)
- Always note the context in "Reference lap context"

### What Little Padawan Will Do

**Facts** (from the tool):

- Speed at 40% lap: Current 95 km/h, Reference 92 km/h
- Brake pressure at T2: Current 0.85, Reference 0.90
- Full throttle %: Current 45%, Reference 50%
- **Lateral G at 40%: Current 1.8g, Reference 2.1g**
- **Steering efficiency: Current 85 g/deg, Reference 95 g/deg**
- **Overdriving %: 15% of lap**

**Meaning** (Little Padawan's coaching):

- "You're carrying 3 km/h MORE through T2! The 50-sign brake breakthrough is WORKING! 🔥"
- "But you're getting on throttle 5% less of the lap - exit speed opportunity!"
- "**At 40% lap (S2 exit?), you're loading tires 0.3g LESS than reference - you're leaving grip on the table!**"
- "**Your steering efficiency is 10% lower - you're working the wheel more but getting less grip. Time to smooth it out.**"
- "**15% of the lap you're overdriving (more steering, less grip) - focus on being gentler with inputs.**"
- "Focus on T5 exit next session - that's where 0.5s is hiding."

---

## Tips For Best Results

1. **Compare recent laps**: Old PBs might have been different conditions/setup
2. **Note the gap**: Small gap (< 0.5s) = polish. Large gap (> 1.0s) = technique difference
3. **Look for patterns**: Consistent theme across sectors = fundamental approach difference
4. **Celebrate wins**: If you're faster in some areas, BUILD on that!
5. **One focus at a time**: Don't try to fix everything - pick the biggest opportunity

---

## Updating Learning Memory

After comparison, Little Padawan will update `learning_memory.json` with:

- Correct reference PB for the track/series
- Insights about strengths/weaknesses vs reference
- Specific focus areas identified from comparison
- Progress tracking (closing the gap over time)

---

## Example Use Case

**Scenario**: Master Lonn just set 1:29.691 at Rudskogen and wants to know where he stands vs his 2024 same-series PB (1:28.969).

**Command**: `/compare-telemetry-vs-reference`

**Result**:

- Visual track map generated showing speed deltas around entire lap
- Little Padawan's narrative reveals:
  - T2 is NOW FASTER than PB (+3.79 km/h) - breakthrough working!
  - 40% lap (late S2) is -2.78 km/h slower (Priority #1: ~0.4s available)
  - Start/Finish straight is -1.42 km/h slower (Priority #2: ~0.2s available)
- Session report updated with embedded map + full coaching narrative
- Specific advice on HOW to attack the problem zones
- Next session focus: Identify and attack the 40% lap corner

---

## Summary

This command transforms raw telemetry data into actionable coaching insights:

1. **Visual Map**: Clean track layout showing exactly where time is gained/lost
2. **Terminal Stats**: Structured data printed for Little Padawan to interpret
3. **Coaching Narrative**: Custom analysis embedded in session file with:
   - Engaging explanation of what the data means
   - Specific problem zones identified with actionable advice
   - Winning zones celebrated to reinforce what's working
   - Ranked priorities for next session
4. **Reusable**: Works for any track, any comparison, any time

**The Result**: Master Lonn gets a visual map + Little Padawan's coaching voice explaining HOW to tackle the differences, not just WHAT the differences are.

---

_"May the Delta Reveal The Way."_ 📊🔍
