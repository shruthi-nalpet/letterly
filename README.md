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

The answer list contains the 5,000 most frequently used words from the Wordle-compatible vocabulary. It is ranked with English Zipf frequencies from [`wordfreq` 3.1.1](https://github.com/rspeer/wordfreq), whose data combines Wikipedia, subtitles, news, books, web text, Twitter, and Reddit. Frequency ties are sorted alphabetically.

- Easy: ranks 1–1,000
- Medium: ranks 1,001–3,000
- Hard: ranks 3,001–5,000

Guess validation combines the comprehensive 14,855-word, MIT-licensed [`tabatkins/wordle-list`](https://github.com/tabatkins/wordle-list) with 78 words retained from Letterly's original frequency corpus, producing 14,933 valid guesses. The answer list is explicitly included in that union, guaranteeing every possible answer is accepted as a guess.

The frequency ranking credits Robyn Speer and `wordfreq`. Its underlying frequency data is distributed under CC BY-SA 4.0; see the [`wordfreq` attribution notice](https://github.com/rspeer/wordfreq/blob/master/NOTICE.md) for its source credits.
