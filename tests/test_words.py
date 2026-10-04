"""Check the built-in word lists in words/."""
import json
import os
import re
import unittest

from lib import lexicon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORDS = os.path.join(ROOT, "words")
TOKEN = re.compile(r"^[^\s/#]+(/S)?$")


def read(name):
    with open(os.path.join(WORDS, name), encoding="utf-8") as f:
        return f.read()


class WordListTest(unittest.TestCase):
    def test_tokens_are_valid(self):
        for name in os.listdir(WORDS):
            for number, line in enumerate(read(name).splitlines(), 1):
                for token in line.split("#", 1)[0].split():
                    self.assertRegex(token, TOKEN, "{}:{}".format(name, number))

    def test_settings_name_every_list(self):
        with open(os.path.join(ROOT, "DevDictionary.sublime-settings"), encoding="utf-8") as f:
            text = f.read()
        # Sublime settings allow comments and trailing commas. Find the list only.
        names = json.loads(re.search(r'"builtin_lists":\s*(\[[^\]]*\])', text).group(1))
        files = sorted(n[:-4] for n in os.listdir(WORDS) if n.endswith(".txt"))
        self.assertEqual(sorted(names), files)

    def test_lists_are_not_empty(self):
        for name in os.listdir(WORDS):
            self.assertTrue(lexicon.parse(read(name)), name)


if __name__ == "__main__":
    unittest.main()
