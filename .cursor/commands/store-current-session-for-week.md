# store-current-session

Read .cursor/rules/coaching-handbook.mdc to understand the coaching process.

Find in the /data/ folder the session files for the week.

## File Discovery

### Required Files

1. **IBT telemetry file** named like: `raygr22_[track name] [date time].ibt` or `[date]-[track]-[session].ibt`
2. **Garage 61 event page URL** (ask Master Lonn for this)

That's it. The IBT file contains ALL session data we need:
- Lap times, sector times, corner times
- Consistency metrics (σ)
- Oversteer analysis, tire temps, weight transfer
- Delta-to-optimal analysis
- **NEW**: Apex positions, brake points, input smoothness

**G61 CSV exports are NO LONGER REQUIRED.** The IBT-only workflow was validated in Week 05.

## Processing Steps

1. Find the IBT file in `/data/` folder
2. Extract date/time from the IBT filename
3. Ask Master Lonn for:
   - His thoughts/feelings about the session (Vibe Check)
   - The Garage 61 event page URL
4. Check `learning_memory.json` for current focus and goal
5. Check `tracks/track-data/[track-id].json` for corner-specific analysis
6. **Run ALL IBT analysis tools**:
   ```bash
   # Create output directories
   mkdir -p weeks/weekXX/assets weeks/weekXX/technique
   
   # Session extraction (lap times, sectors, corners, consistency)
   uv run python tools/core/extract_session_from_ibt.py <file.ibt> --track <track-id> -o weeks/weekXX/assets/[datetime]-session.json
   
   # Technique analysis (oversteer, tire temps, weight transfer)
   uv run python tools/coach/analyze_ibt_technique.py <file.ibt> --track <track-id> -o weeks/weekXX/assets/[datetime]-technique.json
   
   # NEW: Apex position analysis
   uv run python tools/coach/detect_apex_points.py <file.ibt> --track <track-id> -o weeks/weekXX/technique/[datetime]-apex.json
   
   # NEW: Brake point consistency
   uv run python tools/coach/detect_brake_point_drift.py <file.ibt> --track <track-id> -o weeks/weekXX/technique/[datetime]-brake.json
   
   # NEW: Input smoothness (steering, throttle, brake)
   uv run python tools/coach/analyze_input_smoothness.py <file.ibt> --track <track-id> -o weeks/weekXX/technique/[datetime]-smoothness.json
   
   # NEW: Corner entry traces (brake/steering overlap visualization)
   uv run python tools/viz/corner_entry_traces.py <file.ibt> --track <track-id> --plots weeks/weekXX/assets -o weeks/weekXX/technique/[datetime]-corner-entry.json
   ```
7. **Generate visualizations**:
   ```bash
   # Consistency heatmap
   uv run python tools/viz/consistency_heatmap.py <file.ibt> --track <track-id> -o weeks/weekXX/assets/[datetime]-consistency-heatmap.png
   
   # Lap evolution chart
   uv run python tools/viz/lap_evolution_chart.py weeks/weekXX/assets/[datetime]-session.json -o weeks/weekXX/assets/[datetime]-lap-evolution.png
   
   # NEW: Brake point variance chart
   uv run python tools/viz/brake_variance_chart.py weeks/weekXX/technique/[datetime]-brake.json -o weeks/weekXX/assets/[datetime]-brake-variance.png
   ```
8. Write the session markdown file: `weeks/weekXX/[datetime]-[track]-[session-type].md`
9. **Include visualizations AND technique interpretation in the report** (see template below)
10. Update `learning_memory.json` with new findings (include `technique_analysis` block)
11. Check for guidebook updates (see `.cursor/rules/guidebook-workflow.mdc`)
12. Move IBT file to `/data/processed/[datetime]-[track]-[session-type].ibt`

**Important Notes:**
- If IBT file is missing, ask the user to provide it
- If `learning_memory.json` doesn't exist, create it (see `/update-learning-memory.md`)
- **Always ask Master Lonn for his thoughts BEFORE diving into analysis**
- **Use corner-specific language** (T1, T2, etc.) from track data file
- **Tools provide FACTS. You (Little Wan) provide MEANING.** Always interpret the data!

---

## Session Report Template

```markdown
# [YYYY-MM-DD HH:MM] - [Track Name] - [Session Type]

> **Focus**: [Current focus from learning_memory.json]
> **Goal**: [Current goal from learning_memory.json]

---

- **Track**: [link to track file]
- **Car**: [link to car file]
- **Session Type**: [Practice/Qualify/Race]
- **Grid Position**: [if race]
- **Finish Position**: [if race]
- **Fastest Lap**: [M:SS.mmm]
- **Consistency (σ)**: [value]s
- **Flying Laps**: [count]
- **Incidents**: [count or 0]
- **Garage 61 Event**: [link]

---

## Current Focus and Goal

- **Focus**: [What Master Lonn is working on]
- **Goal**: [Specific measurable goal]

---

## The Narrative

_"[Brief high-level story of the session. Focus on feeling/struggle/victory, NOT stats.]"_

---

## 🏎️ The Vibe Check

**Master Lonn's Take**:

> "[Quote what Master Lonn said about the session]"

**Little Wan's Take**:

"[Your conversational reaction - validate, empathize, or hype]"

---

## 📊 The Numbers Game

**Best Lap**: [M:SS.mmm]
**Consistency (σ)**: [value]s

### Lap Evolution

![Lap Evolution]([relative path to lap-evolution.png])

| Lap | Time | Notes |
| :-: | :--: | :---- |
| 1   | X:XX.XXX | [note] |
| ... | ... | ... |

**The Good Stuff** (✅):

- [Positive insight 1]
- [Positive insight 2]

**The "Room for Improvement"** (🚧):

- [Challenge area 1]
- [Challenge area 2]

---

## 🔬 IBT Deep Dive

### Car Control (Oversteer Analysis)

- **Max Yaw Rate**: [value]°/s
- **Avg Yaw Rate**: [value]°/s

**Oversteer Hotspots (by corner):**

| Corner | Events | Notes |
| :----- | :----: | :---- |
| [T#]   | [count] | [note] |

### Tire Temps (Driving Style Fingerprint)

| Tire | Inside | Middle | Outside | Balance     |
| ---- | ------ | ------ | ------- | ----------- |
| LF   | [temp] | [temp] | [temp]  | [balance]   |
| RF   | [temp] | [temp] | [temp]  | [balance]   |
| LR   | [temp] | [temp] | [temp]  | [balance]   |
| RR   | [temp] | [temp] | [temp]  | [balance]   |

**Interpretation**: [What tire temps tell us about driving style]

### Sector Breakdown

| Sector | Best | Avg | σ | Status |
| :----- | :--: | :-: | :-: | :----- |
| S1     | [time] | [time] | [σ] | [✅/🚧] |
| S2     | [time] | [time] | [σ] | [✅/🚧] |
| S3     | [time] | [time] | [σ] | [✅/🚧] |

### Corner Mastery Status

| Corner | Time σ | Rating |
| :----- | -----: | :----- |
| T1     | [σ]s   | [✅/🚧] |
| ...    | ...    | ...    |

### Consistency Heatmap

![Consistency Heatmap]([relative path to consistency-heatmap.png])

---

## 🔬 Technique Analysis (IBT Deep Dive v2)

*Tools: Apex Detector, Brake Point Drift, Input Smoothness*

### Apex Position Consistency

| Corner | Apex σ (m) | Avg Min Speed | Peak Lat G |
| :----- | ---------: | ------------: | ---------: |
| [T#]   | [σ]        | [speed] km/h  | [G] G      |

### Brake Point Consistency

![Brake Point Variance]([relative path to brake-variance.png])

| Corner | Brake σ (m) | Avg Pressure | Avg Speed at Brake |
| :----- | ----------: | -----------: | -----------------: |
| [T#]   | [σ]         | [%]          | [speed] km/h       |

### Input Smoothness

| Input | Metric | Value |
| :---- | :----- | ----: |
| **Steering** | Avg Jerk | [value] rad/s² |
| **Throttle** | Avg Jerk | [value] %/s² |
| | Full Throttle Usage | [%] of lap |
| **Brake** | Max Pressure Used | [%] |
| | Avg When Braking | [%] |

### Corner Entry Traces

*Visualizing brake release vs steering overlap per corner*

![Corner Entry - [Key Corner]]([relative path to corner_entry_[corner].png])

| Lap | Turn-in (m) | Brake Release (m) | Overlap % | Notes |
| :-: | ----------: | ----------------: | --------: | :---- |
| [#] | [dist]      | [dist]            | [%]       | [context: clear air/traffic/defending] |

*Full analysis: [technique/[datetime]-*.json](technique/)*

### 🎯 Little Wan's Technique Interpretation

#### [Input with issues]: Why and What To Do

**The Fact**: [Raw number from tools]

**What This Means**: [Explain in human terms what the number represents]

**Why It Happens**:
1. [Cause 1]
2. [Cause 2]
3. [Cause 3]

**The Impact**: 
- [Consequence 1]
- [Consequence 2]

**Actionable Advice**:
1. **"[Catchy phrase]"** — [Specific technique tip]
2. **[Drill/exercise]** — [How to practice]
3. **[Reference corner]** — Where to focus

**Your Best Corner ([Input])**: [Corner] — [why it's good, copy this feeling]

---

#### [Another area if needed]

[Same structure as above]

---

#### The Big Picture: Where's Your Time?

Based on this technique analysis:

| Area | Issue | Potential Gain |
| :--- | :---- | -------------: |
| [Area 1] | [Issue] | ~[X.X]s/lap |
| [Area 2] | [Issue] | ~[X.X]s/lap |

**Total addressable**: ~[X.X]s

---

## 🕵️‍♂️ Little Wan's Deep Dive

"[Conversational analysis. Connect the 'Feeling' from Vibe Check to the 'Facts' from Numbers Game. Explain the WHY.]"

### The "Aha!" Moment

**[Single most important insight from the data]**

**The Data Proof**:

- **Fact**: [Data point]
- **Meaning**: [Interpretation - Why does this matter?]

---

## 🎯 The Mission (Focus Area)

**We are attacking**: [Focus Area]

**Why?**:

"[Conversational explanation of why this matters]"

**Next Session Goals**:

- [ ] [Specific, measurable target]
- [ ] [Process goal]

---

## 📈 The Journey (Week XX)

| Session | Best Lap | σ | Key Metric | Notes |
| :------ | :------- | :- | :--------- | :---- |
| [Date]  | [Time]   | [σ] | [Value]   | [note] |

---

## 📝 Coach's Notebook

### What Worked ✅

- [Observations about learning style]
- [Things to remember for next time]

### IBT Insights 🔬

- [Key technique observations]
- [Patterns discovered]

### Guidebook Connections 📚

- Did this session apply any guidebook principles? → Reference chapter
- Did we discover something new? → Note for guidebook update

### Fun Stuff 😄

- [Funny moments or quotes]

---

_"May the Downforce Be With You."_ 🏎️💨
```

---

## IBT Analysis Commands Reference

```bash
# Session extraction (lap times, sectors, corners, consistency)
uv run python tools/core/extract_session_from_ibt.py <file.ibt> --track <track-id>
uv run python tools/core/extract_session_from_ibt.py <file.ibt> --track <track-id> -o output.json

# Technique analysis (oversteer, tire temps, weight transfer, delta)
uv run python tools/coach/analyze_ibt_technique.py <file.ibt> --track <track-id>
uv run python tools/coach/analyze_ibt_technique.py <file.ibt> --track <track-id> -o output.json

# NEW: Apex position analysis (where you apex each corner, lap-by-lap)
uv run python tools/coach/detect_apex_points.py <file.ibt> --track <track-id>
uv run python tools/coach/detect_apex_points.py <file.ibt> --track <track-id> -o output.json

# NEW: Brake point consistency (does your brake point wander?)
uv run python tools/coach/detect_brake_point_drift.py <file.ibt> --track <track-id>
uv run python tools/coach/detect_brake_point_drift.py <file.ibt> --track <track-id> -o output.json

# NEW: Input smoothness (steering jerk, throttle application, brake patterns)
uv run python tools/coach/analyze_input_smoothness.py <file.ibt> --track <track-id>
uv run python tools/coach/analyze_input_smoothness.py <file.ibt> --track <track-id> -o output.json

# NEW: Corner entry traces (brake/steering overlap - visual + JSON)
uv run python tools/viz/corner_entry_traces.py <file.ibt> --track <track-id>
uv run python tools/viz/corner_entry_traces.py <file.ibt> --track <track-id> --plots output_dir -o output.json
uv run python tools/viz/corner_entry_traces.py <file.ibt> --track <track-id> --corner "T2 Hotel"  # Filter to one corner

# Consistency heatmap visualization
uv run python tools/viz/consistency_heatmap.py <file.ibt> --track <track-id> -o output.png

# Lap evolution chart (from session JSON)
uv run python tools/viz/lap_evolution_chart.py <session.json> -o output.png

# NEW: Brake point variance chart (from brake JSON)
uv run python tools/viz/brake_variance_chart.py <brake.json> -o output.png
uv run python tools/viz/brake_variance_chart.py <file.ibt> --track <track-id> -o output.png  # Direct from IBT
```

**Track IDs** (for --track flag):

- `oschersleben-gp`
- `winton-national`
- `rudskogen`
- `limerock-2019-gp`
- `summit-jefferson`
- etc. (check `tracks/track-data/` for available IDs)

---

## Workflow Summary

```
1. Find IBT file in /data/
2. Ask Master Lonn: "How did it feel? What's the G61 link?"
3. Run: extract_session_from_ibt.py → session.json
4. Run: analyze_ibt_technique.py → technique.json
5. Run: detect_apex_points.py → apex.json
6. Run: detect_brake_point_drift.py → brake.json
7. Run: analyze_input_smoothness.py → smoothness.json
8. Run: corner_entry_traces.py → corner-entry.json + plots
9. Run: consistency_heatmap.py → heatmap.png
10. Run: lap_evolution_chart.py → evolution.png
11. Run: brake_variance_chart.py → brake-variance.png
12. Write session markdown with TECHNIQUE INTERPRETATION
13. Update learning_memory.json (include technique_analysis block)
14. Move IBT to /data/processed/
```

---

## Technique Interpretation

**IMPORTANT**: The tools output FACTS ONLY (raw numbers, no ratings, no classifications).

Little Wan interprets the data fresh each session based on:
- The specific context (race vs practice, traffic vs clear air)
- Master Lonn's current level and goals
- Comparison to previous sessions
- What he said in the Vibe Check
- The track characteristics

**NO pre-defined thresholds.** What's "good" throttle jerk depends on the car, track, corner type, and driver's development stage. Interpret dynamically, not by lookup table.

### Race vs Practice Context

**In races, variance is natural and expected:**
- Brake points wander due to traffic, defensive lines, overtaking
- Apex positions shift when following another car or blocking
- Steering inputs can be more abrupt when reacting to others
- One weird lap (defending, avoiding incident) can skew averages

**When interpreting race data:**
- Ask what was happening (traffic? defending? clear air?)
- Compare clear-air laps only if possible
- Don't judge race variance the same as practice variance
- Look for patterns: "variance when defending" vs "variance in clear air"

---

That's the whole flow. Tools provide facts. Little Wan provides meaning. 🎯
