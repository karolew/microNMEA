# NMEA Micropython Parser

It is lightweight micropython oriented implementation of NMEA-0183 V4.1 protocol. 

The following documents were used as a source of NMEA information:
* https://help.fieldsystems.trimble.com/sps/nmea0183-messages-vtg.htm
* https://navspark.mybigcommerce.com/content/PX1122R_DS.pdf
* https://aprs.gids.nl/nmea/#latlong

# Usage

* Copy the `MicroNMEA.py` to your project.
* Instantiate microNMEA class.
* Call `parse` method with full NMEA sentence as argument.
* Processed data available via class attributes.
 
Example:
```python 
nmea = MicroNMEA()
nmea.parse("$GNGSA,A,3,67,68,69,84,,,,,,,,,1.2,0.7,1.0,2*3B")
```

# Available attributes
* time
* lat
* lat_ns
* lon
* lon_ew
* alt
* quality
* mode
* number_of_satellites_used
* satellites_used
* hdop
* vdop
* pdop
* dgps_station_id
* dgps_age
* geoidal_separation
* gsv_part