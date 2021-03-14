from unittest import TestCase, mock
from slapjack import Slapjack, Card


class TestSlapjack(TestCase):
    def setUp(self) -> None:
        self.slapjack = Slapjack(1, 1)

    def test__create_stack(self):
        self.assertEqual(len(self.slapjack._create_stack(1)), 52)
        self.assertEqual(len(self.slapjack._create_stack(2)), 2 * 52)
        self.assertEqual(len(self.slapjack._create_stack(3)), 3 * 52)

    def test__draw_card(self):
        self.slapjack.initial_deal()
        drawn_card = self.slapjack.player_draw_card(0, False)
        self.assertLess(drawn_card.number, 14)
        self.assertGreater(drawn_card.number, 0)

    def test__slap_card(self):
        self.slapjack.initial_deal()
        self.slapjack._current_card = Card('D', 12)
        self.slapjack._previous_card = Card('S', 12)
        self.slapjack.round_winner(0)  # test successful slap
        self.assertEqual(len(self.slapjack._main_stack), 0)
        self.slapjack._previous_card = Card('S', 10)
        self.slapjack.round_winner(0)  # test the punish slap
        self.assertEqual(len(self.slapjack._main_stack), 2)

    def test__computer_winner(self):
        self.assertEqual(self.slapjack._compute_winners(0), 'LOSE')
        self.slapjack.initial_deal()
        self.assertEqual(self.slapjack._compute_winners(0), 'WIN')

    @mock.patch('blackjack.input', create=True)
    def test__player_choice(self, mocked_input: mock.Mock):
        mocked_input.side_effect = ['a', 's', 'd']
