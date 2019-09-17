#!/usr/bin/python3



import os
import time



with open("temp-1.tmp", "w") as f:
	f.write("x")
with open("temp-2.tmp", "w") as f:
	f.write("xx")

os.link("temp-1.tmp", "temp.tmp")
os.unlink("temp-1.tmp")

os.link("temp-2.tmp", "temp.tmp")
os.unlink("temp-2.tmp")











