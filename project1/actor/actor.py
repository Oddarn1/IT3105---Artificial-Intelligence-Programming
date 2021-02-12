import random
import copy


class Actor:
    def __init__(
        self,
        lr=0.5,
        eligibility_decay=0,
        discount_factor=0.5,
        initial_epsilon=0.1,
        epsilon_decay_rate=0.1,
    ):
        self.eps = initial_epsilon
        self.eps_dec = epsilon_decay_rate

        self.alpha = lr
        self.lam = eligibility_decay
        self.gamma = discount_factor
        self.policy = {}
        self.eligibility = {}


    def select_action(self, board):
        moves = board.get_all_legal_moves()
        random_choice = random.random()
        if random_choice < self.eps:
            return random.choice(moves)
        else:
            best_move = moves[0]
            best_reward = -10000

            for move in moves:
                if (board.board_state(), move) not in self.policy:
                    self.policy[(board.board_state(), move)] = 0
                move_reward = self.policy[(board.board_state(), move)]
                if move_reward > best_reward:
                    best_move = move
                    best_reward = move_reward
            return best_move

    def update_eligibility(self, board_state, move, elig):
        if elig == 1:
            self.eligibility[(board_state, move)] = elig
        else:
            self.eligibility[(board_state, move)] = (
                self.gamma
                * self.lam
                * self.eligibility[(board_state, move)]
            )
    
    def update(self, delta, sequence):
        """
        This updates all the evaluations of states in the episode sequence based on eligibility traces
        """
        self.eligibility[sequence[-1]] = 1
        
        for state,action in sequence:
            if not (state,action) in self.policy:
                self.policy[(state,action)] = 0.1
            self.policy[(state,action)] += self.alpha * delta * self.eligibility[(state,action)]
            self.eligibility[(state,action)] *= self.gamma * self.lam

    def reset_eligibility(self, board):
        if board.check_losing_state() or board.check_winning_state():
            return 0
        else:
            moves = board.get_all_legal_moves()
            for move in moves:
                self.eligibility[(board.board_state(), move)] = 0
                board_copy = copy.deepcopy(board)
                board_copy.make_move(move)
            return 0
