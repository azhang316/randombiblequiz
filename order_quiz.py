#!/usr/bin/env python3
"""CLI quiz for memorizing the order of a list of strings via pairwise comparison."""

import os
import random
import sys
import tty
import termios

# --- Items to memorize (swap this list later) ---
ITEMS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy",
    "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation",
]

# --- Spaced repetition state ---
# missed pairs stored as (a, b) where a is the correct "earlier" item
# each entry maps to a cooldown counter (questions until it reappears)
review_queue: dict[tuple[str, str], int] = {}
INITIAL_DELAY = 5
MAX_STREAK = 3  # correct consecutive times before removing from review
streak: dict[tuple[str, str], int] = {}


def read_arrow_key() -> str | None:
    """Read a single left/right arrow key press. Returns 'left', 'right', or None."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            if sys.stdin.read(1) == "[":
                code = sys.stdin.read(1)
                if code == "D":
                    return "left"
                if code == "C":
                    return "right"
        elif ch in ("q", "Q", "\x03"):  # q or Ctrl-C
            return "quit"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return None


def pick_pair() -> tuple[str, str]:
    """Pick a pair to quiz. Prioritizes review queue, otherwise random."""
    # Check review queue for any pair whose cooldown has reached 0
    for pair, cooldown in list(review_queue.items()):
        if cooldown <= 0:
            return pair
    # Random pair
    a, b = random.sample(ITEMS, 2)
    idx_a, idx_b = ITEMS.index(a), ITEMS.index(b)
    earlier, later = (a, b) if idx_a < idx_b else (b, a)
    return (earlier, later)


def tick_cooldowns():
    """Decrement all review cooldowns by 1."""
    for pair in review_queue:
        review_queue[pair] = max(0, review_queue[pair] - 1)


def main():
    correct_count = 0
    total = 0
    last_result = ""
    try:
        while True:
            os.system("clear")
            print("=== Order Quiz ===")
            print("Which comes EARLIER? ← or →  |  Q to quit")
            if total:
                pct = correct_count / total * 100
                print(f"Score: {correct_count}/{total} ({pct:.0f}%) | Review queue: {len(review_queue)}")
            if last_result:
                print(f"\n{last_result}")
            print()
            earlier, later = pick_pair()
            if random.random() < 0.5:
                left, right = earlier, later
            else:
                left, right = later, earlier

            print(f"  [{left}]    vs    [{right}]")
            print("    ←                →", end="", flush=True)

            key = None
            while key not in ("left", "right", "quit"):
                key = read_arrow_key()

            if key == "quit":
                print("\n")
                break

            chosen = left if key == "left" else right
            pair_key = (earlier, later)
            total += 1

            if chosen == earlier:
                correct_count += 1
                last_result = f"✓ Correct! {earlier} comes before {later}"
                if pair_key in review_queue:
                    streak[pair_key] = streak.get(pair_key, 0) + 1
                    if streak[pair_key] >= MAX_STREAK:
                        del review_queue[pair_key]
                        del streak[pair_key]
                        last_result += "  (removed from review)"
                    else:
                        review_queue[pair_key] = INITIAL_DELAY
            else:
                last_result = f"✗ Wrong — {earlier} comes before {later}"
                review_queue[pair_key] = INITIAL_DELAY
                streak[pair_key] = 0

            tick_cooldowns()

    except (KeyboardInterrupt, EOFError):
        print("\n")

    if total:
        print(f"Final: {correct_count}/{total} ({correct_count/total*100:.0f}%)")
    print("Bye!")


if __name__ == "__main__":
    main()
