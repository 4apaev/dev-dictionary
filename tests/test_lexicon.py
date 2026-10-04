import unittest

from lib import lexicon


class ParseTest(unittest.TestCase):
    def test_comments_and_blank_lines(self):
        text = "# header\n\nbtw\nidk  # inline comment\n   \n"
        self.assertEqual(lexicon.parse(text), {"btw": "", "idk": ""})

    def test_several_words_on_one_line(self):
        self.assertEqual(lexicon.parse("tl dr"), {"tl": "", "dr": ""})

    def test_plural_flag(self):
        self.assertEqual(lexicon.parse("repo/S"), {"repo": "S"})

    def test_unknown_flags_are_dropped(self):
        self.assertEqual(lexicon.parse("repo/XS word/Q"), {"repo": "S", "word": ""})

    def test_mixed_case_adds_lowercase(self):
        self.assertEqual(lexicon.parse("GitHub API/S"),
                         {"GitHub": "", "github": "", "API": "S", "api": "S"})

    def test_empty_word_is_skipped(self):
        self.assertEqual(lexicon.parse("/S"), {})


class MergeTest(unittest.TestCase):
    def test_flags_merge(self):
        self.assertEqual(lexicon.merge({"repo": ""}, {"repo": "S", "btw": ""}),
                         {"repo": "S", "btw": ""})


class PluralTest(unittest.TestCase):
    def test_rules(self):
        cases = {
            "repo": "repos",
            "dependency": "dependencies",
            "key": "keys",
            "regex": "regexes",
            "subprocess": "subprocesses",
            "hash": "hashes",
            "API": "APIs",
            "LLM": "LLMs",
        }
        for word, expected in cases.items():
            self.assertEqual(lexicon.plural(word), expected, word)


class ExpandTest(unittest.TestCase):
    def test_adds_plurals_for_flagged_words_only(self):
        self.assertEqual(lexicon.expand({"repo": "S", "btw": ""}), {"repo", "repos", "btw"})


class RenderTest(unittest.TestCase):
    def test_count_line_and_sorted_entries(self):
        dic = lexicon.render_dic({"repo": "S", "btw": "", "API": "S"})
        self.assertEqual(dic, "3\nAPI/S\nbtw\nrepo/S\n")

    def test_aff_defines_every_flag(self):
        for flag in lexicon.FLAGS:
            self.assertIn("SFX {} ".format(flag), lexicon.AFF)


if __name__ == "__main__":
    unittest.main()
