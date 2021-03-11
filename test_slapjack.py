from unittest import TestCase, mock
from slapjack import Slapjack, Card


class TestSlapjack(TestCase):
    def setUp(self) -> None:
        self.slapjack = Slapjack(1, 1)

    def test__create_stack(self):
        self.assertEqual(len(self.slapjack._create_stack(1)), 52)
        self.assertEqual(len(self.slapjack._create_stack(2)), 2 * 52)
        self.assertEqual(len(self.slapjack._create_stack(3)), 3 * 52)

    @mock.patch('slapjack.input', create=True)

    def test__draw_card(self):
        self.initial_deal()
        drawn_card = self.slapjack.player_draw_card(0)
        self.assertLess(drawn_card.number, 14)
        self.assertGreater(drawn_card.number, 0)

