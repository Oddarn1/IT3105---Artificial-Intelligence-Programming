from .board import Board
import numpy as np

class GameSimulator:

    def __init__(self, playing_board, board_size, starting_player, tree):
        self.board = Board(board_size, starting_player)
        self.playing_board = playing_board
        self.board_size = board_size
        self.tree = tree
        self.state_action = {}

    def initialize_root(self, state, player):
        player = player
        state_split = state.split()
        state = np.array([[int(i) for i in state_split[n*self.board_size:(n+1)*self.board_size]] for n in range(self.board_size)])
        self.board.player = player
        self.board.board = state


    def rollout_game(self, epsilon, board_copy):
        count = 0
        while not board_copy.check_winning_state():
            next_move = self.tree.rollout_action(board_copy, epsilon, board_copy.player)
            board_copy.make_move(next_move)
            count += 1
        return count

    def tree_search(self, board_copy):
        sequence = self.tree.traverse(board_copy, board_copy.player)
        if not sequence:
            return
        for i in sequence:
            self.state_action[(i[0],i[1])] = i[2]

    def sim_games(self, epsilon, number_of_search_games):
        count = 0
        board_copy = self.board.clone()
        self.tree.expand_tree(board_copy, board_copy.player)
        for i in range(number_of_search_games):
            self.tree_search(board_copy)
            count += self.rollout_game(epsilon, board_copy)
            rewards = {1:board_copy.get_reward(1), 2: board_copy.get_reward(2)}
            for key in self.state_action.keys():
                self.tree.update(key[1], self.state_action[key], rewards[key[0]])
            board_copy = self.board.clone()
        print(count)
        return self.tree.get_distribution(self.board)

    def reset(self, player):
        self.board = Board(self.board_size, player)
        self.state_action = {}
