Similar
=======

Canonicalizer to disambiguate and recognize known names from a poor quality data entry list.
It was tested to achieve a match at much greater than 80% for low quality intentional input.

I will reconstruct this canonicalizer on demand.

It uses (or has hooks for) the following algorithms:

* acronym:     "Massachusetts Institute of Technology" intended for "MIT".
* Levenshtein: "Massachusetts" intended by "Masachusets", "Masssachusetts", or "Massahcusetts".
* fat finger:  a finger strikes a key adjacent to an intended key by accident.
* contraction: "Massachusetts Institute of Technology" for "Mass Inst Tech", or "International" for "Int'l."
* soundex:     two words are pronounced the same, 1st algorithm.
* metaphone:   two words are pronounced the same, 2nd algorithm.
* NYSSIS:      two words are pronounced the same, 3rd algorithm.
