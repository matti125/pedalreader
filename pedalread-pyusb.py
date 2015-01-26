import usb.core
import usb.util
import time

pedals = usb.core.find(idVendor=0x0eb7)
assert pedals is not None

teensy = usb.core.find(idVendor=0x16c0,idProduct=0x0486)
assert teensy is not None

if pedals.is_kernel_driver_active(0):
	print "detaching kernel driver"
	pedals.detach_kernel_driver(0)
if teensy.is_kernel_driver_active(0):
	print "detaching kernel driver"
	teensy.detach_kernel_driver(0)

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
count=1
t_gotdata=0
t_min=5000

d_wrote_max=0
while (1):
   try:
	pdata = pedals.read(ep_pedals_in.bEndpointAddress, ep_pedals_in.wMaxPacketSize, timeout=100000)
	t=time.time();
	t_now=time.time()
	t_since_last_pedal=t_now-t_gotdata
	t_min=min(t_min,t_since_last_pedal)
	t_gotdata=t_now
	acceleration= 1023 - (pdata[0]+ (pdata[1]<<8))
	brake = 1023 -(pdata[2]+ (pdata[3]<<8))
	clutch= 1023 -(pdata[4]+ (pdata[5]<<8))
	temp[1]=acceleration & 255
	temp[2]=(acceleration >> 8) & 255
	temp[3]=brake & 255
	temp[4]=(brake >> 8) & 255
	temp[5]=clutch & 255
	temp[6]=(clutch >> 8) & 255

	
	teensy.clear_halt(ep_teensy_out)
	nw=teensy.write(ep_teensy_out,temp,timeout=2000)
	
	d_wrote=time.time()-t_now
	d_wrote_max=max(d_wrote_max, d_wrote)
	
	
	o=(acceleration >> 4)* "*"
	print o, acceleration, " ",int(d_wrote*1000), " ", int(d_wrote_max*1000), "n",nw
# 	print "a ", acceleration, \
# 		"b ", brake, \
# 		"c ", clutch, \
#  		"pedal-pedal ", int(t_since_last_pedal * 1000),\
# 		"min ", int(t_min * 1000),\
# 		"teeensy", data
#	data=teensy.read(ep_teensy_in, 1000);

   except usb.core.USBError as e:
        data = None
        if e.args == ('Operation timed out',):
            continue
# release the device
usb.util.release_interface(pedals, intf_pedals)
usb.util.release_interface(teensy, intf_teensy)
# reattach the device to the OS kernel
dev.attach_kernel_driver(intfc_pedals)
dev.attach_kernel_driver(intfc_teensy)
