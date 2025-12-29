---
name: week-summary
description: Generate engaging week summary with consistency checks
---

# Week Summary Generator

When the user asks to "summarize the week" or "create week summary" or "week recap":

## 1. Consistency Checks

First, run these checks across ALL session files in the specified week directory:

### Timeline Anomalies

- [ ] Check for "202[34]" (wrong years)
- [ ] Check for "year ago", "1 year", "year off", "year-long" (should be specific months)
- [ ] Verify all dates are in 2025

### PB Reference Anomalies

- [ ] Check for "1:28.762" (open-setup PB - should use same-series PB 1:28.969)
- [ ] Check for inconsistent gap calculations
- [ ] Verify all PB references match current target

### Emphasis Anomalies (per handbook)

- [ ] Check for **BOLD CAPS SENTENCES** (too much shouting)
- [ ] Check for excessive **BOLD** usage
- [ ] Verify emphasis follows handbook guidelines

### Terminology Anomalies

- [ ] Check for "MULTIPLAYER" or "multiplayer race" (should be "Race" vs "AI Race")
- [ ] Check session type consistency

## 2. Week Analysis

Gather from all session files in the week:

### Sessions

- Date, time, session type for each
- Best lap, consistency (σ), clean laps, incidents
- Focus area and goals for each session

### Progress Metrics

- Starting lap time vs ending lap time
- Starting consistency vs ending consistency
- Sector improvements (if applicable)
- Gap to target PB (start vs end)

### Key Moments

- Breakthroughs (identify from session notes)
- Setbacks or challenges
- Mental state evolution
- Quotes from Master Lonn

### Coaching Narrative

- What worked (coaching strategies that clicked)
- What didn't (areas still struggling)
- Pattern recognition (similar to previous weeks?)
- Next week setup (what carries forward?)

## 3. Generate README.md

Create `weeks/weekXX/README.md` with this structure:

```markdown
# Week XX - [Track Name] - Season [Season Year]

**Track**: [Track Name]  
**Car**: [Car Name]  
**Dates**: [Start Date] → [End Date]  
**Status**: [Practice / Qualifying / Race / Complete]

---

## The Story

[Engaging narrative summary - 2-3 paragraphs telling the STORY of the week]

[Use Little Padawan's voice but tone down excessive emphasis]
[Focus on the JOURNEY, not just the numbers]
[Include Master Lonn's quotes if memorable]

---

## The Numbers

| Metric               | Start     | End       | Change   | Notes          |
| -------------------- | --------- | --------- | -------- | -------------- |
| **Best Lap**         | XX:XX.XXX | XX:XX.XXX | ±X.XXXs  | [Context]      |
| **Consistency (σ)**  | X.XXs     | X.XXs     | ±X.XXs   | [Context]      |
| **Gap to Target PB** | X.XXXs    | X.XXXs    | ±X.XXXs  | [PB reference] |
| **Focus Area**       | [Area]    | [Status]  | [Change] | [Result]       |

**Week Stats:**

- **Sessions**: X (Y practice, Z races)
- **Total Laps**: XXX
- **Victories**: X (if applicable)
- **Breakthrough**: [One key technical/mental breakthrough]

---

## Session Log

| Date | Time | Type | Best Lap | σ | Result | Key Takeaway |
| :--- | :--- | :--- | :------- | :- | :----- | :----------- |
| [Links to session files with one-line summaries] |

---

## Breakthroughs 🎯

[List major breakthroughs with brief context]

- **[Breakthrough 1]**: [What happened, why it mattered]
- **[Breakthrough 2]**: [What happened, why it mattered]

---

## Challenges 🚧

[List ongoing challenges or setbacks]

- **[Challenge 1]**: [What's blocking progress]
- **[Challenge 2]**: [Strategy to overcome]

---

## What We Learned

[3-5 key insights from the week]

**Technical:**

- [Driving/setup insight]

**Mental:**

- [Psychology/mindset insight]

**Strategic:**

- [Approach/coaching insight]

---

## Next Week Preview

**Track**: [Next track name]  
**Challenge**: [What's different/new]  
**Goal**: [Primary objective]  
**Strategy**: [Approach based on this week's learnings]

---

_Week XX Complete: [Motivational closing line in Little Padawan voice]_
```

## 4. Output

After generating the README:

1. Report any anomalies found during consistency check
2. Ask if user wants to fix anomalies before finalizing
3. Confirm README has been created
4. Suggest updating `learning_memory.json` with week summary

---

## Example Usage

**User**: "Summarize week 02"

**Little Padawan**:

1. Scans `weeks/week02/*.md` files
2. Runs consistency checks → reports findings
3. Analyzes all sessions → extracts key data
4. Generates engaging narrative summary
5. Creates `weeks/week02/README.md`
6. Reports completion + any anomalies to fix

---

## Notes

- Use Little Padawan's voice but follow emphasis guidelines
- Focus on storytelling, not just data dumping
- Capture the emotional journey, not just lap times
- Make it engaging enough that Master Lonn wants to read it
- Link to individual session files for details
- Keep it concise but complete (aim for 1-2 screen scrolls)
