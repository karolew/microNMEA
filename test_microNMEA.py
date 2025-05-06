import datetime
import random
import unittest

import microNMEA


class BasicMicroNMEA(unittest.TestCase):

    def setUp(self) -> None:
        self.nm = microNMEA.MicroNMEA()
        print("\n".ljust(90, "-"))
        print(f"Start {self.id()} {datetime.datetime.today()}".ljust(90, "-"))
        print("".ljust(90, "-"))

    def tearDown(self) -> None:
        print(self.nm)
        print("End Test".ljust(90, "-"))

    def test_GGA(self) -> None:
        self.nm.parse("$GPGGA,215230.000,5546.7965950,N,01125.3586740,E,1,19,0.7,225.278,M,36.900,M,,0000*5f")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("215230.000", self.nm.time, f"Time incorrect.")
        with self.subTest():
            self.assertEqual("55.77994325", self.nm.lat, f"Latitude incorrect.")
        with self.subTest():
            self.assertEqual("11.4226445666", self.nm.lon, f"Longitude incorrect.")
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

    def test_GLL(self) -> None:
        self.nm.parse("$GNGLL,5546.7965950,N,01125.3586740,E,215230.000,A,A*4f")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("215230.000", self.nm.time, f"Time incorrect.")
        with self.subTest():
            self.assertEqual("55.77994325", self.nm.lat, f"Latitude incorrect.")
        with self.subTest():
            self.assertEqual("11.4226445666", self.nm.lon, f"Longitude incorrect.")
        with self.subTest():
            self.assertEqual("Autonomous Mode", self.nm.mode, f"Mode incorrect.")

    def test_GSA(self) -> None:
        self.nm.parse("$GNGSA,A,3,06,11,16,21,22,,,,,,,,1.2,0.7,1.0,4*33")
        print(self.nm.fields)
        self.nm.parse("$GNGSA,A,3,01,02,03,04,17,19,32,,,,,,1.2,0.7,1.0,1*3F")
        print(self.nm.fields)
        self.nm.parse("$GNGSA,A,3,67,68,69,84,,,,,,,,,1.2,0.7,1.0,2*3B")
        print(self.nm.fields)
        self.nm.parse("$GNGSA,A,3,05,13,15,,,,,,,,,,1.2,0.7,1.0,3*35")
        print(self.nm.fields)
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

    def test_GSV(self) -> None:
        # Stage 1
        self.nm.parse("$GPGSV,3,1,10,01,81,167,33,02,73,168,18,03,63,271,30,21,52,147,,1*68")
        print(self.nm.fields)
        expected_satellite_data = {
            'GP':
                {'satellites_in_view': 10,
                 'satellites':
                     {1: [81, 167, 33], 2: [73, 168, 18],
                      3: [63, 271, 30], 21: [52, 147, 'NA']}
                 }
        }
        with self.subTest("First GSV message"):
            self.assertDictEqual(expected_satellite_data, self.nm._MicroNMEA__tmp_gsv_part,
                                 "Satellites tmp map is incorrect.")
        with self.subTest("First GSV message"):
            self.assertDictEqual({}, self.nm.gsv_data, "Satellites map should be empty.")

        # Stage 2
        self.nm.parse("$GPGSV,3,2,10,17,37,296,49,32,29,051,33,28,27,092,34,04,20,202,32,1*6C")
        print(self.nm.fields)
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
        with self.subTest("Second GSV message"):
            self.assertDictEqual(expected_satellite_data, self.nm._MicroNMEA__tmp_gsv_part,
                                 "Satellites tmp map is incorrect.")
        with self.subTest("Second GSV message"):
            self.assertDictEqual({}, self.nm.gsv_data, "Satellites map should be empty.")

        # Stage 3
        self.nm.parse("$GPGSV,3,3,10,31,18,118,09,19,17,322,41,1*67")
        print(self.nm.fields)
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
        with self.subTest("Third, the last one, GSV message"):
            self.assertDictEqual(expected_satellite_data, self.nm.gsv_data, "Satellites map should be empty.")

    def test_RMC(self) -> None:
        self.nm.parse("$GNRMC,215744.000,A,5546.7893300,N,01125.3576699,E,000.0,000.0,080225,,,A,V*04")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("215744.000", self.nm.time, f"Time incorrect.")
        with self.subTest():
            self.assertEqual("080225", self.nm.date, f"Date incorrect.")
        with self.subTest():
            self.assertEqual("Autonomous Mode", self.nm.mode, f"Mode incorrect.")
        with self.subTest():
            self.assertEqual("55.7798221666", self.nm.lat, f"Latitude incorrect.")
        with self.subTest():
            self.assertEqual("11.4226278316", self.nm.lon, f"Longitude incorrect.")
        with self.subTest():
            self.assertEqual(0, self.nm.speed, f"Speed incorrect.")
        with self.subTest():
            self.assertEqual(0, self.nm.course, f"Course incorrect.")

    def test_VTG(self) -> None:
        self.nm.parse("$GNVTG,122.7,T,,M,015.1,N,000.0,K,A*10")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("Autonomous Mode", self.nm.mode, f"Mode incorrect.")
        with self.subTest():
            self.assertEqual(122.7, self.nm.speed, f"Speed incorrect.")
        with self.subTest():
            self.assertEqual(15.1, self.nm.course, f"Course incorrect.")

    def test_ZDA(self) -> None:
        self.nm.parse("$GNZDA,215744.000,08,02,2025,00,00*46")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("215744.000", self.nm.time, f"Time incorrect.")
        with self.subTest():
            self.assertEqual("080225", self.nm.date, f"Date incorrect.")

    def test_THS(self) -> None:
        self.nm.parse("$GNTHS,121.15,A*1F")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("Autonomous Mode", self.nm.heading_mode, f"Mode incorrect.")
        with self.subTest():
            self.assertEqual(121.15, self.nm.heading, f"Heading incorrect.")

    def test_sti_005(self) -> None:
        self.nm.parse("$PSTI,005,121959.0000003,20,07,2020,,,,,*34")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("121959.0000003", self.nm.time, f"Time incorrect.")
        with self.subTest():
            self.assertEqual("200720", self.nm.date, f"Date incorrect.")

    def test_sti_030(self) -> None:
        self.nm.parse("$PSTI,030,033010.000,A,2447.0895508,N,12100.5234656,E,"
                      "94.615,0.00,-0.01,0.04,111219,R,0.999,3.724*1A")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("033010.000", self.nm.time, f"Time incorrect.")
        with self.subTest():
            self.assertEqual("111219", self.nm.date, f"Date incorrect.")
        with self.subTest():
            self.assertEqual("RTK Fix", self.nm.mode, f"Mode incorrect.")
        with self.subTest():
            self.assertEqual("24.7848258466", self.nm.lat, f"Latitude incorrect.")
        with self.subTest():
            self.assertEqual("121.0087244266", self.nm.lon, f"Longitude incorrect.")
        with self.subTest():
            self.assertEqual(94.615, self.nm.alt, f"Altitude incorrect.")
        with self.subTest():
            self.assertEqual(0.999, self.nm.rtk_age, f"RTK age incorrect.")
        with self.subTest():
            self.assertEqual(3.724, self.nm.rtk_ratio, f"RTK ratio incorrect.")


class UnitsISO8601MicroNMEA(unittest.TestCase):

    def setUp(self) -> None:
        self.nm = microNMEA.MicroNMEA(2)
        print("\n".ljust(90, "-"))
        print(f"Start {self.id()} {datetime.datetime.today()}".ljust(90, "-"))
        print("".ljust(90, "-"))

    def tearDown(self) -> None:
        print(self.nm)
        print("Stop Test".ljust(90, "-"))

    def test_speed_kmh_VTG(self) -> None:
        self.nm.parse("$GNVTG,122.7,T,,M,015.1,N,000.0,K,A*10")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual(227.24, self.nm.speed, f"Speed incorrect.")

    def test_date_YYYYMMDD_RMC(self) -> None:
        self.nm.parse("$GNRMC,215744.000,A,5546.7893300,N,01125.3576699,E,000.0,000.0,080225,,,A,V*04")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("2025-02-08", self.nm.date, f"Date incorrect.")

    def test_date_YYYYMMDD_sti_005(self) -> None:
        self.nm.parse("$PSTI,005,121959.0000003,20,07,2020,,,,,*34")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("2020-07-20", self.nm.date, f"Date incorrect.")


class FormatsMicroNMEA(unittest.TestCase):

    def setUp(self) -> None:
        self.nm = microNMEA.MicroNMEA(formats=1)
        print("\n".ljust(90, "-"))
        print(f"Start {self.id()} {datetime.datetime.today()}".ljust(90, "-"))
        print("".ljust(90, "-"))

    def tearDown(self) -> None:
        print(self.nm)
        print("Stop Test".ljust(90, "-"))

    def test_coordinates_DD_GGA(self) -> None:
        self.nm.parse("$GPGGA,215230.000,5546.7965950,N,01125.3586740,E,1,19,0.7,225.278,M,36.900,M,,0000*5f")
        print(self.nm.fields)
        with self.subTest():
            self.assertEqual("5546.7965950", self.nm.lat, f"Latitude incorrect.")
        with self.subTest():
            self.assertEqual("01125.3586740", self.nm.lon, f"Longitude incorrect.")


class Precise(unittest.TestCase):

    def setUp(self) -> None:
        print("\n".ljust(90, "-"))
        print(f"Start {self.id()} {datetime.datetime.today()}".ljust(90, "-"))
        print("".ljust(90, "-"))

    def tearDown(self) -> None:
        print("Stop Test".ljust(90, "-"))

    def test_precise_addition(self) -> None:
        self.assertEqual("2", microNMEA.Precise("1") + microNMEA.Precise("1"),
                         f"Add integers")
        self.assertEqual("2", microNMEA.Precise("1") + "1",
                         f"Add integers")
        self.assertEqual("3.123456789", microNMEA.Precise("2.123456789") + microNMEA.Precise("1"),
                         f"Add float to integer")
        self.assertEqual("3.123456789", microNMEA.Precise("2.123456789") + "1",
                         f"Add float to integer")
        self.assertEqual("3.12345679", microNMEA.Precise("2.123456789") + microNMEA.Precise("1.000000001"),
                         f"Add floats")
        self.assertEqual("3.12345679", microNMEA.Precise("2.123456789") + "1.000000001",
                         f"Add floats")

    def test_precise_subtraction(self) -> None:
        self.assertEqual("1", microNMEA.Precise("123456789") - microNMEA.Precise("123456788"),
                         f"Subtract integers")
        self.assertEqual("123456788", microNMEA.Precise("123456789") - "1",
                         f"Subtract integers")
        self.assertEqual("1.123456789", microNMEA.Precise("2.123456789") - microNMEA.Precise("1"),
                         f"Subtract integer from float")
        self.assertEqual("0.123456789", microNMEA.Precise("2.123456789") - "2",
                         f"Subtract integer from float")
        self.assertEqual("0.000000001", microNMEA.Precise("2.123456789") - microNMEA.Precise("2.123456788"),
                         f"Subtract floats")
        self.assertEqual("1.123456788", microNMEA.Precise("2.123456789") - "1.000000001",
                         f"Subtract floats")

    def test_precise_multiplication(self) -> None:
        self.assertEqual("49", microNMEA.Precise("7") * microNMEA.Precise("7"),
                         f"Multiple integers")
        self.assertEqual("50038", microNMEA.Precise("394") * "127",
                         f"Multiple integers")
        self.assertEqual("2.246913578", microNMEA.Precise("1.123456789") * microNMEA.Precise("2"),
                         f"Multiple float and integer")
        self.assertEqual("142.679012203", microNMEA.Precise("1.123456789") * "127",
                         f"Multiple float and integer")
        self.assertEqual("1.2621551567", microNMEA.Precise("1.123456789") * microNMEA.Precise("1.123456789"),
                         f"Multiple floats")
        self.assertEqual("2.42", microNMEA.Precise("1.1") * "2.2",
                         f"Multiple floats")

    def test_precise_multiplication_signs(self) -> None:
        self.assertEqual("-5.25", microNMEA.Precise("-1.5") * microNMEA.Precise("3.5"),
                         f"Multiple floats first negative")
        self.assertEqual("-5.25", microNMEA.Precise("1.5") * microNMEA.Precise("-3.5"),
                         f"Multiple floats second negative")
        self.assertEqual("5.25", microNMEA.Precise("-1.5") * microNMEA.Precise("-3.5"),
                         f"Multiple floats both negative")

    def test_precise_division(self) -> None:
        self.assertEqual("2.5", microNMEA.Precise("5") / microNMEA.Precise("2"),
                         f"Divide integers")
        self.assertEqual("2.5", microNMEA.Precise("5") / "2",
                         f"Divide integers")
        self.assertEqual("2.8", microNMEA.Precise("5.6") / microNMEA.Precise("2"),
                         f"Divide float by integer")
        self.assertEqual("2.8", microNMEA.Precise("5.6") / "2",
                         f"Divide float by integer")
        self.assertEqual("5", microNMEA.Precise("5.5") / microNMEA.Precise("1.1"),
                         f"Divide floats")
        self.assertEqual("1001", microNMEA.Precise("100.1") / "0.1",
                         f"Divide floats")

    def test_precise_division_signs(self) -> None:
        self.assertEqual("-3", microNMEA.Precise("-7.5") / microNMEA.Precise("2.5"),
                         f"Divide floats first negative")
        self.assertEqual("-3", microNMEA.Precise("7.5") / microNMEA.Precise("-2.5"),
                         f"Divide floats second negative")
        self.assertEqual("3", microNMEA.Precise("-7.5") / microNMEA.Precise("-2.5"),
                         f"Divide floats both negative")


class RandomPrecise(unittest.TestCase):
    import random

    def setUp(self) -> None:
        print("\n".ljust(90, "-"))
        print(f"Start {self.id()} {datetime.datetime.today()}".ljust(90, "-"))
        print("".ljust(90, "-"))

    def tearDown(self) -> None:
        print("Stop Test".ljust(90, "-"))

    def test_random_precise_multiplication(self) -> None:
        print("Test integer multiplication")
        max_value = 100000
        iterations = 1000
        for iteration in range(1, iterations + 1):
            multiplicative = random.randint(-max_value, max_value)
            multiplier = random.randint(-max_value, max_value)
            with self.subTest(iteration):
                result = microNMEA.Precise(str(multiplicative)) * str(multiplier)
                self.assertEqual(str(multiplicative * multiplier), result,
                                 f"FAILED test {iteration}, multiple integers {multiplicative} by {multiplier}")
                print(f"PASSED test {iteration}, multiple integers {multiplicative} * {multiplier} = {result}")

        print("Test float multiplication")
        max_value = 10
        iterations = 1000
        decrease_precision_places = 2
        for iteration in range(1, iterations + 1):
            multiplicative = random.uniform(-max_value, max_value)
            multiplier = random.uniform(-max_value, max_value)
            with self.subTest(iteration):
                result = microNMEA.Precise(str(multiplicative)) * str(multiplier)
                self.assertAlmostEqual(multiplicative * multiplier, float(result),
                                       microNMEA.Precise.decimal_places-decrease_precision_places,
                                       f"FAILED test {iteration}, multiple floats {multiplicative} by {multiplier}")
                print(f"PASSED test {iteration}, multiple floats {multiplicative} * {multiplier} = {result}")


if __name__ == "__main__":
    unittest.main()
