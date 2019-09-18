# This Python file uses the following encoding: utf-8

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2019 David Shah <dave@ds0.me>
# License: BSD

# Simple parser for Intel pinout files, primary use as MicroFPGA platform generation help utility
# ./extract_pinout.py <pinout file>
# Prints a list of bidirectional, non-JTAG, IO pins


import codecs, sys

delim = "\t"
device_prefix = '"Pin Information for the '


header_fields       = None
header_fields_max10 = ("bank", "vref", "func", "optfunc", "cfunc", "txrx", "elvds", "perf", "pin")
header_fields_c10lp = ("bank", "vref", "func", "optfunc", "cfunc", "elvds", "pin")

curr_family = None
curr_device = None
curr_package = None
curr_pins = []

def print_pinlist():
	if curr_device is None:
		return
	d = curr_device.upper()
	p = curr_package.upper()
	print("# Device {}, Package {}".format(d, p))
	print("_io_{}_{} = [".format(d, p))
	pinlist = ", ".join("\"{}\"".format(x) for x in curr_pins)
	print("    (\"mfio\", 0, Pins({}),".format(pinlist))
	print("        IOStandard(\"3.3-V LVTTL\")),")
	print("]")
	print()

def filter_pin(data):
	# Return True if a pin is to be included in the list, False otherwide
	if data["func"] != "IO":
		return False
	if data["cfunc"] in ("JTAGEN", "TMS", "TCK", "TDI", "TDO"):
		return False
	return True

# Have to use 'codecs' here because the trademark symbol
# Intel® use is not UTF-8....
with codecs.open(sys.argv[1], 'r', 'iso-8859-1') as inf:
	for line in inf:
		if line.startswith("Note:") or  line.startswith("Notes:") :
			print_pinlist()
			curr_package = None
			curr_pins.clear()
		sl = line.strip() # remove whitespace
		if len(sl) == 0: # ignore empty lines
			continue
		if sl.startswith(device_prefix):
			if sl.find("10M") > 0:
				curr_family    = "MAX10"
				header_fields  = header_fields_max10
			if sl.find("10CL") > 0:
				curr_family   ="C10LP"
				header_fields = header_fields_c10lp

			# Initial comment, with device name
#			print_pinlist()
#			curr_package = None
#			curr_pins.clear()
			splitl = sl[len(device_prefix):].split(" ")
			if splitl[0].startswith("Intel"):
				splitl[0]=splitl[1]
				splitl[1]=splitl[2]
			family = splitl[0]
			curr_device = splitl[1]
			continue
		elif curr_device is None:
			continue
		splitl = sl.split(delim)
		if len(splitl) < len(header_fields):
			continue
		if curr_package is None:
			# Should be header line with column labels, including
			# package name
			assert splitl[0] == "Bank Number"
#			curr_package = splitl[-1]
			curr_package = splitl[len(header_fields)-1]
			# remove (n) note at end	
			splitl = curr_package.split(" ")
			curr_package = splitl[0]
			continue
		# Convert from array of fields to a Python dictionary
		# for ease of access
		entries = {}
		for i, k in enumerate(header_fields):
			entries[k] = splitl[i]
		# Apply filter
		if filter_pin(entries):
			curr_pins.append(entries["pin"])
