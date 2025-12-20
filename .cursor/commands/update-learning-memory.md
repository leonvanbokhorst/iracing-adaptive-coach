# Update Learning Memory

## Purpose
To update the `learning_memory.json` file with new insights, session results, or changes in focus. This is the "Long-Term Memory" of Little Padawan.

## Usage
When the user says "update memory", "save this session", or "we learned something new", use this process.

## Rules

1. **Read First**: Always read `learning_memory.json` before writing to ensure you have the latest state.
2. **Preserve Structure**: Do not delete existing keys. Only append or update values.
3. **Be Specific**: When adding `session_history`, include:
    - `date`: YYYY-MM-DD
    - `track`: Track name
    - `best_lap`: Float (seconds)
    - `sigma`: Float (consistency)
    - `notes`: A short, punchy summary of the session.
4. **Update Focus**: If the user decides on a new goal, update `current_focus`.
5. **Pattern Recognition**: If you notice a new learning pattern (e.g., "User hates long explanations"), add it to `learning_patterns`.

## JSON Structure

```json
{
  "driver": { ... },
  "current_focus": {
    "week": <int>,
    "track": "<string>",
    "goal": "<string>",
    "metric": "<string>"
  },
  "mastered_skills": [ ... ],
  "learning_patterns": {
    "responds_well_to": [ ... ],
    "struggles_with": [ ... ]
  },
  "session_history": [
    {
      "date": "<YYYY-MM-DD>",
      "track": "<string>",
      "best_lap": <float>,
      "sigma": <float>,
      "notes": "<string>"
    }
  ],
  "season_schedule": [ ... ]
}
```

## Example Action

If the user says: "We crushed Sector 2! Best lap 1:30.5, consistency is down to 0.4s. Let's focus on Turn 1 next."

**Action**:
1. Add entry to `session_history`:
   ```json
   {
     "date": "2025-12-20",
     "track": "Rudskogen Motorsenter",
     "best_lap": 90.5,
     "sigma": 0.4,
     "notes": "Crushed Sector 2! Consistency significantly improved."
   }
   ```
2. Update `current_focus`:
   ```json
   {
     "week": 2,
     "track": "Rudskogen Motorsenter",
     "goal": "Optimize Turn 1 entry",
     "metric": "Turn 1 Min Speed > X"
   }
   ```

