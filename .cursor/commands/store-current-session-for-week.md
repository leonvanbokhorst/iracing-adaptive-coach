# store-current-session

Read .cursor/rules/coaching-handbook.mdc to understand the coaching process.

Find in the /data/ folder the session files for the week.

## File Discovery

### Required Files (G61)
1. The session file named like this: Garage 61 - [session kind] - Export - [date time].csv
2. The fastest lap telemetry named like this: Garage 61 - Lonn Ponn - [car name] - [circuit name] - [lap time] - [code].csv

### Optional Files (IBT - Deep Technique Analysis)
3. **NEW: IBT telemetry file** named like: `raygr22_[track name] [date time].ibt`
   - If found, run `uv run python tools/coach/analyze_ibt_technique.py <ibt_file> --track <track-id>`
   - This provides ABS triggers, oversteer analysis, tire temps, and delta-to-optimal data
   - IBT data is BONUS - session can be processed without it

## Processing Steps

1. Use the 'Started at' date and time column and read the first row of the session file to get the date and time of the session.
2. Rename the session file like this: [date time] - [circuit name] - [session kind].csv
3. Rename the telemetry file like this: [date time] - [circuit name] - [session kind] - [car name] - [lap time] - [code].csv
4. **If IBT exists**: Rename to [date time] - [circuit name] - [session kind].ibt
5. Name the session markdown file like this: [date time] - [circuit name] - [session kind].md
6. Take the learning memory.json file into account to get the current focus and goal.
7. Check if track data exists in tracks/track-data/ for corner-specific analysis.
8. **If IBT exists**: Run IBT analysis and save output to weeks/weekXX/assets/[date time]-ibt-analysis.json
9. After writing the session file, update the learning memory.json file with the new findings.
10. **Check for guidebook updates** - Did this session discover a principle worth codifying? (See .cursor/rules/guidebook-workflow.mdc)
11. After analyzing the session move ALL files (session CSV, telemetry CSV, IBT) to the /data/processed/ folder.

Important: If you don't find the G61 session data files, ask the user to export the session files. 😌
Important: If IBT file is missing, proceed without it - it's bonus data, not required.
Important: If you don't find the learning memory.json file create it. Use the structure from the /update-learning-memory.md file.
Important: Ask Master Lonn what his thoughts and feeling were about the session before you continue.
Important: Ask Master Lonn for the Garage61 event page of the session for reference in the session file.
Important: **Use corner-specific language** - Check if the track file has a "Corner Reference" table. If available, use corner numbers (T1, T2, T11, etc.) in the report for driver clarity. Keep lap distance percentages internal for your data lookup only.

---

## Session Report Template

Header of the session file: [date time] - [circuit name] - [car name] - [fastest lap time]

- **Track**: [circuit file in /tracks/]
- **Car**: [car file in /cars/]
- **Session kind**: [session kind]
- **Fastest lap time**: [fastest lap time]
- **Consistency (σ)**: [consistency (σ)]
- **Clean laps**: [clean laps]
- **Incidents**: [incidents or 0 if none]
- **Garage 61 event page**: [Garage 61 event page URL]
- **IBT Analysis**: [Yes/No] ← NEW

## Current Focus and Goal

- **Focus**: [What Master Lonn is working on]
- **Goal**: [Specific measurable goal]

---

## The Narrative

"[Brief high-level summary of the session. Focus on the 'Story' - the feeling, the struggle, or the victory. Do NOT list specific stats here - save them for the sections below.]"

---

## 🏎️ The Vibe Check

**Master Lonn's Take**:
"[Quote what Master Lonn said about the session]"
If he has not said anything, ask him what he thought of the session first before you continue.

**Little Wan's Take**:
"[Your conversational reaction - validate his feeling, share empathy, or hype him up]"

---

## 📊 The Numbers Game

**Best Lap**: [M:SS.mmm]
**Consistency (σ)**: [value]s

**The Good Stuff** (✅):

- [Positive insight 1]
- [Positive insight 2]

**The "Room for Improvement"** (🚧):

- [Challenge area 1]
- [Challenge area 2]

---

## 🔬 IBT Deep Dive (if available)

_Only include this section if IBT file was analyzed._

### Braking Technique (ABS cars only)
_Skip this section for cars without ABS (FF1600, Skip Barber, etc.)_

- **ABS Triggers**: [count] ([per lap] per lap)
- **Hotspot Corners**: [list corners with most ABS triggers]

### Car Control (Oversteer Analysis)
- **Max Yaw Rate**: [value]°/s
- **Oversteer Hotspots**: [corners where car rotated most]

### Tire Temps (Driving Style Fingerprint)
| Tire | Inside | Middle | Outside | Balance |
|------|--------|--------|---------|---------|
| LF   | [temp] | [temp] | [temp]  | [balanced/inside_hot/outside_hot] |
| RF   | [temp] | [temp] | [temp]  | [balanced/inside_hot/outside_hot] |
| LR   | [temp] | [temp] | [temp]  | [balanced/inside_hot/outside_hot] |
| RR   | [temp] | [temp] | [temp]  | [balanced/inside_hot/outside_hot] |

**Interpretation**: [What the tire temps tell us about driving style]

### Delta to Optimal
- **Gap to YOUR theoretical best**: [value]s
- **Losing time at**: [zones/corners]
- **Gaining time at**: [zones/corners]

---

## 🕵️‍♂️ Little Wan's Deep Dive

"[Conversational analysis. Do NOT just repeat the stats from above. Explain the **WHY**. Connect the 'Feeling' from the Vibe Check to the 'Facts' from the Numbers Game. If IBT data is available, weave those insights in too.]"

### The "Aha!" Moment

"[The single most important insight from the data]"

**The Data Proof**:

- **Fact**: [Data point]
- **Meaning**: [Interpretation - Why does this matter?]

---

## 🎯 The Mission (Focus Area)

**We are attacking**: [Focus Area]

**Why?**:
"[Conversational and engaging explanation of why this matters]"

**Next Session Goal**:

- [ ] [Specific, measurable target]
- [ ] [Process goal (e.g., 'Stick to one line')]

---

## 📈 The Journey

| Session | Best Lap | Consistency | Key Metric (e.g., S2) | IBT? | Notes           |
| :------ | :------- | :---------- | :-------------------- | :--- | :-------------- |
| [Date]  | [Time]   | [σ]         | [Value]               | ✅/❌ | [Short comment] |

---

## 📝 Coach's Notebook

### What Worked ✅
- [Observations about learning style]
- [Things to remember for next time]

### IBT Insights 🔬 (if available)
- [Key technique observations from IBT data]
- [Patterns discovered (e.g., "ABS triggers concentrated at T3")]

### Guidebook Connections 📚
- Did this session apply any guidebook principles? → Reference chapter
- Did we discover something new? → Note for guidebook update
- Example: "Applied Chapter 8 trail braking successfully at T10"

### Fun Stuff 😄
- [Funny moments or quotes]

---

_"May the Downforce Be With You."_ 🏎️💨

---

## IBT Analysis Commands Reference

```bash
# Quick summary (fast check)
uv run python tools/core/parse_ibt.py <file.ibt> --summary

# Full technique analysis with corner breakdown
uv run python tools/coach/analyze_ibt_technique.py <file.ibt> --track <track-id>

# Save analysis to file
uv run python tools/coach/analyze_ibt_technique.py <file.ibt> --track <track-id> -o weeks/weekXX/assets/ibt-analysis.json
```

**Track IDs** (for --track flag):
- oschersleben-gp
- winton-national
- rudskogen
- lime-rock-gp
- etc. (check tracks/track-data/ for available IDs)

---

## Example with IBT Data

# 2026-01-06 16:00 - Oschersleben GP - Practice #2

> **Focus**: Week 05: Precision on the Plain
> **Goal**: S3 consistency, McDonald's chicane

---

- **Track**: [Oschersleben GP](../../tracks/track-motorsport-arena-oschersleben-grand-prix.md)
- **Car**: [Ray FF1600](../../cars/car-ray-ff1600.md)
- **Session kind**: Practice
- **Fastest lap time**: 1:33.773
- **Consistency (σ)**: 0.42s
- **Clean laps**: 4/4
- **Incidents**: 0
- **Garage 61 event page**: [Link]
- **IBT Analysis**: Yes ✅

## 🔬 IBT Deep Dive

### Car Control (Oversteer Analysis)
- **Max Yaw Rate**: 120.5°/s (big moment somewhere!)
- **Oversteer Hotspots**: T3 Hasseroeder (657), T2 Hotel Exit (633), T7 Hairpin (500)

### Tire Temps
| Tire | Inside | Middle | Outside | Balance |
|------|--------|--------|---------|---------|
| LF   | 53.1°C | 53.4°C | 53.6°C  | balanced |
| RF   | 53.5°C | 53.3°C | 52.9°C  | balanced |
| LR   | 53.1°C | 53.4°C | 53.5°C  | balanced |
| RR   | 53.4°C | 53.4°C | 53.0°C  | balanced |

**Interpretation**: Short session, tires never fully came up to temp. No driving style diagnosis available yet.

### Delta to Optimal
- **Gap to YOUR theoretical best**: +4.796s
- **Losing time at**: T14 Zeppelin (90-100%), Shell/Amman (70-80%)
- **Gaining time at**: Chicane/McDonald's (50-60%)
