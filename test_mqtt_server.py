import pytest
from asyncio_mqtt import Client
import mqtt_server


@pytest.mark.asyncio
async def test_create_game():
    client = Client("localhost")
    message1 = "123, 2, 1, anthony"
    testing = await mqtt_server.create_game(client, message1, test=True)
    term_pass_location = testing[0]
    game_location = testing[1]
    owner_location = testing[2]
    assert term_pass_location == "game_room/123/term_pass"
    assert game_location == "game_room/123/owner"
    assert owner_location == "game_room/123/player_list/anthony"


@pytest.mark.asyncio
async def test_create_user():
    client = Client("localhost")
    message1 = None
    testing = await mqtt_server.create_user(client, message1, test=True)
    assert testing == "ERROR: Username not entered for found!"
    message1 = "anthony"
    testing = await mqtt_server.create_user(client, message1, test=True)
    username = testing[0]
    password = testing[1]
    assert username == "user_base/anthony/username"
    assert password == "user_base/anthony/password"


@pytest.mark.asyncio
async def test_add_player():
    client = Client("localhost")
    message1 = "123,, ggez"
    await mqtt_server.create_game(client, "123, 2, 1, anthony", test=True)
    testing = await mqtt_server.add_player_to_game(client, message1, test=True)
    assert testing == "ERROR: Please enter message in correct format!"
    message1 = "123, anthony"
    testing = await mqtt_server.add_player_to_game(client, message1, test=True)
    assert testing == "ERROR: Player already added!"
    message1 = "123, shiore"
    testing = await mqtt_server.add_player_to_game(client, message1, test=True)
    assert testing == "game_room/123/player_list/shiore"


@pytest.mark.asyncio
async def test_show_stack():
    client = Client("localhost")
    message1 = "123, yes"
    await mqtt_server.create_game(client, "123, 2, 1, anthony", test=True)
    await mqtt_server.add_player_to_game(client, "123, shiore", test=True)
    await mqtt_server.init_game(client, "123", test=True)
    testing = await mqtt_server.show_stack(client, message1, test=True)
    assert testing[0] == "game_room/123/player_list/anthony/stack"
    assert testing[1] == "game_room/123/player_list/anthony/cards_left"
    assert testing[2] == "game_room/123/player_list/shiore/stack"
    assert testing[3] == "game_room/123/player_list/shiore/cards_left"


@pytest.mark.asyncio
async def test_player_action():
    client = Client("localhost")
    message1 = "123, shiore, slap"  # should be invalid move
    await mqtt_server.create_game(client, "123, 2, 1, anthony", test=True)
    await mqtt_server.add_player_to_game(client, "123, shiore", test=True)
    await mqtt_server.init_game(client, "123", test=True)
    testing = await mqtt_server.player_action(client, message1, test=True)
    assert testing == "Can't slap that, lose 2 cards."


@pytest.mark.asyncio
async def test_get_winners():
    client = Client("localhost")
    message1 = "123"  # should be invalid move
    await mqtt_server.create_game(client, "123, 2, 1, anthony", test=True)
    await mqtt_server.add_player_to_game(client, "123, shiore", test=True)
    await mqtt_server.init_game(client, "123", test=True)
    testing = await mqtt_server.get_winner(client, message1, test=True)
    assert testing[0] == "Player 0 is the Winner"
    assert testing[1] == "Player 1 is the Winner"


if __name__ == '__main__':
    pytest.main()
