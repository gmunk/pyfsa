import unittest

from scanner.thompson import format_regex, convert_to_postfix


class TestShuntingYardAlgorithm(unittest.TestCase):
    def test_format_regex(self):
        test_data = [("ab", "a.b"), ("a(a|b)*b", "a.(a|b)*.b"), ("a(b|c)*", "a.(b|c)*")]

        for r, e in test_data:
            with self.subTest("Should have formatted (inserted explicit concatenation operators) the regex properly.",
                              r=r, e=e):
                self.assertEqual(format_regex(r), e)

    def test_convert_to_postfix(self):
        test_data = [("a.a.b", "aa.b."),
                     ("a|b", "ab|"),
                     ("a|b*", "ab*|"),
                     ("a.(a|b)", "aab|."),
                     ("a.(a|b)*.b", "aab|*.b.")]

        for r, e in test_data:
            with self.subTest("Should have converted the regex to a postfix representation properly.", r=r, e=e):
                self.assertEqual(convert_to_postfix(r), e)
