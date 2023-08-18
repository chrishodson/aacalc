# aacalc
Calculates the odds in an Axis & Allies battle.  

Uses [binomial probability distribution function](https://en.wikipedia.org/wiki/Binomial_distribution) to calculate an exact answer rather than simulating battles.
Then recursively calulates the odds on all of those outcomes to calculate the final odds.

## Usage

### Positional units
Infantry
Artillary
Tanks
Fighters
Bombers

### Command line example
`$ aacalc.pl 10 0 1 0 0  8 0 2 1 0`

This will calulate the odds of:
>10 Infantry
>1 Tank

Attacking:
>8 Infantry
>2 Tanks
>1 Fighter

## Results
The odds returned are the percentage of battles that result in:
* Win (all defenders are destroyed)
* Loss (all attackers are destroyed)
* Tie (both all attackers and defenders are destroyed on the last round)
