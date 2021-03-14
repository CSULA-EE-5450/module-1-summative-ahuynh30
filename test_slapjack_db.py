from slapjack_db import AsyncSlapjackGameDB
from user_db import UserDB
import pytest
import asyncio

TEST_USER = 'tester'


@pytest.fixture
def base_user_db():
    the_user_db = UserDB()
    username, passtoken = the_user_db.create_user(TEST_USER)
    return the_user_db, username, passtoken


@pytest.fixture
def base_game_db(base_user_db):
    return AsyncSlapjackGameDB(base_user_db[0])


@pytest.mark.asyncio
async def test_add_game(base_game_db):
    game_uuid, game_term_password, game_owner = await base_game_db.add_game("123", 1, TEST_USER, 2)
    assert len(game_term_password) == 36
    assert game_owner == TEST_USER
    assert base_game_db._current_games_info[game_uuid].termination_password == game_term_password
    assert base_game_db._current_games[game_uuid].num_players == 1

if __name__ == '__main__':
    pytest.main()
