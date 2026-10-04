import unittest

from lib import macos


class PlanTest(unittest.TestCase):
    def test_first_run_learns_everything(self):
        self.assertEqual(macos.plan({"b", "a"}, set()), (["a", "b"], []))

    def test_unlearns_only_words_taught_before(self):
        learn, unlearn = macos.plan({"a"}, {"a", "gone"})
        self.assertEqual(learn, ["a"])
        self.assertEqual(unlearn, ["gone"])

    def test_disabled_sync_unlearns_all(self):
        self.assertEqual(macos.plan(set(), {"a", "b"}), ([], ["a", "b"]))


if __name__ == "__main__":
    unittest.main()
