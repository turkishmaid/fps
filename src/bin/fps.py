#!/usr/bin/env python3

import argparse
from fun import iterate_pattern, create_word_pattern, create_random_pattern, set_recalc_function


def main():
    parser = argparse.ArgumentParser(description="FPS Terminal Pattern Display")
    parser.add_argument(
        "mode",
        choices=["w", "c"],
        nargs="?",
        default="w",
        help="Pattern mode: 'w' for words (default), 'c' for characters"
    )
    parser.add_argument(
        "color_percent",
        type=float,
        nargs="?",
        default=20.0,
        help="Color percentage for word mode (default: 20.0)"
    )

    args = parser.parse_args()

    if args.mode == "w":
        # Word pattern with specified color percentage
        set_recalc_function(
            lambda height, width: [create_word_pattern(height, width, args.color_percent) for _ in range(10)]
        )
    elif args.mode == "c":
        # Character pattern
        set_recalc_function(
            lambda height, width: [create_random_pattern(height, width) for _ in range(10)]
        )

    iterate_pattern()


if __name__ == "__main__":
    main()
