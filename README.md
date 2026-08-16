# Letterly

A polished, dependency-free Wordle-style web game.

## Run locally

Open `index.html` directly in a browser, or serve the directory:

```sh
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Features

- Six-guess game loop with correct duplicate-letter scoring
- Easy, Medium, and Hard answer-frequency tiers with the same rules and attempt count
- Physical and on-screen keyboards
- Responsive desktop and mobile layouts
- Mobile keyboard protection against accidental double-tap zoom
- Animated tile reveals and feedback
- How-to-play and results dialogs
- Word definitions shown after every win or loss via the [Free Dictionary API](https://dictionaryapi.dev/)
- Persistent win rate and streak statistics via `localStorage`

## Dictionary

The answer list contains 5,000 familiar words selected from the Wordle-compatible vocabulary. Ranking uses a hybrid score: 70% English Zipf frequency from [`wordfreq` 3.1.1](https://github.com/rspeer/wordfreq) and 30% subtitle Zipf frequency from [`SUBTLEX-US`](https://github.com/words/subtlex-word-frequencies). A small lexical-confidence penalty keeps questionable variants out of the easier tiers. Frequency ties are sorted alphabetically.

Answer-only filters remove pure proper names, unsupported forms, and offensive or insensitive terms. Proper-name detection combines SUBTLEX capitalization, the [NLTK Names Corpus](https://www.nltk.org/howto/corpus.html), and lowercase dictionary evidence so words that also have ordinary meanings remain eligible. The safety filter uses the CC BY 4.0 [LDNOOBW English list](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words). Filtered entries remain valid guesses.

- Easy: ranks 1–1,000
- Medium: ranks 1,001–3,000
- Hard: ranks 3,001–5,000

Guess validation combines the comprehensive 14,855-word, MIT-licensed [`tabatkins/wordle-list`](https://github.com/tabatkins/wordle-list) with 78 words retained from Letterly's original frequency corpus, producing 14,933 valid guesses. The answer list is explicitly included in that union, guaranteeing every possible answer is accepted as a guess.

The frequency ranking credits Robyn Speer and `wordfreq`, Marc Brysbaert and Boris New for SUBTLEX-US, and Mark Kantrowitz and Bill Ross for the Names Corpus. `wordfreq` and SUBTLEX-derived data are distributed under CC BY-SA terms; see the [`wordfreq` attribution notice](https://github.com/rspeer/wordfreq/blob/master/NOTICE.md) and [SUBTLEX-US dataset notes](https://github.com/chrplr/openlexicon/blob/master/datasets-info/SUBTLEX-US/README-SUBTLEXus.md) for source credits.
