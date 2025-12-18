# Email Warm-up Service

Automated email domain warm-up tool that gradually increases sending volume to improve deliverability and avoid spam filters.

## Features

- 📧 Gradual email volume increase
- 🔄 Automated sending schedule
- 📊 Deliverability tracking
- 🎯 Multiple email provider support
- 📈 Warm-up progress monitoring
- ⚙️ Customizable warm-up curves

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```env
# Email Provider (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Warm-up Settings
WARMUP_DURATION_DAYS=30
INITIAL_VOLUME=5
TARGET_VOLUME=100
```

## Usage

### Start Warm-up

```bash
python warmup.py --start
```

### Monitor Progress

```bash
python warmup.py --status
```

### Pause Warm-up

```bash
python warmup.py --pause
```

### Resume Warm-up

```bash
python warmup.py --resume
```

## Warm-up Strategy

The service uses a gradual warm-up curve:
- Week 1: 5-10 emails/day
- Week 2: 10-25 emails/day
- Week 3: 25-50 emails/day
- Week 4: 50-100 emails/day

## Supported Providers

- Gmail (SMTP)
- Outlook/Office 365
- SendGrid
- Mailgun
- Amazon SES
- Custom SMTP

## License

MIT License


