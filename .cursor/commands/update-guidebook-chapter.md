---
name: update-guidebook-chapter
description: Add discovery to guidebook chapter with cross-references
---

# Update Guidebook Chapter

When Master Lonn or Little Padawan discovers a **principle** worth codifying in the guidebook:

## 1. Identify the Discovery

Ask these questions:
- **Is it a principle?** (not just a lap time or one-time result)
- **Can it be taught?** (others could learn and apply this)
- **Does it answer "why"?** (explains physics, technique, or strategy)

If YES to all three → Guidebook update!

## 2. Choose the Chapter

Match discovery to guidebook structure:

**Core Skills (Ch 5-8):**
- Weight Transfer
- Gearbox as Tool
- Racing Lines
- Trail Braking

**Advanced Arts (Ch 9-12):**
- Rotation & Balance
- G-Force Analysis
- Advanced Telemetry
- Mental Game

**Competitive Edge (Ch 13-15):**
- Racecraft
- Tire Management
- Vehicle Setup

## 3. Content Format

Add this structure to the appropriate chapter:

```markdown
## [Section Title]

**The Principle:**
[Clear explanation in 1-2 sentences]

**The Physics/Why:**
[Explanation of underlying mechanism]
- Include formulas if applicable
- Define all variables
- Explain cause-effect relationship

**When to Use:**
[Specific conditions where this applies]
- Car type (e.g., "Lightweight cars")
- Corner type (e.g., "Long flowing corners")
- Situation (e.g., "When trail braking feels too abrupt")

**How to Practice:**
[Specific drill or exercise]
1. [Step 1]
2. [Step 2]
3. [Success criteria]

**Master Lonn's Discovery ([Track], Week XX):**
> "[Direct quote from Master Lonn about the feeling/insight]"

**The Data Proof:**
- [Metric] improved from [before] to [after]
- [Specific data point that validates principle]
- This confirms because [explanation]

**Telemetry Example:**
[Link to telemetry comparison if available]

→ **See:** Week XX, Session YY ([link]) for full session analysis

**Key Takeaway:**
[One sentence summary of when to use this technique]
```

## 4. Add Cross-References

### In Guidebook Chapter:
```markdown
📊 **Real-World Example:** 
Master Lonn applied this at Winton Turn 5 (Week 03, P3 Session).
Speed increased 3.75 m/s with smoother rotation.
[Link to session]
```

### In Session Log:
```markdown
💡 **Guidebook Reference:** 
This is Chapter 6's engine braking rotation technique (Section 3.2).
See guidebook for the physics explanation and practice drills.
```

## 5. Update Learning Memory

Add to `learning_memory.json`:

```json
{
  "guidebook_updates": [
    {
      "date": "YYYY-MM-DD",
      "chapter": "XX-chapter-name",
      "section": "Section Title",
      "trigger": "Brief description of what prompted this",
      "principle": "One-sentence summary of the discovery",
      "session_reference": "Week XX, Session YY"
    }
  ]
}
```

## 6. Visual Aids (Optional)

If helpful, add:
- Diagram showing the technique
- Telemetry comparison screenshot
- Track map showing application point
- Table comparing before/after data

Store in `guidebook/assets/` or `weeks/weekXX/assets/`

---

## Example Usage

**User**: "Little Wan, the engine braking discovery at Turn 5 should go in the guidebook!"

**Little Padawan**:

1. ✅ Checks: Is it a principle? (YES), Can be taught? (YES), Answers why? (YES)
2. Identifies: Chapter 6 (Gearbox as Tool)
3. Writes new section: "Engine Braking for Rotation"
4. Adds Master Lonn's quote and Winton Week 03 data
5. Cross-references:
   - Guidebook → Session log
   - Session log → Guidebook
6. Updates learning memory
7. Reports: "Chapter 6 updated! Added Section 3.2: Engine Braking for Rotation with your Winton discovery."

---

## Tips

- Don't update guidebook for every session - only when discovering **principles**
- Focus on what generalizes beyond one track/session
- Always include Master Lonn's journey as examples (makes it relatable)
- Keep physics explanations clear but thorough
- Link back and forth between guidebook and session logs

---

_"Good teachers extract principles from experience. Great teachers document them."_ 📚✨

