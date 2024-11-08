from .client import sub_tg_client, phone, pika_channel
from telethon import events
from pydantic import BaseModel
from telethon.types import Message
from telethon.extensions import html
from bs4 import BeautifulSoup
import re

sub_tg_client.start(phone=phone)


class DogeTokenInfo(BaseModel):
    token: str
    name: str
    price: str
    market_cap: str


@sub_tg_client.on(events.NewMessage(chats=[-4553091547]))
async def token_info_api(event: events.NewMessage.Event):
    msg: Message = event.message
    content = html.unparse(msg.message, msg.entities)
    bs = BeautifulSoup(content, "html.parser")
    # get <code> tag element
    code_tag = bs.find("code")
    if not code_tag:
        return
    token = code_tag.text
    name = bs.find("a", href=lambda href: "https://solscan.io/token/" in href).text
    # 提取市值
    market_cap_pattern = r"市值：<strong>(.*?)</strong>"
    market_cap = re.search(market_cap_pattern, content).group(1)

    # 提取价格
    price_pattern = r"价格：<strong>(.*?)</strong>"
    price = re.search(price_pattern, content).group(1).strip()
    data = DogeTokenInfo(token=token, name=name, price=price, market_cap=market_cap)
    pika_channel.basic_publish(
        exchange="tg",
        routing_key=f"pull_token_info.doge.{token}",
        body=data.model_dump_json(),
    )


if __name__ == "__main__":
    sub_tg_client.run_until_disconnected()
