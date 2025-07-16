# Eye-Tracking Based Worker Efficiency Assessment System

This tool analyzes eye-tracking data from airbag assembly lines to evaluate worker efficiency and generate PDF reports.

## How It Works

- Reads CSV gaze data from `/data`
- Calculates AOI coverage, fixation stats, etc.
- Scores efficiency
- Outputs PDF reports to `/reports`

## How to Run

1. Place your CSVs in the `data/` directory.
2. Run:

```bash
pip install -r requirements.txt
python eye_tracking_analysis.py
```
