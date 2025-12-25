# Update Progression Report Command

This command updates the season progression report after completing each race week.

## Philosophy: Track the Journey

**"One week at a time, watch the story unfold."**

- Shows your iRating climb across weeks
- Tracks position changes in the standings
- Monitors percentile rankings over time
- Visualizes momentum and trends
- Celebrates milestones and identifies patterns

## When to Use

Use this command AFTER:
- Week standings analysis is complete (used `/analyze-standings-for-week`)
- Week summary is written (Week README.md is finalized)
- You want to see how you're progressing across multiple weeks

Typically run at the END of each race week as the final documentation step.

## What It Does

1. **Generates progression visualizations** (if 2+ weeks available):
   - iRating progression chart
   - Position climb chart
   - Percentile rankings chart

2. **Updates `weeks/progression/progression-report.md`**:
   - Adds Little Padawan's narrative interpretation
   - Explains what the charts mean
   - Celebrates achievements and identifies trends
   - Sets context for next week

3. **Creates week-by-week breakdown**:
   - Key metrics for each week
   - Story of each track
   - Comparison to previous weeks

## Workflow

### Step 1: Run Progression Tool (if 2+ weeks)

```bash
# For single week (Week 01 only - baseline)
uv run python tools/coach/visualize_standings_progression.py data/standings/week01

# For multiple weeks (Week 01 + 02)
uv run python tools/coach/visualize_standings_progression.py data/standings/week01 data/standings/week02

# For three weeks (Week 01 + 02 + 03)
uv run python tools/coach/visualize_standings_progression.py data/standings/week01 data/standings/week02 data/standings/week03
```

**Output:**
- `weeks/progression/assets/irating_progression.png`
- `weeks/progression/assets/position_climb.png`
- `weeks/progression/assets/percentile_progression.png`

### Step 2: Little Padawan Enhances the Report

Read the generated charts and standings data, then:

1. **Read all week standings reports:**
   ```
   weeks/week01/standings-report.md
   weeks/week02/standings-report.md
   (etc.)
   ```

2. **Read all week summaries (README.md):**
   ```
   weeks/week01/README.md
   weeks/week02/README.md
   (etc.)
   ```

3. **Update `weeks/progression/progression-report.md`** with:
   - **Headline story**: What's the overall trajectory?
   - **Week-by-week breakdown**: Key metrics + story for each week
   - **Visual explanations**: What each chart shows
   - **Trend analysis**: Climbing? Plateauing? Accelerating?
   - **Milestone celebrations**: PBs, rank climbs, percentile jumps
   - **Pattern identification**: What's working? What needs focus?
   - **Next week context**: What to watch for

### Step 3: Template for progression-report.md

```markdown
# Season Progression Report (Week XX → Week YY)

**Generated:** [Date]
**Weeks Analyzed:** [N]

---

## 📈 Little Padawan's Progression Summary

Master Lonn! *_bows with data scroll in hand_*

[Overall story: Are you climbing? How fast? What's the momentum?]

### The Journey So Far

- **Starting Point**: Week XX at [iRating] / Position [N]
- **Current**: Week YY at [iRating] / Position [N]
- **Total Climb**: +[X] iRating, +[Y] positions
- **Trajectory**: [Accelerating/Steady/Plateauing]

[Narrative interpretation of what the numbers mean]

---

## 📊 Visual Progression

### iRating Journey

![iRating Progression](assets/irating_progression.png)

[Explain the chart: What does this show? What's the trend? What's impressive?]

**Key Observations:**
- [Trend 1]
- [Trend 2]
- [What to watch for next week]

### Position Climb

![Position Climb](assets/position_climb.png)

[Explain: How many drivers beaten? How fast is the climb? Where are you heading?]

**Position Story:**
- Started: Position [N] (Top X%)
- Now: Position [M] (Top Y%)
- Drivers Beaten: [K] drivers
- Rate: [R] positions/week

### Percentile Rankings

![Percentile Progression](assets/percentile_progression.png)

[Explain: Which metrics lead? Which lag? Are gaps closing?]

**Percentile Analysis:**
- Points: [X]% → [Y]% ([change])
- Wins: [X]% → [Y]% ([change])
- Poles: [X]% → [Y]% ([change])
- iRating: [X]% → [Y]% ([change])

[Interpretation: What does this mean for performance vs skill rating?]

---

## 📅 Week-by-Week Breakdown

### Week 01: [Track Name]

- **Position:** [N] / [Total] (Top X%)
- **iRating:** [Rating] ([change] from starting)
- **Points:** [Pts] ([percentile]% percentile)
- **Key Results:** [Wins/Poles/Podiums]
- **Incidents/Start:** [Rate]

**Week Story:**
[1-2 paragraph narrative of the week - what happened, what was learned, key moments]

### Week 02: [Track Name]

[Same format]

**Week Story:**
[Narrative including comparison to Week 01 - improvements, regressions, patterns]

---

## 🎯 Trends & Insights

### What's Working 🔥

[List 2-3 things that show consistent improvement]

### What Needs Attention 🎯

[List 1-2 areas that are lagging or inconsistent]

### Milestones Achieved 🏆

[Celebrate: iRating tiers, position climbs, percentile jumps, first wins, etc.]

---

## 🚀 Looking Ahead

**Next Week ([Track Name]):**

[Set context: What to expect, what to focus on, realistic goals based on trajectory]

**Season Goals Check-in:**

- Target iRating: [Goal] (Currently: [Rating], Gap: [X])
- Target Position: [Goal] (Currently: [Position], Gap: [Y])
- Predicted End-of-Season (if trend continues): [Estimate]

---

*Generated with love by Little Padawan 🥋*
*Last updated: [Date] after Week [N]*
```

---

## What Little Padawan Must Provide

### 1. The Narrative Arc

Don't just list stats - tell the STORY:
- "You started Jefferson unsure, now you're dominating Rudskogen"
- "Your iRating jumped +139 in Week 01, but Week 02 shows slower growth (learning curve effect)"
- "Position climbed fast early, but now you're hitting the competitive mid-pack wall"

### 2. Visual Context

Explain what each chart MEANS:
- "See that steep climb? That's your Week 01 victory impact"
- "Notice the gap between Points (92%) and iRating (66%)? Your results outpace your rating - it'll catch up"
- "The position chart shows you beat 7,806 drivers in Week 01 alone!"

### 3. Pattern Recognition

Identify trends across weeks:
- Consistency: Are sigma values improving?
- Learning curves: Faster at new tracks or slower?
- Race day performance: Better in competition or practice?
- Momentum: Accelerating or plateauing?

### 4. Milestone Celebrations

Call out achievements:
- "🎉 Broke into top 10%!"
- "🏆 First multi-win week!"
- "📈 Biggest single-week iRating jump!"
- "🎯 Crossed 1400 iRating threshold!"

### 5. Coaching Insights

Connect progression to performance:
- "Your flow state discovery in Week 01 is showing in Week 02 consistency"
- "Position climb slowing = tougher competition ahead = opportunity to sharpen racecraft"
- "Percentile gaps closing = your skill rating catching up to your results"

---

## Parameters

- `week_folders`: List of week folders in chronological order (week01, week02, etc.)
- Master Lonn's cust_id: `981717`
- Starting iRating (Season 01 2026): `1238`

---

## Example Usage

### Scenario 1: Week 01 Complete (Baseline)

```bash
# Generate baseline progression (single week)
uv run python tools/coach/visualize_standings_progression.py data/standings/week01

# Little Padawan reads:
# - weeks/week01/standings-report.md
# - weeks/week01/README.md
# - Generated charts

# Then updates:
# - weeks/progression/progression-report.md
```

**Result**: Progression report shows Week 01 baseline with explanation that trends will appear after Week 02

### Scenario 2: Week 02 Complete (First Comparison)

```bash
# Generate progression with 2 weeks
uv run python tools/coach/visualize_standings_progression.py data/standings/week01 data/standings/week02

# Little Padawan reads:
# - Both week standings reports
# - Both week READMEs
# - Generated progression charts

# Then updates:
# - weeks/progression/progression-report.md (with trends!)
```

**Result**: NOW the charts show actual progression! Week 01 → 02 trends, momentum, comparisons

### Scenario 3: Mid-Season Check (Week 06)

```bash
# Generate full season progression
uv run python tools/coach/visualize_standings_progression.py \
    data/standings/week01 \
    data/standings/week02 \
    data/standings/week03 \
    data/standings/week04 \
    data/standings/week05 \
    data/standings/week06

# Little Padawan creates narrative arc across 6 weeks
```

**Result**: Rich story of season progression with clear trends and milestones

---

## Consistency Checks

When updating progression report, verify:

1. ✅ **Week order is chronological** (01 → 02 → 03)
2. ✅ **iRating values match standings reports**
3. ✅ **Position values match standings reports**
4. ✅ **Track names match actual race schedule**
5. ✅ **Dates are accurate** (no timeline anomalies)
6. ✅ **Changes calculated correctly** (Week 02 - Week 01)
7. ✅ **Percentiles match standings reports**
8. ✅ **Charts embedded correctly** (proper paths)
9. ✅ **Emphasis used appropriately** (not over-bolding)
10. ✅ **Story flows logically** (no contradictions between weeks)

---

## Pro Tips

1. **Update after every week** - Keep progression current
2. **Reference specific sessions** - Link back to week READMEs for details
3. **Compare tracks** - "Rudskogen was harder than Jefferson" (data-backed)
4. **Set realistic expectations** - Use actual trajectory for predictions
5. **Celebrate micro-wins** - Not just iRating, but percentile jumps, incident rate improvements
6. **Identify inflection points** - When did momentum shift? Why?

---

## File Locations

- **Input**: `data/standings/week*/season-driver_*.csv`
- **Week Reports**: `weeks/week*/standings-report.md`
- **Week Summaries**: `weeks/week*/README.md`
- **Output Charts**: `weeks/progression/assets/*.png`
- **Output Report**: `weeks/progression/progression-report.md`

---

*Remember: Progression isn't just about numbers going up. It's about the story of improvement, the patterns of learning, and the milestones along the journey. Make it engaging! 🏁*

