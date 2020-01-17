"""Implement jsonrpcserver over mqtt

Prerequisite: an mqtt server listening on localhost:1883
"""

import asyncio
import signal
import logging

from jsonrpcserver import method, async_dispatch as dispatch

from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311

logger = logging.getLogger(__name__)

CMD_TOPIC = "test/jsonrpc/cmd"
RSP_TOPIC = "test/jsonrpc/rsp"

STOP = asyncio.Event()


@method
async def ping():
    await asyncio.sleep(3)
    return "pong"


def on_connect(client, flags, rc, properties):
    client.subscribe(CMD_TOPIC, qos=0)
    client.subscribe(RSP_TOPIC, qos=0)


async def on_message(client, topic, payload, qos, properties):
    logger.info("MQTT MSG [%s]: %s", topic, payload.decode())
    if topic == CMD_TOPIC:
        response = await dispatch(payload.decode())
        logger.info("response=%s", str(response))
        if response.wanted:
            client.publish(RSP_TOPIC, payload=str(response),
                           content_type="utf-8", retain=False)


async def main():
    client = MQTTClient(client_id=None)

    client.on_connect = on_connect
    client.on_message = on_message

    await client.connect('localhost', version=MQTTv311)

    # simulate sending a command on CMD_TOPIC
    client.publish(CMD_TOPIC,
                   '{"jsonrpc": "2.0", "method": "ping", "id": "1" }', qos=0)
    client.publish(CMD_TOPIC,
                   '{"jsonrpc": "2.0", "method": "ping", "id": "2" }', qos=0)

    await STOP.wait()
    await client.disconnect()


if __name__ == '__main__':
    def ask_exit(*args):
        STOP.set()

    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()

    loop.add_signal_handler(signal.SIGINT, ask_exit)
    loop.add_signal_handler(signal.SIGTERM, ask_exit)

    loop.run_until_complete(main())
