# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 19:05:37 2020

@author: Tudor Dorobantu
"""

import random
import numpy as np
from itertools import chain, combinations
from collections import namedtuple
from operator import attrgetter

class TexasHoldem:
    """
        Initializes TexasHoldem Table. Works with Player class.
        The rules to the game may be found here:
            https://en.wikipedia.org/wiki/Texas_hold_em

        Example:
            game = TexasHoldem(['TUDOR', 'ANDREW'], 100, 2)
            Initializes a TexasHoldem game with two players, 100 chip count for each player
            and 2 chip big blind limit.

        Constants:
            RANKS(list): List containing card ranks of a typical standard 52-card deck of French playing cards.
            Ranks are stored as str type. The rank values are as follows - 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'
            SUITS(list): List containing card suits of a typical standard 52-card deck of French playing cards.
            Suits are stored as str type. The suit values are as follows - 'spades', 'clubs', 'diamonds', 'hearts'
            RANK_NUM(dict): Dictionary containg the int value of each of the face cards - {'A' : 14, 'K': 13, 'Q': 12, 'J': 11}
            Card(namedtuple): Namedtuple constructor that is used to represent a card in the came e.g. card(rank='8', suit='clubs')
            represents one card of rank 8 and suit clubs.

        Args:
            players (list): List contatining player names as str type.
            buy_in (int): Value represeting the chip count of each player at the start of the game.
            big_blind (int): Big-blind limit.

        Attributes:
            players(list): List contatining player names as str type.
            buy_in (int): Value represeting the fortune of each player at the start of the game.
            deck (list): Playing card deck as a list of namedtuples in the format card('rank', 'suit')
            table(dict): State of all players as dict with format {'name': Player} where Player is the
            class created by the Player class
            community_cards(list): List containing cards on Poker Table; initialized as empty list
            big_blind(int): Big-blind limit.
            small_blind(int): Small-blind limit; initialized as half the big-blind limit - e.g. if big-blind = 2
            then small-blind will be initialized with a value of 1.
            pot(int): Chip count of pot; initialized at 0
            hands_played(int): Counter to keep track of hands played; initialized at 0.
            small_blind_player(str): String containing the player name that is designated to place small-blind;
            initialized as the first entry in the players list.
            big_blind_player(str): String containing the player name that is designated to place big-blind;
            initialized as the second entry in the players list.

        Returns:
            None.

        """

    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    SUITS = ['spades', 'clubs', 'diamonds', 'hearts']
    RANK_NUM = {'A' : 14, 'K': 13, 'Q': 12, 'J': 11}
    NUM_RANK = {14 : 'A', 13 : 'K', 12 : 'Q', 11 : 'J'}
    Card = namedtuple('card', 'rank suit')

    def __init__ (self, players, buy_in, big_blind):
        self.players = players
        self.buy_in = buy_in
        self.deck = [self.Card(rank, suit) for rank in self.RANKS for suit in self.SUITS]
        self.table = {name: Player(name, None, self.buy_in) for name in players}
        self.community_cards = []
        self.big_blind, self.small_blind = big_blind, big_blind/2
        self.pot = 0
        self.hands_played = 0
        self.small_blind_player = self.players[0]
        self.big_blind_player = self.players[1]
        self.reset

    def reset_deck(self):
        """
        Resets playing card deck to its original format by modyfing deck attribute of the TexasHoldem class.
        Reshuffle deck after reset!

        Returns:
            None.

        """
        self.deck = [self.Card(rank, suit) for rank in self.RANKS for suit in self.SUITS]

    def shuffle_cards(self):
        """
        Shuffles deck by modyfing deck attribute of the TexasHoldem class.

        Returns:
            None.

        """
        random.shuffle(self.deck)

    def get_cards(self, count):
        """
        Returns n cards from the card deck using the pop method.
        The returned value is a list of namedtumples of format Card('rank', 'suit').

        Args:
            count (int): Number of cards to be selected from deck.

        Returns:
            card_set (list): List containing n cards.

        """
        card_set = []
        for card in range(count):
            card_set.append(self.deck.pop())
        return card_set

    def deal_players(self):
        """
        Deals players two cards from the deck by modyfing the cards attribute of the player class.
        deal_player uses the get_cards function

        Returns:
            None.

        """
        for player in self.players:
            self.table[player].cards = self.get_cards(2)

    def deal_board(self, flop):
        """
        Deals community cards from the deck by modyfing the community_cards attribute.

        The flop boolean tells the function to deal either three cards (flop = True) or one (flop = False).
        deal_board uses the get_cards function.
        Args:
            flop (bool): Boolean used to specify if deal is going to be flop or not

        Returns:
            None.

        """
        self.deck.pop()
        if flop:
            self.community_cards.extend(self.get_cards(3))
        else:
            self.community_cards.extend(self.get_cards(1))


    def place_bet(self, player, amount):
        """
        Places bet given a player and a chip count. Function modifies the following attributes:
            Increases Player.bet (int) attribute by amount (Args) value
            Decreases Player.fortune (int) attribute by amount (Args) value
            Increases pot (int) attribute by amount (Args) value

        Args:
            player (str): Player name.
            amount (int): Chip amount to place as bet.

        Raises:
            Exception: If player places illegal bet.
            A bet is considered illegal if it is smaller than the big-blind limit or larger than the
            players current chip count (fortune).

        Returns:
            None.

        """
        if amount > self.table[player].fortune:
            raise Exception("Action is not possible. Bet is larger than player's chip count.")
        if amount < self.big_blind:
            raise Exception("Action is not possible. Please make a bet larger than big blind.")
        self.pot += amount
        self.table[player].max_win = self.pot
        self.table[player].bet += amount
        self.table[player].fortune += -amount

    def place_small_blind(self):
        """
        Place small-blind bet. Function modifies the following attributes:
            Increases Player.bet (int) attribute by small_blind value
            Decreases Player.fortune (int) attribute by small_blind value
            Increases pot (int) attribute by small_blind value

        Raises:
            Exception: If player places illegal bet.
            A bet is considered illegal if small blind player chip count is less than the small blind value.

        Returns:
            None.

        """
        if self.small_blind > self.table[self.small_blind_player].fortune:
            raise Exception("Action is not possible. Bet is larger than player's chip count.")
        self.table[self.small_blind_player].bet += self.small_blind
        self.table[self.small_blind_player].fortune += -self.small_blind
        self.pot += self.small_blind
        self.table[self.small_blind_player].max_win = self.pot

    def place_big_blind(self):
        """
        Place big-blind bet. Function modifies the following attributes:
            Increases Player.bet (int) attribute by big_blind value
            Decreases Player.fortune (int) attribute by big_blind value
            Increases pot (int) attribute by big_blind value

        Raises:
            Exception: If player places illegal bet.
            A bet is considered illegal if big blind player chip count is less than the big blind value.

        Returns:
            None.

        """
        if self.big_blind > self.table[self.big_blind_player].fortune:
            raise Exception("Action is not possible. Bet is larger than player's chip count.")
        self.table[self.big_blind_player].bet += self.big_blind
        self.table[self.big_blind_player].fortune += -self.big_blind
        self.pot += self.big_blind
        self.table[self.big_blind_player].max_win = self.pot

    def blinds(self):
        """
        Calls place_small_blind and place_big_blind functions.

        Returns:
            None.

        """
        self.place_small_blind()
        self.place_big_blind()

    def set_blind_buttons(self):
        """
        Designates small_blind_player and big_blind_player. Uses hands_played attribute to compute index
        for small_blind_player and big_blind_player attributes.

        Returns:
            None.

        """
        small_idx = self.hands_played % len(self.players)
        big_idx = (self.hands_played + 1) % len(self.players)
        self.small_blind_player = self.players[small_idx]
        self.big_blind_player = self.players[big_idx]

    def reset(self):
        self.__init__(self.players, self.buy_in, self.big_blind)

    def print_status(self):
        print("£" *30, "\n")
        print(f"TEXAS HOLD'EM with ${self.buy_in} buy-in and ${self.big_blind} big-blind.")
        print(f"Playing: {self.players}\n")
        print(f"GAME {self.hands_played}")
        print("_" *30, "\n")
        print(f"Cards on Table\n {self.community_cards}\nPot: {self.pot}")
        print(f"Small Blind: {self.small_blind_player} / Big Blind: {self.big_blind_player}")
        print("_" *30, "\n")
        for player in self.players:
            self.table[player].print_status()

    def get_five_cards(self, player):
        PlayerFiveCards = namedtuple('PlayerFiveCards', 'player five_cards')
        player_cards = self.table[player].cards
        all_combs = combinations((player_cards + self.community_cards), r=5)
        return [PlayerFiveCards(player, comb) for comb in all_combs]

    def rank_to_number(self, rank):
        if rank in self.RANK_NUM:
            return self.RANK_NUM[rank]
        else:
            return int(rank)

    def number_to_rank(self, number):
        if number in self.NUM_RANK:
            return self.NUM_RANK[number]
        else:
            return int(number)

    def one_suit(self, hand):
        card_suits = [card.suit for card in hand]
        return len(set(card_suits)) ==  1

    def get_high_card(self, hand):
        card_rank = [card.rank for card in hand]
        return max([self.rank_to_number(rank) for rank in card_rank])

    def get_matched_cards(self, hand):
        RankCount = namedtuple('RankCount', 'count rank')
        card_rank = [card.rank for card in hand]
        card_num = [self.rank_to_number(rank) for rank in card_rank]
        matched_cards = [RankCount(card_num.count(rank), rank) for rank in card_num if card_num.count(rank) > 1]
        return list(set(matched_cards))

    def get_matched_cards2(self, hand):
        RankCount = namedtuple('RankCount', 'count rank')
        card_rank = [card.rank for card in hand]
        card_num = [self.rank_to_number(rank) for rank in card_rank]
        matched_cards = [RankCount(card_num.count(rank), rank) for rank in card_num]
        return list(set(matched_cards))

    def pair(self, hand):
        matched_cards = self.get_matched_cards(hand)
        if len(matched_cards) != 1 or self.flush(hand):
            return False
        elif matched_cards[0].count != 2:
            return False
        else:
            return True

    def two_pairs(self, hand):
        matched_cards = self.get_matched_cards(hand)
        if len(matched_cards) !=2 or self.flush(hand):
            return False
        elif matched_cards[0].count == 2 and matched_cards[1].count ==2:
            return True
        else:
            return False

    def three_of_a_kind(self, hand):
        matched_cards = self.get_matched_cards(hand)
        if len(matched_cards) !=1 or self.flush(hand):
            return False
        elif matched_cards[0].count != 3:
            return False
        else:
            return True

    def four_of_a_kind(self, hand):
        matched_cards = self.get_matched_cards(hand)
        if len(matched_cards) != 1 or self.flush(hand):
            return False
        elif matched_cards[0].count !=4:
            return False
        else:
            return True

    def flush(self, hand):
        other_flush = self.straight_flush(hand) or self.royal_flush(hand)
        return (self.one_suit(hand) and not other_flush)

    def is_low_ace_straight(self, hand):
        card_rank = [card.rank for card in hand]
        card_num_high_ace = [self.rank_to_number(rank) for rank in card_rank]
        card_num_low_ace = [1 if card_num == 14 else card_num for card_num in card_num_high_ace]
        card_num_low_ace.sort()
        return (np.diff(card_num_low_ace) == 1).all()

    def is_high_ace_straight(self, hand):
        card_rank = [card.rank for card in hand]
        card_num_high_ace = [self.rank_to_number(rank) for rank in card_rank]
        card_num_high_ace.sort()
        return (np.diff(card_num_high_ace) == 1).all()

    def straight(self, hand):
        if self.royal_flush(hand) or self.one_suit(hand):
            return False
        else:
            return self.is_high_ace_straight(hand) or self.is_low_ace_straight(hand)

    def straight_flush(self, hand):
        straights = self.is_high_ace_straight(hand) or self.is_low_ace_straight(hand)
        if not self.royal_flush(hand) and straights:
            return (self.one_suit(hand))
        else:
            return False

    def full_house(self, hand):
        matched_cards = self.get_matched_cards(hand)
        if len(matched_cards) != 2:
            return False
        elif list(filter(lambda rank_count: rank_count.count == 3, matched_cards)):
            return True
        else:
            False

        return (self.pair(hand) and self.three_of_a_kind(hand))

    def royal_flush(self, hand):
        ranks = [self.rank_to_number(card.rank) for card in hand]
        if min(ranks) >= 10 and self.one_suit(hand):
            return True
        else:
            False

    def sort_cards(self, cards):
        numbered_cards = [self.Card(self.rank_to_number(card.rank), card.suit) for card in cards]
        numbered_cards.sort(key = attrgetter('rank'), reverse = True)
        return [self.Card(self.number_to_rank(card.rank), card.suit) for card in numbered_cards]

    def sort_card_count(self, hands):
        card_count = [self.get_matched_cards2(hand.five_cards) for hand in hands]
        for card in card_count:
            card.sort(key=attrgetter('count', 'rank'), reverse=True)
        return card_count

    def tiebreaker(self, hands):
        sorted_hands = np.transpose(self.sort_card_count(hands))[1]
        columns = sorted_hands.shape[1]
        columns_idx = np.array(range(columns))
        sorted_hands = np.vstack((columns_idx, sorted_hands))
        row_idx = list(range(1, sorted_hands.shape[0]))
        for idx in row_idx:
            col_filter = sorted_hands[idx] == np.max(sorted_hands[idx])
            sorted_hands = sorted_hands[:, col_filter]
        if sorted_hands.shape[1] == 1:
            return hands[int(sorted_hands[0])]
        else:
            return 'Tie'

    def highcard_showdown(self):
        high_card = []
        kicker = []
        for player in self.players:
            high_card.append(self.get_high_card(self.table[player].cards))
            kicker.append(min([self.rank_to_number(card.rank) for card in self.table[player].cards]))
        if len(set(high_card)) != 1:
            return self.players[np.argmax(high_card)]
        elif len(set(kicker)) != 1:
            return self.players[np.argmax(kicker)]
        else:
            return 'Tie'

    def showdown_cards (self):
        available_combs = [self.get_five_cards(player) for player in self.players if not self.table[player].folded]
        return list(chain.from_iterable(available_combs))

    def top_showdown_cards(self):
        possible_hands = self.showdown_cards()
        poker_hands = [
            self.royal_flush, self.straight_flush, self.four_of_a_kind,
            self.full_house, self.flush, self.straight, self.three_of_a_kind,
            self.two_pairs, self.pair
            ]
        for hand in poker_hands:
            top_hands = list(filter(lambda showdown_combs: hand(showdown_combs.five_cards), possible_hands))
            if top_hands:
                return top_hands
        return self.highcard_showdown

    def winner(self):
        possible_hands = self.showdown_cards()
        poker_hands = [
            self.royal_flush, self.straight_flush, self.four_of_a_kind,
            self.full_house, self.flush, self.straight, self.three_of_a_kind,
            self.two_pairs, self.pair
            ]
        for hand in poker_hands:
            top_hands = list(filter(lambda showdown_combs: hand(showdown_combs.five_cards), possible_hands))
            if top_hands:
                return self.tiebreaker(top_hands)
        return self.highcard_showdown()

class Player(TexasHoldem):

    def __init__ (self, name, cards, fortune):
        self.name = name
        self.cards = cards
        self.fortune = fortune
        self.bet = 0
        self.hand = None
        self.folded = False
        self.max_win = 0

    def fold(self):
        self.folded = True

    def print_status(self):
        print(f"{self.name}\nCards: {self.cards}\nFortune: {self.fortune}\nBet: {self.bet}\n")
        print("-"*30)

"______TESTS FROM HERE__________"

"_____Initializing Game_____"


game = TexasHoldem(['TUDOR', 'ANDREW', 'JOHN'], 100, 2)

"_____Test Hands_____"

threes = game.deck[-3:]
twos = game.deck[:2]

full_house_hand = threes + twos
flush_hand = random.choices([hand for hand in game.deck if hand.suit == 'spades'], k = 5)
straight_hand = [game.Card(rank, 'diamonds') for rank in ['8', '9', '10', 'J']]
straight_hand.append(game.Card('Q', 'spades'))
straight_flush_hand = [game.Card(rank, 'clubs') for rank in ['8', '9', '10', 'J', 'Q']]
royal_flush_hand = [game.Card(rank, 'hearts') for rank in ['10', 'J', 'Q', 'K', 'A']]


"_____Shuffle Cards_____"

#game.print_status()
game.shuffle_cards()

"_____Testing Showdown Functions_____"

import winsound

"Test figures are from here -> https://en.wikipedia.org/wiki/Poker_probability"
"Tiebreaker Rules are from https://www.adda52.com/poker/poker-rules/cash-game-rules/tie-breaker-rules"
"Split Pot Logic from https://www.pokerlistings.com/rules-for-poker-all-in-situations-poker-side-pot-calculator"

sample_cards = random.choices(game.deck, k = 52)
sample_hands = list(combinations(game.deck, r=5))

poker_hands = [
    game.royal_flush, game.straight_flush, game.four_of_a_kind,
    game.full_house, game.flush, game.straight, game.three_of_a_kind,
    game.two_pairs, game.pair
    ]

poker_hand_names = [
    'Royal Flush', 'Straight Flush', 'Four of a Kind', 'Full House',
    'Flush', 'Straight', 'Three of a Kind', 'Two Pairs', 'One Pair'
    ]

poker_and_combinations = [4, 36, 624, 3744, 5108, 10200, 54912, 123552, 1098240]

test_hands2_combs = [5108, 36]

test_showdown = False

if test_showdown:
    results = [list(filter(lambda sample_hand: poker_hand(sample_hand), sample_hands)) for poker_hand in poker_hands]
    results_count = [len(result) for result in results]
    passed = [results_count[idx] == poker_and_combinations[idx] for idx in range(9)]


    for idx in range(9):
        print(f'{poker_hand_names[idx]} PASSED {passed[idx]} - {poker_and_combinations[idx]} combinations vs. {results_count[idx]} result')
    print('ALL TESTS PASSED: ', False not in passed)
    winsound.Beep(3000, 1000)

#results = random.choices([(test(hand), hand) for hand in sample_hands if test(hand) == True], k=5)

#results = [(test(hand), hand) for hand in sample_hands if test(hand) == True]
#print(len(results))

#for test_hand in results:
    #print(test_hand)

"_____Testing a Game_____"

game.deal_players()
game.blinds()
game.place_small_blind()
game.place_bet('TUDOR', 20)
game.place_bet('ANDREW', 20)
game.place_bet('JOHN', 22)
game.deal_board(flop=True)
game.place_bet('TUDOR', 30)
game.place_bet('ANDREW', 30)
game.place_bet('JOHN', 30)
game.deal_board(flop=False)
game.place_bet('TUDOR', 30)
game.place_bet('ANDREW', 30)
game.place_bet('JOHN', 30)
game.deal_board(flop = False)
game.print_status()

"""
IDEAS FOR POT SPLIT FUNCTION
create player flag that contains max pot win (this is the side pot for that player)
the function that splits the pot can use the fold attribute to determine the
next winner of the remaining side pots.
"""


#game.reset_deck()
#game.reset()