import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange

from asyncio_mqtt import Client, MqttError

game_uuid, game_term_password, game_owner = ['foodstuffs', 'weedses', 'bob']


async def example():
    async with Client("localhost") as client:
        async with client.filtered_messages("game/" + str(game_uuid) + "/stacks") as messages:
            await client.subscribe("game/#")
            async for message in messages:
                message_str = message.payload.decode()
                print(message_str)


async def main():
    # Run the advanced_example indefinitely. Reconnect automatically
    # if the connection is lost.
    print("hello testing")
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await example()
        except MqttError as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)


# Change to the "Selector" event loop
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Run your async application as usual
asyncio.run(main())