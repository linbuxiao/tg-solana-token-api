import threading
from .client import pub_tg_client, pika_channel, PUSH_QUEUE, pika_conn
from dotenv import load_dotenv
import os
import time

load_dotenv()

CHANNEL_MAP = {
    "dogee": int(os.getenv("dogee_channel") or 0),
}


def send_tg_message(ch, method, properties, body):
    route_keys = method.routing_key.split(".")
    token = route_keys[-1]
    channel = route_keys[-2]
    target_channel = CHANNEL_MAP.get(channel)
    if target_channel:
        pub_tg_client.send_message(target_channel, token)


if __name__ == "__main__":
    pub_tg_client.start()

    pika_channel.basic_consume(
        PUSH_QUEUE, on_message_callback=send_tg_message, auto_ack=True
    )
    pika_channel.start_consuming()
