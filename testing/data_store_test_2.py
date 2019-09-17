#!/usr/bin/python3

import time

from jk_keyvaluestore import DirBasedKeyValueStore



ds1 = DirBasedKeyValueStore("data", 1)
ds1.clear()
print("DS1:", ds1.keys())

ds2 = DirBasedKeyValueStore("data", 2)
print("DS2:", ds2.keys())

ds3 = DirBasedKeyValueStore("data", 3)
print("DS3:", ds3.keys())

ds4 = DirBasedKeyValueStore("data")
print("DS4:", ds4.keys())

assert ds1.get("somekey") == None
assert ds2.get("somekey") == None
assert ds3.get("somekey") == None
assert ds4.get("somekey") == None


# add a file

ds1.put("somekey", [ "a", 1 ])
print("DS1:", ds1.keys())

assert ds1.get("somekey") == [ "a", 1 ]
assert ds2.get("somekey") == None
assert ds3.get("somekey") == None
assert ds4.get("somekey") == None

ds2.synchronize()
print("DS2:", ds2.keys())

ds3.synchronize()
print("DS3:", ds3.keys())

ds4.synchronize()
print("DS4:", ds4.keys())

assert ds1.get("somekey") == [ "a", 1 ]
assert ds2.get("somekey") == [ "a", 1 ]
assert ds3.get("somekey") == [ "a", 1 ]
assert ds4.get("somekey") == [ "a", 1 ]

# remove a file

ds1.remove("somekey")
print("DS1:", ds1.keys())

ds2.synchronize()
print("DS2:", ds2.keys())

ds3.synchronize()
print("DS3:", ds3.keys())

ds4.synchronize()
print("DS4:", ds4.keys())

assert ds1.get("somekey") == None
assert ds2.get("somekey") == None
assert ds3.get("somekey") == None
assert ds4.get("somekey") == None

# add a file

tWrite1 = time.time()
ds1.put("somekey", "xxxx")
tWrite2 = time.time()
print("DS1:", ds1.keys())

tSync1 = time.time()
ds2.synchronize()
tSync2 = time.time()
print("DS2:", ds2.keys())

ds3.synchronize()
print("DS3:", ds3.keys())

ds4.synchronize()
print("DS4:", ds4.keys())

assert ds1.get("somekey") == "xxxx"
assert ds2.get("somekey") == "xxxx"
assert ds3.get("somekey") == "xxxx"
assert ds4.get("somekey") == "xxxx"




print()
print("   put:", int((tWrite2 - tWrite1) * 100000)/100, "ms")
print("  sync:", int((tSync2 - tSync1) * 100000)/100, "ms")
print()


