#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import math
import json
import operator
import sys

class JsonDebugEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return sorted(obj)
        try: ret = json.JSONEncoder.default(self, obj)
        except: ret = (str)(obj)
        return ret

# https://www.python.org/dev/peps/pep-0485/#proposed-implementation
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def gcd(a, b):
    """Calculate the Greatest Common Divisor of a and b.

        Unless b==0, the result will have the same sign as b (so that when
        b is divided by it, the result comes out positive).
        """
    while b:
        a, b = b, a % b
    return a

# https://stackoverflow.com/a/11175154/1187415
def get_notes_info():
    freq_base = 440.00
    midi_base = 69

    notes_info = {midi_base + semitone : { 'name': name, 'midi': midi_base + semitone, "freq": freq_base * math.pow(2., semitone/12.), 'interval': semitone, "ratio": [] }
                  for semitone, name in enumerate(["A4", "B4b/A4#", "B4", "C4", "D4b/C4#", "D4", "E4b/D4#", "E4", "F4", "G4/F4#", "G4", "A4b/G4#", "A5" ])}

    interv_info = {}
    ratios_done = set()
    for denom in range(1, 18):
        for numer in range(denom, 2 * denom + 1):
           common_divisor = gcd(numer, denom)
           (reduced_num, reduced_den) = (int(numer / common_divisor), int(denom / common_divisor))

           if (reduced_num, reduced_den) in ratios_done:
               continue

           freq = freq_base * numer / denom
           cents = 1200. * math.log2(freq / freq_base)
           midi = int(midi_base + round(12. * math.log2(freq / freq_base)))
           freq_midi = freq_base * math.pow(2., (midi - 69) / 12.)
           cents_midi = 1200. * math.log2(freq_midi / freq_base)
           err_cents = abs(cents - cents_midi)

           # https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0008144
           # https://www.ncbi.nlm.nih.gov/pubmed/19997506
           # "A Biological Rationale for Musical Scales" (Kamraan Z. Gill, Dale Purves)
           concordance = (reduced_num + reduced_den - 1) / (reduced_num * reduced_den)

           ratios_done.add((reduced_num, reduced_den))
           if err_cents > 20:
               continue

           closest_note = notes_info[midi]

           new_ratio = (reduced_num, reduced_den, freq, err_cents, concordance)
           closest_note['ratio'].append(new_ratio)
           closest_note['ratio'].sort(key = operator.itemgetter(1))

           low_freq = freq_base / reduced_den

           #eprint(f"{numer}/{denom} ({reduced_num}/{reduced_den}) -> freq={freq:.2f}, midi={midi}, cents={cents:.2f}, err={err_cents:.2f}, low_freq={low_freq:.2f}, concordance={concordance * 100:.2f}%")
    return notes_info

def main():
    interval_names = ['I','ii','II','iii','III','IV','v','V','vi','VI','vii','VII','I\'']
    notes_info = get_notes_info()
    #json.dump(notes_info, sys.stdout, cls=JsonDebugEncoder, indent=2, sort_keys=True, ensure_ascii=False, separators=(',', ':')); sys.stdout.write("\n")

    for k, d in notes_info.items():
        ratios_str = ", ".join([f"{num}/{den}" for num, den, freq, err, conc in d['ratio']])
        eprint(f"{d['name']} ({interval_names[d['interval']]}): midi={d['midi']}, freq={d['freq']:.2f} Hz, ratios=[{ratios_str}]")

if __name__ == '__main__':
    main()
