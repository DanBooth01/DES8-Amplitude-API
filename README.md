# Amplitude Data Export Script

A Python script that pulls raw event data from the [Amplitude Export API](https://amplitude.com/docs/apis/analytics/export), decompresses it, and saves the resulting JSON files locally. It includes retry logic, logging, and handling for common API error responses.

## What it does

1. Requests the last 24 hours of event data from Amplitude's EU export endpoint.
2. Retries automatically on transient failures (up to 5 attempts, 10 seconds apart).
3. On success, extracts the returned `.zip` archive, decompresses each `.json.gz` file inside it, and writes the plain `.json` files to a `data/` folder.
4. Logs every step (successes, failures, retries) to a timestamped log file in a `log/` folder.

## Requirements

- Python 3.9+ (for `str.removesuffix`)
- Packages:
  ```bash
  pip install requests python-dotenv
  ```
- An Amplitude project with API access (EU data residency)

## Setup

1. Create a `.env` file in the same directory as the script with your Amplitude credentials:

   ```env
   AMP_API_KEY=your_amplitude_api_key
   AMP_SECRET_KEY=your_amplitude_secret_key
   ```

2. Install dependencies:

   ```bash
   pip install requests python-dotenv
   ```

## Usage

Run the script directly:

```bash
python amplitude_export.py
```

By default it fetches data for a rolling 24-hour window (`now - 1 day` to `now`, formatted as `%Y%m%dT%H`). To change the range, edit the `start_time` and `end_time` variables near the top of the script.

## Output

- **`data/`** — decompressed `.json` files extracted from the export archive (one per hour/device group, as returned by Amplitude).
- **`log/`** — one log file per run, named with the run's timestamp (e.g. `2026-09-25 14-30-00.log`), containing INFO-level messages for connection status, retries, and errors.

Both folders are created automatically if they don't already exist.

## Error handling

| Status code | Meaning | Behavior |
|---|---|---|
| 200–299 | Success | Extracts and saves the data |
| 400 | Requested time range too large | Logs and exits — shorten the range and retry manually |
| 404 | No data for the requested range | Logs and exits |
| 504 | Request timed out (data too large) | Logs and exits |
| Other | Transient/unexpected error | Retries after a 10-second delay, up to 5 attempts |
