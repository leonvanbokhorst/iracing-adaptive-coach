# Guidebook Integration Guide

This document outlines the process for integrating the existing documentation into the comprehensive guidebook structure and provides guidance for writing the new chapters.

## Existing Documentation Integration

The following existing documents have been moved into the `guidebook/chapters/` directory and renamed to match the chapter numbering system:

| Original File | New Location | Chapter Number | Status |
| :--- | :--- | :--- | :--- |
| `docs/iracing-history.md` | `guidebook/chapters/02-history-of-iracing.md` | Chapter 2 | ✅ Moved |
| `docs/track-terminology-guide.md` | `guidebook/chapters/04-track-terminology.md` | Chapter 4 | ✅ Moved |
| `docs/weight-transfer-guide.md` | `guidebook/chapters/05-weight-transfer.md` | Chapter 5 | ✅ Moved |
| `docs/gears-and-shifting-guide.md` | `guidebook/chapters/06-gears-and-shifting.md` | Chapter 6 | ✅ Moved |
| `docs/trail-braking-technique-guide.md` | `guidebook/chapters/08-trail-braking.md` | Chapter 8 | ✅ Moved |
| `docs/rotation-and-balance-guide.md` | `guidebook/chapters/09-rotation-and-balance.md` | Chapter 9 | ✅ Moved |
| `docs/g-force-analysis-guide.md` | `guidebook/chapters/10-g-force-analysis.md` | Chapter 10 | ✅ Moved |
| `docs/irating-tier-system.md` + `docs/standings-and-point-system.md` | `guidebook/chapters/03-rules-of-the-road.md` | Chapter 3 | ✅ Merged |
| `README.md` | `guidebook/chapters/16-master-lonns-log.md` | Chapter 16 | ✅ Copied |

## New Chapters to Write

The following chapters require new content to be written based on the detailed outlines in the `guidebook/outlines/` directory:

| Chapter Number | Title | Outline File | Status |
| :--- | :--- | :--- | :--- |
| Chapter 1 | Welcome, Padawan | `outlines/01-welcome-padawan.md` | 📝 To Write |
| Chapter 7 | The Art of the Apex: An Introduction to Racing Lines | `outlines/07-racing-lines.md` | 📝 To Write |
| Chapter 11 | Beyond G-Forces: An Advanced Telemetry Deep Dive | `outlines/11-advanced-telemetry.md` | 📝 To Write |
| Chapter 12 | The Mental Game: Flow State and Deliberate Practice | `outlines/12-mental-game.md` | 📝 To Write |
| Chapter 13 | Introduction to Racecraft: From Hot Laps to Wheel-to-Wheel | `outlines/13-racecraft.md` | 📝 To Write |
| Chapter 14 | The Long Game: Tire Management and Fuel Strategy | `outlines/14-tire-management.md` | 📝 To Write |
| Chapter 15 | The Art of the Setup: A Primer on Vehicle Tuning | `outlines/15-vehicle-tuning.md` | 📝 To Write |

## Writing Guidelines

When writing the new chapters, please adhere to the following guidelines to maintain consistency with the existing documentation:

### Narrative Style

The guidebook uses a coaching narrative, with "Little Padawan" serving as the guide and "Master Lonn" as the student. Each chapter should begin with a narrative hook that introduces the topic in the context of a racing scenario or a specific challenge that Master Lonn is facing.

### Physics and Math Integration

Where appropriate, chapters should include explanations of the underlying physics principles that govern the topic. Mathematical formulas should be presented clearly, with each variable defined. The goal is to provide a deep understanding of the "why" behind the "what," not just a list of instructions.

### Practical Application

Every chapter should include practical drills or exercises that the reader can use to apply the concepts learned. These should be specific, actionable, and tied to the chapter's learning objectives.

### Visual Aids

Diagrams, tables, and telemetry screenshots should be used liberally to support the text. Visual aids are particularly important for explaining complex concepts or demonstrating the differences between correct and incorrect techniques.

### Master Lonn's Log

Each chapter should conclude with a brief reflection from Master Lonn on how he applied the chapter's lessons in a recent race or practice session. This serves to connect the theory to the ongoing narrative of his journey.

## Chapter Template

A template for new chapters is provided in `guidebook/chapters/template.md`. This template includes placeholders for the narrative hook, learning objectives, key topics, practice drills, and Master Lonn's log.

## Next Steps

The immediate next steps are to begin writing the new chapters, starting with Chapter 1 (Welcome, Padawan) to establish the tone and philosophy of the guidebook. From there, the chapters can be written in order, or in parallel if multiple authors are contributing.
