import cProfile
import random
import re
cProfile.run("sum([random.randint(1,10) for i in range(1000000)])")


