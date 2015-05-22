import pstats

p = pstats.Stats("stats.txt")
p.sort_stats("cumulative").print_stats(30)
