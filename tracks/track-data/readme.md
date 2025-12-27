# Track Data Directory

This directory contains track definition JSON files used for corner-specific telemetry analysis.

## Source & Attribution

**All track data files in this directory are sourced from:**

**[Lovely Sim Racing - Track Data Project](https://github.com/Lovely-Sim-Racing/lovely-track-data)**  
© 2025 by Lovely Sim Racing  
Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

### Credits

- **Track & Corner Names**: Sourced from [Racing Circuits](https://www.racingcircuits.info/)
- **Data Collection**: Lovely Sim Racing community
- **Special Thanks**: Nicolas of SimHub and Joerg Behrens for feedback on the file format

---

## File Format

Each track JSON file follows the Lovely Sim Racing Track Data v2.0.0 format:

```json
{
  "name": "Track Name",
  "trackId": "track-id",
  "country": "US",
  "length": 3000,
  "pitentry": 0.85,
  "pitexit": 0.05,
  "turn": [
    {
      "name": "Turn Name",
      "start": 0.10,
      "end": 0.15,
      "marker": 0.125
    }
  ],
  "straight": [
    {
      "name": "Straight Name",
      "start": 0.15,
      "end": 0.25
    }
  ],
  "sector": [
    {
      "name": "1",
      "marker": 0.33
    }
  ]
}
```

### Key Properties

- **turn**: Array of corner definitions with start/end percentages (0.0-1.0)
- **straight**: Array of straight definitions with start/end percentages
- **sector**: Array of sector markers
- **length**: Track length in meters
- **pitentry/pitexit**: Pit lane entry/exit percentages

---

## Usage in iRacing Adaptive Coach

These track data files enable **corner-specific telemetry analysis**:

```python
from tools.core.track_data_loader import load_track_data
from tools.core.corner_identifier import identify_location

track_data = load_track_data('winton-national')
location = identify_location(0.4, track_data)
# Returns: {'name': 'Turn 5', 'type': 'turn', 'progress_through': 0.76, ...}
```

This allows Little Padawan to coach Master Lonn with specific corner references:

**Before**: "You're losing time at 40% lap distance"  
**After**: "You're losing 3.75 m/s in **Turn 5** at the **exit phase**"

---

## Adding New Tracks

To add a new track:

1. Find the track on [Lovely Sim Racing Track Data](https://github.com/Lovely-Sim-Racing/lovely-track-data)
2. Download the JSON file from: `main/data/iracing/{track-id}.json`
3. Place in this directory with proper naming
4. Track will automatically be available to analysis tools

### Track ID Format

Track IDs follow the Lovely Sim Racing naming convention:

1. Lowercase
2. Replace accented chars with standard equivalent
3. Replace spaces with hyphen
4. Remove special characters
5. Remove double hyphens

**Examples**:
- `Winton Motor Raceway (National)` → `winton-motor-raceway-national.json`
- `Rudskogen Motorsenter` → `rudskogen-motorsenter.json`

---

## License Compliance

Per CC BY-NC-SA 4.0:

- ✅ **Attribution**: This README credits Lovely Sim Racing
- ✅ **Non-Commercial**: iRacing Adaptive Coach is personal/educational use
- ✅ **ShareAlike**: Any modifications shared under same license
- ✅ **License Notice**: Included in this README

**If you distribute this project, you MUST include this attribution.**

---

## Contributing Track Data

If you want to contribute track data improvements:

1. **Submit to upstream**: [Lovely Sim Racing Track Data](https://github.com/Lovely-Sim-Racing/lovely-track-data)
2. Follow their contribution guidelines (requires `pre-commit` hooks)
3. Once merged there, update files here from upstream

**Do NOT modify track data files directly in this repo** unless you're also submitting to upstream.

---

## Available Tracks

Track data files are organized by sim. For iRacing tracks, check:

```bash
ls tracks/track-data/*.json
```

Or use the track data loader to list available tracks:

```bash
uv run python tools/core/track_data_loader.py
```

---

## Thank You!

Huge thanks to the Lovely Sim Racing community for creating and maintaining this comprehensive track data resource! 🙏🏁

Without your work, corner-specific analysis wouldn't be possible. This data turns generic telemetry into actionable coaching.

---

**Links**:
- [Lovely Sim Racing Website](https://lsr.gg)
- [GitHub Repository](https://github.com/Lovely-Sim-Racing/lovely-track-data)
- [CC BY-NC-SA 4.0 License](https://creativecommons.org/licenses/by-nc-sa/4.0/)
