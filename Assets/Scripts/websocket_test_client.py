import asyncio
import json
import logging
import random
import time
import uuid

import websockets
from common import Client, ClientReport, OffsetTransform, Position, Rotation

logging.basicConfig(level=logging.INFO)

TIME_BETWEEN_UPDATES = 0.0166
LOW_POSITION = -3.0
HIGH_POSITION = 3.0
LOW_ROTATION = 0.0
HIGH_ROTATION = 360
FLUCTUATION_AMOUNT = 0.1

client = Client(
    name=str(uuid.uuid4()),
    timestamp=time.time()
)


def get_operand():
    if bool(random.getrandbits(1)):
        return 1
    else:
        return -1


def randomize_offset_values():
    if client.offset_transform is None:
        client.offset_transform = OffsetTransform(
            Position(
                (random.uniform(LOW_POSITION, HIGH_POSITION),
                 random.uniform(LOW_POSITION, HIGH_POSITION),
                 random.uniform(LOW_POSITION, HIGH_POSITION))
            ),
            Rotation(
                (random.uniform(LOW_ROTATION, HIGH_ROTATION),
                 random.uniform(LOW_ROTATION, HIGH_ROTATION),
                 random.uniform(LOW_ROTATION, HIGH_ROTATION))
            )
        )
    else:
        position_x_fluctuation = random.uniform(0, FLUCTUATION_AMOUNT)
        position_y_fluctuation = random.uniform(0, FLUCTUATION_AMOUNT)
        position_z_fluctuation = random.uniform(0, FLUCTUATION_AMOUNT)
        rotation_x_fluctuation = random.uniform(0, FLUCTUATION_AMOUNT)
        rotation_y_fluctuation = random.uniform(0, FLUCTUATION_AMOUNT)
        rotation_z_fluctuation = random.uniform(0, FLUCTUATION_AMOUNT)
        client.offset_transform = OffsetTransform(
            Position(
                (client.offset_transform.position.x + position_x_fluctuation *
                    get_operand(),
                 client.offset_transform.position.y + position_y_fluctuation
                 * get_operand(),
                 client.offset_transform.position.z + position_z_fluctuation
                 * get_operand())
            ),
            Rotation(
                (client.offset_transform.position.x + rotation_x_fluctuation *
                 get_operand(),
                 client.offset_transform.position.y + rotation_y_fluctuation
                 * get_operand(),
                 client.offset_transform.position.z + rotation_z_fluctuation
                 * get_operand())
            )
        )


async def hello():
    uri = "ws://0.0.0.0:6789"
    async with websockets.connect(uri, ping_interval=None) as websocket:
        client_report = ClientReport(client)
        client_connection_message = dict(client_report.to_dict())
        client_connection_message["type"] = "connect"
        await websocket.send(json.dumps(client_connection_message))
        while True:
            randomize_offset_values()
            client.timestamp = time.time()
            client_report = ClientReport(client)
            client_sync_message = dict(client_report.to_dict())
            client_sync_message["type"] = "sync"
            await websocket.send(json.dumps(client_sync_message))
            greeting = await websocket.recv()
            logging.info(greeting)
            await asyncio.sleep(TIME_BETWEEN_UPDATES)

asyncio.get_event_loop().run_until_complete(hello())
asyncio.get_event_loop().run_forever()
