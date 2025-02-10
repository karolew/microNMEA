import datetime
import unittest

import microNMEA


class BasicMicroNMEA(unittest.TestCase):

    def setUp(self):
        self.nm = microNMEA.microNMEA()
        print(f"\nStart {self.id()} {datetime.datetime.today()}".ljust(90, "-"))

    def tearDown(self):
        print(self.nm)
        print("End Test".ljust(90, "-"))

    def test_GGA(self):
        self.nm.parse("$GPGGA,215230.000,5546.7965950,N,01125.3586740,E,1,19,0.7,225.278,M,36.900,M,,0000*5f")
        with self.subTest():
            self.assertEqual("21:52:30.000", self.nm.time, f"Time incorrect.")
        with self.subTest():
            self.assertEqual(554.11327658, self.nm.lat, f"Latitude incorrect.")
        with self.subTest():
            self.assertEqual(112.08931123, self.nm.lon, f"Longitude incorrect.")
        with self.subTest():
            self.assertEqual(225.278, self.nm.alt, f"Altitude incorrect.")
        with self.subTest():
            self.assertEqual("SPS Fix", self.nm.quality, f"Quality incorrect.")
        with self.subTest():
            self.assertEqual(None, self.nm.mode, f"Mode incorrect.")
        with self.subTest():
            self.assertEqual(19, self.nm.number_of_satellites_used, f"Number of satellites incorrect.")
        with self.subTest():
            self.assertEqual(36.9, self.nm.geoidal_separation, f"Geoidal Separation incorrect.")
        with self.subTest():
            self.assertEqual(None, self.nm.dgps_age, f"Age of DGPS data incorrect.")
        with self.subTest():
            self.assertEqual(0, self.nm.dgps_station_id, f"DGPS ID incorrect.")
        with self.subTest():
            self.assertEqual(0.7, self.nm.hdop, f"HDOP incorrect.")

    def test_GLL(self):
        self.nm.parse("$GNGLL,5546.7965950,N,01125.3586740,E,215230.000,A,A*4f")
        with self.subTest():
            self.assertEqual("21:52:30.000", self.nm.time, f"Time incorrect.")
        with self.subTest():
            self.assertEqual(554.11327658, self.nm.lat, f"Latitude incorrect.")
        with self.subTest():
            self.assertEqual(112.08931123, self.nm.lon, f"Longitude incorrect.")
        with self.subTest():
            self.assertEqual("Autonomous Mode", self.nm.mode, f"Mode incorrect.")

    def test_GSA(self):
        self.nm.parse("$GNGSA,A,3,06,11,16,21,22,,,,,,,,1.2,0.7,1.0,4*33")
        self.nm.parse("$GNGSA,A,3,01,02,03,04,17,19,32,,,,,,1.2,0.7,1.0,1*3F")
        self.nm.parse("$GNGSA,A,3,67,68,69,84,,,,,,,,,1.2,0.7,1.0,2*3B")
        self.nm.parse("$GNGSA,A,3,05,13,15,,,,,,,,,,1.2,0.7,1.0,3*35")
        with self.subTest():
            self.assertEqual(0.7, self.nm.hdop, f"HDOP incorrect.")
        with self.subTest():
            self.assertEqual(1, self.nm.vdop, f"VDOP incorrect.")
        with self.subTest():
            self.assertEqual(1.2, self.nm.pdop, f"PDOP incorrect.")

        expected_satellites = {"BDS": ["06", "11", "16", "21", "22", "", "", "", "", "", "", ""],
                               "GPS": ["01", "02", "03", "04", "17", "19", "32", "", "", "", "", ""],
                               "GLONASS": ["67", "68", "69", "84", "", "", "", "", "", "", "", ""],
                               "GALILEO": ["05", "13", "15", "", "", "", "", "", "", "", "", ""]}
        for gnss, satelites in expected_satellites.items():
            with self.subTest(gnss):
                self.assertListEqual(satelites, self.nm.satellites_used[gnss],
                                     f"Satellites list for {gnss} incorrect.")

    def test_GSV(self):
        self.nm.parse("$GLGSV,3,3,09,77,04,064,,1*47")
        self.nm.parse("$GAGSV,3,3,10,08,08,203,,23,05,354,,7*75")
        with self.subTest():
            # TODO
            pass


if __name__ == "__main__":
    unittest.main()
