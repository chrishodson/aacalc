#!/bin/env python3
# pylint: disable=missing-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name
import unittest
from aacalc import (
    binPDF, casualties, Units, doRound
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

    def test_init_no_input(self):
        units = Units()
        expected_result = {'Att': {'Infantry': 0, 'Artillery': 0, 'Tanks': 0, 'Fighters': 0, 'Bombers': 0},
                           'Def': {'Infantry': 0, 'Artillery': 0, 'Tanks': 0, 'Fighters': 0, 'Bombers': 0}}
        self.assertEqual(units.att, expected_result['Att'])
        self.assertEqual(units.def_, expected_result['Def'])

    def test_init_list_input(self):
        input_list = [10, 5, 3, 2, 1, 8, 3, 2, 1, 0]
        expected_result = {'Att': {'Infantry': 10, 'Artillery': 5, 'Tanks': 3, 'Fighters': 2, 'Bombers': 1},
                           'Def': {'Infantry': 8, 'Artillery': 3, 'Tanks': 2, 'Fighters': 1, 'Bombers': 0}}
        units = Units(input_list)
        self.assertEqual(units.att, expected_result['Att'])
        self.assertEqual(units.def_, expected_result['Def'])

    def test_init_tuple_input(self):
        input_list = (10, 5, 3, 2, 1, 8, 3, 2, 1, 1)
        expected_result = {'Att': {'Infantry': 10, 'Artillery': 5, 'Tanks': 3, 'Fighters': 2, 'Bombers': 1},
                           'Def': {'Infantry': 8, 'Artillery': 3, 'Tanks': 2, 'Fighters': 1, 'Bombers': 1}}
        units = Units(input_list)
        self.assertEqual(units.att, expected_result['Att'])
        self.assertEqual(units.def_, expected_result['Def'])

    def test_init_dict_input(self):
        input_dict = {'Att': {'Infantry': 5, 'Tanks': 3}, 'Def': {'Infantry': 2, 'Tanks': 4}}
        expected_result = {'Att': {'Infantry': 5, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0},
                           'Def': {'Infantry': 2, 'Artillery': 0, 'Tanks': 4, 'Fighters': 0, 'Bombers': 0}}
        units = Units(input_dict)
        self.assertEqual(units.att, expected_result['Att'])
        self.assertEqual(units.def_, expected_result['Def'])


    def test_casualties1(self):
        units = Units({'Att': {'Infantry': 10, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0},
                       'Def': {'Infantry': 10, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}})
        att_kills = 3
        def_kills = 3
        expected_result = {'Att': {'Infantry': 7, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0},
                           'Def': {'Infantry': 7, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}}
        result = casualties(att_kills, def_kills, units)
        self.assertEqual(result.dict(), expected_result)

    def test_casualties2(self):
        units = Units(
            {'Att': {'Infantry': 10, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0},
             'Def': {'Infantry': 10, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}}
        )
        att_kills = 1
        def_kills = 3
        expected_result = {'Att': {'Infantry': 7, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0},
                           'Def': {'Infantry': 9, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}}
        self.assertEqual(casualties(att_kills, def_kills, units).dict(), expected_result)

    def test_casualties3(self):
        units = Units(
            {'Att': {'Infantry': 10, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0},
             'Def': {'Infantry': 10, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}}
        )
        att_kills = 11
        def_kills = 1
        expected_result = {'Att': {'Infantry': 9, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 0}, 'Def': {'Infantry': 0, 'Artillery': 0, 'Tanks': 2, 'Fighters': 0, 'Bombers': 0}}
        self.assertEqual(casualties(att_kills, def_kills, units).dict(), expected_result)

    def test_casualties4(self):
        units = Units(
            {'Att': {'Infantry': 10, 'Artillery': 0, 'Tanks': 3, 'Fighters': 1, 'Bombers': 0},
             'Def': {'Infantry': 10, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 1}}
        )
        att_kills = 2
        def_kills = 2
        expected_result = {'Att': {'Infantry': 8, 'Artillery': 0, 'Tanks': 3, 'Fighters': 1, 'Bombers': 0},
                           'Def': {'Infantry': 8, 'Artillery': 0, 'Tanks': 3, 'Fighters': 0, 'Bombers': 1}}
        self.assertEqual(casualties(att_kills, def_kills, units).dict(), expected_result)


    def test_doRound(self):
        units = (1,0,0,0,0, 0,0,0,0,0)
        expected_result = (1,0,0)
        self.assertEqual(doRound(Units(units)), expected_result)

    def test_doRound1(self):
        units = (0,0,0,0,0, 1,0,0,0,0)
        expected_result = (0,1,0)
        self.assertEqual(doRound(Units(units)), expected_result)

    def test_doRound2(self):
        units = (1,0,0,0,0, 1,0,0,0,0)
        expected_result = (25,62.5,12.5)
        self.assertTupleAlmostEqual(
            self.fix_doround_results(doRound(Units(units))), expected_result,
            places=2)

    def test_doRound3(self):
        units = Units( (3, 0, 0, 0, 0,  1, 0, 2, 0, 0) )
        expected_result = (14.05,84.83,1.12)
        self.assertTupleAlmostEqual(
            self.fix_doround_results(doRound(units)), expected_result,
            places=2)

    def test_doRound4(self):
        units = (1,0,0,0,0, 10,0,0,0,0)
        expected_result = (0,100,0)
        self.assertTupleAlmostEqual(
            self.fix_doround_results(doRound(Units(units))), expected_result,
            places=2)

    def test_doRound5(self):
        units = (10,0,3,0,0, 10,0,0,1,0)
        expected_result = (54.0282548342132,43.9250183197832,2.04672684600364)
        self.assertTupleAlmostEqual(
            self.fix_doround_results(doRound(Units(units))), expected_result,
            places=2)

    def test_binPDF10(self):
        self.assertAlmostEqual(binPDF(0.5, 10, 5), 0.24609375)

    def test_casualties10(self):
        units = Units([10, 5, 3, 2, 1, 8, 3, 2, 1, 0])
        new_units = casualties(5, 5, units)
        self.assertEqual(new_units.values(), [5, 5, 3, 2, 1, 3, 3, 2, 1, 0])

    def test_doRoundBasic(self):
        units = Units([10, 5, 3, 2, 1, 8, 3, 2, 1, 0])
        prob_win, prob_lose, prob_tie = doRound(units)
        self.assertTrue(0 <= prob_win <= 1)
        self.assertTrue(0 <= prob_lose <= 1)
        self.assertTrue(0 <= prob_tie <= 1)

    def test_Units10(self):
        units = Units([10, 5, 3, 2, 1, 8, 3, 2, 1, 0])
        self.assertEqual(units.values(), [10, 5, 3, 2, 1, 8, 3, 2, 1, 0])
        units.assign_hits('Att', 'Infantry', 5)
        self.assertEqual(units.values(), [5, 5, 3, 2, 1, 8, 3, 2, 1, 0])
        self.assertEqual(units.alive('Att'), 16)
        self.assertEqual(units.alive('Def'), 14)


if __name__ == '__main__':
    unittest.main()
