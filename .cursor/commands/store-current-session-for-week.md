# store-current-session

Read .cursor/rules/coaching-handbook.mdc to understand the coaching process.

Find in the /data/ folder the session files for the week.

## File Discovery

### Required Files

1. **IBT telemetry file** named like: `raygr22_[track name] [date time].ibt`
2. **Garage 61 event page URL** (ask Master Lonn for this)

That's it. The IBT file contains ALL session data we need:
- Lap times, sector times, corner times
- Consistency metrics (σ)
- Oversteer analysis, tire temps, weight transfer
- Delta-to-optimal analysis

**G61 CSV exports are NO LONGER REQUIRED.** The IBT-only workflow was validated in Week 05.

## Processing Steps

1. Find the IBT file in `/data/` folder
2. Extract date/time from the IBT filename (format: `raygr22_[track] [YYYY-MM-DD] [HH-MM-SS].ibt`)
3. Ask Master Lonn for:
   - His thoughts/feelings about the session (Vibe Check)
   - The Garage 61 event page URL
4. Check `learning_memory.json` for current focus and goal
5. Check `tracks/track-data/[track-id].json` for corner-specific analysis
6. Run IBT analysis tools:
   ```bash
   # Session extraction (lap times, sectors, corners, consistency)
   uv run python tools/core/extract_session_from_ibt.py <file.ibt> --track <track-id> -o weeks/weekXX/assets/[datetime]-session.json
   
   # Technique analysis (oversteer, tire temps, weight transfer)
   uv run python tools/coach/analyze_ibt_technique.py <file.ibt> --track <track-id> -o weeks/weekXX/assets/[datetime]-technique.json
   ```
7. **Generate visualizations**:
   ```bash
   # Consistency heatmap
   uv run python tools/viz/consistency_heatmap.py <file.ibt> --track <track-id> -o weeks/weekXX/assets/[datetime]-consistency-heatmap.png
   
   # Lap evolution chart
   uv run python tools/viz/lap_evolution_chart.py weeks/weekXX/assets/[datetime]-session.json -o weeks/weekXX/assets/[datetime]-lap-evolution.png
   ```
8. Write the session markdown file: `weeks/weekXX/[datetime]-[track]-[session-type].md`
9. **Include visualizations in the report** (see template below)
10. Update `learning_memory.json` with new findings
11. Check for guidebook updates (see `.cursor/rules/guidebook-workflow.mdc`)
12. Move IBT file to `/data/processed/[datetime]-[track]-[session-type].ibt`

**Important Notes:**
- If IBT file is missing, ask the user to provide it
- If `learning_memory.json` doesn't exist, create it (see `/update-learning-memory.md`)
- **Always ask Master Lonn for his thoughts BEFORE diving into analysis**
- **Use corner-specific language** (T1, T2, etc.) from track data file

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

### Consistency Heatmap

![Consistency Heatmap]([relative path to consistency-heatmap.png])

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

# Consistency heatmap visualization
uv run python tools/viz/consistency_heatmap.py <file.ibt> --track <track-id> -o output.png

# Lap evolution chart (from session JSON)
uv run python tools/viz/lap_evolution_chart.py <session.json> -o output.png
```

**Track IDs** (for --track flag):

- `oschersleben-gp`
- `winton-national`
- `rudskogen`
- `lime-rock-gp`
- `jefferson-circuit`
- etc. (check `tracks/track-data/` for available IDs)

---

## Workflow Summary

```
1. Find IBT file in /data/
2. Ask Master Lonn: "How did it feel? What's the G61 link?"
3. Run: extract_session_from_ibt.py → session.json
4. Run: analyze_ibt_technique.py → technique.json
5. Run: consistency_heatmap.py → heatmap.png
6. Run: lap_evolution_chart.py → evolution.png
7. Write session markdown (include images!)
8. Update learning_memory.json
9. Move IBT to /data/processed/
```

That's the whole flow. No G61 CSV exports needed. 🎯
