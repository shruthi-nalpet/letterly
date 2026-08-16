#!/usr/bin/env python3
"""Build Letterly's ranked answer list and compact offline definition map."""

import argparse
import html
import json
import math
import re
import zipfile

from wordfreq import zipf_frequency


DISCOURAGED_LABELS = (
    "archaic", "obsolete", "dated", "historical", "rare", "vulgar",
    "offensive", "ethnic slur", "alternative spelling", "misspelling",
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--valid-words", required=True)
    parser.add_argument("--subtlex", required=True)
    parser.add_argument("--offensive", required=True)
    parser.add_argument("--names", required=True)
    parser.add_argument("--lexicon", required=True)
    parser.add_argument("--definitions", required=True)
    return parser.parse_args()


def clean_text(value):
    value = re.sub(r"<[^>]+>", "", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def best_definition(entry):
    options = []
    order = 0
    for etymology in entry.get("etymologies", []):
        for group in etymology.get("partsOfSpeech", []):
            part = clean_text(group.get("partOfSpeech", ""))
            if part.lower() == "proper noun":
                continue
            for sense in group.get("senses", []):
                text = clean_text(sense.get("sense", ""))
                if not text:
                    continue
                lowered = text.lower()
                penalty = 100 if any(label in lowered for label in DISCOURAGED_LABELS) else 0
                example = next((clean_text(item) for item in sense.get("examples", []) if clean_text(item)), "")
                options.append((penalty + order, part, text, example))
                order += 1
    if not options:
        return None
    _, part, definition, example = min(options, key=lambda item: item[0])
    return {
        "p": part,
        "d": definition,
        "e": example,
    }


def main():
    args = parse_args()
    with open(args.valid_words) as source:
        valid = {word.strip().lower() for word in source if re.fullmatch(r"[A-Za-z]{5}", word.strip())}
    with open(args.subtlex) as source:
        subtlex_rows = json.load(source)
    subtlex = {row["word"].lower(): row for row in subtlex_rows}
    with open(args.offensive) as source:
        blocked = {line.strip().lower() for line in source if line.strip()}
    blocked.update({"slave", "lynch"})
    with open(args.lexicon, errors="ignore") as source:
        lexical = {word.strip() for word in source if re.fullmatch(r"[a-z]{5}", word.strip())}

    with zipfile.ZipFile(args.names) as archive:
        names = {
            line.strip().lower()
            for filename in ("names/male.txt", "names/female.txt")
            for line in archive.read(filename).decode().splitlines()
            if len(line.strip()) == 5
        }
    capitalized = {word for word, row in subtlex.items() if row["word"][:1].isupper()}
    pure_names = (names | capitalized) - lexical
    unsupported = {word for word in valid if zipf_frequency(word, "en") == 0 and word not in subtlex}
    eligible = valid - blocked - pure_names - unsupported

    def subtitle_zipf(word):
        if word not in subtlex:
            return zipf_frequency(word, "en")
        return math.log10(subtlex[word]["count"]) + math.log10(1e9 / 51e6)

    def score(word):
        lexical_penalty = 0.35 if word not in lexical else 0
        return 0.7 * zipf_frequency(word, "en") + 0.3 * subtitle_zipf(word) - lexical_penalty

    ranked = sorted(eligible, key=lambda word: (-score(word), -zipf_frequency(word, "en"), word))

    definitions = {}
    with zipfile.ZipFile(args.definitions) as archive:
        dictionary = {}
        for filename in archive.namelist():
            if filename.count("/") == 3 and filename.endswith(".json"):
                dictionary.update(json.loads(archive.read(filename)))

    answers = []
    for word in ranked:
        entry = dictionary.get(word)
        if not isinstance(entry, dict):
            continue
        definition = best_definition(entry)
        if not definition:
            continue
        answer = word.upper()
        answers.append(answer)
        definitions[answer] = definition
        if len(answers) == 5000:
            break

    if len(answers) != 5000:
        raise RuntimeError(f"Expected 5,000 defined answers, found {len(answers)}")
    print(json.dumps({"answers": answers, "definitions": definitions}, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
