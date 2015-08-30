#!/usr/bin/env python

"""
-------------------------------------------------------------------------------
Similar.py Copyright(c) 2012, Jonathan D. Lettvin, All Rights Reserved.

Author: Jonathan D. Lettvin
Date: 20120112
Date: 20120124 up to 71% coverage of boards.csv
-------------------------------------------------------------------------------
@brief acronym, fat finger, Levenshtein1, contraction implementations.
soundex, metaphone, and NYSSIS are unimplemented as yet.

acronym:     when American Board of Medical Examiners is intended for ABME.
Levenshtein: when American is intended by Americian, Amercan, or Amercian.
fat finger:  when a finger strikes a key adjacent to an intended key by accident.
contraction: when "American Board" is for "Am Bd", or Internal for Int'l.
soundex:     unimplemented.
metaphone:   unimplemented.
NYSSIS:      unimplemented.

WARNING! This code makes log and csv files in it's local directory
when run from the command-line.

The origins of the fat finger approach is in TECO where key statistics were
measured and typed text corrected based on a guess about hand displacement.
In modern times, a data entry clerk is usually typing rapidly and
may be unaware that a finger has fallen on the wrong key, or hand displaced.

The origins of the Levenshtein1 are in Levenshtein distances of 1.
This function implements an efficient distance of 1 or less evaluation.
This includes 1 character insertion, deletion, typo, or two character swap.

The origins of the contraction is more ancient, but with interesting modern
application, since Levenshtein character swapping deletion and insertion
away from first and last letters is flagged as a valid abbreviation
by this algorithm, and there are numerous examples of misspellings that are
missed as long as first and last letters match.
http://www.mrc-cbu.cam.ac.uk/people/matt.davis/cmabridge/
Also, this class handles acronyms.
"""


import string
import fuzzy

class Similar(dict):

    # These are character classes used in the lexer table.
    X, EXITS =  0,  0 # Detecting this character class should stop the lexer.
    W, WHITE =  1,  1 # space, tab, formfeed, carriage return, newline
    C, COMMA =  2,  2 # Comma
    M, MINUS =  3,  3 # '-' Dash
    R, RATIO =  4,  4 # '/' Slash
    S, SEMIC =  5,  5 # ';' Semicolon
    T, TERMS =  6,  6 # Characters after which lexing should stop.
    O, OTHER =  7,  7 # Anything other than those specified.
    D, DIGIT =  8,  8 # 0-9
    # Keep ALPHA and UCODE last to enable nonAlpha detection as less than ALPHA.
    A, ALPHA =  9,  9 # Alphabetic
    F, FAKES = 10, 10 # Fake alphabetic like apostrophe and dash
    U, UCODE = 11, 11 # Unicode

    # Special cases for this table '\\', '/', and '(' are terminators.
    # Also, '{', '[', and ','.

    # The ASCII-only table.  Unicode is handled as monolithic elsewhere.
    ASCII = [
          # 00 01 02 03  04 05 06 07   08 09 0A 0B  0C 0D 0E 0F
            X, X, X, X,  X, X, X, X,   X, W, W, X,  W, W, X, X, # 00
            X, X, X, X,  X, X, X, X,   X, X, X, X,  X, X, X, X, # 10
            O, O, O, O,  O, O, O, F,   T, O, O, O,  C, F, O, R, # 20
            D, D, D, D,  D, D, D, D,   D, D, O, S,  O, O, O, O, # 30

            O, A, A, A,  A, A, A, A,   A, A, A, A,  A, A, A, A, # 40
            A, A, A, A,  A, A, A, A,   A, A, O, T,  T, O, O, O, # 50
            O, A, A, A,  A, A, A, A,   A, A, A, A,  A, A, A, A, # 60
            A, A, A, A,  A, A, A, A,   A, A, O, T,  O, O, O, X, # 70

            X, X, X, X,  X, X, X, X,   X, X, X, X,  X, X, X, X, # 80
            X, X, X, X,  X, X, X, X,   X, X, X, X,  X, X, X, X, # 90
            U, U, U, U,  U, U, U, U,   U, U, U, U,  U, U, U, U, # A0
            U, U, U, U,  U, U, U, U,   U, U, U, U,  U, U, U, U, # B0

            U, U, U, U,  U, U, U, U,   U, U, U, U,  U, U, U, U, # C0
            U, U, U, U,  U, U, U, U,   U, U, U, U,  U, U, U, U, # D0
            U, U, U, U,  U, U, U, U,   U, U, U, U,  U, U, U, U, # E0
            U, U, U, U,  U, U, U, U,   U, U, U, U,  U, U, U, U] # F0
          # 00 01 02 03  04 05 06 07   08 09 0A 0B  0C 0D 0E 0F

          # Unicode standards: 0x80-0x9F are control characters.
          # http://ascii-table.com/unicode.php

    # This is a table used to directly uppercase alphabetics
    # and retain characters permitted in naming conventions.
    # Currently these include apostrophes and hyphens.
    XLAT = [
             '' , '' , '' , '' , '' , '' , '' , '' , # 00-07
             '' , '' , '' , '' , '' , '' , '' , '' , # 08-0F

             '' , '' , '' , '' , '' , '' , '' , '' , # 10-17
             '' , '' , '' , '' , '' , '' , '' , '' , # 17-1F

             '' , '' , '' , '' , '' , '' , '' ,'\'', # 20-27 Apostrophe
             '' , '' , '' , '' , '' ,'-' , '' , '' , # 27-2F Dash

             '' , '' , '' , '' , '' , '' , '' , '' , # 30-37
             '' , '' , '' , '' , '' , '' , '' , '' , # 37-3F

             '' , 'A', 'B', 'C', 'D', 'E', 'F', 'G', # 40-47 Upper
             'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', # 47-4F Upper

             'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', # 50-57 Upper
             'X', 'Y', 'Z',  '',  '',  '',  '',  '', # 57-5F Upper

             '' , 'A', 'B', 'C', 'D', 'E', 'F', 'G', # 60-67 Lower
             'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', # 67-6F Lower

             'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', # 70-77 Lower
             'X', 'Y', 'Z',  '',  '',  '',  '',  '', # 77-7F Lower

             '' , '' , '' , '' , '' , '' , '' , '' , # 80-87
             '' , '' , '' , '' , '' , '' , '' , '' , # 87-8F

             '' , '' , '' , '' , '' , '' , '' , '' , # 90-97
             '' , '' , '' , '' , '' , '' , '' , '' , # 97-9F

             '' , '' , '' , '' , '' , '' , '' , '' , # A0-A7
             '' , '' , '' , '' , '' , '' , '' , '' , # A7-AF

             '' , '' , '' , '' , '' , '' , '' , '' , # B0-B7
             '' , '' , '' , '' , '' , '' , '' , '' , # B7-BF

             '' , '' , '' , '' , '' , '' , '' , '' , # C0-C7
             '' , '' , '' , '' , '' , '' , '' , '' , # C7-CF

             '' , '' , '' , '' , '' , '' , '' , '' , # D0-D7
             '' , '' , '' , '' , '' , '' , '' , '' , # D7-DF

             '' , '' , '' , '' , '' , '' , '' , '' , # E0-E7
             '' , '' , '' , '' , '' , '' , '' , '' , # E7-EF

             '' , '' , '' , '' , '' , '' , '' , '' , # F0-F7
             '' , '' , '' , '' , '' , '' , '' , '' , # F7-FF
           ]

    # Map qwerty keyboard to possible fat_fingerings.
    QWERTY = {
            # These are lists of all keys within a one key radius of center.
            # Only alphabetics are considered for centers and
            # only uppercase are considered for matching (by using .upper()).
            'A': 'AaQWSXZqwsxz',
            'B': 'BbVGHNvghn',
            'C': 'CcXDFVxdfv',
            'D': 'DdSERFCXserfcx',
            'E': 'EeWSDR34#$wsdr',
            'F': 'FfDRTGVCdrtgvc',
            'G': 'GgFTYHBVftyhbv',
            'H': 'HhGYUJNBgyujnb',
            'I': 'IiUJKO89(*ujko',
            'J': 'JjHUIKMNhuikmn',
            'K': 'KkJIOL<Mjiol,m',
            'L': 'LlKOP:><kop;.,',
            'M': 'MmNJKL< jkl,',
            'N': 'NnBHJM bhjm',
            'O': 'OoI90PLK()iplk',
            'P': 'PpO0-[;Lo)_{:l',
            'Q': 'Qq  12WA!@wa',
            'R': 'Rr45TFDE$%tfde',
            'S': 'SsAWEDXZawedxz',
            'T': 'TtR56YGFr%^ygf',
            'U': 'UuY78IJH&*ijh',
            'V': 'VvCFGB cfgb',
            'W': 'WwQ23ESAq@#esa',
            'X': 'XxZSDC zsdc',
            'Y': 'YyT67UHGt^&uhg',
            'Z': 'ZzASXasx',
    }

    # Map Dvorak keyboard to possible fat_fingerings.
    DVORAK = {
            'A': 'Aa?:,Oo;\'',
            'B': 'BbXxDdHhMm ',
            'C': 'CcGg24$$4TtHh',
            'D': 'DdIiFfGgHhBbXx',
            'E': 'EeOo.PpUuJjQq',
            'F': 'FfYy9%0_GgDdIi',
            'G': 'GgFf0_2CcHhDd',
            'H': 'HhDdGgCcTtMmBb',
            'I': 'IiUuYyFfDdXxKk',
            'J': 'JjQqEeUuKk ',
            'K': 'KkJjUuIiXx ',
            'L': 'LlRr6@8*/&SsNn',
            'M': 'MmBbHhTtWw ',
            'N': 'NnTtRrLlSsVvWw',
            'O': 'OoAa,.EeQq;\'',
            'P': 'Pp.3)1"YyUuEe',
            'Q': 'Qq\':OoEeJj ',
            'R': 'RrCc4$6@LlNnTt',
            'S': 'SsNnLl&/-ZzVv',
            'T': 'TtHhCcRrNnWwMm',
            'U': 'UuEePpYyIiKkJj',
            'V': 'VvWwNnSsZz',
            'W': 'Ww MmTtNnVv',
            'X': 'Xx KkIiDdBb',
            'Y': 'YyPp1"9%FfIiUu',
            'Z': 'ZzVvSs-',
    }

    keyboard = {
            # This dictionary enables consideration of alternate keyboards.
            'QWERTY': QWERTY,
            'DVORAK': DVORAK
            }

    stopwords = [u'THE', u'OF', u'AND', u'FOR', u'INC', u'--']

    ABIM = 'American Board of Internal Medicine'

    def bool_report(self, TF, title, word, canon=None, **kw):
        # A function to generate regular output to the log file.
        used = kw.get('used', '')
        if used:
            octothorpe = 79 - len(used)
            if octothorpe < 1:
                octothorpe = 1
            print>>self.log, used, '#' * octothorpe
        elif TF and self.log:
            # Log result and return True
            if self.log:
                tab, tabs = '  ', int(kw.get('tabs', 1))
                indent = tab * tabs
                tab = tab if not tabs else ''
                qword = '"%s"' % (word)
                if canon:
                    qcanon = '"%s"' % (canon)
                    print>>self.log, '%s%-24s  %s%32s : %s' % (
                            indent, title, tab, qword, qcanon)
                else:
                    print>>self.log, '%s%-24s  %s%32s' % (
                            indent, title, tab, qword)
        return TF

    # This is the table-driven lexer.
    def lex_line(self, rough):
        # Make class statics visible without prefix.
        A =     Similar.ALPHA
        C =     Similar.COMMA
        D =     Similar.DIGIT
        M =     Similar.MINUS
        R =     Similar.RATIO
        S =     Similar.WHITE
        T =     Similar.TERMS
        U =     Similar.UCODE
        ASCII = Similar.ASCII
        XLAT  = Similar.XLAT

        tokens      = [u''] # Storage for separated words.

        if len(rough):
            terminators = [T, R, C] # M?

            # Single letter variables are used to compress visual inspection.
            # c is the current character.
            # o is used for the ordinal throughout lex.
            # t is the type of character (either U or indexed from ASCII).
            # k is the flag for keeping characters (transitions cause new token).
            # s is the current state of the state machine.
            c = rough[0]
            o = ord(c)
            Unicode = o>255
            t = U if Unicode else ASCII[o]
            x = o # * int(not Unicode)
            k = t >= A

            for c in rough:
                # A character ordinal is not enough when using Unicode
                o = ord(c)

                # If it is outside the ASCII range, it is handled differently.
                Unicode = o>255
                t = U if Unicode else ASCII[o]
                x = o * int(not Unicode)

                if t in terminators:
                    # If character is a terminator or context switcher, stop.
                    break

                if k:
                    # If in token building mode, check for transition.
                    if t < A:
                        # Leaving token building mode.
                        k = False
                elif not k:
                    # If not in token building mode, check for transition.
                    if t >= A:
                        # Entering token building mode
                        k = True
                        # Take a list of tokens for identifying Boards

                        if tokens[-1] != u'':
                            # Eliminate empty tokens
                            if tokens[-1] in self.stopwords:
                                # Eliminate stopwords
                                tokens[-1] = u''
                            else:
                                # Begin a new token
                                tokens.append(u'')

                # Append char to latest each of string and token.
                # Note that Unicode uses index of zero which is always False.
                xlat = XLAT[x]
                tokens[-1] += xlat
        if tokens[-1] in self.stopwords:
            # In case a final stopword made it past the transition.
            tokens = tokens[:-1]
        return tokens

    def generate_fat_finger_index(self, C1, C2):
        # This function generates the fat finger array index.
        # If C1 could have been C2, and both are in ASCII range,
        # this function generates in index to a True value.
        I1, I2 = int(ord(C1)), int(ord(C2))
        Unicode = I1 > 255 or I2 > 255
        return 0 if Unicode else int(ord(C1))+(int(ord(C2))<<8)

    def generate_head_tail_indices(self, canon, rough):
        # This function moves the head and tail values to
        # the positions from beginning and end where
        # two tokens first begin to mismatch.
        self.head, self.tail = 0, 0
        self.Clen, self.Rlen = len(canon), len(rough)
        self.Nmin = min(self.Clen, self.Rlen)
        # Find the first non-matching location.
        while self.head < self.Nmin and canon[self.head] == rough[self.head]:
            self.head += 1
        # Find the last non-matching location.
        while self.tail < self.Nmin and canon[-1-self.tail] == rough[-1-self.tail]:
            self.tail += 1
        # How much head and tail match.
        self.both = self.head + self.tail
        # How much combined match differs from total length.
        self.diff = self.Nmin - self.both

    def generate_acronym(self, sequence):
        # This function jams first letters of tokens into an acronym.
        return string.join([word[0] if word else '' for word in sequence], '')

    def fill_arbor(self, rough):
        # Build a dictionary arbor from token lists.
        sequence = self.lex_line(rough)

        # Build the acronym dictionary.
        letters = self.generate_acronym(sequence)
        existing = self.acro.get(letters, set())
        existing.add(rough)
        self.acro[letters] = existing

        # Build the word arbor.
        height, branch = 0, self.root

        branch[u'#'] = 0
        for word in sequence:
            height += 1
            branch[word] = branch.get(word, {})
            branch = branch[word]
            branch[u'#'] = height
        if not branch.get('.'):
            branch['.'] = rough
            branch['.soundex4'] = self.soundex4(rough)
            branch['.dmeta'] = self.dmeta(rough)
            #branch['.nyssis'] = fuzzy.nyssis(rough)

    def bool_algorithm_fat_finger(self, canon, rough):
        # Discover whether all the characters in a token are
        # within one key distance on the keyboard for a given canonical word.
        N, Nc, Nr = 0, len(canon), len(rough)
        if Nc != Nr:
            return False
        for n in range(Nc):
            Cc, Cr = canon[n], rough[n]
            if not self.fast_lookup[self.generate_fat_finger_index(Cr, Cc)]:
                break
            N += 1
        message = 'fat finger [%d/%d] %s' % (N, Nc, str(N == Nc))
        result = self.bool_report(N == Nc, message, rough, canon)
        return result

    def bool_algorithm_Levenshtein1(self, canon, rough):
        # Handle identity.
        if canon == rough:
            return self.bool_report(True, 'Levenshtein1', rough, canon)
        self.generate_head_tail_indices(canon, rough)
        # Handle length difference out-of-range.
        if abs(self.Clen-self.Rlen) > 1:
            return False
        # Handle deletion and insertion.
        if self.Clen != self.Rlen:
            return self.Nmin == self.both
        # Handle a single typo.
        if self.diff == 1:
            return self.bool_report(True, 'Levenshtein1', rough, canon)
        # Handle 1 swapped pair.
        diagonal1 = canon[   self.head] == rough[-1-self.tail]
        diagonal2 = canon[-1-self.tail] == rough[   self.head]
        if diagonal1 and diagonal2:
            return self.bool_report(True, 'Levenshtein1', rough, canon)
        return False

    def bool_algorithm_Lettvin(self, canon, rough, level=0):
        if not rough:
            return True, level
        C, Ctail = canon[0].upper(), canon[1:]
        R, Rtail = rough[0].upper(), rough[1:]
        Oc, Or = ord(C), ord(R)
        for spread in Similar.QWERTY.get(R, ''):
            if C in spread:
                deep, level = self.bool_algorithm_Lettvin(Ctail, Rtail, level+1)
                if deep:
                    return True, level
        return False, level

    def bool_algorithm_contraction(self, canon, rough):
        # Handle identity.
        if canon == rough:
            return self.bool_report(True, 'contraction', rough, canon)
        self.generate_head_tail_indices(canon, rough)
        rlen = len(rough)
        less = rlen - 2
        if rlen == self.head:
            return self.bool_report(True, 'contraction', rough, canon)
        if self.head >= 2:
            return self.bool_report(True, 'contraction', rough, canon)
        if self.both > less:
            return self.bool_report(True, 'contraction', rough, canon)
        return False

    def bool_algorithm_soundex(self, canon, rough):
        return False

    def bool_algorithm_metaphone(self, canon, rough):
        return False

    def bool_algorithm_NYSSIS(self, canon, rough):
        return False

    def bool_algorithm_exact(self, canon, rough):
        return self.bool_report(canon == rough, 'exact', rough, canon)

    def bool_recurse(self, branch, sequence, **kw):
        # This function does the heavy lifting for
        # Determining the type of match a token has
        # at a given branch of dictionary.
        # Care has been taken to walk the entire breadth
        # until either a match is found, or none can be.
        # So if a recursion terminates in a failure,
        # and a branch is not exhausted, the search continues.

        if not isinstance(branch, dict):
            # No dictionary, so stop with no results.
            return False, [], ''
        if not len(sequence):
            # Tokens finished, so return the canonical form.
            return True, [], branch.get('.', '')

        # Get the first word.
        word = sequence[0]
        current_algorithm = '?'
        level = branch['#']

        separate = True
        if separate and branch.get(word):
            # If it has an exact match, recurse.
            flag, result, final = self.bool_recurse(
                branch[word], sequence[1:], **kw)
            if not final:
                # If recursion failed to make canonical
                # Perhaps it is canonical at this branch.
                final = branch.get('.', '')
            if final:
                self.using[level] = '.'
                # If canonical form was found, then report it.
                flag = True
            return flag, [word].append(result), final

        # If no exact match is found, try fuzziness.
        for canon, val in branch.iteritems():
            found = False
            for letter in self.control.get('algorithms'):
                current_algorithm = letter
                algorithm = self.master_algorithm_list[letter]['algorithm']
                found |= algorithm(canon, word)
                if found:
                    # For optimization, take the first match.
                    # If a combined measure is wanted, remove this break.
                    break
            result, final = [], ''

            if found:
                self.using[level] = current_algorithm
                # As with the exact match, report recursed or current match.
                flag, result, final = self.bool_recurse(
                    branch[canon], sequence[1:], **kw)
                if not final:
                    final = branch.get('.', '')
                if final:
                    flag = True
                found &= flag

            if found:
                # Just because a match was found doesn't mean another won't.
                if not final:
                    final = branch.get('.', '')
                if final:
                    flag = True
                # Return a list of findings
                return True, [canon].append(result), final

        return False, [], ''

    def loop(self, sequence, **kw):
        # Handle white-list non-canonicals.
        previous  = 'initialize'
        mBool = False
        result    = []
        while previous:
            # Insane though this may appear,
            # this loop enables sequential re-lookup on a prior search
            # because white-list non-canonicals are permitted to
            # populate the dictionary and return canonicals.
            mBool, result, canon = self.bool_recurse(self.root, sequence, **kw)
            if not canon:
                break
            if previous == canon:
                break
            previous = canon
        return mBool, result, canon

    def __init__(self, canon = {ABIM: ['ABIM']}, **kw):
        # Setup parameters for execution.
        self.control = {
                'algorithms': 'cefLmNs',
                'keyboard'  : 'QWERTY',
                'stopwords' : Similar.stopwords,
                'both'      : 2,
                'left'      : 2,
                'right'     : 2,
                'verbose'   : True,
                'output'    : None
                }
        self.control.update(kw)
        self.good = self.control.get('good', None)
        self.fail = self.control.get('fail', None)
        self.log = self.control.get('output', None)
        self.acronyms = self.control.get('acronym', True)
        self.contraction = self.control.get('contraction', True)
        self.soundex4 = fuzzy.Soundex(4)
        self.dmeta = fuzzy.DMetaphone()
        self.transforms = '' # Must precede self.lex, but follow self.log

        self.master_algorithm_list = {
                '_': {'algorithm': self.bool_algorithm_Lettvin, },
                'c': {'algorithm': self.bool_algorithm_contraction, },
                'e': {'algorithm': self.bool_algorithm_exact, },
                'f': {'algorithm': self.bool_algorithm_fat_finger,},
                'L': {'algorithm': self.bool_algorithm_Levenshtein1,},
                'm': {'algorithm': self.bool_algorithm_metaphone,},
                'N': {'algorithm': self.bool_algorithm_NYSSIS,},
                's': {'algorithm': self.bool_algorithm_soundex},
        }

        # Extract parameters.
        self.stopwords = self.control['stopwords']
        keyboard_layout = self.control['keyboard']
        self.keyboard = Similar.keyboard[keyboard_layout]

        self.root = dict()
        self.acro = dict()

        # Convert fatfinger lists to fast lookup table.
        self.fast_lookup = [False]*65536
        for intended, neighbors in self.keyboard.iteritems():
            for neighbor in neighbors:
                # At this point, characters are known to be 0-255
                self.fast_lookup[
                        self.generate_fat_finger_index(neighbor, intended)
                        ] = True
        N = 0
        for n in range(65536):
            N += int(self.fast_lookup[n])

        # Convert canonical list to all uppercase.
        for key, vals in canon.iteritems():
            VALS = [val.upper() for val in vals]
            VALS = [val for val in VALS if val not in self.stopwords]
            self[key.upper()] = self.get(key.upper(), []).append(VALS)

    def __call__(self, rough, **kw):
        self.transforms = '' # Must precede self.lex
        self.using = {}
        letters, matchBool, result, canonical = False, False, [], ''
        sequence = self.lex_line(rough)

        if sequence and sequence[0]:
            if not self.acronyms:
                matchBool, result, canonical = self.bool_recurse(
                    self.root, sequence, **kw)
            else:
                acronyms = [string.join(sequence, ''), sequence[0]]
                for acronym in acronyms:
                    if self.acro.get(acronym):
                        letters = True
                        matchBool = True
                        canonical = self.acro[acronym]
                        break
                if not matchBool:
                    # A bug forces this back out of the loop until it is fixed.
                    matchBool, result, canonical = self.bool_recurse(
                        self.root, sequence, **kw)
                    #self.loop(sequence)
        if matchBool and canonical:
            # The output to good csv file has two forms:
            # 1. set(...) means acronym with possible ambiguity.
            # 2. "words..." in column 1 means canonical name found.
            if self.good:
                print>>self.good, '"%s", "%s"' % (canonical, rough)
        else:
            # Output to fail csv file are uncanonicalized inputs.
            if self.fail:
                print>>self.fail, '"%s"' % (rough)
        self.bool_report(
                True, '1' if matchBool else '0',
                #str(matchBool),
                canonical,
                rough,
                tabs=0)

        # Build up the matching algorithm string from entries.
        used = ''
        for i in range(30):
            c = self.using.get(i, '')
            used += c
            if not c:
                break

        self.bool_report(True, None, 'canonical', canonical, used=used)

        # If matchBool is True,
        # the dictionary arbor was walked to a proper terminal.
        # If it is True, canonical will have the matching canonical form.
        return matchBool, canonical, used

if __name__ == "__main__":

    import re     # Used during input of CSV files.
    import sys
    import pprint
    import os.path
    import unittest
    import datetime

    class Results(object):

        def open_file(self, directory, name):
            return open(os.path.join(directory, name), "w+")

        def __init__(self, name):
            self.name = name
            self.choose = {
                    "PASS": self.open_file("PASS", name),
                    "FAIL": self.open_file("FAIL", name)}

        def __del__(self):
            for key, stream in self.choose.iteritems():
                stream.close()

        def FAIL(self):
            return self.choose['FAIL']

        def PASS(self):
            return self.choose['PASS']

    class test_Similar(unittest.TestCase):

        def clear(self, stream):
            if stream:
                stream.seek(0)
                stream.truncate(0)

        def setUp(self):
            # These words appear in board.csv
            possibles = [u'DIPLOMAT', u'DIPLOMATE']
            Similar.stopwords += possibles

            # Switch input from shared to local.
            self.boards = True

            # Switch output on or off
            self.output = True

            self.boardname = "boards.csv"
            self.logname   = 'Similar.log'
            self.failname  = 'Fail.csv'
            self.goodname  = 'Good.csv'

            # Prepare the input filename in case it is used.
            self.home = os.environ['HOME']
            self.directory = './'
            if self.boards:
                self.directory = os.path.abspath(os.path.dirname(__file__))
                #self.directory = os.path.join(
                        #self.home, 'src', 'jlettvin', 'data', 'mappings')
            self.boardfile = os.path.join(self.directory, self.boardname)

            if not self.output:
                self.log, self.fail, self.good = None, None, None
            else:
                # Prepare the log file for output.
                self.log  = open(self.logname, 'a+')

                # Prepare logging target for failed canonicalization.
                self.fail = open(self.failname, 'a+')

                # Prepare logging target for successful canonicalization.
                self.good = open(self.goodname, 'a+')

            # Instance a Similar object for testing.
            self.similar = Similar(
                    output=self.log, good=self.good, fail=self.fail)

        def tearDown(self):
            if self.good:
                self.good.close()
            if self.fail:
                self.fail.close()
            if self.log:
                self.log.close()

        def test_000_empty(self):

            self.clear(self.log)
            self.clear(self.good)
            self.clear(self.fail)

            if self.log:
                print>>self.log, 'Similar.py log:', datetime.datetime.today()
                print>>self.log, "LEGEND:"
                print>>self.log, "  0 = phrase mismatch"
                print>>self.log, "  1 = phrase match"
                print>>self.log, "  A = acronym (partially implemented)"
                print>>self.log, "  C = contraction"
                print>>self.log, "  E = exact match"
                print>>self.log, "  F = fat finger match"
                print>>self.log, "  L = Levenshtein 1 change match"
                print>>self.log, "True/False followed by phrase shows result."
                print>>self.log, "Calls summarized by match letter sequence."
                print>>self.log, '#'*79

        def test_001_check_input_transform(self):
            results = Results("1.csv")
            pairs = [
                    # Strip away all but alphanumerics.
                    ([u"HELLO", u"WORLD"], u"  Hello  world!"),
                    # except leave hyphens and apostrophes in names.
                    ([u"JONATHAN'S", u"ALGORITHM-BASE"],
                     u"Jonathan's Algorithm-base"),
                    # Handle the empty set.
                    ([u""], "")
                    ]
            for canon, rough in pairs:
                result = self.similar.lex_line(rough)
                if result == canon:
                    print>>results.PASS(), rough
                else:
                    print>>results.FAIL(), rough
                self.assertEqual(result, canon)

        def test_002_check_QWERTY_fat_finger(self):
            # These character pairings are one key away.
            pairs = [
                    ([u"FAT", u"FINGER"], u"gsy gomhrt"),
                    ([u"FAT", u"FINGER"], u"fat funger"),
                    ([u"FAT", u"FINGER"], u"fat fibger"),
                    ([u"FAT", u"FINGER"], u"fat finfer"),
                    ([u"FAT", u"FINGER"], u"fat fonger"),
                    ([u"FAT", u"FINGER"], u"fat fknger"),
                    ([u"FAT", u"FINGER"], u"fat fjnger"),
                    # Handle the empty set.
                    ([u""], "")
                    ]
            # These character pairings is two keys away.
            error = [
                    #([u"DDDDDD"], u"WTAGZV"),
                    ([u"FFFFFF"], u"EYSHXB"),
                    ([u"GGGGGG"], u"rudjcn"),
                    ([u"HHHHHH"], u"tifkvm")
                    #([u"JJJJJJJ"], u"yoglb,")
                    ]
            for canon, rough in pairs:
                sequence = self.similar.lex_line(rough)
                N = len(sequence)
                message = 'compare "%s" with "%s"' % (canon, rough)
                self.assertTrue(N == len(canon), message)
                for n in range(N):
                    self.assertTrue(
                            self.similar.bool_algorithm_fat_finger(
                                canon[n], sequence[n]))
            for canon, rough in error:
                sequence = self.similar.lex_line(rough)
                N = len(sequence)
                C = len(canon)
                message = 'compare "%s" with "%s (%d/%d)"' % (
                        canon[0], sequence[0], N, C)
                self.assertTrue(N == C, message)
                for n in range(N):
                    message = 'compare "%s" with "%s"' % (canon[n], sequence[n])
                    self.assertFalse(
                            self.similar.bool_algorithm_fat_finger(
                                canon[n], sequence[n]),
                            message)

        def test_003_Check_Acronym(self):
            pairs = [
                    ([u"MIT"], u"Massachusetts Institute of Technology"),
                    ([u"LSMC"], u"Lee's Summit Medical Center"),
                    # Handle the empty set.
                    ([u""], u"")
                    ]
            for canon, rough in pairs:
                sequence = self.similar.lex_line(rough)
                if len(canon):
                    self.assertEqual(
                            canon[0], self.similar.generate_acronym(sequence))

        def test_004_Check_Levenshtein1(self):
            pairs = [
                    ([u"OFF", u"BY", u"ONE", u"INSERT"], u"Off buy one insert."),
                    ([u"OFF", u"BY", u"ONE", u"DELETE"], u"Off b one delete."),
                    ([u"OFF", u"BY", u"ONE", u"TYPO"], u"Off bt one typo."),
                    ([u"OFF", u"BY", u"ONE", u"SWAP"], u"Off yb one swap."),
                    # Handle the empty set.
                    ([u""], "")
                    ]
            for canon, rough in pairs:
                sequence = self.similar.lex_line(rough)
                N = len(sequence)
                C = len(canon)
                self.assertTrue(N == C)
                for n in range(N):
                    self.assertTrue(
                        self.similar.bool_algorithm_Levenshtein1(
                            canon[n], sequence[n]))

        def test_005_Check_contraction(self):
            pairs = [
                    ([u"AMERICAN"], u"Amer."),
                    ([u"INTERNAL"], u"Int'l"),
                    ([u"BOARD"], u"Bd."),
                    ([u"BOARD"], u"Brd."),
                    # Handle the empty set.
                    ([u""], u"")
                    ]
            for canon, rough in pairs:
                sequence = self.similar.lex_line(rough)
                N = len(sequence)
                self.assertTrue(N == len(canon))
                for n in range(N):
                    c, s = canon[n], sequence[n]
                    error = 'No match made "%s" "%s"' % (c, s)
                    self.assertTrue(
                            self.similar.bool_algorithm_contraction(
                                canon[n],
                                sequence[n]),
                            error)

        def test_006_Lettvin(self):
            # Couple the Levenshtein to the fat finger.
            # The results should be much broader and useful.
            # It implies the use of typing errors of both sorts
            # without the exclusions of either for the other.
            pairs = [
                    ([u"FOO"], u"foo"),
                    ([u"BAR"], u"bar"),
                    ([u""], u"")
                    ]
            for canon, rough in pairs:
                sequence = self.similar.lex_line(rough)
                N = len(sequence)
                self.assertTrue(N == len(canon))
                for n in range(N):
                    c, s = canon[n], sequence[n]
                    error = 'No match made "%s" "%s"' % (c, s)
                    self.assertTrue(
                            self.similar.bool_algorithm_Lettvin(
                                canon[n],
                                sequence[n]),
                            error)

        def test_007_Check_all(self):
            pairs = [
                    ([u"FAT", u"FINGER"], u"gsy gomhrt"),
                    ([u"MIT"], u"Massachusetts Institute of Technology"),
                    ([u"LSMC"], u"Lee's Summit Medical Center"),
                    ([u"OFF", u"BY", u"ONE", u"INSERT"], u"Off buy one insert."),
                    ([u"OFF", u"BY", u"ONE", u"DELETE"], u"Off b one delete."),
                    ([u"OFF", u"BY", u"ONE", u"TYPO"], u"Off bt one typo."),
                    ([u"OFF", u"BY", u"ONE", u"SWAP"], u"Off yb one swap."),
                    ([u"AMERICAN"], u"Amer."),
                    ([u"INTERNAL"], u"Int'l"),
                    ([u"BOARD"], u"Bd."),
                    ([u"BOARD"], u"Brd."),
                    ([u""], u"")
                    ]
            for canon, rough in pairs:
                sequence = self.similar.lex_line(rough)
                if len(canon) and canon[0] == self.similar.generate_acronym(
                        sequence):
                    continue
                N = len(sequence)
                C = len(canon)
                message = '(%d/%d) %s/%s' % (C,N,canon,sequence)
                self.assertTrue(N == C, message)
                for n in range(N):
                    c, s = canon[n], sequence[n]
                    if self.similar.bool_algorithm_fat_finger(c, s):
                        continue
                    if self.similar.bool_algorithm_Levenshtein1(c, s):
                        continue
                    if self.similar.bool_algorithm_contraction(c, s):
                        continue
                    error = 'No match made "%s" "%s"' % (c, s)
                    self.assertTrue(False, error)

        def test_008_arbor(self):
            rough = [
                    u"a a a", u"a a b", u"a a c",
                    u"a b a", u"a b b", u"a b c",
                    u"a c a", u"a c b", u"a c c",

                    u"b a a", u"b a b", u"b a c",
                    u"b b a", u"b b b", u"b b c",
                    u"b c a", u"b c b", u"b c c",

                    u"c a a", u"c a b", u"c a c",
                    u"c b a", u"c b b", u"c b c",
                    u"c c a", u"c c b", u"c c c"
                    ]

            final = {u'A': {u'A': {u'A': {u'.': u'a a a'},
                                   u'B': {u'.': u'a a b'},
                                   u'C': {u'.': u'a a c'}},
                            u'B': {u'A': {u'.': u'a b a'},
                                   u'B': {u'.': u'a b b'},
                                   u'C': {u'.': u'a b c'}},
                            u'C': {u'A': {u'.': u'a c a'},
                                   u'B': {u'.': u'a c b'},
                                   u'C': {u'.': u'a c c'}}},
                     u'B': {u'A': {u'A': {u'.': u'b a a'},
                                   u'B': {u'.': u'b a b'},
                                   u'C': {u'.': u'b a c'}},
                            u'B': {u'A': {u'.': u'b b a'},
                                   u'B': {u'.': u'b b b'},
                                   u'C': {u'.': u'b b c'}},
                            u'C': {u'A': {u'.': u'b c a'},
                                   u'B': {u'.': u'b c b'},
                                   u'C': {u'.': u'b c c'}}},
                     u'C': {u'A': {u'A': {u'.': u'c a a'},
                                   u'B': {u'.': u'c a b'},
                                   u'C': {u'.': u'c a c'}},
                            u'B': {u'A': {u'.': u'c b a'},
                                   u'B': {u'.': u'c b b'},
                                   u'C': {u'.': u'c b c'}},
                            u'C': {u'A': {u'.': u'c c a'},
                                   u'B': {u'.': u'c c b'},
                                   u'C': {u'.': u'c c c'}}}}

            # This must be generated by print and inspected visually.
            final = {u'#': 0,
                     u'A': {u'#': 1,
                            u'A': {u'#': 2,
                                   u'A': {u'#': 3,
                                          '.': u'a a a',
                                          '.dmeta': ['A', None],
                                          '.soundex4': 'A000'},
                                   u'B': {u'#': 3,
                                          '.': u'a a b',
                                          '.dmeta': ['AP', None],
                                          '.soundex4': 'A100'},
                                   u'C': {u'#': 3,
                                          '.': u'a a c',
                                          '.dmeta': ['AK', None],
                                          '.soundex4': 'A200'}},
                            u'B': {u'#': 2,
                                   u'A': {u'#': 3,
                                          '.': u'a b a',
                                          '.dmeta': ['AP', None],
                                          '.soundex4': 'A100'},
                                   u'B': {u'#': 3,
                                          '.': u'a b b',
                                          '.dmeta': ['APP', None],
                                          '.soundex4': 'A100'},
                                   u'C': {u'#': 3,
                                          '.': u'a b c',
                                          '.dmeta': ['APK', None],
                                          '.soundex4': 'A120'}},
                            u'C': {u'#': 2,
                                   u'A': {u'#': 3,
                                          '.': u'a c a',
                                          '.dmeta': ['AK', None],
                                          '.soundex4': 'A200'},
                                   u'B': {u'#': 3,
                                          '.': u'a c b',
                                          '.dmeta': ['AKP', None],
                                          '.soundex4': 'A210'},
                                   u'C': {u'#': 3,
                                          '.': u'a c c',
                                          '.dmeta': ['AKK', None],
                                          '.soundex4': 'A200'}}},
                     u'B': {u'#': 1,
                            u'A': {u'#': 2,
                                   u'A': {u'#': 3,
                                          '.': u'b a a',
                                          '.dmeta': ['P', None],
                                          '.soundex4': 'B000'},
                                   u'B': {u'#': 3,
                                          '.': u'b a b',
                                          '.dmeta': ['PP', None],
                                          '.soundex4': 'B100'},
                                   u'C': {u'#': 3,
                                          '.': u'b a c',
                                          '.dmeta': ['PK', None],
                                          '.soundex4': 'B200'}},
                            u'B': {u'#': 2,
                                   u'A': {u'#': 3,
                                          '.': u'b b a',
                                          '.dmeta': ['PP', None],
                                          '.soundex4': 'B100'},
                                   u'B': {u'#': 3,
                                          '.': u'b b b',
                                          '.dmeta': ['PPP', None],
                                          '.soundex4': 'B100'},
                                   u'C': {u'#': 3,
                                          '.': u'b b c',
                                          '.dmeta': ['PPK', None],
                                          '.soundex4': 'B120'}},
                            u'C': {u'#': 2,
                                   u'A': {u'#': 3,
                                          '.': u'b c a',
                                          '.dmeta': ['PK', None],
                                          '.soundex4': 'B200'},
                                   u'B': {u'#': 3,
                                          '.': u'b c b',
                                          '.dmeta': ['PKP', None],
                                          '.soundex4': 'B210'},
                                   u'C': {u'#': 3,
                                          '.': u'b c c',
                                          '.dmeta': ['PKK', None],
                                          '.soundex4': 'B200'}}},
                     u'C': {u'#': 1,
                            u'A': {u'#': 2,
                                   u'A': {u'#': 3,
                                          '.': u'c a a',
                                          '.dmeta': ['K', None],
                                          '.soundex4': 'C000'},
                                   u'B': {u'#': 3,
                                          '.': u'c a b',
                                          '.dmeta': ['KP', None],
                                          '.soundex4': 'C100'},
                                   u'C': {u'#': 3,
                                          '.': u'c a c',
                                          '.dmeta': ['KK', None],
                                          '.soundex4': 'C200'}},
                            u'B': {u'#': 2,
                                   u'A': {u'#': 3,
                                          '.': u'c b a',
                                          '.dmeta': ['KP', None],
                                          '.soundex4': 'C100'},
                                   u'B': {u'#': 3,
                                          '.': u'c b b',
                                          '.dmeta': ['KPP', None],
                                          '.soundex4': 'C100'},
                                   u'C': {u'#': 3,
                                          '.': u'c b c',
                                          '.dmeta': ['KPK', None],
                                          '.soundex4': 'C120'}},
                            u'C': {u'#': 2,
                                   u'A': {u'#': 3,
                                          '.': u'c c a',
                                          '.dmeta': ['KK', None],
                                          '.soundex4': 'C200'},
                                   u'B': {u'#': 3,
                                          '.': u'c c b',
                                          '.dmeta': ['KKP', None],
                                          '.soundex4': 'C210'},
                                   u'C': {u'#': 3,
                                          '.': u'c c c',
                                          '.dmeta': ['KKK', None],
                                          '.soundex4': 'C200'}}}}

            for text in rough:
                self.similar.fill_arbor(text)

            #pprint.pprint(self.similar.root)

            #print '\t\t', final
            #print '\t\t', self.similar.root
            self.assertEqual(self.similar.root, final)

        def test_009_CSV(self):
            csv = re.compile('("[^"]+")+')

            # Canonical names to be ignored from board.csv
            discard = [u'OTHER', u'IGNORE']

            # Generate the internal canonical dictionary.
            canon = []
            other = []
            with open(self.boardfile) as source:
                for line in source:
                    item = [phrase.strip('"') for phrase in csv.findall(line)]
                    first = item[0]
                    if first.upper() in discard:
                        continue
                    other += item[1:]
                    self.similar.fill_arbor(first)

            if self.log:
                print>>self.log, '#'*79

            # Now check the alternate names for match to dictionary.
            count, match = 0, 0
            show = False
            if show:
                print
            for rough in other:
                count += 1
                good, final, transform = self.similar(rough)
                if show and final:
                    print final
                match += good
            result = '\nPerformance %d/%d is %d%%' % (
                    match,
                    count,
                    100*match/count)
            if self.log:
                print result, 'see file named: "%s"' % (self.logname)
                print>>self.log, result
            else:
                print result

    unittest.main()
