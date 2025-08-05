from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from pywebpush import webpush, WebPushException
from apscheduler.schedulers.background import BackgroundScheduler
from models import Event
import requests
import json
from datetime import datetime, timezone
from flask_cors import cross_origin
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

load_dotenv()
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY")
VAPID_EMAIL = os.environ.get("VAPID_EMAIL")
VAPID_CLAIMS = {
    "sub": f"mailto:{VAPID_EMAIL}"
}
CROSS_ORIGIN = os.environ.get("CROSS_ORIGIN")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String, unique=True, nullable=False)
    p256dh = db.Column(db.String, nullable=False)
    auth = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()

last_uids = None


@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "ok"})


@app.route('/subscribe', methods=['POST', 'OPTIONS'])
@cross_origin(origins=[CROSS_ORIGIN], methods=['POST'],
              supports_credentials=True)
def subscribe():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    subscription = Subscription(
        endpoint=data['endpoint'],
        p256dh=data['keys']['p256dh'],
        auth=data['keys']['auth']
    )
    try:
        db.session.add(subscription)
        db.session.commit()
        logging.info('Subscription added successfully')
        # Send a test push notification
        payload = json.dumps({
            "title": "山梨の新着イベント",
            "body": "今後、新着イベントがあれば通知します",
            "url": "https://hub.yamanashi.dev"
        })
        push_data(subscription, payload)
        return jsonify({}), 201

    except Exception as e:
        logging.critical(f"Error adding subscription: {str(e)}")
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({}), 200
        return jsonify({'error': str(e)}), 500


@app.route('/unsubscribe', methods=['POST'])
@cross_origin(origins=[CROSS_ORIGIN], methods=['POST'],
              supports_credentials=True)
def unsubscribe():
    data = request.data.decode('utf-8')
    data = json.loads(data)
    subscription = Subscription.query.filter_by(endpoint=data['endpoint']).first()
    if subscription:
        db.session.delete(subscription)
        db.session.commit()
        logging.info('Subscription deleted successfully')
    return jsonify({}), 200


def push_data(subscription, payload):
    sub_info = {
        "endpoint": subscription.endpoint,
        "keys": {
            "p256dh": subscription.p256dh,
            "auth": subscription.auth
        }
    }
    try:
        webpush(
            subscription_info=sub_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
        logging.info(f"Push notification sent to {subscription.endpoint}")

    except WebPushException as ex:
        logging.error(f"Failed to send push notification: {str(ex)}")
        if ex.response and ex.response.status_code in [404, 410]:
            db.session.delete(subscription)
            db.session.commit()


def is_new_event(e):
    global last_uids
    if last_uids is None:
        return False

    started_at = datetime.strptime(e.started_at, '%Y-%m-%dT%H:%M:%S%z')
    now = datetime.now(timezone.utc)
    return e.uid not in last_uids and started_at > now


def check_new_events():
    global last_uids
    response = requests.get('https://api.event.yamanashi.dev/events')
    data = response.json()
    events = Event.from_json(data)

    new_events = list(filter(is_new_event, events))
    last_uids = [e.uid for e in events]

    with app.app_context():
        for event in new_events:
            logging.info(f"New event found: {event.title} ({event.event_url})")
            payload = json.dumps({
                "title": "山梨の新着イベント",
                "body": event.title,
                "url": event.event_url
            })

            subscriptions = Subscription.query.all()
            for subscription in subscriptions:
                push_data(subscription, payload)


scheduler = BackgroundScheduler()
scheduler.add_job(func=check_new_events, trigger="interval", minutes=60)
scheduler.start()


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        scheduler.shutdown()
