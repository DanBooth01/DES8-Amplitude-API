# Amplitude Data Pipeline

A small pipeline that pulls raw event data from the [Amplitude Export API](https://amplitude.com/docs/apis/analytics/export), uploads it to AWS S3, and loads it into Snowflake via Snowpipe. The Python steps are orchestrated by Kestra.

```
Amplitude Export API  ->  Main.py (extract + load)  ->  S3 bucket  ->  Snowpipe  ->  Snowflake
                                 ^
                              Kestra
```

## Project structure

```
.
├── Main.py                  # Entry point: sets up logging, runs extract, then load
├── modules/
│   ├── log_initialise.py    # Logger setup
│   ├── run_extract.py       # Amplitude export logic (extract_json)
│   └── load_to_S3.py        # S3 upload logic (load_to_S3)
├── data/                    # Temporary local storage for exported files
├── log/                     # Timestamped run logs
└── .env                     # Credentials (not committed)
```

## Components

| Component | Purpose |
|---|---|
| `Main.py` | Orchestrates a single run: initialises logging, extracts the last 24 hours of Amplitude data into `data/`, then uploads it to S3 |
| `modules/run_extract.py` | Downloads and decompresses Amplitude event data into `data/` |
| `modules/load_to_S3.py` | Uploads files from `data/` to S3, skipping any already in the bucket, and removes local copies after upload |
| `modules/log_initialise.py` | Configures logging to a timestamped file in `log/` |
| Kestra | Schedules and runs `Main.py` |
| Snowpipe | Automatically ingests new files landing in the S3 bucket into Snowflake |

## Requirements

- Python 3.12
- Packages can be found in Requirements.txt
```
- An Amplitude project with API access (EU data residency)
- An AWS S3 bucket, and credentials that can list and upload objects
- A Snowflake account with a Snowpipe configured on the bucket
- A Kestra instance to run the flow

## Setup

1. Create a `.env` file in the same directory as `Main.py`:

```env
   # Amplitude
   AMP_API_KEY=your_amplitude_api_key
   AMP_SECRET_KEY=your_amplitude_secret_key

   # AWS
   AWS_ACCESS_KEY=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_BUCKET_NAME=your_bucket_name
```

2. Install dependencies:

```bash
   pip install requests python-dotenv boto3
```

> **Note:** when running under Kestra, provide these values as Kestra secrets or environment variables instead of a `.env` file.

## Usage

### Run manually

```bash
python Main.py
```

This runs the whole pipeline (extract, then upload to S3) in one go. Snowpipe picks up the new files from S3 automatically.

### Run via Kestra

The pipeline is scheduled and run by a Kestra flow: `<flow name / namespace>`, triggered `<schedule, e.g. daily at 06:00>`. The flow runs `Main.py` and passes in the credentials above.

---

## 1. Extract (`modules/run_extract.py`)

### What it does

1. Requests the last 24 hours of event data from Amplitude's EU export endpoint.
2. Retries automatically on transient failures (up to 5 attempts, 10 seconds apart).
3. On success, extracts the returned `.zip` archive, decompresses each `.json.gz` file inside it, and writes the plain `.json` files to `data/`.
4. Logs every step (successes, failures, retries) to the run's log file.

### Configuring the time range and settings

These are defined near the top of `Main.py`:

| Variable | Default | Description |
|---|---|---|
| `start_time` | now - 1 day | Start of the export window (`%Y%m%dT%H`) |
| `end_time` | now | End of the export window (`%Y%m%dT%H`) |
| `url` | EU export endpoint | Amplitude Export API URL |
| `data_dir` | `data` | Local folder for extracted files |
| `max_retry` | `5` | Maximum number of attempts |
| `delay` | `10` | Seconds between retries |

### Error handling

| Status code | Meaning | Behavior |
|---|---|---|
| 200–299 | Success | Extracts and saves the data |
| 400 | Requested time range too large | Logs and exits. Shorten the range and retry manually |
| 404 | No data for the requested range | Logs and exits |
| 504 | Request timed out (data too large) | Logs and exits |
| Other | Transient/unexpected error | Retries after a delay, up to `max_retry` attempts |

---

## 2. S3 upload (`modules/load_to_S3.py`)

### What it does

1. Takes the AWS credentials and bucket name passed in from `Main.py` (loaded from `.env`).
2. Lists the objects already in the S3 bucket.
3. Loops through every file in `data/` and uploads any that aren't already in the bucket, using the local filename as the S3 key.
4. Deletes each local file after a successful upload. Files that fail to upload are kept so they can be retried on the next run.
5. Logs each upload, skip and error to the run's log file.

> **Note:** local files are deleted after upload, so `data/` only holds files that haven't been uploaded yet.

---

## 3. Snowflake ingestion (Snowpipe)

Once files land in the S3 bucket, Snowpipe loads them into Snowflake automatically, with no extra step in the Python code.

- Pipe: `<pipe name>`
- Target table: `<database.schema.table>`
- File format: JSON
- Trigger: S3 event notifications (SQS) on the bucket

Because the S3 step skips files that already exist in the bucket, re-running the pipeline won't upload duplicates.

---

## Output

- **`data/`**: decompressed `.json` files from the Amplitude export (one per hour/device group, as returned by Amplitude). Files are removed once uploaded to S3.
- **`log/`**: one timestamped log file per run of `Main.py`, e.g. `2026-09-30 14-30-00.log`. The folder is created automatically if it doesn't exist.
