#!/usr/bin/python3



import os
import time

t = time.time()
print(t)

with open("test.tmp", "w") as f:
	f.write("")
s = os.stat("test.tmp")
print(s)











