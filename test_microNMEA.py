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
        # Stage 1
        self.nm.parse("$GPGSV,3,1,10,01,81,167,33,02,73,168,18,03,63,271,30,21,52,147,,1*68")
        expected_satellite_data = {
            'GP':
                {'satellites_in_view': 10,
                 'satellites':
                     {1: [81, 167, 33], 2: [73, 168, 18],
                      3: [63, 271, 30], 21: [52, 147, 'NA']}
                 }
        }
        with self.subTest("First GSV message"):
            self.assertDictEqual(expected_satellite_data, self.nm._microNMEA__tmp_gsv_part,
                                 "Satellites tmp map is incorrect.")
        with self.subTest("First GSV message"):
            self.assertDictEqual({}, self.nm.gsv_data, "Satellites map should be empty.")

        # Stage 2
        self.nm.parse("$GPGSV,3,2,10,17,37,296,49,32,29,051,33,28,27,092,34,04,20,202,32,1*6C")
        expected_satellite_data = {
            'GP':
                {'satellites_in_view': 10,
                 'satellites':
                     {1: [81, 167, 33], 2: [73, 168, 18],
                      3: [63, 271, 30], 21: [52, 147, 'NA'],
                      17: [37, 296, 49], 32: [29, 51, 33],
                      28: [27, 92, 34], 4: [20, 202, 32]}
                 }
        }
        with self.subTest("First GSV message"):
            self.assertDictEqual(expected_satellite_data, self.nm._microNMEA__tmp_gsv_part,
                                 "Satellites tmp map is incorrect.")
        with self.subTest("First GSV message"):
            self.assertDictEqual({}, self.nm.gsv_data, "Satellites map should be empty.")

        # Stage 3
        self.nm.parse("$GPGSV,3,3,10,31,18,118,09,19,17,322,41,1*67")
        expected_satellite_data = {
            'GP':
                {'satellites_in_view': 10,
                 'satellites':
                    {1: [81, 167, 33], 2: [73, 168, 18],
                     3: [63, 271, 30], 21: [52, 147, 'NA'],
                     17: [37, 296, 49], 32: [29, 51, 33],
                     28: [27, 92, 34], 4: [20, 202, 32],
                     31: [18, 118, 9], 19: [17, 322, 41]}
                 }
        }
        with self.subTest("First GSV message"):
            self.assertDictEqual(expected_satellite_data, self.nm.gsv_data, "Satellites map should be empty.")


if __name__ == "__main__":
    unittest.main()
