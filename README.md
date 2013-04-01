Similar
=======

Canonicalizer to disambiguate and recognize known names from a poor quality data entry list.
It was tested to achieve a match at much greater than 80% for low quality intentional input.

I will reconstruct this canonicalizer on demand.

It uses the following algorithms:

acronym:     when "Massachusetts Institute of Technology" is intended for "MIT".
Levenshtein: when "Massachusetts" is intended by "Masachusets", "Masssachusetts", or "Massahcusetts".
fat finger:  when a finger strikes a key adjacent to an intended key by accident.
contraction: when "Massachusetts Institute of Technology" is for "Mass Inst Tech", or "International" for "Int'l."
soundex:     when two words are pronounced the same, 1st algorithm.
metaphone:   when two words are pronounced the same, 2nd algorithm.
NYSSIS:      when two words are pronounced the same, 3rd algorithm.
