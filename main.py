from time import sleep
import game
import time
import numpy as np
import random as r
import matplotlib.pyplot as plt
import networkx as nx
import math

def generate_dimension_adj_mx(num_nodes):
    max_size = num_nodes*2
    adj_mx = np.zeros((num_nodes, num_nodes))
    pos = np.random.randint(0, max_size, (num_nodes, 2))
    for i in range(num_nodes):
        for j in range(i, num_nodes):
            diameter = math.sqrt(math.pow(pos[i][0] - pos[j][0], 2) + math.pow(pos[i][1]-pos[j][1], 2))
            third = False
            midpoint = [(pos[i][0] + pos[j][0])/2, (pos[i][1] + pos[j][1])/2]

            for k in range(num_nodes):
                if k != i and k != j:
                    dist = math.sqrt(math.pow(midpoint[0] - pos[k][0], 2) + math.pow(midpoint[1]-pos[k][1], 2))
                    if dist < diameter/2:
                        third = True
                        break
            if not third:
                adj_mx[i][j] = int(diameter)
    adj_mx += np.transpose(adj_mx)
    pos = ((pos - max_size/2)*2.0)/max_size
    return adj_mx, pos

def get_labels(player_locations):
    labels = {}
    for i in range(len(player_locations)):
        labels[int(player_locations[i])] = str(i)
    return labels

def get_edge_colors(G, player_locations, player_strategies):
    edges = [e for e in G.edges]
    values = np.ones(len(edges))*(-1)
    for i in range(len(player_strategies)):
        curr_path = player_strategies[i].curr_path
        if len(curr_path) != 0:
            start_node = int(player_locations[i])
            end_node = int(curr_path[0])
            values[edges.index((min(start_node, end_node), max(start_node, end_node)))] = i
            start_node = end_node
            for j in range(1, len(curr_path)):
                end_node = curr_path[j]
                values[edges.index((min(start_node, end_node), max(start_node, end_node)))] = i
                start_node = end_node
    return values

def to_colors(values):
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'yellow', 'cyan']
    color_list = []
    for value in values:
        if value == -1:
            color_list.append('gray')
        else:
            color_list.append(colors[int(value)])
    return color_list

def run_trial(g, pos, draw_run, draw_results, print_score):
    # start_game = time.perf_counter()
    print("Game start")

    G = nx.from_numpy_array(g.adj_mx)
    width = 0.5
    node_size = 50

    if draw_run:
        nx.draw_networkx(G, pos=pos, node_size=node_size, node_color=to_colors(g.ownership), width=width, labels=get_labels(g.player_locations), edge_color = to_colors(get_edge_colors(G, g.player_locations, g.player_strategies)))
        plt.show(block=False)

    while (not g.game_over()):
        if g.tick(print_score):
            if draw_run:
                nx.draw_networkx(G, pos=pos, node_size=node_size, node_color=to_colors(g.ownership), width=width,labels=get_labels(g.player_locations), edge_color = to_colors(get_edge_colors(G, g.player_locations, g.player_strategies)))
                # plt.show(block=False)
                plt.pause(0.000000000001)
                plt.clf()
    print("Trial done")
    scores = g.calculate_scores()
    # end_game = time.perf_counter()
    # print("Trial Run Time: " + str(end_game - start_game))
    if draw_run or draw_results:
        nx.draw_networkx(G, pos=pos, node_size=node_size, node_color=to_colors(g.ownership), width=width,labels=get_labels(g.player_locations))
        plt.show(block=True)
    return scores



def main():
    num_nodes = 200
    num_players = 2
    # Player Strategies, 0 = random, 1 = shortest dist, 2 = largest out degree, 3 = max num opponents, 4 = weighted neighbors
    strategies = [1, 1]
    draw_results = False
    draw_run = False
    num_maps = 1
    num_trials = 200
    average_scores_between_trials = np.zeros((num_maps, num_players))
    std_between_trials = np.zeros((num_maps, num_players))
    wins = np.zeros((num_maps, num_players))
    start = time.perf_counter()
    for map in range(num_maps):
        # start_gen = time.perf_counter()
        adj_mx, pos = generate_dimension_adj_mx(num_nodes)
        # end_gen = time.perf_counter()
        total_scores = np.zeros((num_trials, num_players))
        for trial in range(num_trials):
            g = game.Game(num_nodes=num_nodes, num_players=num_players, strategies=strategies, adj_mx=adj_mx)
            scores = run_trial(g, pos, draw_run, draw_results, print_score=False)
            total_scores[trial] += scores
            wins[map][np.argmax(scores)] += 1
        #print(total_scores)
        average_scores = np.mean(total_scores, axis=0)
        std_scores = np.std(total_scores, axis=0)
        # print(average_scores)
        # print(std_scores)
        average_scores_between_trials[map] += average_scores
        std_between_trials[map] += std_scores
    average_score_between_maps = np.mean(average_scores_between_trials, axis=0)
    print(wins)
    print(average_scores_between_trials)
    print(std_between_trials)
    print(average_score_between_maps)
    print(np.std(average_scores_between_trials, axis=0))
    end = time.perf_counter()
    print(end - start)

if __name__ == "__main__":
    main()
