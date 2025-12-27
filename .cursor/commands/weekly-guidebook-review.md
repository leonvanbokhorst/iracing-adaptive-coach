---
name: weekly-guidebook-review
description: End-of-week review to identify guidebook updates needed
---

# Weekly Guidebook Review

At the end of each racing week, review discoveries and identify what belongs in the guidebook.

## When to Run

- After completing all sessions for a week
- Before creating the week summary README
- When transitioning to a new track/week

## Review Process

### Step 1: Scan Week's Session Logs

Read all session files in `weeks/weekXX/*.md` and identify:

**Discoveries:**
- [ ] New techniques discovered
- [ ] Breakthrough moments with clear "aha!"
- [ ] Physics insights (why something works)
- [ ] Mental game lessons
- [ ] Strategy insights

**Validations:**
- [ ] Existing guidebook principles confirmed with data
- [ ] Techniques from previous weeks applied successfully
- [ ] Theory validated through practice

**Questions:**
- [ ] "Why does X work?" questions Master Lonn asked
- [ ] Concepts that needed explanation
- [ ] Gaps in current guidebook coverage

### Step 2: Categorize Findings

For each discovery, classify:

**Type:**
- 🔧 **Technique** (how to do something)
- 📐 **Principle** (why something works)
- 🧠 **Mental** (mindset, psychology, flow state)
- 📊 **Analysis** (data interpretation method)
- 🏁 **Strategy** (race craft, tire management)

**Scope:**
- 🌍 **Universal** (applies everywhere)
- 🚗 **Car-specific** (Ray FF1600)
- 🏎️ **Track-specific** (one track only)
- 🎯 **Situation-specific** (certain conditions)

**Priority:**
- 🔴 **High** - Core skill, used frequently
- 🟡 **Medium** - Important but situational
- 🟢 **Low** - Nice to have, edge case

### Step 3: Map to Guidebook Chapters

Assign each HIGH priority discovery to a chapter:

| Discovery | Chapter | Section | Action |
|:----------|:--------|:--------|:-------|
| [Name] | Ch X | [New/Existing] | [Create/Update] |

**Chapter Reference:**
- Ch 5: Weight Transfer
- Ch 6: Gearbox as Tool
- Ch 7: Racing Lines
- Ch 8: Trail Braking
- Ch 9: Rotation & Balance
- Ch 10: G-Force Analysis
- Ch 11: Advanced Telemetry
- Ch 12: Mental Game
- Ch 13: Racecraft
- Ch 14: Tire Management
- Ch 15: Vehicle Setup

### Step 4: Create Update Plan

For each identified update:

```markdown
## Guidebook Update: [Chapter X - Section Name]

**Discovery:** [What was learned]

**From Session:** Week XX, Session YY ([link])

**Master Lonn's Quote:**
> "[Relevant quote if available]"

**Data Supporting This:**
- [Key metric/improvement]
- [Validation from telemetry]

**Why It Matters:**
[Explanation of broader applicability]

**Action Items:**
- [ ] Write/update section in Chapter X
- [ ] Add Master Lonn's discovery as example
- [ ] Include data proof
- [ ] Cross-reference session log
- [ ] Add practice drill
```

### Step 5: Execute Updates

Either:
1. Update chapters immediately (if time permits)
2. Create issues/tasks for later updates
3. Note in learning_memory.json for next session

### Step 6: Update Cross-References

After guidebook updates:
- [ ] Go back to session logs and add guidebook references
- [ ] Update learning_memory.json with guidebook changes
- [ ] Note in week summary which chapters were updated

---

## Output Format

After review, create summary:

```markdown
# Week XX Guidebook Review

**Sessions Reviewed:** [List session dates]

## Discoveries Worth Codifying

### High Priority
1. **[Discovery 1]** → Chapter X, Section Y
   - Type: [Technique/Principle/etc]
   - Scope: [Universal/Car-specific/etc]
   - Action: [Create/Update]

### Medium Priority
2. **[Discovery 2]** → Chapter X, Section Y
   - [Same format]

## Validations of Existing Content
- Chapter X, Section Y: Confirmed with [session data]
- Chapter X, Section Y: Applied successfully at [location]

## Gaps Identified
- Missing explanation for [concept]
- Chapter X needs section on [topic]

## Guidebook Updates Made This Week
- ✅ Chapter 6: Added "Engine Braking for Rotation" section
- ✅ Chapter 8: Updated with Winton T10 example
- ⏳ Chapter 12: Flow state section (pending)

## Cross-References Added
- Week 03, P3 session ↔ Chapter 6, Section 3.2
- Week 03 summary ↔ Chapter 8 validation

---

**Next Week Focus for Guidebook:**
[What concepts to watch for in upcoming sessions]
```

---

## Example Review

**Week 03 - Winton**

**High Priority Discovery:**
- **Engine Braking Rotation** → Chapter 6
  - Type: Technique + Principle
  - Scope: Universal (lightweight cars)
  - Master Lonn: "More smooth than trail braking"
  - Data: S2 loss 0.96s → 0.34s, lateral G reduced 0.40G
  - **Action**: ✅ Added Section 3.2 to Chapter 6

**Validations:**
- Chapter 8 (Trail Braking): Confirmed at T10, T2
- Chapter 5 (Weight Transfer): Progressive transfer concept validated

**Gaps:**
- Chapter 12 missing: Cold Tire Contract (mental discipline)
- Chapter 7 needed: Wide arc geometry explanation

**Updates Made:**
- ✅ Chapter 6.3.2: Engine Braking for Rotation
- ✅ Added Winton examples to Chapter 8
- ⏳ Chapter 12: Flow state section (for next week)

---

## Tips

- Don't force updates - only codify real discoveries
- Prioritize universal principles over one-off results
- Use Master Lonn's quotes - they make it relatable
- Always include data proof when available
- Cross-reference generously

---

_"A week of racing becomes a chapter of knowledge."_ 📚🏁

