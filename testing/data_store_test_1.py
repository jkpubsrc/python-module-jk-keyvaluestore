#!/usr/bin/python3


from jk_keyvaluestore import DirBasedKeyValueStore


ds = DirBasedKeyValueStore("data", 1)
ds.synchronize()


ds.put("somekey", [ "a", 1 ])
print(ds.keys())

ds.remove("somekey")
print(ds.keys())


ds.synchronize()







