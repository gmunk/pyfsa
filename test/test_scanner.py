import unittest

from scanner import create_nfa


class TestThompsonConstruction(unittest.TestCase):
    def test_create_nfa(self):
        test_data = [("a", set("a")), ("b", set("b")), ("ab?", {"a", "b"}), ("ab|", {"a", "b"})]

        for r, e in test_data:
            with self.subTest("Should have created a correct NFA."):
                nfa = create_nfa(r)

                self.assertEqual(nfa.alphabet, e)
