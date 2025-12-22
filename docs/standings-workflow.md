# Season Standings Analysis Workflow

Complete guide to tracking your season progression with statistical analysis.

---

## 🗓️ Weekly Workflow

### After Each Race Week Ends (Sunday/Monday)

```
1. Download CSV from iRacing
   ↓
2. Move to week folder
   ↓
3. Generate weekly report
   ↓
4. (Optional) Compare to previous week
   ↓
5. (Optional) Update progression charts
```

---

## 🛠️ Tool Arsenal

### Tool 1: Weekly Report Generator
**File:** `tools/coach/generate_weekly_standings_report.py`

**Purpose:** Your main weekly analysis tool

**When to use:** After EVERY race week (required)

**What it does:**
- Shows your current position and percentile rankings
- Tracks iRating from starting 1238
- Analyzes your division performance
- Compares to Dutch drivers
- Shows statistical correlations
- Sets short/mid/long-term goals

**Command:**
```bash
uv run python tools/coach/generate_weekly_standings_report.py <week_number> data/standings/week<XX>/season-driver_*.csv 1238
```

**Output:** `weeks/week<XX>/standings-report.md`

---

### Tool 2: Week Comparison
**File:** `tools/coach/compare_weekly_standings.py`

**Purpose:** See EXACTLY what changed between two weeks

**When to use:** When you want to understand week-over-week changes

**What it does:**
- Position changes (up/down/same)
- iRating gained per race
- New wins/poles
- Percentile shifts
- Incident rate trends
- Performance insights

**Command:**
```bash
uv run python tools/coach/compare_weekly_standings.py \
    data/standings/week01/season-driver_*.csv \
    data/standings/week02/season-driver_*.csv \
    981717
```

**Output:** JSON with detailed comparison (pipe to file or use in reports)

**Example Use Cases:**
- "Did my iRating gain accelerate or slow down?"
- "Which metrics improved most this week?"
- "Am I gaining or losing ground in my division?"

---

### Tool 3: Progression Visualizations
**File:** `tools/coach/visualize_standings_progression.py`

**Purpose:** See trends and patterns visually

**When to use:** After 2+ weeks when you want to spot trends

**What it does:**
- iRating trajectory chart with trend line
- Position climb visualization
- Percentile progression across metrics
- Summary report with all charts

**Command:**
```bash
# Multiple weeks
uv run python tools/coach/visualize_standings_progression.py \
    data/standings/week01 \
    data/standings/week02 \
    data/standings/week03
```

**Output:** 
- `weeks/progression/irating_progression.png`
- `weeks/progression/position_climb.png`
- `weeks/progression/percentile_progression.png`
- `weeks/progression/progression-report.md`

**Learning Focus:**
- Momentum: Is your improvement accelerating or plateauing?
- Consistency: Smooth climb or volatile swings?
- Weak spots: Which percentiles are lagging?
- Goals: What's your realistic trajectory?

---

### Tool 4: Rival Tracking (Optional)
**File:** `tools/coach/track_rivals.py`

**Purpose:** Compare yourself to specific competitors

**When to use:** When you want competitive context

**What it does:**
- Tracks gaps to specific drivers
- iRating, position, wins, incidents comparison
- Division differences
- Insights on where you stand

**Command:**
```bash
uv run python tools/coach/track_rivals.py \
    data/standings/week01/season-driver_*.csv \
    981717 \
    <rival_custid>
```

**Example Rivals:**
- Roel de Fouw (209147) - Top Dutch driver, P16 overall
- Division leaders - See who's ahead in your div
- Friends/competitors - Track friendly rivalries

---

## 📊 Workflow Examples

### Scenario 1: Week 01 Complete

```bash
# 1. Move downloaded CSV
mkdir -p data/standings/week01
mv ~/Downloads/season-driver_*.csv data/standings/week01/

# 2. Generate report
uv run python tools/coach/generate_weekly_standings_report.py 1 data/standings/week01/season-driver_*.csv 1238

# 3. Read report
cat weeks/week01/standings-report.md
```

**Result:** Full Week 01 analysis saved

---

### Scenario 2: Week 02 Complete (with comparison)

```bash
# 1. Move CSV
mkdir -p data/standings/week02
mv ~/Downloads/season-driver_*.csv data/standings/week02/

# 2. Generate Week 02 report
uv run python tools/coach/generate_weekly_standings_report.py 2 data/standings/week02/season-driver_*.csv 1238

# 3. Compare Week 01 vs Week 02
uv run python tools/coach/compare_weekly_standings.py \
    data/standings/week01/season-driver_*.csv \
    data/standings/week02/season-driver_*.csv \
    981717 > weeks/week02/comparison-week01-vs-week02.json

# 4. Read comparison
cat weeks/week02/comparison-week01-vs-week02.json | jq .summary
```

**Result:** Week 02 report + detailed comparison

---

### Scenario 3: Mid-Season Review (Week 04)

```bash
# 1. Generate Week 04 report (as usual)
uv run python tools/coach/generate_weekly_standings_report.py 4 data/standings/week04/season-driver_*.csv 1238

# 2. Create progression visualizations
uv run python tools/coach/visualize_standings_progression.py \
    data/standings/week01 \
    data/standings/week02 \
    data/standings/week03 \
    data/standings/week04

# 3. Review progression report
open weeks/progression/progression-report.md
```

**Result:** Full season trajectory with visual trends

---

## 🎯 What to Look For

### Weekly Report
- ✅ Are you above division average in iRating, points, incidents?
- ✅ Which percentiles are your strengths? (90%+)
- ✅ Which need improvement? (<50%)
- ✅ How far to next goal? (e.g., 69 points to 75th %ile)

### Week Comparison
- ✅ Did you gain more iRating/race than last week?
- ✅ Are your percentile rankings improving?
- ✅ Is incident rate stable or improving?
- ✅ Position change matches effort? (more races = more gain)

### Progression Charts
- ✅ Is iRating trend line going up consistently?
- ✅ Any sudden drops to investigate?
- ✅ Which metrics are plateauing?
- ✅ Are you on track for season goals?

---

## 🚀 Season Goals (Based on Data)

**From Week 01 Analysis:**

### Short-term (Next 2 weeks)
- More races (2 starts → 6+ starts)
- Maintain 3.5 inc/race (elite level)
- Target avg finish < 3.5

### Mid-term (Rest of season)
- Break 1446 iRating (75th percentile) - Currently 69 points away
- Top 500 overall - Currently P704
- Division 6-7 promotion

### Long-term (Next season)
- Top 100 overall
- Division 3-4
- 2000+ iRating (elite tier)

---

## 💡 Pro Tips

1. **Download standings AFTER week officially ends** (Sunday night/Monday)
2. **Keep iRacing filename format** - tools auto-detect data
3. **Generate report immediately** - Don't wait, track while fresh
4. **Compare every 2-3 weeks** - Too frequent = noise, too rare = miss trends
5. **Visualize at milestones** - Mid-season, end-season reviews
6. **Track rivals sparingly** - Only when competitive context helps

---

## 📁 File Organization

```
data/standings/
├── week01/
│   └── season-driver_*.csv
├── week02/
│   └── season-driver_*.csv
└── ...

weeks/
├── week01/
│   └── standings-report.md
├── week02/
│   ├── standings-report.md
│   └── comparison-week01-vs-week02.json
└── progression/
    ├── irating_progression.png
    ├── position_climb.png
    ├── percentile_progression.png
    └── progression-report.md
```

---

## 🔧 Troubleshooting

### "No standings CSV found"
- Make sure file is in `data/standings/week<XX>/` folder
- Check filename starts with `season-driver_`

### "Driver not found"
- Verify custid is correct (981717)
- Make sure you've completed at least 1 race that week

### "Not enough data for visualizations"
- Need at least 1 week for charts
- Progression charts work best with 3+ weeks

### Charts won't generate
- Check matplotlib is installed: `uv add matplotlib`
- Verify `weeks/progression/` folder exists

---

**Questions?** Check the tool source code - each file has detailed documentation!

