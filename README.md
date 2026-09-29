# Amplitude Data Export & S3 Upload

Two Python scripts that form a simple pipeline: the first pulls raw event data from the [Amplitude Export API](https://amplitude.com/docs/apis/analytics/export) and saves it locally, and the second uploads those files to an AWS S3 bucket.

```
Amplitude Export API  ->  amplitude_export.py  ->  data/  ->  s3_upload.py  ->  S3 bucket
```

## Scripts

| Script | Purpose |
|---|---|
| `Export.py` | Downloads and decompresses the last 24 hours of Amplitude event data into `data/` |
| `Load.py` | Uploads files from `data/` to S3, skipping any already in the bucket, and removes local copies after upload |

## Requirements

- Python 3.9+ (for `str.removesuffix`)
- Packages:
```bash
  pip install requests python-dotenv boto3
```
- An Amplitude project with API access (EU data residency)
- An AWS account with an S3 bucket and credentials that can list and upload objects

## Setup

1. Create a `.env` file in the same directory as the scripts:

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

## Usage

Run the scripts in order:

```bash
python amplitude_export.py
python s3_upload.py
```

---

## 1. Amplitude export (`amplitude_export.py`)

### What it does

1. Requests the last 24 hours of event data from Amplitude's EU export endpoint.
2. Retries automatically on transient failures (up to 5 attempts, 10 seconds apart).
3. On success, extracts the returned `.zip` archive, decompresses each `.json.gz` file inside it, and writes the plain `.json` files to a `data/` folder.
4. Logs every step (successes, failures, retries) to a timestamped log file in a `log/` folder.

### Configuring the time range

By default it fetches a rolling 24-hour window (`now - 1 day` to `now`, formatted as `%Y%m%dT%H`). To change the range, edit the `start_time` and `end_time` variables near the top of the script.

### Error handling

| Status code | Meaning | Behavior |
|---|---|---|
| 200–299 | Success | Extracts and saves the data |
| 400 | Requested time range too large | Logs and exits. Shorten the range and retry manually |
| 404 | No data for the requested range | Logs and exits |
| 504 | Request timed out (data too large) | Logs and exits |
| Other | Transient/unexpected error | Retries after a 10-second delay, up to 5 attempts |

---

## 2. S3 upload (`load.py`)

### What it does

1. Loads AWS credentials and the bucket name from `.env`.
2. Lists the objects already in the S3 bucket.
3. Loops through every file in `data/` and uploads any that aren't already in the bucket, using the local filename as the S3 key.
4. Deletes each local file after a successful upload. Files that fail to upload are kept so they can be retried on the next run.
5. Logs each upload, skip and error to a timestamped log file in `log/`.

> **Note:** local files are deleted after upload, so `data/` only holds files that haven't been uploaded yet.

---

## Output

- **`data/`**: decompressed `.json` files from the Amplitude export (one per hour/device group, as returned by Amplitude). Files are removed once uploaded to S3.
- **`log/`**: one log file per run of each script, named with the run's timestamp:
  - `2026-09-25 14-30-00.log` for the export script
  - `load_2026-09-25 14-35-00.log` for the S3 upload script

Both folders are created automatically if they don't already exist, though `load.py` expects `data/` to exist, so run the export first.