import pytest
import mqtt_server
from asyncio_mqtt import Client, MqttError


def test_create_game(mqtt_server):
    async with Client("localhost") as client:
        message1 = "123, 2, 1, anthony "
        message_split = message1.split(", ")
        game_room = message_split[0]
        mqtt_server.create_game(client, message1)
        await client.subscribe("#")
        async with client.filtered_messages("game_room/" + str(game_room) + "/create_success") as messages:
            async for message_mqtt in messages:
                message = message_mqtt.payload.decode()
                assert message == "True"
