# Architecture

## Purpose

email-warmup-service gradually increases outbound email volume over a warm-up
window to build sender reputation and improve deliverability.

## Components

- **CLI** (`main` in `warmup.py`) — parses flags and dispatches actions.
- **EmailWarmupService** — the engine: volume curve, state persistence, sending.
- **State file** (`warmup_state.json`) — persisted progress across runs.
- **Recipients list** (`recipients.txt`) — warm-up destination addresses.

## Runtime Flow

1. Determine the current warm-up day from the stored start date.
2. Compute the target daily volume from the exponential ramp curve.
3. Send the remaining emails for the day over SMTP, rate-limited.
4. Persist updated counters back to the state file.
