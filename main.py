from time import sleep
import game
import time

start = time.perf_counter()
# Player Strategies, 0 = random, 1 = shortest dist, 2 = largest out degree
g = game.Game(300, 3, [0,1,2])
print("Game start")
i = 0
# print(g.adj_mx)
while (not g.game_over()):
    g.tick()
    # print(g.player_locations)
    # print("Tick: " + str(i))
    # i += 1
g.calculate_scores()
    # sleep(1)
end = time.perf_counter()
print(end - start)
