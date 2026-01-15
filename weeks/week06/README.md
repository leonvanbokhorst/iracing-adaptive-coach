# Week 06 - Oran Park Raceway GP - Season 01 2026

**Track**: [Oran Park Raceway - Grand Prix](../../tracks/track-oran-park-raceway-grand-prix.md)  
**Car**: [Ray FF1600](../../cars/car-ray-ff1600.md)  
**Dates**: January 15–21, 2026  
**Status**: 🔄 In Progress

---

## The Story

The track bit first.

Champion Curve—a blind entry climbing into a tightening radius—and Foster's Dip—where the elevation drops away mid-corner—weren't asking if Master Lonn belonged. They were telling him he didn't. Not yet.

Multiple offs. Multiple spins. A 3-second swing at Champion Curve alone. The "ups and downs" Master Lonn mentioned? The data showed exactly what he meant: 8.5 seconds on one lap, 5.5 seconds the next. Lottery. Pure lottery.

And yet.

Lap 14: **1:12.583**. Five seconds faster than Lap 1. In 23 minutes. After the offs. After the spins. The PB came *because* he pushed, found the limits, got bitten, and kept going.

Then the alien arrived.

Shuning Gong. **1:09.856**. A 2.7-second gap that lived almost entirely in the corners—not the straights. The telemetry didn't lie: Master Lonn was slower on **96.3%** of the lap. The deepest red? The Sweeper. **-23 km/h**.

*"You're braking 75% of that corner. Gong brakes 42%."*

The Sweeper isn't a brake zone. It's a lift zone. Gong carries 160+ km/h through. Master Lonn was treating it like Turn 2 at Oschersleben—heavy braking before a tight corner. But this isn't a tight corner. It's a fast sweeper into Coca-Cola.

The path to 1:11 is clear: stop braking where braking isn't needed.

---

## The Numbers

| Metric | Start | Current | Change | Notes |
| :----- | :---- | :------ | :----- | :---- |
| **Best Lap** | — | 1:12.583 | — | Baseline established |
| **Consistency (σ)** | — | 1.539s | — | High variance (expected Day 1) |
| **Gap to Gong** | — | 2.727s | — | 96.3% of lap slower |
| **Corners Solid** | — | 6/9 | — | 67% dialed on first contact |

**Week Stats:**
- **Sessions**: 1 (baseline practice)
- **Total Laps**: 16
- **Offs/Spins**: Multiple (Champion Curve, Foster's Dip)
- **Key Discovery**: The Sweeper is NOT a brake zone

---

## Session Log

| Date | Time | Type | Best Lap | σ | Result | Key Takeaway |
| :--- | :--- | :--- | :------- | :- | :----- | :----------- |
| Jan 15 | 13:48 | [Practice 01](2026-01-15-13-48-oran-park-practice-01.md) | **1:12.583** | 1.539s | Baseline | Champion Curve = nemesis, Gong gap = 2.7s |

---

## Track Overview

| Metric | Value |
| :----- | :---- |
| **Location** | Narellan, New South Wales, Australia |
| **Length** | 2.60 km (1.63 mi) |
| **Corners** | 12 |
| **Sectors** | 5 |
| **Character** | Momentum playground, figure-eight with bridge |

**The Corners (12 Turns):**

| # | Corner | Apex % | Notes |
| :- | :----- | :----- | :---- |
| 1 | The Sweeper | 17% | LIFT, don't brake! -23 km/h vs Gong |
| 2 | Coca-Cola Corner | 23% | Tight right, pinches on exit |
| 3 | Shell Corner | 35% | ✅ Solid |
| 4 | Champion Curve Entry | 43% | 🎰 LOTTERY (σ 0.898s) - blind, climbing |
| 5 | Champion Curve Exit | 47% | Tightening radius, -9 km/h vs Gong |
| 6 | Yokohama Bridge | 51% | Over the bridge, figure-8 crossing |
| 7 | Foster's Dip Entry | 59% | 🎰 LOTTERY (σ 0.475s) - compression |
| 8 | Foster's Dip Exit | 64% | -2.1 km/h exit vs Gong |
| 9 | Momo Corner | 70% | ✅ Solid variance BUT -11 km/h vs Gong! |
| 10 | O'Brien Entry | 77% | Quick right into dogleg |
| 11 | O'Brien Dogleg | 79% | ✅ Solid, flat-out in FF1600 |
| 12 | Recaro Corner | 89% | ✅ Solid |

---

## Reference Times

| Benchmark | Time | Gap | Notes |
| :-------- | :--- | :-- | :---- |
| **Alien (Gong)** | **1:09.856** | -2.727s | Previous season, same fixed setup |
| Master Lonn PB | 1:12.583 | — | Baseline (Day 1) |
| Target (next session) | 1:11.xxx | -1.5s | Fix The Sweeper alone |

---

## Priority Fixes (from Gong Comparison)

1. **The Sweeper** — STOP BRAKING. Lift only. Carry 160+ km/h. Worth ~0.3s.
2. **Champion Curve** — Later apex, more commitment. 9 km/h slower than Gong.
3. **Momo Corner** — Hidden loss! 11 km/h slower despite "solid" variance.
4. **Full throttle** — Get from 66.6% to 70%+ (Gong at 72.3%).

---

## Targets

- [x] Baseline lap time (first session) → **1:12.583**
- [x] Identify problem corners → **Champion Curve, Foster's Dip, The Sweeper**
- [x] Compare vs alien → **Gong gap: 2.727s**
- [ ] Fix The Sweeper technique (lift, don't brake)
- [ ] Champion Curve consistency (σ < 0.4s)
- [ ] Break 1:11.0
- [ ] First official race

---

## Assets

- [Speed Delta Map (vs Gong)](assets/2026-01-15-lonn-vs-gong-speed-map.png)
- [Consistency Heatmap](assets/2026-01-15-13-48-consistency-heatmap.png)
- [Lap Evolution](assets/2026-01-15-13-48-lap-evolution.png)
- [Gong Comparison JSON](comparison/2026-01-15-gong-comparison.json)

---

## Notes

Track data: `tracks/track-data/oran-gp.json`  
Track dossier: `tracks/track-oran-park-raceway-grand-prix.md`

---

_"Tricky track with, eh, ups and downs. I think in time I'll get the hang of it though... Fun track."_ — Master Lonn 🦜
