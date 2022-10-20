from gamer import Gamer
from csv import DictReader
from turtle import distance
from relativeNeighborhoodGraph import returnRNG
import numpy as np
from sympy import print_glsl
import pandas as pd
import heapq

# 1st argument --> numbers ranging from 0 to 9,
# 2nd argument, row = 2, col = 3
num = 600
distance_matrix = np.random.randint(2, size=(num, num))
print(distance_matrix)

# RNG = returnRNG.returnRNG(distance_matrix)

# print(RNG)

def distance_change (distance_matrix):
  for i in range(num):
    for j in range(i, num):
      distance_matrix[j][i] = distance_matrix[i][j]

distance_change(distance_matrix)
print(distance_matrix)


dict = {}

def transfer_dataframe(dict, df):
  for i in range(num):
    dict[i] = {};
    for j in range(num):
      if i!=j :
        if df[i][j] == 1.0:
          dict[i][j]=1;

transfer_dataframe(dict, distance_matrix)

print(dict)

ownership = [0]*num
p1 = Gamer(1, 0)
p2 = Gamer(2, num-1)
while 0 in ownership:
  p1.make_choice(distance_matrix, ownership)
  p2.make_choice(distance_matrix, ownership)
  # p2.make_choice(distance_matrix, ownership)
  # p1.make_choice(distance_matrix, ownership)
  # p1.make_choice(distance_matrix, ownership)
  # p1.make_choice(distance_matrix, ownership)
  # p1.make_choice(distance_matrix, ownership)
  # p1.make_choice(distance_matrix, ownership)
  # p1.make_choice(distance_matrix, ownership)
  # p1.make_choice(distance_matrix, ownership)
  # p1.make_choice(distance_matrix, ownership)
print(ownership)
path = p1.find_path()
path2 = p2.find_path()