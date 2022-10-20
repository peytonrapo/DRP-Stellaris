from msilib.schema import Class
from turtle import distance
from matplotlib.pyplot import flag
import numpy as np
import heapq
from queue import PriorityQueue

from sklearn.linear_model import GammaRegressor


class Gamer:
  def __init__(self, play_number,start_point):
    self.point = start_point
    self.play_number = play_number
    self.path = [start_point]
    self.step = 0

  def make_choice(self, distance_matrix, ownership):
    if ownership[self.point] != self.play_number:
      ownership[self.point] = self.play_number
    if self.point == self.path[len(self.path) - 1]:
      distance_graph = self.adjust_map(distance_matrix, ownership)
      distance_graph = self.transfer_dictionary(distance_graph)
      destiny = self.calculate_distances(distance_graph, self.point, ownership)
      path = self.dijkstra(distance_graph, self.point, destiny)
      self.path = self.path + path
    self.step = self.step + 1
    if ownership[self.path[self.step]] != 0 and ownership[self.path[self.step]] != self.play_number:
      del self.path[self.step:len(self.path)]
      self.step = self.step - 1
      self.make_choice(distance_matrix, ownership)
    self.point = self.path[self.step]
    ownership[self.point] = self.play_number



  def calculate_distances(self, graph, starting_vertex, ownership):
    distances = {vertex: float('infinity') for vertex in graph}
    distances[starting_vertex] = 0

    pq = [(0, starting_vertex)]
    while len(pq) > 0:
        current_distance, current_vertex = heapq.heappop(pq)

        # Nodes can get added to the priority queue multiple times. We only
        # process a vertex the first time we remove it from the priority queue.
        if current_distance > distances[current_vertex]:
            continue

        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight

            # Only consider this new path if it's better than any path we've
            # already found.
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
        real_distances = self.get_target(distances,ownership)
    return min(real_distances, key=distances.get)

  def adjust_map(self, distance_matrix, ownership):
    distance_graph = distance_matrix.copy()
    length = len(ownership)
    for i in range(len(ownership)):
      if ownership[i] != 0 and ownership[i] != self.play_number:
        distance_graph[i]= np.zeros(length);
        distance_graph[:,i] = np.zeros((length))
    return distance_graph

  def dijkstra(self,G, start, goal):
    """ Uniform-cost search / dijkstra """
    visited = set()
    cost = {start: 0}
    parent = {start: None}
    todo = PriorityQueue()

    todo.put((0, start))
    while todo:
        while not todo.empty():
            _, vertex = todo.get() # finds lowest cost vertex
            # loop until we get a fresh vertex
            if vertex not in visited: break
        else: # if todo ran out
            break # quit main loop
        visited.add(vertex)
        if vertex == goal:
            break
        for neighbor, distance in G[vertex].items():
            if neighbor in visited: continue # skip these to save time
            old_cost = cost.get(neighbor, 10000) # default to infinity
            new_cost = cost[vertex] + distance
            if new_cost < old_cost:
                todo.put((new_cost, neighbor))
                cost[neighbor] = new_cost
                parent[neighbor] = vertex

    return (self.make_path(parent, goal))

  def make_path(self,parent, goal):
    if goal not in parent:
        return None
    v = goal
    path = []
    while v is not None: # root has null parent
        path.append(v)
        v = parent[v]
    return path[len(path)- 2::-1]

  def transfer_dictionary(self, distance_graph):
    dict = {}
    for i in range(len(distance_graph)):
      dict[i] = {};
      for j in range(len(distance_graph)):
        if i!=j :
          if distance_graph[i][j] == 1.0:
            dict[i][j]=1;
    return dict

  def find_path(self):
    print(self.path)
    return self.path

  def get_target(self, distances, ownership):
    dict = {}
    for key in distances:
      if ownership[key] == 0 and distances[key] < 10000:
        dict[key] = distances[key]
    if dict:
      return dict
    else:
      return {self.point: 0}
