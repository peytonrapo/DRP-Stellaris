import numpy as np
import strategy_shortest_dist
import strategy_random
import strategy_highest_outdegree
from random import randrange
# Thoughts to think about, should players be aware of the other's movement? 
# Like think about the case where they can go to the same node but the distances are different
class Game:
    def __init__(self, num_nodes, num_players, strategies=None):
        self.num_nodes = num_nodes
        self.num_players = num_players
        # to use adj_mx[node 1][node 2] is 1 if path from node 1 to node 2
        # for now create a graph of all ones TODO replace with random graph generator
        self.adj_mx = self.initialize_adj_mx()
        # ownership[node] gives you the player number of owner
        self.player_locations = np.zeros(num_players)
        self.ownership = self.initialize_ownership()
        self.move_progress = np.zeros(num_players)
        self.move_goal = np.zeros(num_players)
        self.player_strategies = self.initialize_player_strategies(strategies)

    def initialize_adj_mx(self):
        arr = np.random.randint(1, 5, (self.num_nodes, self.num_nodes))
        arr += np.transpose(arr)
        np.fill_diagonal(arr, 0)
        # print(arr)
        return arr
        # return np.ones((self.num_nodes, self.num_nodes)) - np.identity(self.num_nodes)

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
                    print("short")
                    strategies.append(strategy_shortest_dist.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))

                elif player_strategies[i] == 2:
                    print("outdegree")
                    strategies.append(strategy_highest_outdegree.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))

                else:
                    print("random")
                    strategies.append(strategy_random.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))
                self.move_goal[i] = strategies[i].peek_move()
                self.move_progress[i] = self.adj_mx[int(self.player_locations[i])][int(self.move_goal[i])]
        else:
            for i in range(0, self.num_players):
                print("random")
                strategies.append(strategy_random.Strategy(i, self.adj_mx, self.ownership, np.where(self.ownership == i)[0][0], self.num_nodes))
                self.move_goal[i] = strategies[i].peek_move()
                self.move_progress[i] = self.adj_mx[int(self.player_locations[i])][int(self.move_goal[i])]
        return strategies

    def game_over(self):
        return -1 not in self.ownership

    def tick(self):
        # For each player see if the player is at its destination, if so claim that node and then update
        # everyone's strategies, if not at destination but still at end go to next node on path and update move_progress.
        # Then decrease that persons' move_progress by 1
        for i in range(self.num_players):
            # print("Player " + str(i) + "'s turn: moving to " + str(self.move_goal[i]) + " progress left is " + str(self.move_progress[i]))
            # print(self.ownership)
            # print(self.player_locations)
            if self.move_progress[i] == 0:
                move = self.player_strategies[i].get_move()
                self.player_locations[i] = move
                # if no more nodes, claim the node moved to
                if (not self.player_strategies[i].has_move()):
                    if self.claim_node(move, i):
                        self.calculate_scores()
                        for j in range(self.num_players):
                            if self.player_strategies[j].update(self.ownership, self.player_locations[j]):
                                # if self.player_strategies[j].has_move():
                                # print("Player " + str(j) + " path: " + str(self.player_strategies[j].peek_move()))
                                if (self.player_strategies[j].has_move()):
                                    self.move_goal[j] = self.player_strategies[j].peek_move()
                                    self.move_progress[j] = self.adj_mx[int(self.player_locations[j])][int(self.move_goal[j])]
                                else:
                                    self.move_goal[j] = -1
                                    self.move_progress[j] = -1
                else:
                    self.move_goal[i] = self.player_strategies[i].peek_move()
                    self.move_progress[i] = self.adj_mx[int(move)][int(self.move_goal[i])]
            self.move_progress[i] -= 1

    def claim_node(self, node, player):
        if node < len(self.ownership) and self.ownership[node] == -1:
            self.ownership[node] = player
            return True
        else:
            return False

    def calculate_scores(self):
        print("Scores: ")
        for i in range(self.num_players):
            score = 0
            for node in self.ownership:
                if node == i:
                    score += 1
            print("  Player " + str(i) + "'s score: " + str(score))

