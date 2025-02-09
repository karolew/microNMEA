# NMEA Micropython Parser

It is lightweight micropython oriented implementation of NMEA-0183 V4.1 protocol. 

The following documents were used as a source of information on NMEA:
* https://help.fieldsystems.trimble.com/sps/nmea0183-messages-vtg.htm
* https://navspark.mybigcommerce.com/content/PX1122R_DS.pdf
* https://aprs.gids.nl/nmea/#latlong

# Usage

* Copy the `microNMEA.py` to your project.
* Instatiate class microNMEA
```python 
nmea = microNMEA()
nmea.parse("$GNGSA,A,3,67,68,69,84,,,,,,,,,1.2,0.7,1.0,2*3B")
```
