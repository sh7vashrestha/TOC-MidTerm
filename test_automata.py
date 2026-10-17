"""Correctness matters here: degree bounds alone would not prove anything."""

import random
import re
import unittest
from itertools import product

from automata import (NFA, accepts, degrees, equivalent, high_degree_example,
                      make_2_nfa, minimize_dfa, thompson, to_dfa)
from main import REQUIRED_REGEX


class AutomataTests(unittest.TestCase):
    def check_bounded(self, original):
        result = make_2_nfa(original)
        incoming, outgoing = degrees(result)
        self.assertTrue(all(incoming[q] <= 2 and outgoing[q] <= 2 for q in result.states))
        self.assertEqual(equivalent(original, result), (True, None))
        old_in, old_out = degrees(original)
        extra = sum(max(0, old_in[q] - 2) + max(0, old_out[q] - 2)
                    for q in original.states)
        self.assertEqual(len(result.states), len(original.states) + extra)
        self.assertEqual(len(result.edges), len(original.edges) + extra)
        return result

    def test_required_expression_counts(self):
        original = thompson(REQUIRED_REGEX)
        bounded = self.check_bounded(original)
        dfa, subsets = to_dfa(original)
        minimal = minimize_dfa(dfa)
        self.assertEqual((len(original.states), len(original.edges)), (26, 29))
        self.assertEqual(set(original.edges), set(bounded.edges))
        self.assertEqual((len(dfa.states), len(dfa.edges)), (11, 33))
        self.assertEqual((len(minimal.states), len(minimal.edges)), (7, 21))
        self.assertEqual(equivalent(original, dfa), (True, None))
        self.assertEqual(equivalent(original, minimal), (True, None))

    def test_parser_against_python_regex(self):
        patterns = ["a", "ab", "a|b", "a|bc", "ab|c", "a*", "ab*", "(ab)*",
                    "(a|b)*a", "((a|b)*)*", "a(b|c)*", REQUIRED_REGEX]
        for pattern in patterns:
            machine = thompson(pattern)
            for length in range(7):
                for chars in product("abc", repeat=length):
                    word = "".join(chars)
                    self.assertEqual(accepts(machine, word),
                                     re.fullmatch(pattern, word) is not None,
                                     (pattern, word))

    def test_all_sixteen_words_and_rejections(self):
        machine = thompson(REQUIRED_REGEX)
        accepted = []
        for chars in product("abc", repeat=5):
            word = "".join(chars)
            if accepts(machine, word):
                accepted.append(word)
        expected = {first + "c" + "".join(tail)
                    for first in "ab" for tail in product("ab", repeat=3)}
        self.assertEqual(set(accepted), expected)
        for word in ["", "acaa", "acaaaa", "aacaa", "ccaaa", "acaca", "acaaax"]:
            self.assertFalse(accepts(machine, word), word)

    def test_real_degree_reduction(self):
        original = high_degree_example()
        result = self.check_bounded(original)
        self.assertEqual((len(original.states), len(original.edges)), (11, 16))
        self.assertEqual((len(result.states), len(result.edges)), (19, 24))
        self.assertTrue(accepts(result, "ab"))
        for word in ["", "a", "b", "ba", "aab", "abb"]:
            self.assertFalse(accepts(result, word))

    def test_fifteen_connections(self):
        self.check_bounded(high_degree_example(15))

    def test_epsilon_and_empty_languages(self):
        for pattern in ["ε", "∅", "∅*", "ε|a", "(ε|a)*", "a∅", "εa"]:
            machine = thompson(pattern)
            self.check_bounded(machine)
            dfa, subsets = to_dfa(machine)
            self.assertTrue(equivalent(machine, minimize_dfa(dfa))[0])
        self.assertTrue(accepts(thompson("ε"), ""))
        self.assertFalse(accepts(thompson("∅"), ""))
        self.assertFalse(accepts(thompson("∅"), "a"))
        self.assertTrue(accepts(thompson("∅*"), ""))

    def test_random_nfas_with_cycles_and_multiple_finals(self):
        # Fixed seed makes failures reproducible. These are arbitrary NFAs,
        # not just the already-bounded NFAs built by Thompson's method.
        rng = random.Random(8041)
        for trial in range(30):
            machine = NFA()
            for i in range(5):
                machine.new_state()
            machine.start = 0
            machine.finals = {q for q in machine.states if rng.choice([True, False])}
            for i in range(18):
                edge = (rng.randrange(5), rng.choice(["", "a", "b"]), rng.randrange(5))
                if edge not in machine.edges:
                    machine.add_edge(*edge)
            self.check_bounded(machine)
            dfa, subsets = to_dfa(machine)
            self.assertTrue(equivalent(machine, minimize_dfa(dfa))[0])

    def test_counterexample_finder(self):
        self.assertEqual(equivalent(thompson("a"), thompson("b")), (False, "a"))
        self.assertEqual(equivalent(thompson("ε"), thompson("a")), (False, ""))

    def test_invalid_regex(self):
        for pattern in ["", "()", "a|", "|a", "(a", "a)", "*a", "a+", "a.b"]:
            with self.assertRaises(ValueError, msg=pattern):
                thompson(pattern)


if __name__ == "__main__":
    unittest.main()
