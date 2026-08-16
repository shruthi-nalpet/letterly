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
    parser.add_argument("--compact-definitions", required=True)
    parser.add_argument("--report-only", action="store_true")
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


def best_compact_definition(entry):
    parts = entry.get("p", [])
    if parts and all(part in {"name", "proper noun"} for part in parts):
        return None

    options = []
    for order, raw_text in enumerate(entry.get("d", [])):
        definition = clean_text(raw_text)
        if not definition:
            continue
        lowered = definition.lower()
        penalty = 100 if any(label in lowered for label in DISCOURAGED_LABELS) else 0
        options.append((penalty + order, definition))
    if not options:
        return None

    part_names = {
        "adj": "adjective", "adv": "adverb", "conj": "conjunction",
        "det": "determiner", "intj": "interjection", "num": "numeral",
        "prep": "preposition", "pron": "pronoun", "verb": "verb",
        "noun": "noun",
    }
    part = part_names.get(parts[0], parts[0]) if len(parts) == 1 else ""
    _, definition = min(options, key=lambda item: item[0])
    return {"p": part, "d": definition, "e": ""}


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

    baseline = ranked[:5000]
    baseline_set = set(baseline)

    open_definitions = {}
    with zipfile.ZipFile(args.definitions) as archive:
        dictionary = {}
        for filename in archive.namelist():
            if filename.count("/") == 3 and filename.endswith(".json"):
                dictionary.update(json.loads(archive.read(filename)))
    for word in baseline:
        entry = dictionary.get(word)
        if isinstance(entry, dict) and (definition := best_definition(entry)):
            open_definitions[word] = definition

    compact_definitions = {}
    with open(args.compact_definitions) as source:
        for line in source:
            entry = json.loads(line)
            word = entry.get("")
            if word not in baseline_set:
                continue
            if definition := best_compact_definition(entry):
                compact_definitions[word] = definition

    definitions = {}
    answers = []
    missing = []
    retained_by_tier = [0, 0, 0]
    for rank, word in enumerate(baseline):
        definition = open_definitions.get(word) or compact_definitions.get(word)
        if not definition:
            missing.append(word.upper())
            continue
        answer = word.upper()
        answers.append(answer)
        definitions[answer] = definition
        retained_by_tier[0 if rank < 1000 else 1 if rank < 3000 else 2] += 1

    tier_ends = [retained_by_tier[0], retained_by_tier[0] + retained_by_tier[1], len(answers)]

    report = {
        "baseline": len(baseline),
        "openCoverage": len(open_definitions),
        "compactCoverage": len(compact_definitions),
        "combinedCoverage": len(answers),
        "recoveredByCompact": len(set(compact_definitions) - set(open_definitions)),
        "retainedByTier": retained_by_tier,
        "removedByTier": [1000 - retained_by_tier[0], 2000 - retained_by_tier[1], 2000 - retained_by_tier[2]],
        "missing": missing,
    }
    output = report if args.report_only else {"answers": answers, "definitions": definitions, "tierEnds": tier_ends, "report": report}
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
