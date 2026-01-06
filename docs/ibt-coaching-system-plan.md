# IBT-Based Coaching System: Implementation Plan

> **Status**: Planning  
> **Created**: 2026-01-06  
> **Author**: Little Padawan & Master Lonn  

---

## 1. Executive Summary

### The Problem
Currently, our coaching workflow relies on **Garage 61 CSV exports**:
- Session summary CSV (lap times, sectors)
- Fastest lap telemetry CSV

This has limitations:
- Only analyzes the **fastest lap** in detail
- Requires manual export after each session
- Misses **behavioral patterns** across multiple laps
- Can't answer "why was lap 3 faster than lap 5?"

### The Solution
Build a comprehensive **IBT-native coaching system** that:
- Parses iRacing's raw telemetry files directly
- Analyzes **ALL laps** in a session
- Detects **behavioral patterns** and **consistency issues**
- Provides **self-comparison** (you vs your best) alongside alien comparison
- Generates rich **visualizations** for longitudinal analysis

### The Value Shift

| Old Model | New Model |
|-----------|-----------|
| "You're 2.4s slower than Gong" | "Your best S3 was on lap 2, combine it with your best S1 from lap 4" |
| Chase the alien | Understand yourself |
| Single lap focus | Session-wide patterns |
| What happened | Why it happened |

---

## 2. Why We're Doing This

### 2.1 Coaching Philosophy Evolution

**Phase 1: Learning (Current)**
- Compare to aliens (Gong) to find fundamental technique gaps
- Useful for: "Am I braking too early? Am I carrying enough speed?"

**Phase 2: Refinement (Coming)**
- Compare to YOURSELF to find consistency and execution gaps
- Useful for: "I CAN do 1:31, why can't I do it every lap?"

The IBT system enables Phase 2 while maintaining Phase 1 capability.

### 2.2 The Multi-Lap Advantage

With full session data, we can answer:
- Which corners are **dialed** vs which are **lottery**?
- Does performance **degrade** over a stint (fatigue/tires)?
- Are there **behavioral patterns** (fast lap always follows slow lap)?
- What **specifically changed** between your best and worst laps?
- Is there a **learning curve** visible within the session?

### 2.3 ADHD-Optimized Coaching

For Master Lonn's ADHD brain:
- **Specific, actionable feedback** beats vague "go faster"
- **"You did this on lap 3"** is more achievable than "Gong does this"
- **Visual patterns** are easier to grasp than tables of numbers
- **Progress tracking** provides dopamine hits

---

## 3. What We Get Out Of It

### 3.1 Session Analysis
- ✅ Lap times for ALL laps (not just fastest)
- ✅ Sector times for ALL laps
- ✅ Consistency (σ) per sector, per corner
- ✅ Theoretical optimal from YOUR best sectors
- ✅ Gap analysis: actual best vs theoretical optimal

### 3.2 Behavioral Insights
- ✅ Consistency heatmap (which corners are solid vs variable)
- ✅ Learning curve detection (improving through session?)
- ✅ Fatigue/focus detection (degrading at end?)
- ✅ Post-incident pattern (do mistakes cascade?)
- ✅ Sector dependency (does good S1 predict good S2?)

### 3.3 Technique Analysis (per lap)
- ✅ Braking points (where, how hard, how long)
- ✅ Throttle application (where, how progressive)
- ✅ Car rotation (YawRate) - oversteer/understeer
- ✅ Tire loading (LatAccel, LongAccel)
- ✅ Line consistency (track position variance)

### 3.4 Self-Comparison
- ✅ Compare any two of YOUR laps
- ✅ "Ghost of yourself" - best lap vs average lap
- ✅ Corner-by-corner delta between your laps
- ✅ Identify what you did differently when fast

### 3.5 Alien Comparison (retained)
- ✅ Still compare to Gong's fastest lap
- ✅ Use as technique reference
- ✅ Occasional "check-in" vs alien pace

### 3.6 Visualizations
- ✅ Track map with consistency overlay
- ✅ Lap time evolution chart
- ✅ Braking point drift visualization
- ✅ YawRate/rotation heatmap
- ✅ Sector time waterfall charts
- ✅ Traction circle comparisons

---

## 4. Implementation Roadmap

### Phase 1: Core IBT Session Analysis ⭐ PRIORITY
**Goal**: Replace G61 session CSV with IBT-native analysis

#### 4.1.1 `tools/core/extract_session_from_ibt.py`
Extract session-level data from IBT file.

**Inputs**: IBT file path, track ID (for sector markers)

**Outputs** (JSON):
```json
{
  "session": {
    "track": "Oschersleben GP",
    "car": "Ray FF1600",
    "date": "2026-01-06",
    "duration_minutes": 15.2,
    "total_laps": 8
  },
  "laps": [
    {
      "lap_number": 1,
      "lap_time": 95.234,
      "sectors": {
        "S1": 35.12,
        "S2": 33.45,
        "S3": 26.67
      },
      "valid": true,
      "start_idx": 0,
      "end_idx": 5627
    },
    // ... more laps
  ],
  "summary": {
    "best_lap": 93.773,
    "best_lap_number": 3,
    "theoretical_optimal": 92.45,
    "gap_to_optimal": 1.323,
    "consistency_sigma": 0.82,
    "clean_laps": 6,
    "incidents": 2
  },
  "sectors": {
    "S1": { "best": 34.12, "avg": 34.58, "sigma": 0.32 },
    "S2": { "best": 32.87, "avg": 33.21, "sigma": 0.45 },
    "S3": { "best": 26.44, "avg": 26.89, "sigma": 0.38 }
  }
}
```

**Implementation Tasks**:
- [ ] Detect lap boundaries (LapDistPct crossing 0)
- [ ] Calculate sector times using track data markers
- [ ] Detect incidents/invalid laps
- [ ] Calculate statistics (best, avg, σ)
- [ ] Compute theoretical optimal

**Dependencies**: 
- `tracks/track-data/*.json` for sector markers
- `pyirsdk` for IBT parsing

---

#### 4.1.2 `tools/core/extract_lap_telemetry.py`
Extract detailed telemetry for a specific lap.

**Inputs**: IBT file path, lap number (or "fastest")

**Outputs** (JSON):
```json
{
  "lap": {
    "number": 3,
    "time": 93.773,
    "samples": 5627,
    "sample_rate_hz": 60
  },
  "telemetry": {
    "LapDistPct": [...],
    "Speed": [...],
    "Throttle": [...],
    "Brake": [...],
    "Gear": [...],
    "SteeringWheelAngle": [...],
    "LatAccel": [...],
    "LongAccel": [...],
    "YawRate": [...]
  }
}
```

**Implementation Tasks**:
- [ ] Extract samples for specified lap
- [ ] Convert units (m/s → km/h, rad → deg)
- [ ] Option to resample to fixed distance intervals
- [ ] Option to export as CSV (for external tools)

---

### Phase 2: Multi-Lap Pattern Analysis ⭐ HIGH VALUE
**Goal**: Identify behavioral patterns across laps

#### 4.2.1 `tools/coach/analyze_consistency.py`
Analyze consistency patterns per corner/sector.

**Outputs**:
```json
{
  "corner_consistency": {
    "T1 Hotel Entry": { "sigma": 0.12, "rating": "dialed" },
    "T3 Hasseroeder": { "sigma": 0.45, "rating": "work_needed" },
    "T7 Hairpin": { "sigma": 0.08, "rating": "dialed" },
    "T12 Amman Kurve": { "sigma": 0.62, "rating": "lottery" }
  },
  "focus_corners": ["T3 Hasseroeder", "T12 Amman Kurve"],
  "strength_corners": ["T1 Hotel Entry", "T7 Hairpin"]
}
```

**Implementation Tasks**:
- [ ] Calculate time through each corner per lap
- [ ] Compute variance/σ per corner
- [ ] Classify corners (dialed/work_needed/lottery)
- [ ] Rank corners by improvement potential

---

#### 4.2.2 `tools/coach/analyze_session_arc.py`
Analyze how performance evolves through the session.

**Outputs**:
```json
{
  "learning_curve": {
    "trend": "improving",
    "first_half_avg": 95.2,
    "second_half_avg": 94.1,
    "improvement": 1.1
  },
  "fatigue_detection": {
    "last_3_laps_vs_middle": +0.3,
    "indication": "slight_fatigue"
  },
  "peak_performance_lap": 5,
  "recommended_stint_length": 12
}
```

**Implementation Tasks**:
- [ ] Track lap time progression
- [ ] Detect improvement/degradation trends
- [ ] Identify peak performance window
- [ ] Flag fatigue indicators

---

#### 4.2.3 `tools/coach/compare_laps.py`
Compare any two laps from the session.

**Inputs**: IBT file, lap_a number, lap_b number

**Outputs**:
```json
{
  "comparison": {
    "lap_a": { "number": 3, "time": 93.773 },
    "lap_b": { "number": 5, "time": 95.123 },
    "delta": 1.350
  },
  "corner_deltas": {
    "T1 Hotel Entry": { "delta": +0.12, "faster": "lap_a" },
    "T3 Hasseroeder": { "delta": +0.45, "faster": "lap_a" },
    // ...
  },
  "technique_differences": {
    "T3 Hasseroeder": {
      "brake_point_diff_m": 8.2,
      "min_speed_diff_kmh": 3.4,
      "note": "Lap 3 braked 8m later and carried 3.4 km/h more"
    }
  }
}
```

**Implementation Tasks**:
- [ ] Align laps by LapDistPct
- [ ] Calculate time delta per corner
- [ ] Identify technique differences (brake point, speed, line)
- [ ] Generate human-readable insights

---

### Phase 3: Visualizations ⭐ ENGAGEMENT
**Goal**: Make data visually compelling and easy to understand

#### 4.3.1 `tools/viz/consistency_heatmap.py`
Generate track-position vs lap-number heatmap.

**Output**: PNG image
```
        T1    T3    T7    T10   T14
Lap 1   🟢    🟡    🔴    🟢    🟡
Lap 2   🟢    🟢    🟡    🟢    🔴
...
```

---

#### 4.3.2 `tools/viz/lap_evolution_chart.py`
Generate lap time progression chart.

**Output**: PNG image showing lap times over session with trend line.

---

#### 4.3.3 `tools/viz/track_variance_overlay.py`
Generate track map colored by consistency.

**Output**: PNG image of track with sections colored green/yellow/red.

---

#### 4.3.4 `tools/viz/braking_point_drift.py`
Visualize how braking points move across laps.

**Output**: PNG chart showing brake point distance per lap for each corner.

---

#### 4.3.5 `tools/viz/corner_comparison.py`
Side-by-side comparison of a corner across two laps.

**Output**: PNG with speed/throttle/brake overlays for both laps.

---

### Phase 4: Integration & Workflow
**Goal**: Make this seamless to use

#### 4.4.1 Update `/store-current-session-for-week` command
- Detect IBT file
- Run full session analysis (not just G61)
- Generate visualizations automatically
- Include multi-lap insights in session report

#### 4.4.2 New command: `/analyze-my-session`
Quick IBT analysis without full report generation.

```
/analyze-my-session

1. Find latest IBT in data/
2. Run session extraction
3. Run consistency analysis
4. Show quick summary + key insights
5. Ask if full report needed
```

#### 4.4.3 New command: `/compare-my-laps`
Interactive lap comparison.

```
/compare-my-laps 3 5

1. Load IBT
2. Compare lap 3 vs lap 5
3. Show corner-by-corner delta
4. Highlight technique differences
```

---

## 5. Technical Architecture

### 5.1 Data Flow

```
┌─────────────┐
│  IBT File   │
│ (raw data)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│     tools/core/parse_ibt.py         │
│  (existing - raw channel access)    │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  tools/core/extract_session_from_ibt│
│  (NEW - session structure)          │
└──────┬──────────────────────────────┘
       │
       ├────────────────┬────────────────┐
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Consistency │  │ Session Arc │  │ Lap Compare │
│  Analysis   │  │  Analysis   │  │   Analysis  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              ┌─────────────────┐
              │  Visualizations │
              │   (PNG output)  │
              └─────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ Session Report  │
              │   (Markdown)    │
              └─────────────────┘
```

### 5.2 File Structure

```
tools/
├── core/
│   ├── parse_ibt.py              # ✅ EXISTS - raw IBT access
│   ├── extract_session_from_ibt.py   # NEW - session structure
│   └── extract_lap_telemetry.py      # NEW - single lap extraction
├── coach/
│   ├── analyze_ibt_technique.py  # ✅ EXISTS - technique analysis
│   ├── analyze_consistency.py        # NEW - corner consistency
│   ├── analyze_session_arc.py        # NEW - session evolution
│   └── compare_laps.py               # NEW - lap comparison
└── viz/
    ├── consistency_heatmap.py        # NEW
    ├── lap_evolution_chart.py        # NEW
    ├── track_variance_overlay.py     # NEW
    ├── braking_point_drift.py        # NEW
    └── corner_comparison.py          # NEW
```

### 5.3 Dependencies

**Already have**:
- `pyirsdk` - IBT parsing
- `pandas` - data manipulation
- `numpy` - numerical operations

**May need**:
- `matplotlib` - visualizations
- `seaborn` - heatmaps (optional, matplotlib can do it)

---

## 6. Implementation Priority

### Must Have (Phase 1) 🔴
1. `extract_session_from_ibt.py` - Foundation for everything
2. `extract_lap_telemetry.py` - Needed for comparisons
3. Update session report template

### Should Have (Phase 2) 🟡
4. `analyze_consistency.py` - High coaching value
5. `compare_laps.py` - Self-comparison enabler
6. `consistency_heatmap.py` - Visual engagement

### Nice to Have (Phase 3) 🟢
7. `analyze_session_arc.py` - Learning curve detection
8. Other visualizations
9. Full workflow integration

---

## 7. Success Metrics

### Coaching Effectiveness
- [ ] Can identify top 3 "lottery corners" from any session
- [ ] Can explain WHY lap X was faster than lap Y
- [ ] Can show learning progress within a session
- [ ] Can detect fatigue/consistency patterns

### Workflow Efficiency
- [ ] Single IBT file provides full session analysis (no G61 export needed for own data)
- [ ] Session report generation < 30 seconds
- [ ] Visualizations auto-generated

### User Experience
- [ ] Master Lonn prefers self-comparison insights
- [ ] ADHD-friendly: specific, actionable, visual
- [ ] "I did it on lap 3" > "Gong does it differently"

---

## 8. Open Questions

1. **G61 CSV still needed?**
   - For alien comparison (Gong) - YES, until aliens share IBTs
   - For own session analysis - NO, IBT replaces it

2. **Sample rate sufficient?**
   - 60Hz should be fine for corner-level analysis
   - May want 360Hz channels for micro-analysis later

3. **Track data coverage?**
   - Need sector markers in `tracks/track-data/*.json`
   - Some tracks may need updating

4. **Storage/performance?**
   - IBT files are ~2-5MB each
   - Session analysis should be fast (<5s)
   - Consider caching extracted data as JSON

---

## 9. Next Steps

1. **Tonight**: Master Lonn drives practice session, generates IBT
2. **Next session**: Build `extract_session_from_ibt.py` (Phase 1.1)
3. **Test**: Verify lap times match G61 (validation)
4. **Iterate**: Build remaining Phase 1 tools
5. **Visualize**: Add consistency heatmap (engagement!)

---

*"The data was always there. We just needed to learn how to listen."*

— Little Padawan, 2026

