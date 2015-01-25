import hid
import time


pedals = hid.device()
pedals.open(0x0eb7,0x1839)

teensy = hid.device()
teensy.open(0x16c0,0x0486)

pedals.set_nonblocking(1)
teensy.set_nonblocking(1)
pdata=bytearray(64)
temp=bytearray(8)
temp[0]=255 #dummy to work around the bug when first byt is 0
count=1
t_gotdata=0
t_min=5000
while (1):
	t=time.time();
	pdata = pedals.read(64)
	if pdata:
		t_now=time.time()
		t_since_last_pedal=t_now-t_gotdata
		t_min=min(t_min,t_since_last_pedal)
		t_gotdata=t_now
		count += 1
		acceleration= 1023 - (pdata[0]+ (pdata[1]<<8))
		brake = 1023 -(pdata[2]+ (pdata[3]<<8))
		clutch= 1023 -(pdata[4]+ (pdata[5]<<8))
		temp[1]=acceleration & 255
		temp[2]=(acceleration >> 8) & 255
		temp[3]=brake & 255
		temp[4]=(brake >> 8) & 255
		temp[5]=clutch & 255
		temp[6]=(clutch >> 8) & 255
		teensy.write(temp)
		t_wrote=time.time()
		data=teensy.read(8);
# 		print "a ", acceleration, \
# 				"b ", brake, \
# 				"c ", clutch, \
# 				"loop-pedal ", int((t_gotdata-t) * 1000),\
# 				"loop-wrote ", int((t_wrote-t ) * 1000),\
#  				"pedal-pedal ", int(t_since_last_pedal * 1000),\
# 				"min ", int(t_min * 1000),\
# 				"teeensy", data
pedals.close()
teensy.close()
