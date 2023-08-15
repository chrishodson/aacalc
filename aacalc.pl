#!/usr/bin/perl
use Storable qw(dclone);
use Memoize;

memoize('binPDF');

#I don't think memoizing these will speed things up
#memoize('factorial'); memoize('power');
#memoize('min'); memoize('max');

#Memoizing doRound saves a *huge* amount of work.  In one test of
#10 Inf vs 10 Inf the processing time went from 70+ minutes (I stopped it)
#to a mere 1.4 seconds.  And the difference gets more impressive with
#more troops.

memoize('doRound');

@possible_units = ( 'Infantry', 'Artillary', 'Tanks', 'Fighters', 'Bombers' );

#------------------------------
$VERBOSE  = 0;
$VERBOSE2 = 0;

if (@ARGV) {
    %troops = long_units(@ARGV);
}
else {
    $troops{'Att'}{'Infantry'}  = 10;
    $troops{'Att'}{'Artillary'} = 0;
    $troops{'Att'}{'Tanks'}     = 3;
    $troops{'Att'}{'Fighters'}  = 0;
    $troops{'Att'}{'Bombers'}   = 0;

    $troops{'Def'}{'Infantry'}  = 10;
    $troops{'Def'}{'Artillary'} = 0;
    $troops{'Def'}{'Tanks'}     = 0;
    $troops{'Def'}{'Fighters'}  = 0;
    $troops{'Def'}{'Bombers'}   = 0;
}

#------------------------------

$odds{'Infantry'}{'Att'}  = 1;
$odds{'Infantry'}{'Def'}  = 2;
$odds{'Artillary'}{'Att'} = 2;
$odds{'Artillary'}{'Def'} = 2;
$odds{'Tanks'}{'Att'}     = 3;
$odds{'Tanks'}{'Def'}     = 2;
$odds{'Fighters'}{'Att'}  = 3;
$odds{'Fighters'}{'Def'}  = 4;
$odds{'Bombers'}{'Att'}   = 4;
$odds{'Bombers'}{'Def'}   = 1;

### Main ##############################################################
print STDERR ( ( join ',', 'Outcome', 'Odds', short_units_hdr() ), "\n" )
  if $VERBOSE;

# Here we do the "promotion" of troops in the presense of artillary
# Since these troops attack as artillary, we just make them artillary
# and keep track of things so we can reduce the number at the end (if
# any are left)
my $orig_infantry = $troops{'Att'}{'Infantry'};    #save this

my $promotions = min( $troops{'Att'}{'Infantry'}, $troops{'Att'}{'Artillary'} );
$troops{'Att'}{'Infantry'} -= $promotions;
$troops{'Att'}{'Artillary'} += $promotions;

( $win_pct, $lose_pct, $tie_pct ) = doRound( short_units(%troops) );

print( 'WIN,LOSE,TIE', "\n" );
my $total = ( $win_pct + $lose_pct + $tie_pct );
print(
    join ",",
    (
        $win_pct / $total * 100,
        $lose_pct / $total * 100,
        $tie_pct / $total * 100
    ),
    "\n"
);

#print ((join ",", ($win_pct,$lose_pct,$tie_pct)), "\n");
### End Main ##########################################################
exit int( $win_pct / ( $win_pct + $lose_pct ) * 100 );

sub doRound {
    print "Round\t", $round++, "\n" if ( $VERBOSE and not( $round % 10 ) );
    print "Called doRound(@_)", "\n" if $VERBOSE2;

    #process a round
    my %units = long_units(@_);

    #figure out if someone is dead
    my $Att_units_alive = 0;
    my $Def_units_alive = 0;

    foreach $unittype (@possible_units) {
        $Att_units_alive += $units{'Att'}{$unittype};
        last if $Att_units_alive;
    }
    foreach $unittype (@possible_units) {
        $Def_units_alive += $units{'Def'}{$unittype};
        last if $Def_units_alive;
    }

    if ( $Att_units_alive == 0 and $Def_units_alive == 0 ) {

        #TIE
        print STDERR ( ( join ',', 'TIE', short_units(%units) ), "\n" )
          if $VERBOSE;
        return ( 0, 0, 1 );
    }
    elsif ( $Att_units_alive == 0 ) {

        #LOSE
        print STDERR ( ( join ',', 'LOSE', short_units(%units) ), "\n" )
          if $VERBOSE;
        return ( 0, 1, 0 );
    }
    elsif ( $Def_units_alive == 0 ) {

        #WIN
        print STDERR ( ( join ',', 'WIN', short_units(%units) ), "\n" )
          if $VERBOSE;
        return ( 1, 0, 0 );
    }

    my %max_hits;
    my %hits_prob;
    my @hits;
    foreach $side ( 'Att', 'Def' ) {
        $max_hits{$side} = sum( values %{ $units{$side} } );
        foreach $infantry_hits ( 0 .. $units{$side}{'Infantry'} ) {
            foreach $artillary_hits ( 0 .. $units{$side}{'Artillary'} ) {
                foreach $tank_hits ( 0 .. $units{$side}{'Tanks'} ) {
                    foreach $fighter_hits ( 0 .. $units{$side}{'Fighters'} ) {
                        foreach $bomber_hits ( 0 .. $units{$side}{'Bombers'} ) {

                            $hits_prob{$side}[ $infantry_hits +
                              $artillary_hits +
                              $tank_hits +
                              $fighter_hits +
                              $bomber_hits ] += binPDF(
                                $odds{'Infantry'}{$side} / 6,
                                $units{$side}{'Infantry'},
                                $infantry_hits
                              ) * binPDF(
                                $odds{'Artillary'}{$side} / 6,
                                $units{$side}{'Artillary'},
                                $artillary_hits
                              ) * binPDF( $odds{'Tanks'}{$side} / 6,
                                $units{$side}{'Tanks'}, $tank_hits ) * binPDF(
                                $odds{'Fighters'}{$side} / 6,
                                $units{$side}{'Fighters'},
                                $fighter_hits
                                ) * binPDF( $odds{'Bombers'}{$side} / 6,
                                $units{$side}{'Bombers'}, $bomber_hits );
                        }
                    }
                }
            }
        }
    }
    my ( $prob_win, $prob_lose, $prob_tie ) = ( 0, 0, 0 );
    my ( $ahp, $dhp ) = ( 0, 0 );
    my $odds = 0;
    foreach $ahp ( 0 .. $max_hits{'Att'} ) {
        foreach $dhp ( 0 .. $max_hits{'Def'} ) {
            next if ( $ahp == 0 and $dhp == 0 );
            $odds = $hits_prob{'Att'}[$ahp] * $hits_prob{'Def'}[$dhp];
            ( $return_win, $return_lose, $return_tie ) =
              doRound(
                short_units( casualties( $ahp, $dhp, dclone( \%units ) ) ) );

 #multiply the probabilities of win and loss by the probability of us being here
            $prob_win  += $return_win * $odds;
            $prob_lose += $return_lose * $odds;
            $prob_tie  += $return_tie * $odds;
        }
    }

   #return ($prob_win/($prob_win+$prob_lose),$prob_lose/($prob_win+$prob_lose));
    return ( $prob_win, $prob_lose, $prob_tie );
}

sub casualties {

    #Decide on which units to remove
    #($hits{'Att'},$hits{'Def'},%cas_units) = @_;
    my %hits;

    # Reverse Attack and defence hits.  Before it meant "how many hits did
    # that side get."  Now it means "how many times did that side get hit."
    ( $hits{'Def'} ) = shift @_;
    ( $hits{'Att'} ) = shift @_;
    @orig_units = (@_);
    my %cas_units;
    my $reduce;

    foreach $side ( 'Att', 'Def' ) {
        foreach $trooptype (@possible_units) {
            $reduce =
              min( $hits{$side}, $orig_units[0]->{$side}{$trooptype} ) + 0;
            $cas_units{$side}{$trooptype} =
              $orig_units[0]->{$side}{$trooptype} - $reduce;
            $hits{$side} -= $reduce;
        }
    }
    return %cas_units;
}

sub max {
    return $_[0] if $_[0] >= $_[1];
    return $_[1];
}

sub min {
    return $_[0] if $_[0] <= $_[1];
    return $_[1];
}

sub binPDF {
    my ( $P, $N, $K ) = @_;

    # $P = probability of hitting
    # $N = number of dice thrown
    # $K = number of kills
    # returns chance of that many hits happening

    return 1 if ( $N == 0 );
    return power( 1 - $P, $N ) if ( $K == 0 );
    return factorial($N) /
      ( factorial($K) * factorial( $N - $K ) ) *
      power( $P,     $K ) *
      power( 1 - $P, $N - $K );
}

sub binPDF2 {
    my ( $P, $N, $K ) = @_;
    print "$P,$N,$K\n";
    return 1 if ( $N == 0 );
    return power( 1 - $P, $N ) if ( $K == 0 );
    return factorial($N) /
      ( factorial($K) * factorial( $N - $K ) ) *
      power( $P,     $K ) *
      power( 1 - $P, $N - $K );

}

sub factorial {
    my $n = shift;
    return undef if $n < 0;
    return 1 if $n == 0;
    return $n * factorial( $n - 1 );
}

sub power {
    return $_[0] ** $_[1];
}

sub sum {
    my (@array) = @_;
    my $sum;
    $sum = 0;
    while (@array) { $sum += pop(@array) }
    return $sum;
}

sub short_units {
    my %unit_hash = @_;
    my @return_array;

    foreach $side ( 'Att', 'Def' ) {
        foreach $unit (@possible_units) {
            @return_array = ( @return_array, $unit_hash{$side}{$unit} );
        }
    }
    return @return_array;
}

sub short_units_hdr {
    my @return_array;
    foreach $side ( 'Att', 'Def' ) {
        foreach $unit (@possible_units) {
            @return_array = ( @return_array, $side . $unit );
        }
    }
    return @return_array;
}

sub long_units {
    my @short_units = @_;
    my %return_hash;

    foreach $side ( 'Att', 'Def' ) {
        foreach $unit (@possible_units) {
            $return_hash{$side}{$unit} = ( shift @short_units ) + 0;
        }
    }
    return %return_hash;
}

sub print_results {
    my @p_results   = (@_);
    my $num_records = ( 1 + 1 + ( @possible_units * 2 ) );
    my $num_rows    = ( @p_results + 0 ) / $num_records;

    foreach $x ( 1 .. $num_rows ) {
        my @curr_row = ();
        foreach $y ( 1 .. $num_records ) {
            @curr_row = ( @curr_row, shift @p_results );
        }
        print join (",", @curr_row ), "\n";
    }
}

# vi:ts=4:
