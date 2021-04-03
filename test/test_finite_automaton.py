import unittest
from finite_automaton import DFA, NFA

VALID_WORD_ERROR = "Should have accepted this word, since it was valid for this automaton."
INVALID_WORD_ERROR = "Should have rejected this word, since it was invalid for this automaton."


class TestFiniteAutomaton(unittest.TestCase):
    __test__ = False

    def setUp(self):
        self.fa = None
        self.valid_words = []
        self.invalid_words = []

    def test_accepts(self):
        for w in self.valid_words:
            with self.subTest(VALID_WORD_ERROR, w=w):
                self.assertTrue(self.fa.accepts(w))

        for w in self.invalid_words:
            with self.subTest(INVALID_WORD_ERROR, w=w):
                self.assertFalse(self.assertFalse(self.fa.accepts(w)))


class TestDeterministicFiniteAutomaton(TestFiniteAutomaton):
    __test__ = True

    def setUp(self):
        self.fa = DFA(states={"s0", "s1", "s2", "s3", "s4", "s5"},
                      alphabet={"n", "e", "w", "o", "t"},
                      transition_mappings={"s0": {"n": "s1"}, "s1": {"e": "s2", "o": "s4"},
                                                                    "s2": {"w": "s3"}, "s4": {"t": "s5"}},
                      start_state="s0",
                      accepting_states={"s3", "s5"})
        self.valid_words = ["new", "not"]
        self.invalid_words = ["nwt", "anew", "notnot"]


class TestNondeterministicFiniteAutomaton(TestFiniteAutomaton):
    __test__ = True

    def setUp(self):
        self.fa = NFA(states={"s0", "s1", "s2", "s3"},
                      alphabet={"a", "b"},
                      transition_mappings={"s0": {"a": {"s0"}, "": {"s1"}},
                                                                       "s1": {"a": {"s2"}},
                                                                       "s2": {"b": {"s3"}}},
                      start_state="s0",
                      accepting_states={"s3"})
        self.valid_words = ["ab", "aab"]
        self.invalid_words = ["aba", "abab", "aabaab", "test"]
