from dotenv import load_dotenv
import os
import pika.adapters.asyncio_connection
from telethon.sync import TelegramClient
import pika
import time
import threading

load_dotenv()
lang_code = os.getenv("lang_code") or "en"

redis_host = os.getenv("redis_host")
redis_db = os.getenv("redis_db")
redis_password = os.getenv("redis_password")

proxy_host = os.getenv("proxy_host")
proxy_port = os.getenv("proxy_port")

proxy = None
if proxy_host and proxy_port:
    proxy = ("socks5", proxy_host, int(proxy_port))

api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")
phone = os.getenv("phone")
pub_tg_client = TelegramClient(
    "pub_tg.session",
    api_id,
    api_hash,
    lang_code=lang_code,
    proxy=proxy,
)

sub_tg_client = TelegramClient(
    "sub_tg.session",
    api_id,
    api_hash,
    lang_code=lang_code,
    proxy=proxy,
)

pika_conn = pika.BlockingConnection(
    parameters=pika.ConnectionParameters(
        host="host.docker.internal",
        heartbeat=0,
    )
)
pika_channel = pika_conn.channel()

PUSH_QUEUE = "push_token_info.*.*"
PULL_QUEUE = "pull_token_info.*.*"
EXCHANGE = "tg"

pika_channel.exchange_declare(
    exchange=EXCHANGE, exchange_type="topic", auto_delete=True
)
pika_channel.queue_declare(queue=PUSH_QUEUE, auto_delete=True)
pika_channel.queue_declare(queue=PULL_QUEUE, auto_delete=True)
pika_channel.queue_bind(
    queue=PUSH_QUEUE, exchange=EXCHANGE, routing_key="push_token_info.*.*"
)
pika_channel.queue_bind(
    queue=PULL_QUEUE, exchange=EXCHANGE, routing_key="pull_token_info.*.*"
)

if __name__ == "__main__":
    pub_tg_client.start(phone=phone)
    sub_tg_client.start(phone=phone)
