#!/usr/bin/env python3


class Position(object):

    @classmethod
    def from_dict(cls, position_dict):
        return Position(
            (
                position_dict["positionX"],
                position_dict["positionY"],
                position_dict["positionZ"]
            )
        )

    def __init__(self, position_matrix):
        self.x: float = position_matrix[0]
        self.y: float = position_matrix[1]
        self.z: float = position_matrix[2]

    def __str__(self):
        return f"x: {self.x}, y: {self.y}, z: {self.z}"

    def to_dict(self):
        return {"x": self.x, "y": self.y, "z": self.z}


class Rotation(object):

    @classmethod
    def from_dict(cls, rotation_dict):
        return Rotation(
            (
                rotation_dict["rotationX"],
                rotation_dict["rotationY"],
                rotation_dict["rotationZ"]
            )
        )

    def __init__(self, rotation_matrix):
        self.x: float = rotation_matrix[0]
        self.y: float = rotation_matrix[1]
        self.z: float = rotation_matrix[2]

    def __str__(self):
        return f"x: {self.x}, y: {self.y}, z: {self.z}"

    def to_dict(self):
        return {"x": self.x, "y": self.y, "z": self.z}


class OffsetTransform(object):

    def __init__(self, position, rotation):
        self.position: Position = position
        self.rotation: Rotation = rotation

    def __str__(self):
        return f"position: ({self.position}), rotation: ({self.rotation})"

    def to_dict(self):
        return {
            "position": self.position.to_dict(),
            "rotation": self.rotation.to_dict()
        }


class Client(object):

    def __init__(
        self, websocket=None, name=None, address=None,
        offset_transform=None, timestamp=None, data=None
    ):
        self.websocket = websocket
        self.name: str = name
        self.address: str = address
        self.offset_transform: OffsetTransform = offset_transform
        self.timestamp: float = timestamp
        self.data: dict = data or {}


class ClientReport(object):

    def __init__(self, client):
        self.name: str = client.name
        self.address: str = client.address
        self.offset_transform: OffsetTransform = client.offset_transform
        self.timestamp: float = client.timestamp
        self.data: dict = client.data

    def __str__(self):
        return (
            f"clientName: {self.name}, clientAddress: {self.address}, "
            f"offsetTransform: {self.offset_transform}, "
            f"lastTimestamp: {self.timestamp}, data: {self.data}"
        )

    def to_dict(self):
        offset_transform = None
        if self.offset_transform:
            offset_transform = self.offset_transform.to_dict()
        return {
            "clientName": self.name,
            "clientAddress": self.address,
            "positionX": offset_transform[
                "position"]["x"] if offset_transform else 0.0,
            "positionY": offset_transform[
                "position"]["y"] if offset_transform else 0.0,
            "positionZ": offset_transform[
                "position"]["z"] if offset_transform else 0.0,
            "rotationX": offset_transform[
                "rotation"]["x"] if offset_transform else 0.0,
            "rotationY": offset_transform[
                "rotation"]["y"] if offset_transform else 0.0,
            "rotationZ": offset_transform[
                "rotation"]["z"] if offset_transform else 0.0,
            "lastTimestamp": self.timestamp,
            "data": self.data
        }


class ClientDisconnectReport(object):

    def __init__(self, client):
        self.name = client.name
        self.address = client.address
        self.timestamp = client.timestamp
        self.data = client.data

    def __str__(self):
        return (
            f"clientName: {self.name}, clientAddress: {self.address}, "
            f"lastTimestamp: {self.timestamp}, data: {self.data}"
        )

    def to_dict(self):
        return {
            "clientName": self.name,
            "clientAddress": self.address,
            "lastTimestamp": self.timestamp,
            "data": self.data
        }
