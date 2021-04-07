import unittest
from pathlib import Path

from fa import NFA


class TestNFA(unittest.TestCase):
    def test_accepts(self):
        valid_words = ["ab", "aab"]
        invalid_words = ["aba", "abab", "aabaab", "invalid"]

        filepath = Path(__file__).parent.joinpath("resources", "nfa.json")
        nfa = NFA.from_json_file(filepath)

        for w in valid_words:
            with self.subTest("Should have validated the word.", w=w):
                self.assertTrue(nfa.accepts(w))

        for w in invalid_words:
            with self.subTest("Should not have validated the word", w=w):
                self.assertFalse(nfa.accepts(w))
