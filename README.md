# Yamanashi Tech Events Notify Backend

## About the Project

This is a backend service that periodically fetches event information for Yamanashi Prefecture and delivers notifications to users via Web Push.  
Built with Flask, APScheduler, Web Push, and SQLite.

## Features

- Periodically fetches new events from the Yamanashi event API
- Sends Web Push notifications for new events
- Manages push subscriptions (subscribe/unsubscribe API)
- Includes a VAPID key pair generator

## Requirements

- Python 3.11 or higher
- Docker / Docker Compose (recommended)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yuukis/yamanashi-event-notify-backend.git
cd yamanashi-event-notify-backend
```

### 2. Generate VAPID keys

```bash
pip install ecdsa
python vapid_helper.py
```

Copy the output `VAPID_PUBLIC_KEY` and `VAPID_PRIVATE_KEY` to your `.env` file.

### 3. Create a `.env` file

Copy `.env.sample` to `.env` and fill in the required values.

```bash
cp .env.sample .env
```

### 4. Start with Docker
```bash
docker-compose up --build
```

Or run locally:

```bash
pip install -r requirements.txt
python main.py
```

## API Endpoints
### Subscribe
```
POST /subscribe
Content-Type: application/json

{
  "endpoint": "...",
  "keys": {
    "p256dh": "...",
    "auth": "..."
  }
}
```

### Unsubscribe
```
POST /unsubscribe
Content-Type: application/json

{
  "endpoint": "..."
}
```

## License

Distributed under the Apache License, Version 2.0. See `LICENSE` for more information.

## Contact

Yuuki Shimizu - [@yuuki_maxio](https://x.com/yuuki_maxio) 

## Acknowledgements

* [shingen.py](https://shingenpy.connpass.com)
  - python user community in Yamanashi, Japan