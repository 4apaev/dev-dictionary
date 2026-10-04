# dev-dictionary

A spell-check dictionary for developers, for Sublime Text 4. On macOS, it also shares its words with the system spell checker, so Mail, Notes, Messages and other Mac apps accept them too.

In Sublime the package is called **DevDictionary**.

```text
btw the repo uses pnpm, idk why the tsx config fails rn
~~~     ~~~~      ~~~~  ~~~         ~~~ ~~~~~~       ~~    ← en_US only
                                                           ← with dev-dictionary
```


## macOS integration

On a Mac, dev-dictionary keeps one shared word list between Sublime and the system spell checker. The sync works in both directions:

- **Sublime → macOS.** The built-in lists, your own lists and the words you add with *Add to Dictionary* in Sublime are all taught to macOS.
- **macOS → Sublime.** Words you add with *Learn Spelling* in other Mac apps are added to the Sublime dictionary on the next start.
- **Removal works too.** When you delete a word from your list, it is also removed from macOS. Words you learned yourself in other apps are not touched.
- **Opt out.** Set `"macos_sync": false` and dev-dictionary removes every word it added.

It needs no admin rights and does not change System Settings. It uses the same system API as the *Learn Spelling* menu item.

<details>
<summary>Why not edit <code>~/Library/Spelling/LocalDictionary</code> directly?</summary>

macOS keeps learned words in memory (`AppleSpell`). It ignores changes to that file and later overwrites it with its own copy. So dev-dictionary calls `NSSpellChecker` (`learnWord` / `unlearnWord`) through `osascript`, like a native app does.

The words it taught are recorded in `Packages/User/DevDictionary/.macos-learned`, so it knows which ones to remove later.
</details>


## Install

The package is not on Package Control yet. Clone it into your Packages folder. The folder name must be `DevDictionary`:

```bash
git clone https://github.com/4apaev/dev-dictionary.git "$HOME/Library/Application Support/Sublime Text/Packages/DevDictionary"
```

Sublime loads the plugin, builds the dictionary and adds it to the `"dictionary"` setting. `en_US` stays active next to it.

Spell check must be on: `"spell_check": true`.


## Word lists

About 470 words in six built-in lists:

| List         | Examples                              |
| :----------- | :------------------------------------ |
| `chat`       | btw, rn, idk, lgtm, imo, tbh, wip      |
| `dev`        | repo, config, enum, async, stdout      |
| `keywords`   | elif, typeof, nullptr, goroutine       |
| `shell`      | chmod, xargs, rsync, pnpm, ripgrep     |
| `extensions` | tsx, yml, jsonc, woff, dylib           |
| `names`      | GitHub, macOS, ESLint, Kubernetes      |

To turn a list off, remove it from `"builtin_lists"`.

### Your own words

Run **DevDictionary: Edit My Words** from the Command Palette. It opens `my-words.txt`, one word per line:

```text
# comments start with #
btw
repo/S        # /S adds the plural: repo, repos
API/S         # API, APIs
GitHub        # also adds the lowercase form: github
```

- A lowercase word matches any case: `btw` also covers `Btw` and `BTW`.
- Every `*.txt` file in `Packages/User/DevDictionary/` is a word list.

When you save a list, the dictionary is rebuilt and macOS is updated right away. Sublime itself loads the new words after a restart, because it caches dictionaries. Words added with *Add to Dictionary* work immediately.


## Commands

| Command Palette                                  | Action                                         |
| :----------------------------------------------- | :--------------------------------------------- |
| `DevDictionary: Edit My Words`                   | Open your word list (creates it if missing)     |
| `DevDictionary: Rebuild`                         | Rebuild the dictionary                          |
| `DevDictionary: Add to Spell Check Dictionaries` | Add it back to `"dictionary"` after a removal   |
| `Preferences: DevDictionary Settings`            | Open the settings                               |

The same items are in **Preferences → Package Settings → DevDictionary**.


## Settings

```jsonc
{
	// Built-in lists to use.
	"builtin_lists": ["chat", "dev", "extensions", "keywords", "names", "shell"],

	// macOS: teach the words to the system spell checker.
	// false removes them from macOS again.
	"macos_sync": true,

	// macOS: add words learned in other Mac apps to the Sublime dictionary.
	"macos_import": true,
}
```


## Notes

- On Linux and Windows, you get the Sublime dictionary only. The macOS sync is skipped.
- The only suffix rule is `/S` for plurals.
- The generated files are `Packages/User/DevDictionary/DevDictionary.dic` and `.aff`.
- If you remove the dictionary from your `"dictionary"` setting, the plugin does not add it back.


## Development

```text
plugin.py        Sublime commands, events, settings
lib/lexicon.py   word list parser and Hunspell writer (no Sublime imports)
lib/macos.py     macOS spell checker sync
words/           built-in lists
tests/           unit tests
```

For development, symlink your clone instead:

```bash
ln -s "$PWD" "$HOME/Library/Application Support/Sublime Text/Packages/DevDictionary"
```

The tests run with plain Python:

```bash
python3 -m unittest discover -s tests -t .
```


## License

MIT
