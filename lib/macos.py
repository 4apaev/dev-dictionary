"""macOS spell checker sync. No Sublime Text imports.

AppleSpell keeps learned words in memory and saves them to LocalDictionary
on its own schedule. A direct write to that file gets lost. Thus this module
uses the NSSpellChecker API (learnWord / unlearnWord) through osascript.
"""
import json
import os
import subprocess

LOCAL_DICTIONARY = os.path.expanduser("~/Library/Spelling/LocalDictionary")

JXA = """
ObjC.import("AppKit");
function run(argv) {
    var sc = $.NSSpellChecker.sharedSpellChecker;
    var data = JSON.parse(argv[0]);
    data.learn.forEach(function (w) { if (!sc.hasLearnedWord(w)) sc.learnWord(w); });
    data.unlearn.forEach(function (w) { if (sc.hasLearnedWord(w)) sc.unlearnWord(w); });
}
"""


def plan(words, previous):
    """Return (learn, unlearn). Unlearn only the words that we taught before."""
    return sorted(words), sorted(set(previous) - set(words))


def sync(learn, unlearn):
    data = json.dumps({"learn": learn, "unlearn": unlearn})
    subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", JXA, data],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True, universal_newlines=True)


def learned_words():
    """Return the words in LocalDictionary. AppleSpell can save them late."""
    try:
        with open(LOCAL_DICTIONARY, encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()
