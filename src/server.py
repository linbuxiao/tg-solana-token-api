from sanic import Sanic
from sanic import response
import logging
from .client import pika_channel, PULL_QUEUE
import asyncio
import json
from sanic_ext import Extend

logger = logging.getLogger(__name__)

app = Sanic(__name__)
Extend(app)


@app.get("/token/<channel>/<token>")
async def get_token_info(request, token: str, channel: str):
    pika_channel.basic_publish(
        exchange="tg",
        routing_key=f"push_token_info.{channel}.{token}",
        body=token,
    )
    timeout = 10
    while True:
        if timeout <= 0:
            return response.json({"data": None})
        try:
            method, properties, body = pika_channel.basic_get(PULL_QUEUE)
            if body:
                route_keys = method.routing_key.split(".")
                token = route_keys[-1]
                channel = route_keys[-2]
                if token == token and channel == channel:
                    pika_channel.basic_ack(method.delivery_tag)
                    return response.json(
                        {"channel": channel, "data": json.loads(body.decode())}
                    )
        except Exception as e:
            logger.error(e)
            return response.json({"data": None})
        await asyncio.sleep(1)
        timeout -= 1


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
