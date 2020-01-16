#!/usr/bin/env python3

# pip install websockets

import asyncio
import json
import logging
import socket
import time

import websockets
from common import (Client, ClientDisconnectReport, ClientReport,
                    OffsetTransform, Position, Rotation)

logging.basicConfig(level=logging.INFO)

clients = {}


def state_event(websocket):
    client_report = ClientReport(clients[websocket])
    return json.dumps({"type": "state", **client_report.to_dict()})


def disconnect_event(websocket):
    client_disconnect_report = ClientDisconnectReport(clients[websocket])
    return json.dumps(
        {"type": "disconnect", **client_disconnect_report.to_dict()})


def clients_event():
    return json.dumps({"type": "clients", "count": len(clients)})


def ip_address_event(websocket):
    return json.dumps({
        "type": "ipAddress", "ipAddress": websocket.remote_address[0]
    })


async def notify_disconnect(reporting_websocket):
    if clients:  # asyncio.wait doesn't accept an empty list
        message = disconnect_event(reporting_websocket)
        for client_websocket in clients:
            if client_websocket == reporting_websocket:
                continue
            await client_websocket.send(message)


async def notify_state(reporting_websocket):
    if clients:  # asyncio.wait doesn't accept an empty list
        message = state_event(reporting_websocket)
        for client_websocket in clients:
            if client_websocket == reporting_websocket:
                continue
            await client_websocket.send(message)


async def notify_clients(reporting_websocket):
    if clients:  # asyncio.wait doesn't accept an empty list
        message = clients_event()
        for client_websocket in clients:
            await client_websocket.send(message)


async def update_client_from_websocket(websocket):
    async for message in websocket:
        websocket_data = json.loads(message)
        clients[websocket].name = websocket_data["clientName"]
        clients[websocket].address = websocket.remote_address[0]
        clients[websocket].offset_transform = OffsetTransform(
            Position.from_dict({
                "positionX": websocket_data["positionX"],
                "positionY": websocket_data["positionY"],
                "positionZ": websocket_data["positionZ"]
            }),
            Rotation.from_dict({
                "rotationX": websocket_data["rotationX"],
                "rotationY": websocket_data["rotationY"],
                "rotationZ": websocket_data["rotationZ"]
            })
        )
        clients[websocket].timestamp = websocket_data["lastTimestamp"]
        clients[websocket].data = websocket_data["data"] or {}
        await notify_state(websocket)


async def register(websocket, websocket_data):
    if websocket not in clients:
        try:
            timestamp = websocket_data["lastTimestamp"]
        except KeyError:
            timestamp = time.time()
        client = Client(
            websocket=websocket,
            name=websocket_data["clientName"],
            address=websocket.remote_address[0],
            timestamp=timestamp
        )
        clients[websocket] = client
        logging.info(
            f"{websocket.remote_address[0]} has registered. "
            f"(name: {client.name})"
        )
        logging.info(f"{len(clients)} clients connected.")
        await websocket.send(ip_address_event(websocket))
        await notify_clients(websocket)


async def unregister(websocket, reason):
    await notify_disconnect(websocket)
    if websocket in clients:
        client_name = clients[websocket].name
        del clients[websocket]
        logging.info(
            f"{websocket.remote_address[0]}"
            " has unregistered "
            f"(name: {client_name})"
            f"({reason})"
        )
        logging.info(f"{len(clients)} clients connected.")
    await notify_clients(websocket)


async def ingest(websocket, path):
    try:
        async for message in websocket:
            websocket_data = json.loads(message)
            if websocket_data["type"] == "connect":
                await register(websocket, websocket_data)
            elif websocket_data["type"] == "sync":
                logging.debug(websocket_data)
                await update_client_from_websocket(websocket)
    except websockets.ConnectionClosed as error:
        await unregister(websocket, error)
    except asyncio.streams.IncompleteReadError as error:
        await unregister(websocket, error)


start_server = websockets.serve(ingest, "0.0.0.0", 6789, ping_interval=None)
asyncio.get_event_loop().run_until_complete(start_server)
logging.info(f"Server started at {socket.gethostname()}:6789")
asyncio.get_event_loop().run_forever()
