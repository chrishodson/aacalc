#!/bin/env python3
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
    casualties(*args): Calculates the number of casualties for each side in a battle.
    doRound(*args): Simulates one round of a battle.
    long_units(units_dict): Converts list of units into dict.
    short_units(units_dict): Converts dict of units into list.

Global Variables:
    possible_units: A list of the possible unit types in the game.
    odds: A dictionary containing the odds of hitting for each unit type on each side.
    VERBOSE: A boolean variable used to control the level of verbosity in the output.
    VERBOSE2: A boolean variable used to control the level of verbosity in the output.

Usage:
    python aacalc.py [att_inf att_art att_tan att_fig att_bom def_inf def_art def_tan def_fig def_bom]

Example:
    python aacalc.py 10 5 3 2 1 8 3 2 1 0
"""

import copy
import math
import functools
import sys

VERBOSE = False
VERBOSE2 = False

odds = {
    'Infantry': {'Att': 1, 'Def': 2},
    'Artillary': {'Att': 2, 'Def': 2},
    'Tanks': {'Att': 3, 'Def': 2},
    'Fighters': {'Att': 3, 'Def': 4},
    'Bombers': {'Att': 4, 'Def': 1}
}

POSSIBLE_UNITS = ['Infantry', 'Artillary', 'Tanks', 'Fighters', 'Bombers']

@functools.lru_cache(maxsize=None)
def binPDF(P=0, N=0, K=0):
    """Binomial probability of K successes out of N trials with P success rate
    """
    # P = probability of hitting
    # N = number of dice thrown
    # K = number of kills
    # returns chance of that many hits happening
    if N == 0:
        return 1
    if K == 0:
        return (1 - P) ** N
    return math.factorial(N) / \
     (math.factorial(K) * math.factorial(N - K)) * \
     P ** K * \
     (1 - P) ** (N - K)

def short_units(units):
    """
    Returns a list of the number of units for each unit type on each side.

    Args:
        unit_hash: A dictionary containing the number of units for each unit type on each side.

    Returns:
        A list of the number of units for each unit type on each side.
    """
    return tuple(list(units['Att'].values() ) + list( units['Def'].values()))

def short_units_hdr():
    """
    Returns a list of the unit types for each side.
    """
    return [ side + unit for side in ['Att', 'Def'] for unit in odds ]

def long_units(input_units):
    """
    Returns a dictionary containing the number of units for each unit type on each side.
    """
    return_hash = {}
    for side in ('Att', 'Def'):
        return_hash[side] = {}
        for unit in POSSIBLE_UNITS:
            return_hash[side][unit] = int(input_units[0])
            input_units = input_units[1:]
    return return_hash

def casualties(def_hits, att_hits, myunits):
    """
    Calculates the number of casualties for each side in a battle.

    Args:
        def_hits: The number of hits for the defending side.
        att_hits: The number of hits for the attacking side.
        myunits: A dictionary containing the number of units for each unit type on each side.

    Returns:
        A dictionary containing the number of casualties for each unit type on each side.
    """
    hits = {'Def': def_hits, 'Att': att_hits}
    orig_units = copy.deepcopy(myunits)
    casualty_units = {'Att': {}, 'Def': {}}

    for side in ['Att', 'Def']:
        for unit in POSSIBLE_UNITS:
            if unit in orig_units[side]:
                reduced_units = min(hits[side], orig_units[side][unit])
                casualty_units[side][unit] = orig_units[side][unit] - reduced_units
                hits[side] -= reduced_units

    return casualty_units

def normalize(arr):
    """
    Normalizes an array of numbers.
    """
    total = sum(arr)/100
    return [x / total for x in arr]

@functools.lru_cache(maxsize=None)
def doRound(in_units):
    """
    Simulates one round of a battle.
    """
    if VERBOSE2:
        print(f"Called doRound({in_units})")

    # process a round
    units = long_units(list(in_units))

    # figure out if someone is dead
    attacking_units_alive = any(units['Att'][unittype] for unittype in POSSIBLE_UNITS)
    defending_units_alive = any(units['Def'][unittype] for unittype in POSSIBLE_UNITS)

    if attacking_units_alive == 0 and defending_units_alive == 0:
        # TIE
        if VERBOSE:
            print(f"TIE,{short_units(units)}", file=sys.stderr)
        return (0, 0, 1)
    elif attacking_units_alive == 0:
        # LOSE
        if VERBOSE:
            print(f"LOSE,{short_units(units)}", file=sys.stderr)
        return (0, 1, 0)
    elif defending_units_alive == 0:
        # WIN
        if VERBOSE:
            print(f"WIN,{short_units(units)}", file=sys.stderr)
        return (1, 0, 0)

    max_hits = {}
    hits_prob = {'Att': {}, 'Def': {}}
    for side in ['Att', 'Def']:
        max_hits[side] = sum(units[side].values())
        for infantry_hits in range(units[side]['Infantry'] + 1):
            for artillary_hits in range(units[side]['Artillary'] + 1):
                for tank_hits in range(units[side]['Tanks'] + 1):
                    for fighter_hits in range(units[side]['Fighters'] + 1):
                        for bomber_hits in range(units[side]['Bombers'] + 1):
                            hits_prob[side][infantry_hits + artillary_hits + tank_hits + fighter_hits + bomber_hits] = \
                                binPDF(odds['Infantry'][side] / 6, units[side]['Infantry'], infantry_hits) * \
                                binPDF(odds['Artillary'][side] / 6, units[side]['Artillary'], artillary_hits) * \
                                binPDF(odds['Tanks'][side] / 6, units[side]['Tanks'], tank_hits) * \
                                binPDF(odds['Fighters'][side] / 6, units[side]['Fighters'], fighter_hits) *\
                                binPDF(odds['Bombers'][side] / 6, units[side]['Bombers'], bomber_hits)

    prob_win, prob_lose, prob_tie = 0, 0, 0
    for ahp in range(max_hits['Att'] + 1):
        for dhp in range(max_hits['Def'] + 1):
            if ahp == 0 and dhp == 0:
                continue
            return_win, return_lose, return_tie = doRound(short_units(casualties(ahp, dhp, units)))
            # multiply the probabilities of win and loss by the probability of us being here
            myodds = hits_prob['Att'][ahp] * hits_prob['Def'][dhp]
            prob_win += return_win * myodds
            prob_lose += return_lose * myodds
            prob_tie += return_tie * myodds

    return (prob_win, prob_lose, prob_tie)

def main():
    """
    The main function for the script.
    """
    if len(sys.argv) > 1:
        try:
            troops = long_units(sys.argv[1:])
        except ValueError as err:
            # Handle the case where the user specifies an invalid unit.
            if str(err) == "Invalid unit":
                print("Invalid unit specified")
            else:
                # Re-raise the exception if it wasn't due to an invalid unit.
                raise
    else:
        troops = {
            'Att': {
                'Infantry': 10,
                'Artillary': 0,
                'Tanks': 3,
                'Fighters': 0,
                'Bombers': 0,
            },
            'Def': {
                'Infantry': 10,
                'Artillary': 0,
                'Tanks': 0,
                'Fighters': 0,
                'Bombers': 0,
            }
        }

    if VERBOSE:
        print(','.join(['Outcome', *short_units_hdr()]))
    # Here we do the "promotion" of troops in the presense of artillary
    # Since these troops attack as artillary, we just make them artillary
    # and keep track of things so we can reduce the number at the end (if
    # any are left)
    promotions = min(troops['Att']['Infantry'], troops['Att']['Artillary'])
    troops['Att']['Infantry'] -= promotions
    troops['Att']['Artillary'] += promotions

    win_pct, lose_pct, tie_pct = doRound(short_units(troops))
    if VERBOSE:
        print(doRound.cache_info())
        print(binPDF.cache_info())
    if VERBOSE:
        print('WIN,LOSE,TIE')
    total = win_pct + lose_pct + tie_pct
    print(f'{win_pct / total * 100:.2f},{lose_pct / total * 100:.2f},{tie_pct / total * 100:.2f}')

if __name__ == '__main__':
    main()
