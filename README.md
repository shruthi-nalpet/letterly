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
- Physical and on-screen keyboards
- Responsive desktop and mobile layouts
- Animated tile reveals and feedback
- How-to-play and results dialogs
- Persistent win rate and streak statistics via `localStorage`

## Dictionary

The game selects answers from the top 1,000 five-letter alphabetic words, in frequency order, filtered from the swear-free edition of [`first20hours/google-10000-english`](https://github.com/first20hours/google-10000-english). That source derives its ranking from Google's Trillion Word Corpus.

Guess validation uses the comprehensive 14,855-word, MIT-licensed [`tabatkins/wordle-list`](https://github.com/tabatkins/wordle-list), taken from the original game's source. The final valid-guess set is the union of that list and the answer pool, ensuring every possible answer is also accepted as a guess.
