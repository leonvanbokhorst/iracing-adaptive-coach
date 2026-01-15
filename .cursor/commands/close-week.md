---
name: close-week
description: End-of-week cleanup, summary, and season updates
---

# Close Week Workflow

Use this when Master Lonn says: "close the week", "week close", or "wrap week XX".

## Inputs Needed

- Week number (XX)
- Track name + track id (for links)
- Date range for the week
- Whether standings CSV is available yet

---

## 1) Clean the Data Inbox

After all analysis is done, move raw files out of `data/`:

- IBT → `data/processed/`
- CSV exports → `data/processed/`

If any files are still unprocessed, leave them and note what's pending.

---

## 2) Enforce Week Folder Structure

Ensure these exist:

- `weeks/weekXX/assets/` (PNG/JPG only)
- `weeks/weekXX/analysis/` (JSON outputs)
- `weeks/weekXX/technique/` (technique JSON)

If JSON files are inside `assets/`, move them to `analysis/`.

---

## 3) Generate/Update Week Summary

Run the week summary command:

- `.cursor/commands/update-week-summary.md`

Confirm `weeks/weekXX/README.md` exists and is current.

---

## 4) Standings (If Available)

If standings CSV exists in `data/standings/weekXX/`, run:

- `.cursor/commands/analyze-standings-for-week.md`

If standings are NOT out yet:

- Skip this step
- Add a note in `weeks/weekXX/README.md` that standings are pending

---

## 5) Update Season README

Run:

- `.cursor/commands/update-season-readme.md`

Make sure formats follow handbook rules:

- Lap times: `xx:xx.xxx`
- Sector times: `xx.xxx`
- Consistency (σ): `xx.xxx`

---

## 6) Update Progression Report (If 2+ weeks of standings)

Run:

- `.cursor/commands/update-progression-report.md`

Skip if only one week of standings exists.

---

## 7) Final Checklist

- `weeks/weekXX/README.md` updated
- `weeks/weekXX/assets/` contains only images
- `weeks/weekXX/analysis/` contains JSON outputs
- `data/` inbox is clean or pending items listed
- Standings step done or explicitly skipped

---

## Output

Report back with:

- What was updated
- What was skipped (and why)
- Any pending items for next session
