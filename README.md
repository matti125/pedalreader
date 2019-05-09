# pedalreader
pedalreader makes the Fanatec CSPv2 and CSPv3 pedals able to connect to the Thrusrmaster T300 wheelbase. Pedalreader reads the pedal values it receives via USB, and talks to a DA converter to convert the values in the voltage ranges that the T300 expects to get from its "native" pedals.

Pedalreader runs on Raspberry Pi. 

You do need the custom-built DA converter, which is based on the Teens board and a custom DA converter.

Reads Fanatec CSPv2 via USB and writes to a custom-built USB DA converter
pedalread-pyusb.py is the one that has successfully been used for a few years.
Now (2018-02-03) starting a new development for CSPv3
Identifeid with lsusb as:
CSPv2: Bus 001 Device 005: ID 0eb7:1839 Endor AG 
CSPv3: Bus 001 Device 007: ID 0eb7:183b Endor AG
