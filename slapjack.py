import math
import random
from dataclasses import dataclass
from typing import List

SLAPJACK_INSTRUCTIONS = {
    'English': {
        'WELCOME': 'Welcome to Slapjack!',
        'NUM_PLAYERS': 'How many players? ',
        'NUM_DECKS': 'How many decks? ',
        'START': 'Starting game... ',
        'PLAYER_INST': 'Type s(player0)/a(player1) to slap or d to draw.',
        'PLAYER_SLAP': 'Chose to slap',
        'PLAYER_DRAW': 'Chose to play.',
        'PLAY_AGAIN': 'Type y to play another game: '
    }
}


@dataclass
class Card(object):
    suit: str
    number: int

    @staticmethod
    def _convert_card_num_to_str(num) -> str:
        if num == 1:
            return 'A'
        elif num == 11:
            return 'J'
        elif num == 12:
            return 'Q'
        elif num == 13:
            return 'K'
        else:
            return str(num)

    def __str__(self):
        return f'{self._convert_card_num_to_str(self.number)}{self.suit}'


class Slapjack(object):
    """ Slapjack game object.
    """

    def __init__(self, num_decks: int = 1, num_players: int = 1):
        """
        Constructor for the Blackjack game object.

        :param num_decks: number of decks in this game; defaults to 1 deck
        :param num_players: number of players in this game; defaults to 1 player
        """
        self.num_players = num_players
        self._LOWEST_CARD = 1
        self._HIGHEST_CARD = 13
        spades = u"\u2660"
        hearts = u"\u2665"
        clubs = u"\u2663"
        diamonds = u"\u2666"
        self._SUITS = (spades, hearts, clubs, diamonds)
        self._num_decks = num_decks
        self._num_players = num_players
        self._main_stack = self._create_stack(num_decks)
        self._player_stacks = [[] for _ in range(self._num_players)]
        self._player_dones = [False for _ in range(self._num_players)]
        # self._player_stack_sizes = self._stack_size(num_players)
        self._current_turn = 0
        self._previous_card = " "
        self._current_card = " "

    # def _stack_size(self, num_players: int) -> List[int]:
    #     """
    #     lens the player stacks
    #     :param num_players:
    #     :return: stack sizes in order
    #     """
    #     size = []
    #     test = []
    #     try:
    #         for i in range(num_players):
    #             temp = len(self._player_stacks[i])
    #             size.append(temp)
    #         return size
    #     except IndexError:
    #         return test

    def _create_stack(self, num_decks: int) -> List[Card]:
        """
        Creates the stack of the cards (52 * num_decks), shuffled.

        :param num_decks: number of decks to use
        :return: stack of all card objects, shuffled.
        """
        the_list = []
        for _ in range(num_decks):
            for suit in self._SUITS:
                the_list.extend([Card(suit, num)
                                 for num in range(self._LOWEST_CARD, self._HIGHEST_CARD + 1)])
        random.shuffle(the_list)
        return the_list

    def get_player_stacks(self):
        return self._player_stacks

    def get_main_stack(self):
        return self._main_stack

    def get_current_card(self):
        return self._current_card

    def get_previous_card(self):
        return self._previous_card

    def player_draw_card(self, player_idx: int, silent: bool) -> Card:
        """
        Draw a card from the players stack to play.

        :return: Card object
        """
        card_played = self._player_stacks[player_idx].pop()
        self._main_stack.append(card_played)
        if not silent:
            self._previous_card = self._current_card
            self._current_card = card_played
        return card_played

    def _player_choice(self, player_idx: int) -> bool:
        """
        Ask player for the choice.

        :param player_idx:
        :return: player is done with their turn
        """
        player_input = 'g'
        while player_input not in ('a', 's', 'd'):
            player_input = input(f"Player {player_idx}: {SLAPJACK_INSTRUCTIONS['English']['PLAYER_INST']} ")
            if player_input == 's':
                if len(self._player_stacks[player_idx]) <= 0:
                    return True
                # slaps function
                print(f"Player 0: {SLAPJACK_INSTRUCTIONS['English']['PLAYER_SLAP']}")
                self.round_winner(0)
                return False
            elif player_input == 'a':
                if len(self._player_stacks[player_idx]) <= 0:
                    return True
                # slaps function
                print(f"Player 1: {SLAPJACK_INSTRUCTIONS['English']['PLAYER_SLAP']}")
                self.round_winner(1)
                return False
            elif player_input == 'd':
                if len(self._player_stacks[player_idx]) <= 0:
                    return True
                drawn_card = self.player_draw_card(player_idx, False)
                print(f"Player {player_idx}: {SLAPJACK_INSTRUCTIONS['English']['PLAYER_DRAW']}{drawn_card}")
                return False

    def slap_card(self) -> bool:
        """
        :return: if slap was done correctly
        """
        if self._current_card != " ":
            if self._current_card.number == 11:
                return True
            if self._previous_card != " ":
                if self._current_card.number == self._previous_card.number:
                    return True
        else:
            return False

    def round_winner(self, player_idx: int):
        """
        :param player_idx:
        :return: if stack is won.
        """
        if self.slap_card():
            temp = len(self._main_stack)
            for card in range(temp):
                win = self._main_stack.pop()
                self._player_stacks[player_idx].append(win)
            random.shuffle(self._player_stacks[player_idx])
            print("SLAPJACK! take the pile.")
            self._current_card = " "
            self._previous_card = " "
            return True
        else:
            punish = self._player_stacks[player_idx].pop()
            self._main_stack.append(punish)
            punish = self._player_stacks[player_idx].pop()
            self._main_stack.append(punish)
            print("Can't slap that, lose 2 cards")
            return False

    def _compute_winners(self, player_idx: int) -> str:
        """
        Computes the winners of the current game.

        :return: List of the winner between each player and the dealer.
        """
        if len(self._player_stacks[player_idx]) <= 0:
            return 'LOSE'
        else:
            return 'WIN'

    def compute_winners(self) -> List[str]:

        return [self._compute_winners(player) for player in range(0, self._num_players)]

    def deal_cards(self, player_idx: int):
        card = self._main_stack.pop()
        self._player_stacks[player_idx].append(card)
        return card

    def initial_deal(self):
        for player_idx in range(self._num_players):
            for _ in range(math.floor((self._num_decks * 52) / self._num_players)):
                self.deal_cards(player_idx)

    # noinspection PyMethodMayBeStatic
    def only1(self, done: List[bool]):
        true_found = False
        for v in done:
            if v:
                # a True was found!
                if true_found:
                    # found too many True's
                    return False
                else:
                    # found the first True
                    true_found = True
        # found zero or one True value
        return true_found

    # noinspection PyUnboundLocalVariable
    def run(self):
        print(SLAPJACK_INSTRUCTIONS['English']['START'])
        self.initial_deal()
        while not self.only1(self._player_dones):
            for player_idx in range(self._num_players):
                if not self._player_dones[player_idx]:
                    self._player_dones[player_idx] = self._player_choice(player_idx)
                    print(self._current_card)
            self._current_turn += 1

        print(f"Final winners: {self.compute_winners()}")
        return


def main():
    # print(u"\u2660")
    # print(u"\u2665")
    # print(u"\u2663")
    # print(u"\u2666")
    play_another = True
    while play_another:
        print(f"{SLAPJACK_INSTRUCTIONS['English']['WELCOME']}")
        num_players_input = int(input(f"{SLAPJACK_INSTRUCTIONS['English']['NUM_PLAYERS']}"))
        num_decks_input = int(input(f"{SLAPJACK_INSTRUCTIONS['English']['NUM_DECKS']}"))
        the_game = Slapjack(num_decks=num_decks_input, num_players=num_players_input)
        the_game.run()
        play_another_input = input(f"{SLAPJACK_INSTRUCTIONS['English']['PLAY_AGAIN']}")
        if play_another_input != 'y':
            play_another = False
    return False


if __name__ == '__main__':
    # logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=print)
    main()
