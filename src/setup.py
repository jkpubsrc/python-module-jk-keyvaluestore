################################################################################
################################################################################
###
###  This file is automatically generated. Do not change this file! Changes
###  will get overwritten! Change the source file for "setup.py" instead.
###  This is either 'packageinfo.json' or 'packageinfo.jsonc'
###
################################################################################
################################################################################


from setuptools import setup

def readme():
	with open("README.md", "r", encoding="UTF-8-sig") as f:
		return f.read()

setup(
	author = "Jürgen Knauth",
	author_email = "pubsrc@binary-overflow.de",
	classifiers = [
		"Programming Language :: Python :: 3",
		"Development Status :: 4 - Beta",
		"License :: OSI Approved :: Apache Software License",
	],
	description = "This python module implements a simple key-value data base based on JSON data stored in a directory.",
	download_url = "https://github.com/jkpubsrc/python-module-jk-keyvaluestore/tarball/0.2019.9.17.1",
	include_package_data = False,
	install_requires = [
	],
	keywords = [
		"kvp",
		"json",
	],
	license = "Apache 2.0",
	name = "jk_keyvaluestore",
	packages = [
		"jk_keyvaluestore",
	],
	url = "https://github.com/jkpubsrc/python-module-jk-keyvaluestore",
	version = "0.2019.9.17.1",
	zip_safe = False,
	long_description = readme(),
	long_description_content_type="text/markdown",
)
