from time import sleep
import game
import time
import numpy as np
import random as r
import matplotlib.pyplot as plt
import networkx as nx
import math
from multiprocessing import Lock, Process, Queue, current_process, cpu_count
import json
import queue # imported for using queue.Empty exception

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
    # print("Game start")

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
    # print("Trial done")
    scores = g.calculate_scores()
    # end_game = time.perf_counter()
    # print("Trial Run Time: " + str(end_game - start_game))
    if draw_run or draw_results:
        nx.draw_networkx(G, pos=pos, node_size=node_size, node_color=to_colors(g.ownership), width=width,labels=get_labels(g.player_locations))
        plt.show(block=True)
    return scores

def run_game(experiment, num_nodes = 200, num_players = 5, strategies = [0,1,2,3,4], draw_results = True, draw_run = True, num_maps = 5, num_trials = 25):
    # Player Strategies, 0 = random, 1 = shortest dist, 2 = largest out degree, 3 = max num opponents, 4 = weighted neighbors
    game_summary = {}
    average_scores_between_trials = np.zeros((num_maps, num_players))
    std_between_trials = np.zeros((num_maps, num_players))
    wins = np.zeros((num_maps, num_players))
    start = time.perf_counter()
    maps = []
    for map in range(num_maps):
        map_summary = {}
        # start_gen = time.perf_counter()
        adj_mx, pos = generate_dimension_adj_mx(num_nodes)
        # end_gen = time.perf_counter()
        total_scores = np.zeros((num_trials, num_players))
        trials = []
        for trial in range(num_trials):
            trial_summary = {}
            g = game.Game(num_nodes=num_nodes, num_players=num_players, strategies=strategies, adj_mx=adj_mx)
            scores = run_trial(g, pos, draw_run, draw_results, print_score=False)
            total_scores[trial] += scores
            wins[map][np.argmax(scores)] += 1
            trial_summary['trial'] = trial
            trial_summary['scores'] = scores.tolist()
            trial_summary['winner'] = np.argmax(scores).item()
            trials.append(trial_summary)
        #print(total_scores)
        average_scores = np.mean(total_scores, axis=0)
        std_scores = np.std(total_scores, axis=0)
        # print(average_scores)
        # print(std_scores)
        average_scores_between_trials[map] += average_scores
        std_between_trials[map] += std_scores
        map_summary['map'] = map
        map_summary['wins_per_player'] = wins[map].tolist()
        map_summary['average_scores'] = average_scores.tolist()
        map_summary['standard_deviation_scores'] = std_scores.tolist()
        map_summary['adj_mx'] = adj_mx.tolist()
        map_summary['trials'] = trials
        maps.append(map_summary)
    average_score_between_maps = np.mean(average_scores_between_trials, axis=0)
    standard_deviation_between_maps = np.std(average_scores_between_trials, axis=0)
    # print(wins)
    # print(average_scores_between_trials)
    # print(std_between_trials)
    # print(average_score_between_maps)
    # print(np.std(average_scores_between_trials, axis=0))
    end = time.perf_counter()
    # print(end - start)
    game_summary['num_nodes'] = num_nodes
    game_summary['num_players'] = num_players
    game_summary['strategies'] = strategies
    game_summary['num_maps'] = num_maps
    game_summary['num_trials'] = num_trials
    game_summary['total_wins_per_player'] = np.sum(wins, axis=0).tolist()
    game_summary['average_scores_between_maps'] = average_score_between_maps.tolist()
    game_summary['standard_deviation_between_maps'] = standard_deviation_between_maps.tolist()
    game_summary['maps'] = maps
    # print(game_summary)
    game_summary_json = json.dumps(game_summary, indent=2)
    file_name = 'experiments/' + str(experiment) + '.json'
    with open(file_name, "w") as outfile:
        outfile.write(game_summary_json)
    # print(game_summary)

# Tutorial found: https://www.digitalocean.com/community/tutorials/python-multiprocessing-example
def do_job(tasks_to_accomplish, tasks_that_are_done):
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will 
                raise queue.Empty exception if the queue is empty. 
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get_nowait()
            (num_nodes, strategies) = task
            file_name = str(num_nodes) + '_nodes' + str(strategies[0]) + str(strategies[1])
            run_game(file_name, num_nodes=num_nodes, num_players = 2, strategies=strategies, draw_results=False, draw_run=False)
        except queue.Empty:

            break
        else:
            '''
                if no exception has been raised, add the task completion 
                message to task_that_are_done queue
            '''
            print(task)
            tasks_that_are_done.put(str(task) + ' is done by ' + current_process().name)
            time.sleep(.5)
    return True

def main():
    number_of_processes = cpu_count()
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []

    num_nodes_options = [100, 300, 600]
    for num_nodes in num_nodes_options:
        for player_0 in range(5):
            for player_1 in range(player_0 + 1, 5):
                tasks_to_accomplish.put((num_nodes, [player_0, player_1]))

    # creating processes
    for w in range(number_of_processes):
        p = Process(target=do_job, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    # completing process
    for p in processes:
        p.join()

    # print the output
    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())

    return True


if __name__ == "__main__":
    # print("Number of cpu : ", multiprocessing.cpu_count())
    main()
