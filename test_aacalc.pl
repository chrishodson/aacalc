#!/usr/bin/env perl
use Test::More;
use JSON::XS;
use Data::Dumper;
use strict;
use warnings;

require "./aacalc.pl";

my @result;
my %result_hash;

# Test binPDF with a positive number
is(binPDF(0.5, 3, 2), 0.375, "binPDF works with positive numbers");

my $json_str = '{"Att": {"Infantry": 10, "Artillary": 5, "Tanks": 3, "Fighters": 2, "Bombers": 1},
                 "Def": {"Infantry": 8, "Artillary": 3, "Tanks": 2, "Fighters": 1, "Bombers": 0}}';
my @short_arr = (10, 5, 3, 2, 1, 8, 3, 2, 1, 0);

my $troop_ref = decode_json($json_str);
my %troops = %{$troop_ref};

# Test short_units
@result = short_units(%troops);
is_deeply(\@result,  \@short_arr, "short_units works");

@result = sort {$a <=> $b} @short_arr;
ok(! eq_array(\@result,  \@short_arr), "short_units works sorted");

# Test long_units
%result_hash = long_units(@short_arr);
is_deeply(\%result_hash, $troop_ref, "long_units works");


# Test casualties
my @input_arr;
my @output_arr;
my %longs;
my @hits;

# Test casualties (1)
@input_arr  = (9, 0, 3, 0, 0, 9, 0, 3, 0, 0);
@output_arr = (6, 0, 3, 0, 0, 6, 0, 3, 0, 0);
@hits = (3, 3);

%longs = long_units(@input_arr); @result = short_units(casualties(@hits, \%longs));
is_deeply(\@result, \@output_arr, "casualties works1");

# Test casualties (2)
@input_arr  = (1, 0, 1, 1, 1,  1, 0, 1, 1, 1);
@output_arr = (0, 0, 0, 1, 1,  0, 0, 0, 1, 1);
@hits = (2, 2);

%longs = long_units(@input_arr); @result = short_units(casualties(@hits, \%longs));
is_deeply(\@result, \@output_arr, "casualties works2");

# Test casualties (3)
@input_arr  = (1, 0, 1, 1, 1,  1, 0, 1, 1, 1);
@output_arr = (0, 0, 0, 0, 1,  0, 0, 1, 1, 1);
@hits = (1, 3);

%longs = long_units(@input_arr); @result = short_units(casualties(@hits, \%longs));
is_deeply(\@result, \@output_arr, "casualties works3");

my @expected_output;
# test normalize
@result = normalize(1, 1, 1);
@expected_output = (33.3333333333333, 33.3333333333333, 33.3333333333333);
is_deeply(\@result, \@expected_output, "normalize works");

# test normalize
@result = normalize(1, 2, 3);
@expected_output = (16.6666666666667, 33.3333333333333, 50);
is_deeply(\@result, \@expected_output, "normalize works1");

# test normalize
@result = normalize(.1, .2, .3);
@expected_output = (16.6666666666667, 33.3333333333333, 50);
is_deeply(\@result, \@expected_output, "normalize works2");

# Test doRound
@result = doRound((1,0,0,0,0, 0,0,0,0,0));
@expected_output = (1,0,0);
is_deeply(\@result, \@expected_output, "doRound works");

# Test doRound
@result = doRound((0,0,0,0,0, 1,0,0,0,0));
@expected_output = (0,1,0);
is_deeply(\@result, \@expected_output, "doRound works1");

# Test doRound
@result = normalize(doRound((1,0,0,0,0, 1,0,0,0,0)));
@expected_output = (25,62.5,12.5);
is_deeply(\@result, \@expected_output, "doRound works2");

# Test doRound
@result = doRound((3,0,0,0,0, 1,0,2,0,0));
print Dumper(\@result) . "\n";
@expected_output = (3,99,0);
is_deeply(\@result, \@expected_output, "doRound works3");


=begin comment

=end comment
=cut

done_testing();
