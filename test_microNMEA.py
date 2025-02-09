import unittest
import microNMEA


class BasicMicroNMEA(unittest.TestCase):

    def setUp(self):
        self.nm = microNMEA.microNMEA()

    def test_example(self):
        self.nm.parse("$GPGGA,215230.000,5546.7965950,N,01125.3586740,E,1,19,0.7,225.278,M,36.900,M,,0000*5f")
        self.nm.parse("$GNGLL,5546.7965950,N,01125.3586740,E,215230.000,A,A*4f")
        self.nm.parse("$GNGSA,A,3,06,11,16,21,22,,,,,,,,1.2,0.7,1.0,4*33")
        self.nm.parse("$GNGSA,A,3,01,02,03,04,17,19,32,,,,,,1.2,0.7,1.0,1*3F")
        self.nm.parse("$GNGSA,A,3,67,68,69,84,,,,,,,,,1.2,0.7,1.0,2*3B")
        self.nm.parse("$GNGSA,A,3,05,13,15,,,,,,,,,,1.2,0.7,1.0,3*35")

        self.assertEqual(554.11327658, self.nm.lat)
        self.assertEqual(112.08931123, self.nm.lon)
        self.assertEqual(225.278, self.nm.alt)


if __name__ == '__main__':
    unittest.main()
