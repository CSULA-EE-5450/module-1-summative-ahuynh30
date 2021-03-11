import uvicorn
from typing import Optional
from fastapi import FastAPI, HTTPException, Path, status, Query, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slapjack_db import AsyncSlapjackGameDB, Slapjack
from user_db import UserDB

USER_DB = UserDB()
SLAPJACK_DB = AsyncSlapjackGameDB(USER_DB)
app = FastAPI(
    title="Slapjack Server",
    description="Implementation of a simultaneous multi-game Slapjack server by[Your name here]."
)
security = HTTPBasic()


async def get_game(game_id: str) -> Slapjack:
    """
    Get a game from the slapjack game database, otherwise raise a 404.

    :param game_id: the uuid in str of the game to retrieve
    """
    the_game = await SLAPJACK_DB.get_game(game_id)
    if the_game is None:
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found.")
    return the_game


@app.get('/')
async def home():
    return {"message": "Welcome to Slapjack!"}


@app.post('/user/create')
async def create_user(username: str):
    if username is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Username {username} not entered or found.")
    else:
        user, password = UserDB.create_user(self=USER_DB, username=username)
        return {'success': True,
                'username': user,
                'password': password}


@app.get('/game/create/{num_players}', status_code=status.HTTP_201_CREATED)
async def create_game(num_players: int = Path(..., gt=0, description='the number of players'),
                      num_decks: Optional[int] = Query(2, description='the number of decks to use'),
                      credentials: HTTPBasicCredentials = Depends(security)):
    user = credentials.username
    password = credentials.password
    if UserDB.is_valid(self=USER_DB, username=user, password=password):
        owner_username = user
        new_uuid, new_term_pass, game_owner = await SLAPJACK_DB.add_game(owner=owner_username,
                                                                         num_players=num_players,
                                                                         num_decks=num_decks)
        game_info = await SLAPJACK_DB.get_game_info(new_uuid)
        player_list = game_info.players
        player_list.append(owner_username)
        return {'success': True,
                'game_id': new_uuid,
                'termination_password': new_term_pass,
                'game_owner': owner_username}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Game unauthorized access and command.")


@app.post('/game/{game_id}/add_player')
async def add_player_to_game(game_id: str = Path(..., description='the unique game id'),
                             username: str = Query(..., description='the unique game id'),
                             credentials: HTTPBasicCredentials = Depends(security)):
    if username is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Username {username} not entered or found.")
    else:
        game_info = await SLAPJACK_DB.get_game_info(game_id)
        player_list = game_info.players
        if len(player_list) == game_info.num_players:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Game, Max players capped.")
        else:
            if credentials.username == game_info.owner:
                if username not in player_list:
                    player_list.append(username)
                    player_idx = player_list.index(username)
                    return {'success': True,
                            'game_id': game_id,
                            'player_username': username,
                            'player_idx': player_idx}
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"player already added.")
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail=f"Game unauthorized access and command.")


@app.get('/game/{game_id}/get_player_idx')
async def get_player_idx(game_id: str = Path(..., description='the unique game id'),
                         username: str = Query(..., description='the unique game id'),
                         credentials: HTTPBasicCredentials = Depends(security)):
    game_info = await SLAPJACK_DB.get_game_info(game_id)
    player_list = game_info.players
    idx = 0
    if credentials.username in player_list:
        for player in player_list:
            if player == username:
                player_idx = idx
                player_username = username
                return {'success': True,
                        'game_id': game_id,
                        'player_username': player_username,
                        'player_idx': player_idx}
            idx += 1
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Game unauthorized access and command.")


@app.post('/game/{game_id}/initialize')
async def init_game(game_id: str = Path(..., description='the unique game id'),
                    credentials: HTTPBasicCredentials = Depends(security)):
    game_info = await SLAPJACK_DB.get_game_info(game_id)
    if credentials.username == game_info.owner:
        the_game = await get_game(game_id)
        the_game.initial_deal()
        return {'success': True}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Game unauthorized access and command.")


@app.post('/game/{game_id}/player/{player_idx}/slap')
async def player_slap(game_id: str = Path(..., description='the unique game id'),
                      player_idx: int = Path(..., description='the player index (zero-indexed)'),
                      credentials: HTTPBasicCredentials = Depends(security)):
    game_info = await SLAPJACK_DB.get_game_info(game_id)
    if credentials.username == game_info.players[player_idx]:
        the_game = await get_game(game_id)
        the_game.slap_card()

        return {'player': player_idx,
                'current_card': str(the_game.current_card()),
                'main_stack': the_game.main_stack(),
                'player_stack': the_game.player_stacks[player_idx]}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Game unauthorized access and command.")


@app.post('/game/{game_id}/player/{player_idx}/play')
async def player_play(game_id: str = Path(..., description='the unique game id'),
                      player_idx: int = Path(..., description='the player index (zero-indexed)'),
                      credentials: HTTPBasicCredentials = Depends(security)):
    game_info = await SLAPJACK_DB.get_game_info(game_id)
    if credentials.username == game_info.players[player_idx]:
        the_game = await get_game(game_id)
        the_game.slap_card()
        drawn_card = the_game.player_draw_card(player_idx)
        return {'player': player_idx,
                'drawn_card': str(drawn_card),
                'main_stack': the_game.main_stack(),
                'player_stack': the_game.player_stacks[player_idx]}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Game unauthorized access and command.")


@app.get('/game/{game_id}/player/{player_idx}/stack')
async def player_stack(game_id: str = Path(..., description='the unique game id'),
                       player_idx: int = Path(..., description='the player index (zero-indexed)'),
                       credentials: HTTPBasicCredentials = Depends(security)):
    game_info = await SLAPJACK_DB.get_game_info(game_id)
    if credentials.username == game_info.players[player_idx]:
        the_game = await get_game(game_id)
        return {'player': player_idx,
                'player_stack': the_game.player_stacks[player_idx]}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Game unauthorized access and command.")


@app.get('/game/{game_id}/winners')
async def get_winners(game_id: str = Path(..., description='the unique game id')):
    the_game = await get_game(game_id)
    winner_list = the_game.compute_winners()
    return {'game_id': game_id,
            'winners': winner_list}


@app.post('/game/{game_id}/terminate')
async def delete_game(game_id: str = Path(..., description='the unique game id'),
                      password: str = Query(..., description='the termination password'),
                      credentials: HTTPBasicCredentials = Depends(security)):
    the_game = await SLAPJACK_DB.del_game(game_id, password, credentials.username)
    if password is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Game {password} not entered or found.")
    if the_game is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Game not found.")
    return {'success': True, 'deleted_id': game_id}


if __name__ == '__main__':
    # running from main instead of terminal allows for debugger
    # TODO: modify the below to add HTTPS (SSL/TLS) support
    uvicorn.run('web_slapjack:app', port=8000,
                log_level='info', reload=True,
                ssl_keyfile='C:/Users/agree/Documents/GitHub/module-1-summative-ahuynh30/keys/public.pem',
                ssl_certfile='C:/Users/agree/Documents/GitHub/module-1-summative-ahuynh30/keys/private.pem')
