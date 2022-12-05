import numpy as np
import strategies.strategy_shortest_dist as strategy_shortest_dist
import strategies.strategy_random as strategy_random
import strategies.strategy_highest_outdegree as strategy_highest_outdegree
import strategies.strategy_most_pressured as strategy_most_pressured
import strategies.strategy_weighted_neighbors as strategy_weighted_neighbors

from random import randrange
from random import shuffle
# Thoughts to think about, should players be aware of the other's movement? 
# Like think about the case where they can go to the same node but the distances are different
class Game:
    def __init__(self, num_nodes, num_players, strategies=None, adj_mx =None):
        self.num_nodes = num_nodes
        self.num_players = num_players
        # to use adj_mx[node 1][node 2] is 1 if path from node 1 to node 2
        # for now create a graph of all ones TODO replace with random graph generator
        if adj_mx is not None:
            self.adj_mx = adj_mx
        else:
            self.adj_mx = self.initialize_adj_mx()
        self.player_locations = np.zeros(num_players)
        self.ownership = self.initialize_ownership()
        self.move_progress = np.zeros(num_players)
        self.move_goal = np.zeros(num_players)
        self.player_strategies = self.initialize_player_strategies(strategies)

    def initialize_adj_mx(self):
        arr = np.random.randint(1, 5, (self.num_nodes, self.num_nodes))
        arr += np.transpose(arr)
        np.fill_diagonal(arr, 0)
        return arr

    def initialize_ownership(self):
        ownership = np.ones(self.num_nodes) * -1
        for i in range(self.num_players):
            assigned = False
            while not assigned:
                index = randrange(self.num_nodes)
                if ownership[index] == -1:
                    ownership[index] = i
                    assigned = True
                    self.player_locations[i] = index
        return ownership

    def initialize_player_strategies(self, player_strategies):
        strategies = []
        if player_strategies is not None and len(player_strategies) == self.num_players:
            for i in range(0, self.num_players):
                if player_strategies[i] == 1:
                    strategies.append(strategy_shortest_dist.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))

                elif player_strategies[i] == 2:
                    strategies.append(strategy_highest_outdegree.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))
                elif player_strategies[i] == 3:
                    strategies.append(strategy_most_pressured.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))
                elif player_strategies[i] == 4:
                    strategies.append(strategy_weighted_neighbors.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))
                else:
                    strategies.append(strategy_random.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))
                self.move_goal[i] = strategies[i].peek_move()
                self.move_progress[i] = self.adj_mx[int(self.player_locations[i])][int(self.move_goal[i])]
        else:
            for i in range(0, self.num_players):
                strategies.append(strategy_random.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))
                self.move_goal[i] = strategies[i].peek_move()
                self.move_progress[i] = self.adj_mx[int(self.player_locations[i])][int(self.move_goal[i])]
        return strategies

    def game_over(self):
        return -1 not in self.ownership

    # return true if game state changed
    def tick(self, show_score):
        change = False
        # For each player see if the player is at its destination, if so claim that node and then update
        # everyone's strategies, if not at destination but still at end go to next node on path and update move_progress.
        # Then decrease that persons' move_progress by 1
        min_move = np.inf
        for i in range(self.num_players):
            if self.player_strategies[i].has_move() and self.move_progress[i] < min_move:
                min_move = self.move_progress[i]
        r = list(range(self.num_players))
        shuffle(r)
        for i in r:
            if self.move_progress[i] == 0 and self.player_strategies[i].has_move():
                change = True
                move = self.player_strategies[i].get_move()
                self.player_locations[i] = move
                # if no more nodes, claim the node moved to
                if (not self.player_strategies[i].has_move()):
                    if self.claim_node(move, i):
                        change = True
                        if show_score:
                            self.calculate_scores()
                        for j in range(self.num_players):
                            old_move_goal = None
                            if self.player_strategies[j].has_move():
                                old_move_goal = self.player_strategies[j].peek_move()
                            if self.player_strategies[j].update(self.ownership, self.player_locations[j]):
                                if (self.player_strategies[j].has_move()):
                                    self.move_goal[j] = self.player_strategies[j].peek_move()
                                    if old_move_goal is None or (old_move_goal is not None and old_move_goal != self.move_goal[j]): # update move progress if move goal has changed
                                        self.move_progress[j] = self.adj_mx[int(self.player_locations[j])][int(self.move_goal[j])]
                else:
                    self.move_goal[i] = self.player_strategies[i].peek_move()
                    self.move_progress[i] = self.adj_mx[int(move)][int(self.move_goal[i])]
            self.move_progress[i] -= min_move
            self.move_progress[i] = max(self.move_progress[i], 0)
        return change

    def claim_node(self, node, player):
        if self.ownership[node] == -1:
            self.ownership[node] = player
            return True
        else:
            return False

    def calculate_scores(self, print_results = False):
        if print_results:
            print("Scores: ")
        scores = np.zeros(self.num_players)
        for i in range(self.num_players):
            score = 0
            for node in self.ownership:
                if node == i:
                    score += 1
            if print_results:
                print("  Player " + str(i) + "'s score: " + str(score)  + " Strategy " + str(self.player_strategies[i]))
            scores[i] = score
        return scores

