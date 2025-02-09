
class microNMEA:

    QUALITY = (
        "Fix Unavailable",
        "SPS Fix",
        "DGPS Fix",
        "PPS Fix",
        "RTK Fix",
        "RTK Float",
        "Estimated (dead reckoning) Mode",
        "Manual Input Mode",
        "Simulator Mode"
    )

    MODES = {
        "A": "Autonomous Mode",
        "D": "Differential Mode",
        "E": "Estimated (dead reckoning) Mode",
        "M": "Manual Mode",
        "S": "Simulator Mode",
        "N": "Data Noe Valid"
    }

    GNSS_IDS = {
        1: {"system": "GPS", "talker": "GP", "signals": {
                                                         "0": "All signals",
                                                         "1": "L1 C/A",
                                                         "2": "L1 P(Y)",
                                                         "3": "L1C",
                                                         "4": "L2 P(Y)",
                                                         "5": "L2C-M",
                                                         "6": "L2C-L",
                                                         "7": "L5-I",
                                                         "8": "L5-Q"}},
        2: {"system": "GLONASS", "talker": "GL", "signals": {
                                                         "0": "All signals",
                                                         "1": "G1 C/A",
                                                         "2": "G1P",
                                                         "3": "G2 C/A",
                                                         "4": "GLONASS (M) G2P"}},
        3: {"system": "GALILEO", "talker": "GA", "signals": {
                                                         "0": "All signals",
                                                         "1": "E5a",
                                                         "2": "E5b",
                                                         "3": "E5 a+b",
                                                         "4": "E6-A",
                                                         "5": "E6-BC",
                                                         "6": "L1-A",
                                                         "7": "L1-BC"}},
        4: {"system": "BDS", "talker": "BD", "signals": {
                                                         "0": "All signals",
                                                         "1": "B1",
                                                         "5": "B2A",
                                                         "B": "B2",
                                                         "8": "B3",
                                                         "3": "B1C"}},
        5: {"system": "IRNSS", "talker": "GI", "signals": {
                                                         "0": "All signals",
                                                         "4": "L2 P(Y) "}}
    }

    HEMISPHERES = (
        "N", "S", "E", "W"
    )

    DIRECTIONS = (
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    )

    MONTHS = (
        "January", "February", "March",
        "April", "May", "June",
        "July", "August", "September",
        "October", "November", "December"
    )

    SEN_START = "$"
    SEN_CRC = "*"
    VALID = "A"

    def __init__(self, crc: bool = True) -> None:
        self.crc = crc
        self.fields = []
        self.time = None
        self.lat = None
        self.lat_ns = None
        self.lon = None
        self.lon_ew = None
        self.alt = None
        self.quality = None
        self.mode = None
        self.number_of_satellites_used = None
        self.satellites_used = dict()
        self.hdop = None
        self.vdop = None
        self.pdop = None
        self.dgps_station_id = None
        self.dgps_age = None
        self.geoidal_separation = None

    def parse(self, raw_sentence: str) -> None:
        sentence_type = raw_sentence[3:6]
        sentence, expected_crc = raw_sentence.split(self.SEN_CRC)
        if self.crc_check(sentence, expected_crc):
            __call = getattr(self, sentence_type.lower(), None)
            self.fields = sentence.split(",")
            if __call:
                __call()
            else:
                print(f"Not supported sentence: {sentence_type}")
        else:
            print(f"Incorrect CRC for {sentence_type}")

    def crc_check(self, message: str, expected_crc: str) -> bool:
        if not self.crc:
            return True
        crc = 0
        for __char in message[1:]:
            crc ^= ord(__char)
        return format(crc, "02x") == expected_crc

    def get_lat(self, lat: str, lns: str) -> None:
        if lat and lns and lns in self.HEMISPHERES:
            la_deg = int(lat[:3])
            la_minutes = float(lat[3:])
            decimal_degrees = la_deg + (la_minutes / 60)
            self.lat = round(decimal_degrees, 8)
            self.lat_ns = lns

    def get_lon(self, lon: str, lew: str) -> None:
        if lon and lew and lew in self.HEMISPHERES:
            lo_deg = int(lon[:4])
            lo_minutes = float(lon[4:])
            decimal_degrees = lo_deg + (lo_minutes / 60)
            self.lon = round(decimal_degrees, 8)
            self.lon_ew = lew

    def get_quality(self, field: str) -> None:
        if field and int(field) in range(len(self.QUALITY)):
            self.quality = self.QUALITY[int(field)]

    def get_satellites_used(self, field: str) -> None:
        if field:
            self.number_of_satellites_used = int(field)

    def get_satellites_used_list(self, gnss_id: str, satellites: list) -> None:
        if gnss_id and int(gnss_id) in self.GNSS_IDS and satellites:
            self.satellites_used[self.GNSS_IDS[int(gnss_id)]["system"]] = satellites

    def get_pdop(self, field: str) -> None:
        if field and 0 < float(field) < 100:
            self.pdop = float(field)

    def get_hdop(self, field: str) -> None:
        if field and 0 < float(field) < 100:
            self.hdop = float(field)

    def get_vdop(self, field: str) -> None:
        if field and 0 < float(field) < 100:
            self.vdop = float(field)

    def get_alt(self, field: str) -> None:
        if field:
            self.alt = float(field)

    def get_dgps_station_id(self, field: str) -> None:
        if field:
            self.dgps_station_id = int(field)

    def get_dgps_age(self, field: str) -> None:
        if field:
            self.dgps_age = field

    def get_geoidal_separation(self, field: str) -> None:
        if field:
            self.geoidal_separation = float(field)

    def get_time(self, field: str) -> None:
        if field:
            self.time = f"{field[:2]}:{field[2:4]}:{field[4:]}"

    def gga(self) -> None:
        self.get_time(self.fields[1])
        self.get_lat(self.fields[2], self.fields[3])
        self.get_lon(self.fields[4], self.fields[5])
        self.get_quality(self.fields[6])
        self.get_satellites_used(self.fields[7])
        self.get_hdop(self.fields[8])
        self.get_alt(self.fields[9])
        self.get_geoidal_separation(self.fields[11])
        self.get_dgps_age(self.fields[13])
        self.get_dgps_station_id(self.fields[14])

    def gll(self) -> None:
        if self.fields[6] == self.VALID:
            self.get_lat(self.fields[1], self.fields[2])
            self.get_lon(self.fields[3], self.fields[4])
            self.get_time(self.fields[5])
            self.mode = self.MODES.get(self.fields[7])

    def gsa(self) -> None:
        self.get_satellites_used_list(self.fields[18], self.fields[3:15])
        self.get_pdop(self.fields[16])
        self.get_hdop(self.fields[16])
        self.get_vdop(self.fields[16])

    def __repr__(self) -> str:
        return (f"Time: {self.time}\n"
                f"Latitude: {self.lat} {self.lat_ns}\n"
                f"Longitude: {self.lon} {self.lon_ew}\n"
                f"Altitude {self.alt}\n"
                f"Quality Indicator: {self.quality}\n"
                f"Mode Indicator: {self.mode}\n"
                f"Number of satellites used: {self.number_of_satellites_used}\n"
                f"Statellites used: {self.satellites_used}\n"
                f"Geoidal Separation: {self.geoidal_separation}\n"
                f"Age of DGPS data: {self.dgps_age}\n"
                f"DGPS station ID: {self.dgps_station_id}\n"
                f"PDOP: {self.pdop}\n"
                f"HDOP: {self.hdop}\n"
                f"VDOP: {self.vdop}\n"
                )


if __name__ == "__main__":
    mn = microNMEA()

    mn.parse("$GPGGA,215230.000,5146.7965950,N,01925.3586740,E,1,19,0.7,225.278,M,36.900,M,,0000*53")
    print(mn)

    mn.parse("$GNGLL,5146.7965950,N,01925.3586740,E,215230.000,A,A*43")
    print(mn)

    mn.parse("$GNGSA,A,3,06,11,16,21,22,,,,,,,,1.2,0.7,1.0,4*33")
    mn.parse("$GNGSA,A,3,01,02,03,04,17,19,32,,,,,,1.2,0.7,1.0,1*3F")
    mn.parse("$GNGSA,A,3,67,68,69,84,,,,,,,,,1.2,0.7,1.0,2*3B")
    mn.parse("$GNGSA,A,3,05,13,15,,,,,,,,,,1.2,0.7,1.0,3*35")
    print(mn)
