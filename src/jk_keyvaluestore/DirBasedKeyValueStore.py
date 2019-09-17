


import os
import time
import json
import re
import typing




class DataRecord(object):

	def __init__(self, tNanoSecondsSinceEpoch:int, key:str, bDeleted:bool, value):
		self.key = key
		self.tNanoSecondsSinceEpoch = tNanoSecondsSinceEpoch
		self.value = value
		self.bDeleted = bDeleted
	#

	def store(self, dirPathTemp:str, dirPathData:str):
		tOld = self.tNanoSecondsSinceEpoch
		tNew = int(time.time() * 1000000)

		filePathTemp = os.path.join(dirPathTemp, str(tNew))

		with open(filePathTemp, "w") as f:
			json.dump({
				"key": self.key,
				"bDeleted": self.bDeleted,
				"value": self.value,
			}, f)

		tMax = tNew + 10
		while True:
			filePathData = os.path.join(dirPathData, str(tNew))
			try:
				os.link(filePathTemp, filePathData)
				os.unlink(filePathTemp)
				break
			except FileExistsError as ee:
				tNew += 1
				if tNew >= tMax:
					try:
						os.unlink(filePathTemp)
					except:
						pass
					raise Exception("FAIL! Target was: " + repr(filePathData))
		#print("\t\tWriting:", tNew)

		if tOld:
			#print("\t\tDeleting:", tOld)
			oldFilePath = os.path.join(dirPathData, str(tOld))
			try:
				os.unlink(oldFilePath)
			except:
				pass

		self.tNanoSecondsSinceEpoch = tNew
	#

#





class DirBasedKeyValueStore(object):

	def __init__(self, dirPath:str, identifier:typing.Union[str,int] = None):

		assert isinstance(dirPath, str)
		assert os.path.isdir(dirPath)

		if identifier is not None:
			if isinstance(identifier, str):
				if re.match(r"^[a-zA-Z0-9_+-\.]+$", identifier) is None:
					raise Exception("Invalid identifier specified: " + repr(identifier))
			elif isinstance(identifier, int):
				assert identifier >= 0
			else:
				raise Exception("Invalid identifier specified: " + repr(identifier))
			self.__bReadWrite = True
		else:
			self.__bReadWrite = False

		self.__dirPathData = os.path.join(dirPath, "d")
		os.makedirs(self.__dirPathData, exist_ok=True)

		if self.__bReadWrite:
			self.__dirPathTemp = os.path.join(dirPath, "t." + str(identifier))
			os.makedirs(self.__dirPathTemp, exist_ok=True)
		else:
			self.__dirPathTemp = None

		self.__dirPath = dirPath
		self.__dataRecordMap = {}
		self.__lastFileNames = set()

		self.synchronize()
	#

	#
	# This method is called if new data is encountered.
	#
	def __onChangeExternal(self, tNanoSecondsSinceEpoch:int, key:str, bDeleted:bool, value):
		assert isinstance(tNanoSecondsSinceEpoch, int)
		assert isinstance(key, str)
		assert isinstance(bDeleted, bool)

		dataRecord = self.__dataRecordMap.get(key)
		if dataRecord is None:
			#print("\tUnique:", tNanoSecondsSinceEpoch)
			dataRecord = DataRecord(tNanoSecondsSinceEpoch, key, bDeleted, value)
			self.__dataRecordMap[key] = DataRecord(tNanoSecondsSinceEpoch, key, bDeleted, value)
		else:
			if tNanoSecondsSinceEpoch > dataRecord.tNanoSecondsSinceEpoch:
				# the other version is newer
				#print("\tNewer:", tNanoSecondsSinceEpoch)
				dataRecord.tNanoSecondsSinceEpoch = tNanoSecondsSinceEpoch
				dataRecord.bDeleted = bDeleted
				dataRecord.value = value
			elif tNanoSecondsSinceEpoch == dataRecord.tNanoSecondsSinceEpoch:
				raise Exception("Implementation Error!")
			else:
				# the other version is older => delete it
				#print("\tOlder:", tNanoSecondsSinceEpoch)
				filePath = os.path.join(self.__dirPathData, str(tNanoSecondsSinceEpoch))
				#print("\t\tDeleting:", tNanoSecondsSinceEpoch)
				try:
					os.unlink(filePath)
				except Exception as ee:
					#print(ee)
					pass
	#

	#
	# This method is called if new data is encountered.
	#
	def __onChangeInternal(self, key:str, bDeleted:bool, value):
		assert isinstance(key, str)
		assert isinstance(bDeleted, bool)

		dataRecord = self.__dataRecordMap.get(key)
		if dataRecord is None:
			dataRecord = DataRecord(None, key, bDeleted, value)
			self.__dataRecordMap[key] = DataRecord(None, key, bDeleted, value)
			dataRecord.store(self.__dirPathTemp, self.__dirPathData)
			self.__lastFileNames.add(str(dataRecord.tNanoSecondsSinceEpoch))
		else:
			dataRecord.bDeleted = bDeleted
			dataRecord.value = value
			tOld = dataRecord.tNanoSecondsSinceEpoch
			dataRecord.store(self.__dirPathTemp, self.__dirPathData)
			self.__lastFileNames.remove(str(tOld))
			self.__lastFileNames.add(str(dataRecord.tNanoSecondsSinceEpoch))
	#

	#
	# Scan the directory for new files (and process them).
	#
	def synchronize(self):
		entriesLeft = set(self.__lastFileNames)

		# process all files found

		for dirEntryName in os.listdir(self.__dirPathData):
			if dirEntryName in self.__lastFileNames:
				# existing file; do nothing;
				#print("existing file found:", dirEntry)
				entriesLeft.remove(dirEntryName)

			else:
				# new file; process it's content;
				#print("new file found:", dirEntry)

				try:
					filePath = os.path.join(self.__dirPathData, dirEntryName)
					with open(filePath, "r") as f:
						dataRecord = json.load(f)

					key = dataRecord["key"]
					bDeleted = dataRecord["bDeleted"]
					value = dataRecord["value"]

					self.__onChangeExternal(int(dirEntryName), key, bDeleted, value)
				except Exception as ee:
					# TODO
					pass

				self.__lastFileNames.add(dirEntryName)

		# now let's deal with files that have been removed

		for fileName in entriesLeft:
			#print("file deleted:", dirEntry)
			self.__lastFileNames.remove(fileName)
	#

	def keys(self) -> list:
		return sorted([ dataRecord.key for dataRecord in self.__dataRecordMap.values() if not dataRecord.bDeleted ])
	#

	def __len__(self) -> int:
		n = 0
		for dataRecord in self.__dataRecordMap.values():
			if not dataRecord.bDeleted:
				n += 1
		return n
	#

	def _keysAll(self) -> list:
		return sorted([ dataRecord.key for dataRecord in self.__dataRecordMap.values() ])
	#

	def _keysDeleted(self) -> list:
		return sorted([ dataRecord.key for dataRecord in self.__dataRecordMap.values() if dataRecord.bDeleted ])
	#

	def get(self, key:str):
		assert isinstance(key, str)

		dataRecord = self.__dataRecordMap.get(key)
		if dataRecord is None:
			return None
		elif dataRecord.bDeleted:
			return None
		else:
			return dataRecord.value
	#

	def put(self, key:str, value):
		if self.__bReadWrite:
			assert isinstance(key, str)
			if value is not None:
				assert isinstance(value, (int, str, bool, dict, list, tuple))

			self.__onChangeInternal(key, False, value)

		else:
			raise Exception("Data store is read only!")
	#

	def remove(self, key:str):
		if self.__bReadWrite:
			assert isinstance(key, str)

			dataRecord = self.__dataRecordMap.get(key)
			if dataRecord is not None:
				self.__onChangeInternal(key, True, None)

		else:
			raise Exception("Data store is read only!")
	#

	def contains(self, key:str):
		assert isinstance(key, str)

		dataRecord = self.__dataRecordMap.get(key)
		if dataRecord is None:
			return False
		else:
			return True
	#

	def __getitem__(self, key:str):
		assert isinstance(key, str)

		dataRecord = self.__dataRecordMap.get(key)
		if dataRecord is None:
			return None
		elif dataRecord.bDeleted:
			return None
		else:
			return dataRecord.value
	#

	def __setitem__(self, key:str, value):
		if self.__bReadWrite:
			assert isinstance(key, str)
			if value is not None:
				assert isinstance(value, (int, str, bool, dict, list, tuple))

			self.__onChangeInternal(key, False, value)

		else:
			raise Exception("Data store is read only!")
	#

	def __delitem__(self, key:str):
		if self.__bReadWrite:
			assert isinstance(key, str)

			dataRecord = self.__dataRecordMap.get(key)
			if dataRecord is not None:
				self.__onChangeInternal(key, True, None)

		else:
			raise Exception("Data store is read only!")
	#

	def clear(self):
		if self.__bReadWrite:
			for dataRecord in list(self.__dataRecordMap.values()):
				self.__onChangeInternal(dataRecord.key, True, None)

		else:
			raise Exception("Data store is read only!")
	#

#



























