
class MicroNMEA:

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
        "N": "Data Not Valid",
        "V": "Data Not Valid",
        "R": "RTK Fix",
        "F": "RTK Float",
        "P": "Precise"
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
        4: {"system": "BDS", "talker": "GB", "signals": {
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

    SEN_START = "$"
    SEN_SEPARATOR = ","
    SEN_CRC = "*"
    VALID = "A"
    SPEED_KNOTS_2_KMH = 1.852

    def __init__(self, units: int = 1, crc: bool = True) -> None:
        self.units = units  # 1 raw, 2 EU
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
        self.__tmp_gsv_part = dict()
        self.gsv_data = dict()
        self.speed = None
        self.course = None
        self.date = None
        self.heading = None
        self.east_velocity = None
        self.north_velocity = None
        self.up_velocity = None
        self.rtk_age = None
        self.rtk_ratio = None

    @staticmethod
    def catch_err(func):
        def inner(*args, **kwargs):
            try:
                val = func(*args, **kwargs)
                return val
            except Exception as e:
                print(f"ERR {func.__name__}: {e}")
        return inner

    @catch_err
    def parse(self, raw_sentence: str) -> None:
        sentence_type = raw_sentence[3:6]
        sentence, expected_crc = raw_sentence.split(self.SEN_CRC)
        if self.crc_check(sentence, expected_crc):
            __call = getattr(self, sentence_type.lower(), None)
            self.fields = sentence.split(self.SEN_SEPARATOR)
            if __call:
                __call()
            else:
                print(f"Not supported sentence: {sentence_type}")
        else:
            print(f"Incorrect CRC for {sentence_type}")

    @catch_err
    def crc_check(self, message: str, expected_crc: str) -> bool:
        if not self.crc:
            return True
        crc = 0
        for __char in message[1:]:
            crc ^= ord(__char)
        return format(crc, "02x") == expected_crc.lower()

    @catch_err
    def get_lat(self, lat: str, lns: str) -> None:
        if lat and lns and lns in self.HEMISPHERES:
            la_deg = int(lat[:3])
            la_minutes = float(lat[3:])
            decimal_degrees = la_deg + (la_minutes / 60)
            self.lat = round(decimal_degrees, 8)
            self.lat_ns = lns

    @catch_err
    def get_lon(self, lon: str, lew: str) -> None:
        if lon and lew and lew in self.HEMISPHERES:
            lo_deg = int(lon[:4])
            lo_minutes = float(lon[4:])
            decimal_degrees = lo_deg + (lo_minutes / 60)
            self.lon = round(decimal_degrees, 8)
            self.lon_ew = lew

    @catch_err
    def get_quality(self, field: str) -> None:
        if field and int(field) in range(len(self.QUALITY)):
            self.quality = self.QUALITY[int(field)]

    @catch_err
    def get_satellites_used(self, field: str) -> None:
        if field:
            self.number_of_satellites_used = int(field)

    @catch_err
    def get_satellites_used_list(self, gnss_id: str, satellites: list) -> None:
        if gnss_id and int(gnss_id) in self.GNSS_IDS and satellites:
            self.satellites_used[self.GNSS_IDS[int(gnss_id)]["system"]] = satellites

    @catch_err
    def get_pdop(self, field: str) -> None:
        if field and 0 < float(field) < 100:
            self.pdop = float(field)

    @catch_err
    def get_hdop(self, field: str) -> None:
        if field and 0 < float(field) < 100:
            self.hdop = float(field)

    @catch_err
    def get_vdop(self, field: str) -> None:
        if field and 0 < float(field) < 100:
            self.vdop = float(field)

    @catch_err
    def get_alt(self, field: str) -> None:
        if field:
            self.alt = float(field)

    @catch_err
    def get_dgps_station_id(self, field: str) -> None:
        if field:
            self.dgps_station_id = int(field)

    @catch_err
    def get_dgps_age(self, field: str) -> None:
        if field:
            self.dgps_age = field

    @catch_err
    def get_geoidal_separation(self, field: str) -> None:
        if field:
            self.geoidal_separation = float(field)

    @catch_err
    def get_time(self, field: str) -> None:
        if field:
            self.time = f"{field[:2]}:{field[2:4]}:{field[4:]}"

    @catch_err
    def get_elevation(self, field: str) -> int:
        if field and int(field) in range(0, 90 + 1):
            return int(field)

    @catch_err
    def get_azimuth(self, field: str) -> int:
        if field and int(field) in range(0, 359 + 1):
            return int(field)

    @catch_err
    def get_snr(self, field: str) -> int:
        if field and int(field) in range(0, 99 + 1):
            return int(field)

    @catch_err
    def get_mode(self, field: str) -> None:
        if field and field in self.MODES:
            self.mode = self.MODES.get(field)

    @catch_err
    def get_speed(self, field: str) -> None:
        if field:
            speed_knots = float(field)
            if self.units == 1:
                self.speed = speed_knots
            elif self.units == 2:
                self.speed = round(speed_knots * self.SPEED_KNOTS_2_KMH, 2)

    @catch_err
    def get_course(self, field: str) -> None:
        if field:
            self.course = float(field)

    @catch_err
    def get_date(self, field: str) -> None:
        if field:
            if self.units == 1:
                self.date = field
            elif self.units == 2:
                dd = field[:2]
                mm = field[2:4]
                yy = field[4:]
                self.date = f"{2000 + int(yy)}-{mm}-{dd}"

    @catch_err
    def get_date_2(self, day: str, month: str, year: str) -> None:
        if day and month and year:
            if self.units == 1:
                self.date = f"{day}{month}{year[2:]}"
            elif self.units == 2:
                self.date = f"{year}-{month}-{day}"

    @catch_err
    def get_heading(self, field: str) -> None:
        if field:
            self.heading = float(field)

    @catch_err
    def get_east_velocity(self, field: str) -> None:
        if field:
            self.east_velocity = float(field)

    @catch_err
    def get_north_velocity(self, field: str) -> None:
        if field:
            self.north_velocity = float(field)

    @catch_err
    def get_up_velocity(self, field: str) -> None:
        if field:
            self.up_velocity = float(field)

    @catch_err
    def get_rtk_age(self, field: str) -> None:
        if field:
            self.rtk_age = float(field)

    @catch_err
    def get_rtk_ratio(self, field: str) -> None:
        if field:
            self.rtk_ratio = float(field)

    @catch_err
    def gga(self) -> None:
        """
         Global positioning system fix data.
        """
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

    @catch_err
    def gll(self) -> None:
        """
         Geographic position latitude and longitude.
        """
        if self.fields[6] == self.VALID:
            self.get_lat(self.fields[1], self.fields[2])
            self.get_lon(self.fields[3], self.fields[4])
            self.get_time(self.fields[5])
            self.get_mode(self.fields[7])

    @catch_err
    def gsa(self) -> None:
        """
         GNSS DOP and active satellites.
        """
        self.get_satellites_used_list(self.fields[18], self.fields[3:15])
        self.get_pdop(self.fields[15])
        self.get_hdop(self.fields[16])
        self.get_vdop(self.fields[17])

    @catch_err
    def gsv(self) -> None:
        """
        GNSS satellites in view.

        GSV sentence may be part of bigger message. This means all sentences of the
        message must be read to get correct content. Correct satellites data are in
        gsv_data attribute.
        """
        # Check GNSS is supported.
        talker = self.fields[0][1:3]

        if not any(talker in x["talker"] for x in self.GNSS_IDS.values()):
            # Talker incorrect or not supported.
            return

        if self.fields[1] and self.fields[2]:
            number_of_messages = int(self.fields[1])
            sentence_number = int(self.fields[2])
            if self.fields[3]:
                if talker not in self.__tmp_gsv_part:
                    self.__tmp_gsv_part[talker] = {"satellites_in_view": 0, "satellites": dict()}
                self.__tmp_gsv_part[talker]["satellites_in_view"] = int(self.fields[3])
                if len(self.fields) <= 5:
                    # Nothing else to update.
                    return
                else:
                    for offset in range(4, len(self.fields[4:]), 4):
                        satellite_id, elev, azim, snr = self.fields[offset:offset+4]
                        if satellite_id:
                            __sats = {int(satellite_id): [int(elev) if elev else "NA",
                                                          int(azim) if azim else "NA",
                                                          int(snr) if snr else "NA"]}
                            self.__tmp_gsv_part[talker]["satellites"].update(__sats)
            if (sentence_number == number_of_messages and
                    len(self.__tmp_gsv_part[talker]["satellites"].keys()) ==
                    self.__tmp_gsv_part[talker]["satellites_in_view"]):
                self.gsv_data = self.__tmp_gsv_part

    @catch_err
    def rmc(self) -> None:
        """
        Recommended minimum specific GNSS data
        """
        if self.fields[2] == self.VALID:
            self.get_time(self.fields[1])
            self.get_lat(self.fields[3], self.fields[4])
            self.get_lon(self.fields[5], self.fields[6])
            self.get_speed(self.fields[7])
            self.get_course(self.fields[8])
            self.get_date(self.fields[9])
            self.get_mode(self.fields[12])

    @catch_err
    def vtg(self) -> None:
        """
        Course Over Ground and Ground Speed.
        """
        if self.fields[9] != "N":
            self.get_speed(self.fields[1])
            self.get_course(self.fields[5])
            self.get_mode(self.fields[9])

    @catch_err
    def zda(self) -> None:
        """
        Time and date.
        """
        self.get_time(self.fields[1])
        self.get_date_2(self.fields[2], self.fields[3], self.fields[4])

    @catch_err
    def ths(self) -> None:
        """
        True Heading and Status.
        """
        if self.fields[2] != "V":
            self.get_heading(self.fields[1])
            self.get_mode(self.fields[2])

    @catch_err
    def sti(self):
        """
        TODO STI 005 Time Stamp Output
        TODO STI 030 Recommended Minimum 3D GNSS Data
        TODO STI 032 RTK Baseline Data
        TODO STI 033 RTK RAW Measurement Monitoring Data
        TODO STI 035 RTK Baseline Data of Rover Moving Base Receiver
        """
        if "005" in self.fields[1]:
            self.get_time(self.fields[2])
            self.get_date_2(self.fields[3], self.fields[4], self.fields[5])

        elif "030" in self.fields[1]:
            if self.fields[3] == self.VALID:
                self.get_time(self.fields[2])
                self.get_lat(self.fields[4], self.fields[5])
                self.get_lon(self.fields[6], self.fields[7])
                self.get_alt(self.fields[8])
                self.get_east_velocity(self.fields[9])
                self.get_north_velocity(self.fields[10])
                self.get_up_velocity(self.fields[11])
                self.get_date(self.fields[12])
                self.get_mode(self.fields[13])
                self.get_rtk_age(self.fields[14])
                self.get_rtk_ratio(self.fields[15])

        elif "032" in self.fields[1]:
            if self.fields[4] == self.VALID:
                self.get_time(self.fields[2])
                self.get_date(self.fields[3])
                self.get_mode(self.fields[5])
                # TODO

    def __repr__(self) -> str:
        return (f"Time: {self.time}\n"
                f"Date: {self.date}\n"
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
                f"GNSS satellites in view: {self.gsv_data}\n"
                f"Speed: {self.speed}\n"
                f"Course: {self.course}\n"
                )
