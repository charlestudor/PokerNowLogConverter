from card import Card
from utils import eval_final_hand, PokerHand


def test_hand_eval_high_card():
    community_board = [Card('s3'), Card('s7'), Card('hJ'), Card('cA'), Card('h2')]
    hole_cards = [Card('h9'), Card('h4')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "high card Ace"
    assert best_hand[1] == PokerHand.HIGH_CARD


def test_hand_eval_pair_hole():
    community_board = [Card('s3'), Card('s7'), Card('hJ'), Card('cA'), Card('h2')]
    hole_cards = [Card('h9'), Card('c9')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a pair of Nines"
    assert best_hand[1] == PokerHand.PAIR


def test_hand_eval_pair_community():
    community_board = [Card('s3'), Card('s7'), Card('h3'), Card('cA'), Card('h2')]
    hole_cards = [Card('h9'), Card('c8')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a pair of Threes"
    assert best_hand[1] == PokerHand.PAIR


def test_hand_eval_pair_mixed():
    community_board = [Card('s3'), Card('s7'), Card('hJ'), Card('cA'), Card('h2')]
    hole_cards = [Card('c2'), Card('c9')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a pair of Deuces"
    assert best_hand[1] == PokerHand.PAIR


def test_hand_eval_two_pair_hole():
    community_board = [Card('s3'), Card('h3'), Card('hJ'), Card('cA'), Card('h2')]
    hole_cards = [Card('h9'), Card('c9')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "two pair, Nines and Threes"
    assert best_hand[1] == PokerHand.TWO_PAIR


def test_hand_eval_two_pair_community():
    community_board = [Card('s2'), Card('h3'), Card('hJ'), Card('cJ'), Card('h2')]
    hole_cards = [Card('h8'), Card('c9')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "two pair, Jacks and Deuces"
    assert best_hand[1] == PokerHand.TWO_PAIR


def test_hand_eval_two_pair_mixed():
    community_board = [Card('h9'), Card('s7'), Card('hJ'), Card('cA'), Card('h2')]
    hole_cards = [Card('c2'), Card('c9')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "two pair, Nines and Deuces"
    assert best_hand[1] == PokerHand.TWO_PAIR


def test_hand_eval_set():
    community_board = [Card('h9'), Card('s7'), Card('hJ'), Card('cA'), Card('h2')]
    hole_cards = [Card('s9'), Card('c9')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "three of a kind, Nines"
    assert best_hand[1] == PokerHand.THREE_OF_KIND


def test_hand_eval_straight():
    community_board = [Card('h8'), Card('s7'), Card('hJ'), Card('cA'), Card('hT')]
    hole_cards = [Card('s6'), Card('c9')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a straight, Seven to Jack"
    assert best_hand[1] == PokerHand.STRAIGHT


def test_hand_eval_straight_ace_low():
    community_board = [Card('h4'), Card('s5'), Card('hJ'), Card('cA'), Card('hT')]
    hole_cards = [Card('s2'), Card('c3')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a straight, Ace to Five"
    assert best_hand[1] == PokerHand.STRAIGHT


def test_hand_eval_flush():
    community_board = [Card('h4'), Card('s5'), Card('hJ'), Card('sA'), Card('sT')]
    hole_cards = [Card('s2'), Card('s3')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a flush, Ace high"
    assert best_hand[1] == PokerHand.FLUSH


def test_hand_eval_full_house():
    community_board = [Card('h3'), Card('s5'), Card('hT'), Card('sA'), Card('sT')]
    hole_cards = [Card('c3'), Card('s3')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a full house, Threes full of Tens"
    assert best_hand[1] == PokerHand.FULL_HOUSE


def test_hand_eval_four_of_kind():
    community_board = [Card('h2'), Card('d2'), Card('hJ'), Card('sA'), Card('sT')]
    hole_cards = [Card('s2'), Card('c2')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "four of a kind, Deuces"
    assert best_hand[1] == PokerHand.FOUR_OF_KIND


def test_hand_eval_straight_flush():
    community_board = [Card('s4'), Card('s5'), Card('s6'), Card('sJ'), Card('sT')]
    hole_cards = [Card('s2'), Card('s3')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a straight flush, Deuce to Six"
    assert best_hand[1] == PokerHand.STRAIGHT_FLUSH


def test_hand_eval_straight_flush_ace_low():
    community_board = [Card('s4'), Card('s5'), Card('sJ'), Card('sA'), Card('sT')]
    hole_cards = [Card('s2'), Card('s3')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a straight flush, Ace to Five"
    assert best_hand[1] == PokerHand.STRAIGHT_FLUSH


def test_hand_eval_royal_flush():
    community_board = [Card('h4'), Card('dK'), Card('dJ'), Card('sA'), Card('dT')]
    hole_cards = [Card('dQ'), Card('dA')]

    all_cards = community_board + hole_cards
    best_hand = eval_final_hand(all_cards)

    assert best_hand[0] == "a royal flush"
    assert best_hand[1] == PokerHand.ROYAL_FLUSH
