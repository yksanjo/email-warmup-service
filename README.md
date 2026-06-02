# email-warmup-service

Gradually ramps up the volume of email sent from a mailbox over a configurable
period to improve sender reputation and deliverability. State is persisted to a
local JSON file so the ramp survives restarts, and the service can run once,
on demand, or continuously on a daily schedule.

## How it works

- Sends warm-up messages over SMTP starting at a low daily volume and increasing
  toward a target volume on an exponential curve across the warm-up window.
- Tracks progress (current day, emails sent today, total sent, paused state) in
  `warmup_state.json`.
- Reads warm-up recipients from `recipients.txt` (one address per line).
- Rate-limits sends and resets the daily counter at the start of each day.

## Stack

Python 3, standard-library `smtplib`, plus `python-dotenv`, `schedule`,
`requests`, and `pyyaml` (see `requirements.txt`).

## Configuration

Set via a `.env` file or environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server host |
| `SMTP_PORT` | `587` | SMTP server port (STARTTLS) |
| `SMTP_USER` | _(required)_ | SMTP username / from address |
| `SMTP_PASSWORD` | _(required)_ | SMTP password |
| `WARMUP_DURATION_DAYS` | `30` | Length of the warm-up ramp |
| `INITIAL_VOLUME` | `5` | Emails per day at the start |
| `TARGET_VOLUME` | `100` | Emails per day at the end |

Add recipient addresses (one per line) to `recipients.txt`.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 warmup.py --start        # begin the warm-up and send the first batch
python3 warmup.py --run          # run today's warm-up once
python3 warmup.py --status       # show current progress
python3 warmup.py --pause        # pause sending
python3 warmup.py --resume       # resume after a pause
python3 warmup.py --continuous   # run a long-lived daily scheduler (09:00)
```

`SMTP_USER` and `SMTP_PASSWORD` must be set before the service will run.

## Repository structure

```text
warmup.py          # the service (CLI + EmailWarmupService)
tests/             # tests
docs/              # architecture and roadmap notes
requirements.txt   # Python dependencies
```
