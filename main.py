from time import sleep
import game
import time
import numpy as np
import random as r
import matplotlib.pyplot as plt
import networkx as nx

num_nodes = 200
num_players = 3
strategies = [1, 1, 1]
draw = True

def generate_adj_mx(num_nodes):
    max_dist = 5
    adj_mx = np.zeros((num_nodes, num_nodes))
    unexplored = np.arange(num_nodes)
    np.random.shuffle(unexplored)
    unexplored = unexplored.tolist()
    connected = []
    connected.append(unexplored.pop())
    node1 = unexplored.pop()
    node2 = connected[0]
    dist = r.randint(1,max_dist)
    adj_mx[node1][node2] = dist
    adj_mx[node2][node1] = dist
    connected.append(node1)
    for i in range(num_nodes - 2):
        node1 = unexplored.pop()
        node2 = connected[r.randint(0, len(connected)-1)]
        dist = r.randint(1,max_dist)
        adj_mx[node1][node2] = dist
        adj_mx[node2][node1] = dist
        node3 = connected[r.randint(0, len(connected)-1)]
        dist = r.randint(1,max_dist)
        adj_mx[node1][node3] = dist
        adj_mx[node3][node1] = dist
        connected.append(node1)
    return adj_mx
adj_mx = generate_adj_mx(num_nodes)

start = time.perf_counter()
# Player Strategies, 0 = random, 1 = shortest dist, 2 = largest out degree
g = game.Game(num_nodes=num_nodes, num_players=num_players, strategies=strategies, adj_mx=adj_mx)
print("Game start")
i = 0

# def own_loc(ownership, player_locations):
#     num_players = len(player_locations)
#     combined = np.copy(ownership)
#     for i in range(num_players):
#         combined[int(player_locations[i])] += num_players
#     return combined

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
    

G = nx.from_numpy_array(g.adj_mx)
width = 0.3
node_size = 30
# draw initial graph
if draw:
    pos=nx.spring_layout(G)
    nx.draw_networkx(G, pos=nx.spring_layout(G, pos=pos), node_size=node_size, node_color=g.ownership, width=width, labels=get_labels(g.player_locations), edge_color = get_edge_colors(G, g.player_locations, g.player_strategies))
    plt.show(block=False)

while (not g.game_over()):
    if g.tick():
        if draw:
            nx.draw_networkx(G, pos=nx.spring_layout(G, pos=pos), node_size=node_size, node_color=g.ownership, width=width,labels=get_labels(g.player_locations), edge_color = get_edge_colors(G, g.player_locations, g.player_strategies))
            plt.show(block=False)
            plt.pause(0.00000001)
            plt.clf()
g.calculate_scores()
end = time.perf_counter()
print(end - start)
if draw:
    nx.draw_networkx(G, pos=nx.spring_layout(G, pos=pos), node_size=node_size, node_color=g.ownership, width=width,labels=get_labels(g.player_locations))
    plt.show(block=True)
