import asyncio
from slapjack_db import AsyncSlapjackGameDB, Slapjack
from user_db import UserDB
from asyncio_mqtt import Client, MqttError

USER_DB = UserDB()
SLAPJACK_DB = AsyncSlapjackGameDB(USER_DB)


async def get_game(client, message) -> Slapjack:
    """
    Get a game from the slapjack game database, otherwise raise a 404.
    FORMAT of message "game_room"
    :param client: the MQTT client
    :param message: the uuid in str of the game to retrieve which is got from message
    """

    message_split = message.split(", ")
    game_room = message_split[0]
    the_game = await SLAPJACK_DB.get_game(game_room)
    if the_game is None:
        error_message = "ERROR: game_id: " + str(game_room) + " not found."
        await client.publish("game/error", error_message, qos=1)
        raise MqttError(error_message)
    return the_game


async def home(client):
    await client.publish("game/home/message", "Welcome to MQTT Slapjack!", qos=1)


async def create_game(client, message, test: bool = False):
    """
    Create game using MQTT inputs
    FORMAT of message "game_room, num_players, num_decks, owner name"
    :param test: if testing with pytest will be true, default is false
    :param client: the MQTT client
    :param message: the message command string
    :return:
    """
    test_str = []
    message_split = message.split(', ')
    game_room = message_split[0]
    num_players = message_split[1]
    num_decks = message_split[2]
    owner_user = message_split[3]
    if not test:
        await client.publish(("game_room/" + str(game_room) + "/create_success"), "True", qos=1)
        await client.publish(("game_room/" + str(game_room) + "/num_players"), num_players, qos=1)
        await client.publish(("game_room/" + str(game_room) + "/num_decks"), num_decks, qos=1)
    game_id, term_pass, owner = await SLAPJACK_DB.add_game(game_room=game_room,
                                                           num_players=int(num_players),
                                                           num_decks=int(num_decks),
                                                           owner=owner_user)
    game_info = await SLAPJACK_DB.get_game_info(game_id)
    player_list = game_info.players
    player_list.append(owner)
    player_idx = player_list.index(owner)
    if not test:
        await client.publish(("game_room/" + str(game_room) + "/term_pass"), term_pass, qos=1)
        await client.publish(("game_room/" + str(game_room) + "/owner"), owner, qos=1)
        await client.publish(("game_room/" + str(game_room) +
                              "/player_list/" + str(owner)),
                             "player_idx: " + str(player_idx), qos=1)
    else:
        test_str.append("game_room/" + str(game_room) + "/term_pass")
        test_str.append("game_room/" + str(game_room) + "/owner")
        test_str.append("game_room/" + str(game_room) + "/player_list/" + str(owner))
        return test_str


async def init_game(client, message, test: bool = False):
    """
    FORMAT of message "game_room"
    starts the game for the specified game room and will
    print the player stacks and main stack
    :param test: if testing with pytest will be true, default is false
    :param client: the MQTT client
    :param message: the message command string
    :return:
    """
    game_room = message
    the_game = await get_game(client, game_room)
    the_game.initial_deal()
    if not test:
        await client.publish("game_room/" + str(game_room), "Game started", qos=1)
        await show_stack(client, message)


async def show_stack(client, message, test: bool = False):
    """
    prints the stack to display in the MQTT server for each
    game_room whenever it is called and will update the stacks shown
    FORMAT of message "game_room, anything after doesnt matter just needs game_room"
    format is like this because of how show_stack is called in different functions
    so the messages would be different except the gamer_room
    :param client: the MQTT client
    :param message: the message command string
    :param test: if testing with pytest will be true, default is false
    :return:
    """
    test_str = []
    message_split = message.split(", ")
    game_room = message_split[0]
    the_game = await get_game(client, game_room)
    game_info = await SLAPJACK_DB.get_game_info(game_room)
    player_list = game_info.players
    player_stacks = the_game.get_player_stacks()
    main_stack = the_game.get_main_stack()
    current_card = the_game.get_current_card()
    previous_card = the_game.get_previous_card()
    if not test:
        await client.publish(("game_room/" + str(game_room) + "/Main_stack"), str(main_stack), qos=1)
        await client.publish(("game_room/" + str(game_room) + "/previous_card"), str(previous_card), qos=1)
        await client.publish(("game_room/" + str(game_room) + "/current_card"), str(current_card), qos=1)
    for player in player_list:
        player_idx = await get_player_idx(game_room, player)
        if not test:
            await client.publish(("game_room/" + str(game_room) +
                                  "/player_list/" + str(player) +
                                  "/stack"), str(player_stacks[player_idx]), qos=1)
            await client.publish(("game_room/" + str(game_room) +
                                  "/player_list/" + str(player) +
                                  "/cards_left"), str(len(player_stacks[player_idx])), qos=1)
        else:
            test_str.append("game_room/" + str(game_room) +
                            "/player_list/" + str(player) +
                            "/stack"), str(player_stacks[player_idx])
            test_str.append("game_room/" + str(game_room) +
                            "/player_list/" + str(player) +
                            "/cards_left")
    return test_str


async def get_player_idx(game_room, username):
    """
    Gets the player index of a particular user within a game.
    :param game_room: Room number
    :param username: The target username
    :return: The index of the user within the game room number
    """
    game_info = await SLAPJACK_DB.get_game_info(game_room)
    player_list = game_info.players
    player_idx = player_list.index(username)
    return player_idx


async def create_user(client, message, test: bool = False):
    """
    creates a user with the message name given and will create it if a username is given
    FORMAT "username"
    :param test: if testing with pytest will be true, default is false
    :param client:
    :param message:
    :return:
    """
    test_str = []
    user = message
    if user is None:
        if not test:
            await client.publish("game/error",
                                 "ERROR: Username not entered for found!", qos=1)
            raise MqttError("ERROR: Username not entered for found!")
        else:
            return "ERROR: Username not entered for found!"
    else:
        username, password = UserDB.create_user(self=USER_DB, username=user)
        if not test:
            await client.publish("user_base/" + str(user) + "/username", str(username), qos=1)
            await client.publish("user_base/" + str(user) + "/password", str(password), qos=1)
        else:
            test_str.append("user_base/" + str(user) + "/username")
            test_str.append("user_base/" + str(user) + "/password")
            return test_str


async def add_player_to_game(client, message, test: bool = False):
    """
    Will add a player to a game that exists in the database.
    the user must publish a message of his desired username
    under the designated topic and message in the format below.
    FORMAT of message is "game_id, user_adding"
    :param test: if testing with pytest will be true, default is false
    :param client: the MQTT client
    :param message: the message command string
    :return: sending player added to game
    """
    message_split = message.split(", ")
    game_room = message_split[0]
    user_adding = message_split[1]
    try:
        game_info = await SLAPJACK_DB.get_game_info(message_split[0])
        player_list = game_info.players
    except KeyError:
        if not test:
            await client.publish(("game_room/" + str(game_room) + "/error"),
                                 "ERROR: Please enter message in correct format!", qos=1)
            raise MqttError("ERROR: Please enter message in correct format!")
        else:
            return "ERROR: Please enter message in correct format!"

    if len(player_list) == game_info.num_players:
        await client.publish(("game_room/" + str(game_room) + "/error"),
                             "ERROR: Room is full. Max players capped!", qos=1)
        raise MqttError("ERROR: Room is full. Max players capped!")
    else:
        if user_adding not in player_list:
            player_list.append(user_adding)
            player_idx = player_list.index(user_adding)
            if not test:
                await client.publish(("game_room/" + str(game_room) +
                                      "/player_list/" + str(user_adding)),
                                     "player_idx: " + str(player_idx), qos=1)
            else:
                return "game_room/" + str(game_room) + "/player_list/" + str(user_adding)
        else:
            if not test:
                await client.publish(("game_room/" + str(game_room) + "/error"),
                                     "ERROR: Player already added!", qos=1)
                raise MqttError("ERROR: Player already added!")
            else:
                return "ERROR: Player already added!"


async def player_action(client, message, test: bool = False):
    """
    player slaps the card or draws a card down
    message layout, "game_room, player_name, action"
    actions are "slap" or "draw"
    :param client: the MQTT client
    :param message: the message command string:
    :param test: if testing with pytest will be true, default is false
    :return:
    """
    message_split = message.split(", ")
    game_room = message_split[0]
    player_name = message_split[1]
    player_idx = await get_player_idx(game_room, player_name)
    action = message_split[2]
    the_game = await get_game(client, game_room)
    game_info = await SLAPJACK_DB.get_game_info(game_room)
    player_stack = the_game.get_player_stacks()
    if len(player_stack[player_idx]) <= 0:
        if not test:
            await client.publish(("game_room/" + str(game_room) +
                                  "/player_list/" + str(player_name) +
                                  "/action"), "No more cards you lose!.", qos=1)
    else:
        if action == "slap":
            if len(player_stack[player_idx]) <= 1:
                if not test:
                    await client.publish(("game_room/" + str(game_room) +
                                          "/player_list/" + str(player_name) +
                                          "/action"), "No more cards you lose!.", qos=1)
                the_game = await get_game(client, message)
                the_game.player_draw_card(player_idx, True)
            else:
                if player_name in game_info.players:
                    the_game = await get_game(client, message)
                    if the_game.round_winner(player_idx):
                        if not test:
                            await client.publish(("game_room/" + str(game_room) +
                                                  "/player_list/" + str(player_name) +
                                                  "/action"), "SLAPJACK! take the pile.", qos=1)
                    else:
                        if not test:
                            await client.publish(("game_room/" + str(game_room) +
                                                  "/player_list/" + str(player_name) +
                                                  "/action"), "Can't slap that, lose 2 cards.", qos=1)
                        else:
                            return "Can't slap that, lose 2 cards."

        elif action == "draw":
            if player_name in game_info.players:
                the_game = await get_game(client, message)
                drawn_card = the_game.player_draw_card(player_idx, False)
                await client.publish(("game_room/" + str(game_room) +
                                      "/player_list/" + str(player_name) +
                                      "/action"), "Played down a " + str(drawn_card), qos=1)
        else:
            await client.publish(("game_room/" + str(game_room) + "/error"),
                                 "ERROR: Invalid Action!", qos=1)
            raise MqttError("ERROR: Invalid Action!")
        await show_stack(client, message)


async def get_winner(client, message, test: bool = False):
    """
    Format "Game_room"
    gets game_room and returns the winners
    :param client: the MQTT client
    :param message: the message command string
    :param test: if testing with pytest will be true, default is false
    :return:
    """
    test_str = []
    message_split = message.split(", ")
    game_room = message_split[0]
    the_game = await get_game(client, message)
    winner_list = the_game.compute_winners()
    for idx in range(len(winner_list)):
        if winner_list[idx] == "WIN":
            if not test:
                await client.publish(("game_room/" + str(game_room) +
                                      "/winner"), "Player " + str(idx) + " is the Winner", qos=1)
            else:
                test_str.append("Player " + str(idx) + " is the Winner")
    return test_str


async def message_handler():
    """
    runs MQTT client and message handler using different messages commands
    """
    async with Client("localhost") as client:
        await client.subscribe("#")
        async with client.filtered_messages("game_commands") as messages:
            async for message_mqtt in messages:
                message = message_mqtt.payload.decode()
                message_split = message.split(": ")
                message_command = message_split[0]
                message_param = message_split[1]
                if message_command == "welcome":
                    await home(client)
                if message_command == "create_game":
                    await create_game(client, message_param)
                if message_command == "start_game":
                    await init_game(client, message_param)
                if message_command == "create_user":
                    await create_user(client, message_param)
                if message_command == "add_player":
                    await add_player_to_game(client, message_param)
                if message_command == "get_winner":
                    await get_winner(client, message_param)
                if message_command == "player_action":
                    await player_action(client, message_param)


async def main():
    # Run the advanced_example indefinitely. Reconnect automatically
    # if the connection is lost.
    print("hello testing")
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await message_handler()
        except MqttError as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)


# Change to the "Selector" event loop
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Run your async application as usual
if __name__ == '__main__':
    asyncio.run(main())
