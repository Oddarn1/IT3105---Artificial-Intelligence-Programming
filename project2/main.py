from NeuralNetwork.neuralnet import NeuralNet
from parameters import Parameters
from board.board import Board
from board.board_visualizer import BoardVisualizer
from board.game_simulator import GameSimulator
from Client_side.BasicClientActor import BasicClientActor
from MCTS.montecarlo import MCTS
import numpy as np

p = Parameters()
# Initialize save interval, RBUF, ANET and board (state manager)
save_interval = p.number_of_games // p.number_of_cached_anet
rbuf = {}
nn = NeuralNet(p.nn_dims, p.board_size, p.lr, p.activation_function, p.optimizer)
board = Board(p.board_size, p.starting_player)
board_visualizer = BoardVisualizer()
tree = MCTS((p.starting_player, board.get_state()), nn)
sim = GameSimulator(board, p.board_size, 1, tree)


def run_full_game(epsilon):
    board.reset_board()
    while not board.check_winning_state():
        tree.root = board.get_state()
        sim.initialize_root(tree.root, board.player)
        D = sim.sim_games(epsilon, p.number_of_search_episodes)
        rbuf[tree.root] = D
        next_move=NeuralNet.convert_to_2d_move(np.argmax(D), p.board_size)
        board.make_move(next_move)
        sim.reset()
    print(rbuf)
    nn.fit([np.concatenate((r[0], [int(i) for i in r[1].split()])) for r in rbuf.keys()],\
         [NeuralNet.normalize(rbuf[key]) for key in rbuf.keys()])


if __name__ == "__main__":
    epsilon = p.epsilon
    for game in range(p.number_of_games):
        run_full_game(epsilon)
        epsilon *= p.epsilon_decay
        if game % save_interval == 0:
            nn.save_model(f"{p.board_size}x{p.board_size}_ep", game)
