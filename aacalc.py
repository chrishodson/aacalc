#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :
# vim: set tabstop=4 shiftwidth=4 autoindent expandtab :
# pylint: disable=line-too-long
# pylint: disable=invalid-name
"""
aacalc.py - A script for calculating the odds of winning a battle in a game.

This script contains several functions for calculating the odds of winning a battle in a game. The script imports the necessary modules and defines some global variables, including the `POSSIBLE_UNITS` list and the `odds` dictionary.

The script can be run from the command line with the appropriate arguments to calculate the odds of winning a battle. The script also includes some Vim configuration comments and pylint configuration comments.

Functions:
    binPDF(p, n, k): Calculates the binomial probability mass function.
    casualties(att_hits, def_hits, units): Applies the hits to the units and returns the new units.

Global Constants:
    possible_units: A list of the possible unit types in the game.
    odds: A dictionary containing the odds of hitting for each unit type on each side.

Usage:
    python aacalc.py [att_inf att_art att_tan att_fig att_bom def_inf def_art def_tan def_fig def_bom]

Example:
    python aacalc.py 10 5 3 2 1 8 3 2 1 0
Output:
    99.90,0.08,0.01
"""

from math import (comb, prod)
from copy import deepcopy
from itertools import product
from functools import lru_cache

# Global constants
VERBOSE = 0
POSSIBLE_UNITS = ['Infantry', 'Artillery', 'Tanks', 'Fighters', 'Bombers']
ODDS = {
    'Infantry': {'Att': 1, 'Def': 2},
    'Artillery': {'Att': 2, 'Def': 2},
    'Tanks': {'Att': 3, 'Def': 2},
    'Fighters': {'Att': 3, 'Def': 4},
    'Bombers': {'Att': 4, 'Def': 1}
}

class Units:
    """
    The Units class is used to store the number of units of each type on each side of the battle.
    The class also contains a method for applying the hits to the units and returning the new units.
    If called as a hash return the frozenset of the units.
    """
    def __init__(self, inUnits=None):
        if inUnits is None:
            self.att = {}
            self.def_ = {}
        elif isinstance(inUnits, list) or isinstance(inUnits, tuple):
            self.att = {unit: inUnits[i] for i, unit in enumerate(POSSIBLE_UNITS)}
            self.def_ = {unit: inUnits[i + 5] for i, unit in enumerate(POSSIBLE_UNITS)}
        elif isinstance(inUnits, dict):
            self.att = inUnits['Att']
            self.def_ = inUnits['Def']
        elif isinstance(inUnits, Units):
            self.att = deepcopy(inUnits.att)
            self.def_ = deepcopy(inUnits.def_)
        else:
            raise ValueError('Invalid input type')
        # Set all units to 0 if they are not present
        for side in [self.att, self.def_]:
            for unit in POSSIBLE_UNITS:
                if unit not in side:
                    side[unit] = 0

    def __list__(self):
        return list(self.att.values()) + list(self.def_.values())

    def __str__(self):
        return str(self.__list__())

    def __hash__(self):
        return_code = self.__str__()
        return hash(return_code)

    def __dict__(self):
        return {'Att': self.att, 'Def': self.def_}

    def values(self):
        """Convert to list"""
        return self.__list__()

    def units(self, side):
        """Units by side"""
        return self.att if side == 'Att' else self.def_

    def assign_hits(self, side, unittype, hits):
        """Assign hits to units"""
        if side == 'Att':
            self.att[unittype] -= hits
        else:
            self.def_[unittype] -= hits

    def alive(self,side):
        """Returns the number of units alive on the given side"""
        return sum(self.att.values()) if side == 'Att' else sum(self.def_.values())

@lru_cache(maxsize=None)
def binPDF(P: float, N: int, K: int) -> float:
    """
    Binomial Probability Distribution Function
    P = probability of hitting
    N = number of dice thrown
    K = number of kills
    returns chance of that many hits happening (0,1)
    """
    if N == 0:
        return 1.0
    if K == 0:
        return (1 - P) ** N
    return comb(N, K) * P ** K * (1 - P) ** (N - K)

def casualties(att_hits, def_hits, orig_units):
    """
    Applies the hits to the units and returns the new units.
    """
    units = Units(orig_units)
    # Reverse Attack and defence hits.  Before it meant "how many hits did
    # that side get."  Now it means "how many times did that side get hit."
    hits = {'Att': def_hits, 'Def': att_hits}
    for side in ['Att', 'Def']:
        for unittype in POSSIBLE_UNITS:
            reduce = min(hits[side], units.units(side)[unittype])
            units.assign_hits(side, unittype, reduce)
            hits[side] -= reduce
    return units

# Can take either 1 argument of type Units, or 10 items
@lru_cache(maxsize=None)
def doRound(*args):
    """
    Calculates a round of combat.
    """
    if len(args) == 1 and isinstance(args[0], Units):
        units = args[0]
    elif len(args) == 10:
        units = Units(args)
    else:
        raise ValueError("doRound expects either 1 dictionary or 10 items")

    #Check to see if one side won
    if units.alive('Att') == 0 and units.alive('Def') == 0:
        return (0,0,1)
    elif units.alive('Att') == 0:
        return (0,1,0)
    elif units.alive('Def') == 0:
        return (1,0,0)

    max_hits = {}
    hits_prob = {}
    # Do we need to copy units to a new object?

    for side in ['Att', 'Def']:
        hits_prob[side] = [0] * (units.alive(side)+1)
        max_hits[side] = units.alive(side)
        for hits in product(*(range(units.units(side)[unit_type] + 1) for unit_type in POSSIBLE_UNITS)):
            total_hits = sum(hits)
            hits_prob[side][total_hits] += (
                prod(binPDF(ODDS[POSSIBLE_UNITS[i]][side] / 6, units.units(side)[POSSIBLE_UNITS[i]], hits[i]) for i in range(len(POSSIBLE_UNITS)))
            )
    prob_win, prob_lose, prob_tie = 0, 0, 0
    odds = 0
    for ahp in range(max_hits['Att'] + 1):
        for dhp in range(max_hits['Def'] + 1):
            if ahp == 0 and dhp == 0:
                continue
            odds = hits_prob['Att'][ahp] * hits_prob['Def'][dhp]
            return_win, return_lose, return_tie = doRound(*casualties(ahp, dhp, units).values())

            # multiply the probabilities of win and loss by the probability of us being here
            prob_win += return_win * odds
            prob_lose += return_lose * odds
            prob_tie += return_tie * odds
    return (prob_win, prob_lose, prob_tie)

def main(units):
    """
    Main function for running the script.
    """
    prob_win, prob_lose, prob_tie = doRound(units)
    total = prob_win + prob_lose + prob_tie
    print(f"{(prob_win / total) * 100:.2f},{(prob_lose / total) * 100:.2f},{(prob_tie / total) * 100:.2f}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        input_units = Units({
            'Att': {'Infantry': 10, 'Tanks': 3},
            'Def': {'Infantry': 10, }
        })
    elif len(sys.argv) == 11:
        input_units = Units([int(arg) for arg in sys.argv[1:]])
    else:
        print('Usage: python aacalc.py [att_inf att_art att_tan att_fig att_bom def_inf def_art def_tan def_fig def_bom]')
        sys.exit(1)
    main(input_units)

    if VERBOSE & 0b01:  # check if the first bit is set
        for func in [
            binPDF, 
            casualties, 
            doRound,
        ]:
            if callable(func) and hasattr(func, 'cache_info'):
                print(func.__name__, "   \t", func.cache_info()) # pylint: disable=no-member disable=no-value-for-parameter
