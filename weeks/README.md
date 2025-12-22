# Weeks Directory Structure

This directory contains all your session data, reports, and visualizations organized by week.

## 📁 Organization Pattern

```
weeks/
├── week01/
│   ├── assets/                          ← All charts/images here!
│   │   ├── irating_distribution_ranges.png
│   │   └── irating_distribution_histogram.png
│   ├── standings-report.md              ← Markdown reports
│   ├── 2025-12-11-session.md
│   └── README.md
├── week02/
│   ├── assets/
│   │   └── (charts generated here)
│   ├── standings-report.md
│   └── ...
└── progression/
    ├── assets/                          ← Multi-week progression charts
    │   ├── irating_progression.png
    │   ├── position_climb.png
    │   └── percentile_progression.png
    └── progression-report.md
```

## 🎨 Why Assets Folders?

**Clean Separation:**
- Markdown files stay at the top level (easy to find)
- Charts/images grouped in `assets/` subdirectory (visual clutter hidden)
- Clear separation between content and visuals

**Better Organization:**
- Week folders don't get cluttered with PNGs
- Easy to `.gitignore` assets if needed
- Professional project structure

**Markdown Simplicity:**
- Reference images: `![Chart](assets/chart.png)`
- All charts in one predictable location

## 📊 Visualization Types

### Per-Week Charts (in `week<XX>/assets/`)
- **iRating Distribution (Ranges):** Bar chart showing where you sit in the field
- **iRating Distribution (Histogram):** Detailed distribution with percentiles

### Multi-Week Charts (in `progression/assets/`)
- **iRating Progression:** Your rating climb over the season
- **Position Climb:** Standings position change week-by-week
- **Percentile Rankings:** Track your percentiles across multiple metrics

## 🛠️ Auto-Generation

All visualization tools automatically create and use the `assets/` subdirectory:

```bash
# iRating distribution charts → weeks/week01/assets/
uv run python tools/coach/visualize_irating_distribution.py \\
    data/standings/week01/*.csv 981717 weeks/week01

# Progression charts → weeks/progression/assets/
uv run python tools/coach/visualize_standings_progression.py \\
    data/standings/week01 data/standings/week02
```

No manual directory creation needed - the tools handle it! 🚀

## 📝 Report References

Markdown reports reference their charts using relative paths:

```markdown
![iRating Distribution](assets/irating_distribution_ranges.png)
```

This keeps reports portable and clean.

---

**Keep it clean, Master!** 🧹📊

