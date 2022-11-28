from time import sleep
import game
import time
import numpy as np
import random as r
import matplotlib.pyplot as plt
import networkx as nx
import math

num_nodes = 200
num_players = 4
# Player Strategies, 0 = random, 1 = shortest dist, 2 = largest out degree, 3 = max num opponents
strategies = [0, 1, 2, 3]
draw_results = True
draw_run = True
test = False

# TODO add more edges and maybe smarter?
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

start_gen = time.perf_counter()
adj_mx, pos = generate_dimension_adj_mx(num_nodes)
end_gen = time.perf_counter()
start_game = time.perf_counter()
g = game.Game(num_nodes=num_nodes, num_players=num_players, strategies=strategies, adj_mx=adj_mx)
print("Game start")

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
width = 0.5
node_size = 50
# draw initial graph

def to_colors(values):
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'yellow', 'cyan']
    color_list = []
    for value in values:
        if value == -1:
            color_list.append('gray')
        else:
            color_list.append(colors[int(value)])
    return color_list

if draw_run:
    nx.draw_networkx(G, pos=pos, node_size=node_size, node_color=to_colors(g.ownership), width=width, labels=get_labels(g.player_locations), edge_color = to_colors(get_edge_colors(G, g.player_locations, g.player_strategies)))
    plt.show(block=False)


while (not g.game_over()):
    if g.tick():
        if draw_run:
            nx.draw_networkx(G, pos=pos, node_size=node_size, node_color=to_colors(g.ownership), width=width,labels=get_labels(g.player_locations), edge_color = to_colors(get_edge_colors(G, g.player_locations, g.player_strategies)))
            # plt.show(block=False)
            plt.pause(0.000000000001)
            plt.clf()
g.calculate_scores()
end_game = time.perf_counter()
print("Game Generation Time: " + str(end_gen + start_gen))
print("Game Run Time: " + str(end_game - start_game))
if draw_results:
    nx.draw_networkx(G, pos=pos, node_size=node_size, node_color=to_colors(g.ownership), width=width,labels=get_labels(g.player_locations))
    plt.show(block=True)
