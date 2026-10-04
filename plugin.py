"""DevDictionary: a spell check dictionary for developers.

Sublime Text loads the generated Hunspell files. On macOS, the plugin also
teaches the words to the system spell checker, so all Mac apps accept them.
"""
import os
import subprocess
import sys

import sublime
import sublime_plugin

from .lib import lexicon, macos

NAME = "DevDictionary"
SETTINGS = NAME + ".sublime-settings"
PREFERENCES = "Preferences.sublime-settings"
DIC_RESOURCE = "Packages/User/{0}/{0}.dic".format(NAME)
MY_WORDS = "my-words.txt"
MY_WORDS_TEMPLATE = """\
# DevDictionary: your words.
# One word per line. `#` starts a comment.
# `/S` adds a plural: repo/S -> repo, repos.
# Mixed case also adds the lowercase form: GitHub -> github.
# Every *.txt file in this folder is a word list.
# Save the file to rebuild the dictionary.

"""

_added_words = None


def user_dir():
    return os.path.join(sublime.packages_path(), "User", NAME)


def state_file():
    """The words that the plugin taught to macOS."""
    return os.path.join(user_dir(), ".macos-learned")


def read_lines(path):
    try:
        with open(path, encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()


def write_if_changed(path, text):
    try:
        with open(path, encoding="utf-8") as f:
            if f.read() == text:
                return False
    except FileNotFoundError:
        pass
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return True


def read_lists(settings):
    """Return the text of the enabled built-in lists and of all user lists."""
    texts = []
    enabled = set(settings.get("builtin_lists") or [])
    prefix = "Packages/{}/words/".format(__package__)
    for resource in sublime.find_resources("*.txt"):
        if resource.startswith(prefix) and resource[len(prefix):-4] in enabled:
            texts.append(sublime.load_resource(resource))

    # The User folder is always on disk. Read it directly: the resource index
    # can lag behind a save.
    for name in sorted(os.listdir(user_dir())):
        if name.endswith(".txt"):
            with open(os.path.join(user_dir(), name), encoding="utf-8") as f:
                texts.append(f.read())
    return texts


def sync_macos(settings, words):
    """Teach words to macOS. Return the words that macOS must forget."""
    if not settings.get("macos_sync", True):
        words = set()
    learn, unlearn = macos.plan(words, read_lines(state_file()))
    if learn or unlearn:
        macos.sync(learn, unlearn)
    write_if_changed(state_file(), "".join(w + "\n" for w in learn))
    return set(unlearn)


def build():
    """Write the Hunspell files. Return (word count, file changed, file created)."""
    global _added_words
    settings = sublime.load_settings(SETTINGS)
    _added_words = list(sublime.load_settings(PREFERENCES).get("added_words") or [])
    os.makedirs(user_dir(), exist_ok=True)

    entries = lexicon.merge(*(lexicon.parse(text) for text in read_lists(settings)))
    words = lexicon.expand(entries)

    if sys.platform == "darwin":
        try:
            removed = sync_macos(settings, words | set(_added_words))
        except (OSError, subprocess.CalledProcessError) as e:
            # The Sublime Text dictionary does not need macOS. Continue.
            print("{}: macOS sync failed: {}".format(NAME, getattr(e, "stderr", None) or e))
            removed = set()
        if settings.get("macos_import", True):
            # LocalDictionary can still hold removed words until AppleSpell saves it.
            for word in macos.learned_words() - words - set(_added_words) - removed:
                entries.setdefault(word, "")

    dic = os.path.join(user_dir(), NAME + ".dic")
    created = not os.path.exists(dic)
    write_if_changed(os.path.join(user_dir(), NAME + ".aff"), lexicon.AFF)
    changed = write_if_changed(dic, lexicon.render_dic(entries))
    return len(entries), changed, created


def dictionaries():
    value = sublime.load_settings(PREFERENCES).get("dictionary")
    return [value] if isinstance(value, str) else list(value or [])


def enable():
    """Add the generated dictionary to the "dictionary" setting."""
    current = dictionaries()
    if DIC_RESOURCE not in current:
        sublime.load_settings(PREFERENCES).set("dictionary", current + [DIC_RESOURCE])
        sublime.save_settings(PREFERENCES)


def rebuild():
    try:
        count, changed, created = build()
    except OSError as e:
        print("{}: {}".format(NAME, e))
        sublime.status_message("{}: build failed. See the console.".format(NAME))
        return

    if created:
        # A new dictionary path loads at once. Sublime Text caches a known
        # path until restart, so a changed file needs a restart.
        sublime.set_timeout(enable)
        message = "{} words".format(count)
    elif changed:
        message = "{} words. Restart Sublime Text to load the changes".format(count)
    else:
        message = "{} words, no changes".format(count)
    sublime.status_message("{}: {}".format(NAME, message))


def _on_preferences_change():
    if list(sublime.load_settings(PREFERENCES).get("added_words") or []) != _added_words:
        sublime.set_timeout_async(rebuild)


def plugin_loaded():
    sublime.load_settings(PREFERENCES).add_on_change(NAME, _on_preferences_change)
    sublime.load_settings(SETTINGS).add_on_change(NAME, lambda: sublime.set_timeout_async(rebuild))
    sublime.set_timeout_async(rebuild)


def plugin_unloaded():
    sublime.load_settings(PREFERENCES).clear_on_change(NAME)
    sublime.load_settings(SETTINGS).clear_on_change(NAME)


class DevDictionaryRebuildCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        sublime.set_timeout_async(rebuild)


class DevDictionaryEnableCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        enable()

    def is_enabled(self):
        return DIC_RESOURCE not in dictionaries()


class DevDictionaryEditWordsCommand(sublime_plugin.WindowCommand):
    def run(self):
        os.makedirs(user_dir(), exist_ok=True)
        path = os.path.join(user_dir(), MY_WORDS)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(MY_WORDS_TEMPLATE)
        self.window.open_file(path)


class DevDictionaryListener(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        path = view.file_name() or ""
        if path.endswith(".txt") and os.path.dirname(path) == user_dir():
            rebuild()














