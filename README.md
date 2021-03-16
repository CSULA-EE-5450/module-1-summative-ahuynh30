# EE 5450 Module 1 Summative
Add your text here.  If you would like a 
Markdown cheatsheet: https://www.markdownguide.org/cheat-sheet/

# Slapjack in MQTT
Rules to Slapjack: Choose the number of players and decks 
you would like to use to play. Then deal cards to all players place cards in order from 0-#
slap only pairs or jacks
if slapping wrong card
then put 2 card more cards in the pile
if you run out of cards you lose

## Commands for MQTT game
```
Game commands must alway start with "game_commands:" followed by the message string 
game_commands: message
they are also sent to the topic: game_commands

The game commands we have are:
welcome:
create_game:
start_game:
create_user:
add_player:
get_winner:
player_action:
```
### welcome: message
```
The welcome: message command will send the 
command to print the Welcome to MQTT Slapjack!
```
### create_game: game_room, num_decks, num_players, owner_name
```
The create_game: message command will prompt 
the server to create a game using the parameters 
in the message given. The parameters that it needs 
are how many decks do you want to use, number of players, 
and the owner of the game room.
```
### start_game: game_room
```
The start_game: message command will prompt the 
server to start the game for the given game_room 
in the message sent.
```
### create_user: username
```
The create_user: message command will prompt the 
server to create the username and add them to the 
user_base topic with their username and password
```
### add_player: game_room, user
```
The add_player: message command will prompt the 
server to add a user to a game for the game_room 
mentioned. The parameters given needed are game_room
and the username of the user that you want to add.
```
### get_winner: game_room
```
The get_winner: message command will prompt the 
server to retrieve the player that has won and 
print the winning message in the mentioned game_room
```
### player_action: game_room, user, action
```
The player_action: message command will prompt the
server to execute the players action they wanted to 
do. The parameters that are needed are the game room number,
the user that is executing the action, and what action they want.
The actions avaiable are: slap, draw.
If there is an invalid move being made, the game will return that 
it was an invalid move. If the user slapped before it was possible,
then they will be punished and lose 2 cards. If the players deck 
ever reaches 0 they cannot make anymore moves.
```