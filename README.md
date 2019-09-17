jk_keyvaluestore
==========

Introduction
------------

This python module implements a simple key-value data base based on JSON data stored in a directory.

Information about this module can be found here:

* [github.org](https://github.com/jkpubsrc/....)
* [pypi.python.org](https://pypi.python.org/pypi/jk_keyvaluestore)

### Goals

This module provides a simple key-value-based data store. The current implementation does not aim for highes performance but for ease of use, even in interprocess domain. This means that ...

* You can instantiate a data store class right away and use it to read and write key-value data. The only thing you need to provide is a writable data directory.
* A data store can be read-write or read-only.
* A key can be associated with arbitrary amounts of JSON data.
* Other data store instances (sharing the same directory) can perform writes as well. These will be visible to the other data store instances.

### Limitations

The current implementation is pretty straight forward. Every change causes a write of a JSON file that contains that data. This way a) persistency is ensured and b) other instances of a data store will receive the new data. Therefore the concurrency model is very simple: THe most recent write wins.

Though this concept has drawbacks:

* Managing thousands of key-value-pairs will be inefficient as for every key-value-pair a single file is required to hold that data.
* High frequent changes of data will be inefficient as well.
* As time stamps are used to synchronize one or more data store instances if you use multiple processes residing on multiple hosts you need to ensure that the system time will not be much different accross all nodes.

This key-value store is ment for use cases where you desire to keep things simple in your software as the amount of data you need to manage is quite limited.

### Use cases

Use cases for this implementation is:

* Write out state information of an application and monitor it
* Implement simple interprocess communication
* Modify configuration data of an application while the application is running

### Benefits of this approach

Nevertheless this approach has a variety of benefits:

* Portability: If you (would) require the cooperation of programs written in different languages this can be achieved very easily. Porting this python implementation to other programming languages would be very simple.

How to use this module
----------------------

### Import this module

Please include this module into your application using the following code:

```python
from jk_keyvaluestore import DirBasedKeyValueStore
```

Importing this way is recommended as currently `DirBasedKeyValueStore` is the only class. (This might change in the future.)

Using a single instance of the data store
-----------------------------------------

### Create an instance

To set up a data store instance is easy:

```python
ds = DirBasedKeyValueStore(dirPath="my/data/directory", identifier=1)
```

For clarification all arguments have been named in this example (in their order of declaration).

* `dirPath` must refer to an existing directory that will hold the data. If multiple instances are created they must refer to the same directory.
* If this is not a read only instance `identifier` must be either a valid string or a valid integer value. If it is a string the identifier is matched against `r[a-zA-Z0-9_+-\.]+`. If it is an integer the value must be greater or equal to zero. If you specify `None` (which is the default) the data store will be read only.

### Write data

Writing data is very simple. Example:

```python
ds.put("someKey", [ "some", "value" ])
```

or:

```python
ds["someKey"] = [ "some", "value" ]
```

The keys must be strings of arbitrary size. Values can be anything that is storable in JSON.

### Read data

Reading data is very simple. Example:

```python
value = ds.get("someKey")
```

or:

```python
value = ds["someKey"]
```

This operation will return `None` by default if the key does not exist. (No exception will be raised.)

### Check if a key exists

Performing a check for existance of a key in the data store is easy. Example:

```python
bKeyValuePairExists = ds.contains("someKey")
```

Please note that the data store will maintain a list of all deleted entries to be able to still synchronize such information with other instances. The data returned by `contains()` will **not** reflect deleted entries. Example:

```python
ds.put("someKey", "someValue")
ds.delete("someKey")
assert ds.contains("someKey") == False
```

### Delete a single key value pair

Deleting data is very simple. Example:

```python
ds.remove("someKey")
```

or:

```python
del ds["someKey"]
```

This operation is indempotent. No exception will be raised if the key has already been deleted.

Please note that in ordert to maintain synchronization capabilities with other data stores information about this delete will be kept internally in the data store.

### Delete all key value pairs

Removing all data from a data store is simple. Example:

```python
ds.clear()
```

This operation is indempotent. No exception will be raised if the data store is already empty.

Please note that in order to maintain synchronization capabilities with other data stores information about this delete will be kept internally in the data store.

### Get a list of all keys

It is possible to get a list of all keys currently in use in the data store. Example:

```python
allKeys = ds.keys()
```

The methhod `keys()` will return a list of keys.

Please note that the data store will maintain a list of all deleted entries. The data returned by `keys()` will **not** contain deleted entries.

Using a multipe instances of the data store
-------------------------------------------

### Instantiation

Using multiple instances is easy. Example:

```python
# In program A
dsA = DirBasedKeyValueStore(dirPath="my/data/directory", identifier=1)
```

```python
# In program B
dsB = DirBasedKeyValueStore(dirPath="my/data/directory", identifier=2)
```

Please note that both instances must be distinguishable. Therefore you need to provide unique identifiers for each instance matching the regular expression `r[a-zA-Z0-9_+-\.]+`. (If you specify an identifier of `None` you will create a read only instance.)

After this you can use `get()`, `put()`, `remove()` and other methods.

### Synchronization

If intermediate changes occurred in other instances of a data store these changes are not synchronized automatically to other data store. Synchronization is entirely up to you: As synchronization is not cheap you as the developer has to decide when a synchronization should be performed.

During synchronization the directory of files storing the key-value pairs is scanned for new entries. If new entries are found they will get loaded. The information contained in these files will then be incorporated into the current data store instance. As this is directly dependend on the number of files written since the last time synchronization has been performed, this might be a bit costly. Therefore it is up to you as a developer to decide when exactly these synchronizations should occur.

Performance
-----------

As files are read and written in order to manage all data the time required for file operations is the limiting factor. Here are some performance values based on experience in Python on Linux with a regular SATA-SSD:

| Operation					| Performance	|
| ------------------------- | ------------- |
| get						| Limited by python interpreter performance only.	|
| put						| ~15ms												|
| synchronize single change	| ~10ms												|

As during instantiation `synchronize()` is called to read all existing data, instantiation performance is very similar to synchronization performance.

(Possible) Future Development
-----------------------------

The current implementation is based on synchroneous I/O operations. Future implementation options therefore would be:

* provide an implementation based on asynchroneous I/O
* provide an implementation for C, Java, C#, maybe even JavaScript
* maybe provide an implementation accessing data via SFTP
* explore even better ways of implementing such a data store:
	* using named pipes to communicate to a single process

Other things to do:

* test the current implementation on an NFS share

If you would be interested in improving or porting the current implementation you're welcome. Feel free to contact me.

Contact Information
-------------------

This is Open Source code. That not only gives you the possibility of freely using this code it also
allows you to contribute. Feel free to contact the author(s) of this software listed below, either
for comments, collaboration requests, suggestions for improvement or reporting bugs:

* Jürgen Knauth: jknauth@uni-goettingen.de, pubsrc@binary-overflow.de

License
-------

This software is provided under the following license:

* Apache Software License 2.0



