# EE 5450 Module 1 Summative
Add your text here.  If you would like a Markdown cheatsheet: https://www.markdownguide.org/cheat-sheet/

# Introduction for Slapjack game
```
plans to do chess game
rules to Slapjack:
deal cards to all players
players place cards in order from 0-#
slap only pairs or jacks
if slapping wrong card
then put 2 card more cards in the pile
if you run out of cards you lose
```
## create_stack()
```
Creates the stack of the cards (52 * num_decks), shuffled.

        :param num_decks: number of decks to use
        :return: stack of all card objects, shuffled.
```
## player_draw_card()
```
draw/ play a card down
        :return: Card object
```
## slap_card()
```
slap card if 
2 cards seen in a row ex: 2 and 2 
or
jack is seen so slap
```
## round_winner()
```
who slapped the pair or Jack gets the cards
```