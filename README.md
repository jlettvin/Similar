Similar
=======

A canonicalizer attempts to convert
low quality database entries with
known canonical target names
into those target names.

When data entry personnel enter data
they will contract, abbreviate, acronym,
misspell, and make mistakes such as
transposing, skipping, or adding letters,
or having their fingers over the wrong keys.

A canonicalizer works with a limited set of target names
and computes the least statistical distance between
the entered data and a specific canonical target name.

This canonicalizer uses multiple algorithms
to compute multiple statistical distances
and uses a least product of these distances
to choose a best fit to a target name.

Before this code was deployed
the conversion rate for target names was about 17%.
After this code was deployed
the conversion rate rose to above 80%.
The remainder of the failures was submitted
for hand-canonicalization off-shore.

It uses (or has hooks for) the following algorithms:

* acronym:     "Massachusetts Institute of Technology" intended for "MIT".
* Levenshtein: "Massachusetts" intended by "Masachusets", "Masssachusetts", or "Massahcusetts".
* fat finger:  a finger strikes a key adjacent to an intended key by accident.
* contraction: "Massachusetts Institute of Technology" for "Mass Inst Tech", or "International" for "Int'l."
* soundex:     two words are pronounced the same, 1st algorithm.
* metaphone:   two words are pronounced the same, 2nd algorithm.
* NYSSIS:      two words are pronounced the same, 3rd algorithm.
