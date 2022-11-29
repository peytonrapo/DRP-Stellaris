import numpy as np
import heapq
# TODO insert detailed description of Strategy One here
class Strategy:
    # Should store which player the strategy is applying for use in checking board positions
    # Also stores an adj_mx of the game board (value of the distance is the cost to travel between nodes)

    def __init__(self, player, adj_mx, init_ownership, start_node, num_nodes):
        self.player = player 
        self.adj_mx = adj_mx
        # Maybe not needed for now, we should just calculate the shortest path.
        # Player will follow current path and whenever there is an update in ownership we will
        # recalculate shortest path
        # self.dist_mx = np.zeros(np.shape(adj_mx))
        self.num_nodes = num_nodes
        self.curr_path = []
        self.update_curr_path(init_ownership, start_node)

    def has_move(self):
        return len(self.curr_path) > 0

    def peek_move(self):
        if self.has_move():
            return self.curr_path[0]
        else:
            return -1

    def get_move(self):
        return self.curr_path.pop(0)

    def update(self, ownership, start_node):
        update_path = False
        for node in self.curr_path:
            if int(ownership[int(node)]) != self.player and int(ownership[int(node)]) != -1:
                update_path = True
        if update_path or not self.has_move():
            self.update_curr_path(ownership, start_node)
            return True
        return update_path

    def update_curr_path(self, ownership, start_node):
        # insert dijkstra's here from current position of player
        # based on algorithm described here https://inst.eecs.berkeley.edu/~cs61bl/r//cur/graphs/dijkstra-algorithm-runtime.html?topic=lab24.topic&step=4&course=
        fringe = []
        explored = np.zeros(self.num_nodes)
        heapq.heappush(fringe, (0, (start_node, start_node)))
        from_node = np.ones(self.num_nodes) * -1
        distances = np.ones(self.num_nodes) * np.inf
        distance = 0
        while (len(fringe) > 0):
            distance, node = heapq.heappop(fringe)
            u, prev_node = node
            u = int(u)
            distances[u] = distance
            if explored[u] == 0:
                from_node[u] = prev_node
                if ownership[u] == self.player:
                    neighbors = self.get_neighbors(u, ownership)
                    for v in neighbors:
                        heapq.heappush(fringe, (distance + self.adj_mx[u][int(v)], (v, u)))
                explored[u] = 1
        goal_node = self.get_goal_node(ownership, distances)
        if goal_node == -1:
            self.curr_path = []
        else:
            self.curr_path = self.get_path(from_node, start_node, goal_node)

    def get_neighbors(self, node1, ownership):
        neighbors = []
        for node2 in range(len(self.adj_mx[int(node1)])):
            if self.adj_mx[node1][node2] > 0 and node1 != node2 and (int(ownership[node2]) == self.player or int(ownership[node2]) == -1):
                neighbors.append(node2)
        return neighbors

    def get_goal_node(self, ownership, distances):
        index_of_minimum_unexplored = -1
        for i in range(len(distances)):
            if ownership[i] == -1 and distances[i] != np.inf:
                if index_of_minimum_unexplored == -1 or distances[i] < distances[index_of_minimum_unexplored]:
                    index_of_minimum_unexplored = i
        return index_of_minimum_unexplored  

    def get_path(self, from_node, start_node, end_node):
        path = []
        curr_node = end_node
        while curr_node != start_node:
            path.append(curr_node)
            curr_node = from_node[int(curr_node)]
        path.reverse()
        return path

    def __str__(self):
        return "Shortest Distance"