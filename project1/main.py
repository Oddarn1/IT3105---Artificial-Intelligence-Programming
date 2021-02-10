from game.board import Board
from game.board_visualizer import BoardVisualizer
from actor.actor import Actor
from critic.nn_critic import CriticNN
from critic.table_lookup_critic import TableLookupCritic
import numpy as np
import time
import copy


# ------ VARIABLES --------
# Board and Game Variables
board_type = "T"  # "T" or "D"
board_size = 4
open_cells = [(1, 0)]
number_of_episodes = 100
display_episode = number_of_episodes - 1  # Display final run
display_delay = 2  # Number of seconds between board updates in visualization

# Critic Variables
critic_method = "NN"  # "TL" or "NN"
critic_nn_dims = (10, 20, 30, 5, 1)
lr_critic = 0.001
eligibility_decay_critic = 0.95
discount_factor_critic = 0.95
table_lookup = False

# Actor Variables
lr_actor = 0.1
eligibility_decay_actor = 0.95
discount_factor_actor = 0.95
epsilon = 0.4
epsilon_decay = 0.9
# -------------------------

# ------- FUNCTIONS -------
def find_saps(board):
    saps = []
    if board.check_losing_state() or board.check_winning_state():
        return saps
    else:
        moves = board.get_all_legal_moves()
        for move in moves:
            board_copy = copy.deepcopy(board)
            board_copy.make_move(move)
            saps.append((board.board_state(), move))
            saps = saps + find_saps(board_copy)
        return saps


def create_critic(
    method, nn_dimensions, lr, eligibility_decay, discount_factor, board, table_lookup
):
    if table_lookup:
        return TableLookupCritic(board, lr, eligibility_decay, discount_factor)
    return CriticNN(
        lr, nn_dimensions, eligibility_decay, discount_factor, nn_dimensions[0], board
    )


def run_game_instance(board, actor, critic, visualize=False):
    actor.reset_eligibility(board)
    critic.reset_eligibility()
    action = actor.select_action(board)
    state_and_rewards = []
    state_and_rewards.append((board.board_state(), 0))
    state_and_action = []
    state_and_action.append((board.board_state(), action))
    while True:
        prev_state, prev_action = board.board_state(), action
        board.make_move(action)
        reward = board.get_reward()
        state_and_rewards.append((board.board_state(), reward))
        state_and_action.append((board.board_state(), action))
        if board.check_losing_state() or board.check_winning_state():
            if board.check_winning_state():
                print("WIN")
                board.reset_board()
                return 1
            board.reset_board()
            return 0
        action = actor.select_action(board)
        actor.update_eligibility(prev_state, prev_action, 1)
        critic.update_eligibility(prev_state, 1)
        if True:  # if critic and actor should update TODO fix this
            td_error = critic.calculate_td_error(
                prev_state, board.board_state(), reward
            )
            critic.update_expected_reward(state_and_rewards)
            actor.update(td_error, state_and_action)
        if visualize:
            boardVisualizer.draw_board(board.board, board.board_type)
            time.sleep(display_delay)  # Sleep to display the board for some time


# -------------------------

# Main-function for running everything
if __name__ == "__main__":

    # Initialize all components
    board = Board(board_type=board_type, board_size=board_size, open_cells=open_cells)
    boardVisualizer = BoardVisualizer(width=1000, height=800)
    actor = Actor(
        lr=lr_actor,
        eligibility_decay=eligibility_decay_actor,
        discount_factor=discount_factor_actor,
        initial_epsilon=epsilon,
        epsilon_decay_rate=epsilon_decay,
    )
    critic = create_critic(
        method=critic_method,
        nn_dimensions=critic_nn_dims,
        lr=lr_critic,
        eligibility_decay=eligibility_decay_critic,
        discount_factor=discount_factor_critic,
        board=board,
        table_lookup=False,
    )
    actor.init_policy(board)

    # Run episodes
    # TODO: Init V(s) for Critic
    number_of_wins = 0
    for i in range(number_of_episodes):
        actor.eps *= actor.eps_dec
        print("Episode %d" % i)
        number_of_wins += run_game_instance(board, actor, critic)
    print("Finished with %d wins in %d episodes" % (number_of_wins, number_of_episodes))
