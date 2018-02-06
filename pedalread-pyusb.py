#!/usr/bin/python
import usb.core
import usb.util
import time
import argparse

brakeGain=2	#the pedals can be pretty heavy to press without adding some gain

parser = argparse.ArgumentParser("pedalreader")
parser.add_argument("--noDA", help="No Digital to Analog converter is used or probed for", action = "store_true")
parser.add_argument("--printDvalues", help="No Digital to Analog converter is used or probed for", action = "store_true")
args = parser.parse_args()

useDA = True
if args.noDA:
	print "No DA to be used"
	useDA = False

printDvalues = False
if args.printDvalues:
	print "DA values will be printed"
	printDvalues = True


pedals = usb.core.find(idVendor=0x0eb7)
assert pedals is not None
#Decide whether we have a v2 or v3.
#v3: ID 0eb7:183b Endor AG
#v2: ID 0eb7:1839 Endor AG

vPedals=3
if (pedals.idProduct == 0x1839):
	vPedals=2
	print "old (v2) pedals detected"

if pedals.is_kernel_driver_active(0):
	print "detaching kernel driver"
	pedals.detach_kernel_driver(0)

#dev.set_configuration()
cfg = pedals.get_active_configuration()
intf_pedals = cfg[(0,0)]
usb.util.claim_interface(pedals, intf_pedals)

ep_pedals_in = usb.util.find_descriptor(
	intf_pedals,
	# match the first IN endpoint
	custom_match = \
	lambda e: \
		usb.util.endpoint_direction(e.bEndpointAddress) == \
		usb.util.ENDPOINT_IN)
assert ep_pedals_in is not None

if useDA:
	teensy = usb.core.find(idVendor=0x16c0,idProduct=0x0486)
	assert teensy is not None
	if teensy.is_kernel_driver_active(0):
		print "detaching kernel driver"
		teensy.detach_kernel_driver(0)

	cfg = teensy.get_active_configuration()
	intf_teensy = cfg[(0,0)]
	usb.util.claim_interface(teensy, intf_teensy)
	ep_teensy_in = usb.util.find_descriptor(
		intf_teensy,
		# match the first OUT endpoint
		custom_match = \
		lambda e: \
			usb.util.endpoint_direction(e.bEndpointAddress) == \
			usb.util.ENDPOINT_IN)
	assert ep_teensy_in is not None

	ep_teensy_out = usb.util.find_descriptor(
		intf_teensy,
		# match the first OUT endpoint
		custom_match = \
		lambda e: \
			usb.util.endpoint_direction(e.bEndpointAddress) == \
			usb.util.ENDPOINT_OUT)
	assert ep_teensy_out is not None

pdata=bytearray(64)
temp=bytearray(8)
temp[0]=255 #dummy to work around the bug somewhere (not with pyusb?) when first byte is 0
t_readPrevious=time.time()
durationCycleMax = 0

acceleration= 0
brake = 0
clutch= 0
dataFromTeensy="nul"
firstRound=True
diffAMax=0
diffBMax=0
diffCMax=0
while (1):
	try:
		pdata = pedals.read(ep_pedals_in.bEndpointAddress, ep_pedals_in.wMaxPacketSize, timeout=500)
		t_read=time.time()
		if (vPedals == 3):
	 		acceleration= pdata[0]+ (pdata[1]<<8)
			brake = int((pdata[2]+ (pdata[3]<<8)) * brakeGain)
			brake = min(brake, 4095) #limit to 12 bits
			clutch= pdata[4]+ (pdata[5]<<8)
		else:
	 		acceleration= 1023 - (pdata[0]+ (pdata[1]<<8))
			brake = 1023 -(pdata[2]+ (pdata[3]<<8))
			clutch= 1023 -(pdata[4]+ (pdata[5]<<8))
			acceleration = (acceleration << 2) #make 10 bits into 12 bits
			brake = (brake << 2)
			clutch = (clutch << 2)
		if firstRound:
			accelerationPrevious=acceleration
			brakePrevious=brake
			clutchPrevious=clutch
			t_readPrevious=t_read
			firstRound=False
		diffA=abs(acceleration-accelerationPrevious)
		diffB=abs(brake-brakePrevious)
		diffC=abs(clutch-clutchPrevious)
		diffAMax=max(diffA,diffAMax)
		diffBMax=max(diffB,diffBMax)
		diffCMax=max(diffC,diffCMax)
		temp[1]=acceleration & 255
		temp[2]=(acceleration >> 8) & 255
		temp[3]=brake & 255
		temp[4]=(brake >> 8) & 255
		temp[5]=clutch & 255
		temp[6]=(clutch >> 8) & 255
		if useDA:
			bytesWritten=teensy.write(ep_teensy_out,temp,timeout=2000)
		else:
			bytesWritten=0

		durationCycle=t_read-t_readPrevious 
		t_readPrevious=t_read
		durationCycleMax=max(durationCycle, durationCycleMax)	
	
		if printDvalues:
			#o=(acceleration >> 6)* "*"
			#print o, acceleration, "w",int(d_wrote*1000), "wmax", int(d_wrote_max*1000), "n",bytesWritten
		 	print "a ", acceleration," ", accelerationPrevious, " ", diffA, " ", diffAMax,\
		 		"b ", brake, " ", diffB, " ", diffBMax,\
		 		"c ", clutch, " ", diffC, " ", diffCMax, \
				"cycle ", int(durationCycle * 1000),\
				"max cycle ", int(durationCycleMax * 1000),\
				"teeensy ", dataFromTeensy
#			if useDA:
#				dataFromTeensy=teensy.read(ep_teensy_in, 1000)

		accelerationPrevious=acceleration
		brakePrevious=brake
		clutchPrevious=clutch
	except usb.core.USBError as e: 
		#we get here if there is a timeout for reading the pedals, which is normal with v2,
		# as they only report on changed values
		if vPedals == 3:
			print e, "args", e.args
		if useDA:
			teensy.write(ep_teensy_out,temp,timeout=2000) #this keeps something alive, 
#so there will not be a max 1000 ms delay when writing to teensy. 
#The delay happens after the USB is idle for more than about 1 sec, AFAIR 
#I do not know what sleeps,is is the RPi or smthng else. I should check for errors now, but I don't

usb.util.release_interface(pedals, intf_pedals)
usb.util.release_interface(teensy, intf_teensy)
# reattach the device to the OS kernel
dev.attach_kernel_driver(intfc_pedals)
dev.attach_kernel_driver(intfc_teensy)
