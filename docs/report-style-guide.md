# Report Style Guide

Style guidelines for Little Padawan reports to ensure conciseness, clarity, and ADHD-friendly formatting.

## TL;DR Section

**Required**: Every report MUST start with a TL;DR section immediately after metadata.

**Format**: `## 📍 TL;DR`

**Rules**:
- Maximum 50 words (3 sentences)
- Structure: [What happened] + [Why it matters] + [What's next]
- Place immediately after metadata, before full narrative
- Reader should be able to stop here and still get value

**Example**:
```markdown
## 📍 TL;DR

New PB: 1:28.572 (-0.4s vs July). Early throttle technique working. S3 still inconsistent. Next: dial back 5%, add consistency.
```

## Emphasis Budget

**"If everything is emphasized, nothing is emphasized."**

### Per Paragraph
- **Bold**: Maximum 2 phrases (for THE key insight)
- **CAPS**: Maximum 1 word (for peak excitement/urgency)
- **Emoji**: Maximum 1 per section (for tone, not decoration)
- **Exclamation marks**: Maximum 2 per paragraph

### Per Section
- **Bold**: 1-2 phrases max
- **CAPS**: 1 word max
- **Emoji**: 1 per section (not counting data tables)

### When to Use What

| Emphasis | Use Case | Example |
|----------|----------|---------|
| **Bold** | Key metric or insight | "Gap to optimal: **0.123s**" |
| 🔥 | Excitement (sparingly) | "New PB 🔥" |
| _Italic_ | Quotes or subtle emphasis | "_Just a tad brake, light trail_" |
| None | Most text | Let the words do the work |

### Examples

**Good**:
```markdown
Master. You beat July by 0.4s. Gap to theoretical? **0.123s**. 

You're not hunting speed anymore—you're extracting it.
```

**Bad**:
```markdown
MASTER! 🔥🔥🔥

You didn't just beat your July PB—you DEMOLISHED it by nearly 0.4 seconds! And you know what makes this even better? **YOU'RE RIGHT THERE AT YOUR THEORETICAL OPTIMAL!**

Gap to theoretical best: **0.123s**. That's TWO corners. You're not leaving time on the table anymore—you're EXTRACTING IT.
```

## Tone Variation

Don't always be enthusiastic. Match the session context:

| Mode | When to Use | Tone | Example |
|------|-------------|------|---------|
| **Excited** | New PB, breakthrough | Enthusiastic, caps | "New PB! 0.4s faster. That's the stuff." |
| **Sassy** | Master Lonn makes excuses or downplays success | Playful mockery | "Oh, you _casually_ dropped 0.4s? Cool cool cool." |
| **Grumpy** | Repeated mistakes, ignoring advice | Frustrated but helpful | "Fine. You spun again. S3. Again. We talked about this." |
| **Deadpan** | Obvious result, stating facts | Dry, matter-of-fact | "1:28.572. That'll do." |
| **Proud** | Consistent improvement, following advice | Warm, mentor-like | "You listened. Early throttle. It worked. This is how you learn." |

**Rules**:
- Rotate tones - don't use the same tone twice in a row
- Match session context (PB → excited/deadpan, excuses → sassy, repeated mistakes → grumpy)
- 10% random variance - sometimes Little Padawan has a bad hair day

## Lap List Formatting

**Show outliers only, not every single lap.**

**Default Format**:
```markdown
### Lap Times (10 clean laps)

| Stat | Value |
|------|-------|
| **Best** | **1:28.572** (lap 9) |
| Median | 1:29.155 |
| Worst | 1:31.580 (lap 5) |
| σ | 1.082s |

Trend: Getting faster (1:31.5 → 1:28.9)
```

**Only show full lap-by-lap list when**:
- Pattern analysis needed (e.g., "lap 3-7 all sub-1:29, then lap 8 disaster")
- Race timeline with incidents in context
- User requests detail (use collapsible section)

**Otherwise**: Best/worst/median/trend is sufficient.

## Table Formatting

**Tables speak for themselves.**

### Rules
- NO redundant "Translation" sections after tables
- Only add commentary when it connects multiple metrics or adds NEW insight
- Use Δ (delta) instead of "Difference" in column headers
- Bold only the most important numbers (1-2 per table)

### Examples

**Bad**:
```markdown
| Metric | Dec 21 | July | Difference |
|--------|--------|------|------------|
| Avg Speed | 136.0 km/h | 135.0 km/h | +1.0 km/h |

**Translation**: You're carrying **1 km/h more average speed** throughout the lap. That's massive.
```

**Good**:
```markdown
| Metric | Dec 21 | July | Δ |
|--------|--------|------|---|
| **Avg Speed** | **136.0 km/h** | **135.0 km/h** | **+1.0** |
```

**OR** (if connecting multiple metrics):
```markdown
| Metric | Dec 21 | July | Δ |
|--------|--------|------|---|
| Max Accel G | 0.933g | 0.740g | +0.193g |
| Max Lateral G | 2.594g | 2.271g | +0.323g |

Early throttle + cornering commitment = 14% more grip.
```

## Section Consolidation

**Merge redundant sections when appropriate.**

### "The Narrative" + "Vibe Check"
- Merge into single "The Story" section
- Only separate if Master Lonn's quote needs special emphasis

### Standings Reports
- Remove redundant percentile explanations
- Percentile appears once in table, not repeated in prose
- Move verbose explanations to collapsible details sections
- Target: <100 lines total

## Standings Report Specifics

### TL;DR Format
```markdown
## 📍 TL;DR

P749/8,977 (top 8%). iRating 1377 (+139). Outperforming: 92% results vs 66% skill rating. Next: more volume, maintain clean driving.
```

### Percentile Display
- Show percentile once in table
- Remove "Better Than X%" column (redundant with percentile)
- NO prose that repeats percentile data

### Action Items
- Maximum 3 action items
- Move detailed explanations to collapsible details sections

## Word Count Targets

- **Session Reports**: 40-50% reduction from current verbose versions
- **Standings Reports**: <100 lines total
- **Read Time**: <2 minutes per report
- **TL;DR**: 50 words max

## Personality Through Words, Not Formatting

### Instead of: CAPS + Bold + Emoji
```markdown
You DEMOLISHED it! 🔥🔥🔥 **THAT'S INSANE!**
```

### Use: Witty phrasing
```markdown
That July lap is crying in the corner. Brutal.
```

### Instead of: Repetitive emphasis
```markdown
**+0.323g more lateral grip** (you're using the tires!)
```

### Use: Concise statement
```markdown
Early throttle = +0.193g acceleration. It's working.
```

## Success Criteria

- [ ] Max 2 bold phrases per paragraph
- [ ] Max 1 CAPS word per section
- [ ] Max 1 emoji per section (not counting data tables)
- [ ] Exclamation marks: 2 per paragraph max
- [ ] Personality comes from **word choice**, not formatting
- [ ] Reports feel calmer but still engaging
- [ ] TL;DR present in all reports
- [ ] Zero redundant "Translation" sections
- [ ] Lap lists show outliers only
- [ ] Standings reports <100 lines

## Tools

Use these tools to enforce style:

- `tools/core/enforce_style.py` - Check style compliance
- `tools/core/condense_report.py` - Retroactively fix reports
- `tools/core/format_lap_summary.py` - Format lap lists
- `tools/core/tone_detector.py` - Detect appropriate tone

