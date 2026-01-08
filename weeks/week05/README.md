# Week 05 - Motorsport Arena Oschersleben - Season 01 2026

**Track**: [Motorsport Arena Oschersleben - Grand Prix](../../tracks/track-motorsport-arena-oschersleben-grand-prix.md)  
**Car**: [Ray FF1600](../../cars/car-ray-ff1600.md)  
**Dates**: Jan 6 → Jan 12, 2026  
**Status**: Racing 🏁

---

## The Story

There's a particular cruelty to Oschersleben. It sits there on the German plain—flat, featureless, honest—and asks one question over and over: *can you hit your marks?*

Master Lonn showed up on January 6th with an advantage and a problem. The advantage: he'd driven this track before in the GR86. The layout was in his bones. The problem: the FF1600 isn't a GR86. Same corners, different language.

The first session was promising. A 1:33.818 baseline, only 0.037s off the theoretical optimal. The raw pace was there. But lurking in Sector 1 was a nemesis waiting to introduce itself: **T2 Hotel Exit**—a long, decreasing-radius, downhill corner where GR86 muscle memory goes to die.

Session 2 revealed the scale of the problem. Three separate incidents at T2. Lap times swinging by 7 seconds. The variance at that one corner: **2.257 seconds**. A lottery. *"I remember that being a strange corner from my GR86 times,"* Master Lonn admitted. Strange was an understatement.

But something remarkable happened over the next 48 hours. Instead of chasing speed, Master Lonn chased consistency. *"Hit the same mark ten times"* became the mantra. And the data responded. T2 variance plummeted—90% improvement in one session. The corner went from lottery to learnable.

By Practice 03, the fear had left the building. *"Hotel is still shaky, but not scary."* A new PB: **1:33.167**. Zero incidents. The strange corner was becoming familiar.

Then came the real test: **AI Race 01**. Grid position P6. Cold Tire Contract activated. Laps 3-6 stuck behind traffic—patient, waiting, refusing to send it into gaps that weren't there. Then clear air on Lap 7. Attack mode. Final lap? **1:33.983**—the fastest lap of the race, on the lap that mattered most.

**P6 → P1.** Cold Tire Contract Win #5.

And here's what made the data sing: T2 Hotel Exit variance in the race? **σ 0.066s**. Not shaky. Not solid. **DIALED**. The nemesis corner, conquered under race pressure.

---

## The Numbers

| Metric               | Start (Practice 01) | End (AI Race 01) | Change    | Notes                          |
| -------------------- | ------------------- | ---------------- | --------- | ------------------------------ |
| **Best Lap**         | 1:33.818            | 1:33.167 (PB)    | **-0.651s** | Practice PB; race best 1:33.983 |
| **Consistency (σ)**  | 0.38s               | 0.40s / 0.97s    | ✅ Stable  | Practice / Race (traffic)      |
| **T2 Hotel Exit σ**  | N/A                 | 0.066s           | **DIALED** | Was 2.257s lottery in P02      |
| **Gap to Alien**     | 2.42s               | 1.77s            | **-0.65s** | vs Gong (1:31.396)             |
| **Incidents**        | 4                   | 0                | **-4**     | First clean sessions           |

**Week Stats:**

- **Sessions**: 4 (3 practice, 1 AI race)
- **Total Laps**: 45+
- **Victories**: 1 (P6→P1) 🏆
- **Breakthrough**: T2 Hotel Exit mastered—97% variance reduction across 3 sessions

---

## Session Log

| Date       | Time  | Type         | Best Lap     | σ      | Result   | Key Takeaway                           |
| :--------- | :---- | :----------- | :----------- | :----- | :------- | :------------------------------------- |
| 2026-01-06 | 13:45 | [Practice 01](2026-01-06-13-45-Oschersleben-Practice-01-Baseline.md) | 1:33.818 | 0.38s | Baseline | GR86 layout memory + Gong comparison   |
| 2026-01-06 | 18:18 | [Practice 02](2026-01-06-18-18-Oschersleben-Practice-02.md) | 1:33.333 🏆 | 2.84s | PB! | T2 = lottery (σ 2.257s), but learning visible |
| 2026-01-07 | 18:07 | [Practice 03](2026-01-07-18-07-Oschersleben-Practice-03.md) | 1:33.167 🏆 | 0.40s | PB! | T2 tamed (σ 0.231s), zero incidents    |
| 2026-01-08 | 10:21 | [AI Race 01](2026-01-08-10-21-Oschersleben-AI-Race-01.md) | 1:33.983 | 0.97s | **P6→P1** 🏆 | T2 DIALED (σ 0.066s), Cold Tire Contract #5 |

---

## Breakthroughs 🎯

### T2 Hotel Exit: From Lottery to Dialed

| Session     | T2 σ     | Status    |
| :---------- | :------- | :-------- |
| Practice 02 | 2.257s   | 🎰 Lottery |
| Practice 03 | 0.231s   | 🟡 Solid   |
| AI Race 01  | **0.066s** | ✅ **DIALED** |

**97% variance reduction.** The corner that was causing +7s incidents became a repeatable 7.5s passage. And it happened by focusing on consistency, not speed. Speed followed.

### Cold Tire Contract v2.0: Win #5

The race arc tells the story:

| Lap | Time       | Mode     |
| :-: | :--------: | :------- |
| 1   | 1:39.733   | Outlap/chaos |
| 2   | 1:34.667   | Survival |
| 3-6 | 1:35-1:36  | Patient (stuck behind traffic) |
| 7   | 1:34.867   | Attack (clear air) |
| 8   | **1:33.983** | **Victory lap (fastest!)** |

Four laps of patience. Then the kill. Fastest lap on the final lap. Ice cold.

---

## Challenges 🚧

- **T12 Amman Kurve**: Only corner flagged as "work_needed" in the race (σ 0.276s)
- **S3 Race Variance**: σ 0.67s in race vs 0.055s in practice—traffic management, not skill
- **1:33.0 Barrier**: Still unbroken (PB 1:33.167, need 0.167s more)
- **Gap to Alien**: 1.77s to Gong—braking and throttle deployment, not cornering

---

## What We Learned

**Technical:**

- **T2 Hotel Exit Technique**: The VRS wisdom—*"Turn first, brake second. Initial brake 25-30% only. Reserve heavy braking for AFTER the T1 kink."* GR86 muscle memory was causing over-braking too early.
- **Consistency-First Produces Speed**: Practice 03 goal was ONLY consistency. Result: PB anyway, zero incidents. Repeatability unlocks speed.

**Mental:**

- **"Shaky but not scary"** is the correct intermediate state. Fear prevents learning. Shakiness allows adaptation.
- **Patience in traffic pays**: L3-L6 stuck behind someone, didn't force it. L7-L8 clear air, delivered fastest laps.

**Strategic:**

- **IBT-Only Workflow Validated**: No G61 CSV exports needed anymore. IBT provides all session data.
- **Oschersleben Overtaking**: Main straight into T1-T2 is THE spot. Requires clean T14 Zeppelin exit → slipstream → late brake.

---

## Next: Continue Week 05

**Challenge**: Break 1:33.0 barrier (need -0.167s from PB)  
**Focus**: T12 Amman Kurve consistency, maintain T2 discipline  
**Strategy**: Same approach—consistency first, speed follows  
**Goal**: Official race ready, deploy Cold Tire Contract

---

## Contracts Active

| Contract                  | Status      | Notes                              |
| :------------------------ | :---------- | :--------------------------------- |
| **Cold Tire Contract v2.0** | ✅ Win #5   | Survive L1-L3, attack L4+          |
| **Meebewegen**            | ✅ Active   | Patience in L3-L6 → victory        |
| **Edge Mapping Drill**    | ✅ Applied  | T2 spatial calibration complete    |
| **Zero Incident Discipline** | ✅ Active | 2 consecutive clean sessions       |

---

_"The Hotel stopped being a horror movie. The strange corner is becoming familiar."_ 🏨🏎️
