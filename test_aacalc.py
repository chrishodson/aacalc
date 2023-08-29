#!/bin/env python3
# pylint: disable=missing-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name
import unittest
from aacalc import (
    binPDF, short_units, long_units, casualties, doRound, normalize
)

class TestAACalc(unittest.TestCase):

    def assertTupleAlmostEqual(self, tuple1, tuple2, places=7):
        self.assertEqual(len(tuple1), len(tuple2))
        for val1, val2 in zip(tuple1, tuple2):
            self.assertAlmostEqual(val1, val2, places=places)

    def fix_doround_results(self, inbound):
        win_pct, lose_pct, tie_pct = inbound
        total = win_pct + lose_pct + tie_pct
        return(win_pct/total*100, lose_pct/total*100, tie_pct/total*100)
    
    def test_normalize(self):
        self.assertTupleAlmostEqual(normalize((1, 2, 3)), (100/6, 200/6, 300/6),places=2)

    def test_normalize1(self):
        self.assertTupleAlmostEqual(normalize((.5, .5, .5)), (100/3, 100/3, 100/3),places=2)
    
    def test_normalize2(self):
        self.assertTupleAlmostEqual(normalize((.1, .2, .3)), (100/6, 200/6, 300/6),places=2)

    def test_binPDF(self):
        P = 0.5
        N = 3
        K = 2
        expected_result = 0.375
        self.assertAlmostEqual(binPDF(P, N, K), expected_result, places=3)

    def test_binPDF1(self):
        P = 4/6
        N = 3
        K = 2
        expected_result = 0.444
        self.assertAlmostEqual(binPDF(P, N, K), expected_result, places=3)

    def test_binPDF2(self):
        P = 1/6
        N = 4
        K = 2
        expected_result = 0.116
        self.assertAlmostEqual(binPDF(P, N, K), expected_result, places=3)

    def test_short_units(self):
        units = {'Att': {'Infantry': 10, 'Artillary': 5, 'Tanks': 3, 'Fighters': 2, 'Bombers': 1},
                 'Def': {'Infantry': 8, 'Artillary': 3, 'Tanks': 2, 'Fighters': 1, 'Bombers': 0}}
        expected_result = (10, 5, 3, 2, 1, 8, 3, 2, 1, 0)
        self.assertEqual(short_units(units), expected_result)

    def test_long_units(self):
        input_units = [10, 5, 3, 2, 1, 8, 3, 2, 1, 0]
        expected_result = {'Att': {'Infantry': 10, 'Artillary': 5, 'Tanks': 3, 'Fighters': 2, 'Bombers': 1},
                           'Def': {'Infantry': 8, 'Artillary': 3, 'Tanks': 2, 'Fighters': 1, 'Bombers': 0}}
        self.assertEqual(long_units(input_units), expected_result)

    def test_casualties1(self):
        units = {'Att': {'Infantry': 10, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}, 'Def': {'Infantry': 10, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}}
        att_kills = 3
        def_kills = 3
        expected_result = {'Att': {'Infantry': 7, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}, 'Def': {'Infantry': 7, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}}
        self.assertEqual(casualties(att_kills, def_kills, units), expected_result)

    def test_casualties2(self):
        units = {'Att': {'Infantry': 10, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}, 'Def': {'Infantry': 10, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}}
        att_kills = 1
        def_kills = 3
        expected_result = {'Att': {'Infantry': 7, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}, 'Def': {'Infantry': 9, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}}
        self.assertEqual(casualties(att_kills, def_kills, units), expected_result)

    def test_casualties3(self):
        units = {'Att': {'Infantry': 10, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}, 'Def': {'Infantry': 10, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}}
        att_kills = 11
        def_kills = 1
        expected_result = {'Att': {'Infantry': 9, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}, 'Def': {'Infantry': 0, 'Artillary': 0, 'Tanks': 2, 'Fighters': 0, 'Bombers': 0}}
        self.assertEqual(casualties(att_kills, def_kills, units), expected_result)

    def test_casualties4(self):
        units = {'Att': {'Infantry': 10, 'Artillary': 0, 'Tanks': 3, 'Fighters': 1, 'Bombers': 0}, 'Def': {'Infantry': 10, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 1}}
        att_kills = 2
        def_kills = 2
        expected_result = {'Att': {'Infantry': 8, 'Artillary': 0, 'Tanks': 3, 'Fighters': 1, 'Bombers': 0}, 'Def': {'Infantry': 8, 'Artillary': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 1}}
        self.assertEqual(casualties(att_kills, def_kills, units), expected_result)

    def test_doRound(self):
        units = (1,0,0,0,0, 0,0,0,0,0)
        expected_result = (1,0,0)
        self.assertEqual(doRound(units), expected_result)

    def test_doRound1(self):
        units = (0,0,0,0,0, 1,0,0,0,0)
        expected_result = (0,1,0)
        self.assertEqual(doRound(units), expected_result)

    def test_doRound2(self):
        units = (1,0,0,0,0, 1,0,0,0,0)
        expected_result = (25,62.5,12.5)
        self.assertTupleAlmostEqual(
            self.fix_doround_results(doRound(units)), expected_result,
            places=2)

    def test_doRound3(self):
        units = (3, 0, 0, 0, 0,  1, 0, 2, 0, 0)
        expected_result = (3, 99, 0)
        print(doRound(units))
        self.assertTupleAlmostEqual(
            doRound(units), expected_result,
            places=2)

    def test_doRound4(self):
        units = (1,0,0,0,0, 10,0,0,0,0)
        expected_result = (0,100,0)
        self.assertTupleAlmostEqual(
            self.fix_doround_results(doRound(units)), expected_result,
            places=2)

if __name__ == '__main__':
    unittest.main()
