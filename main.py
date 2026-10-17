"""Run this file: python3 main.py"""

import argparse
from itertools import product
from pathlib import Path

from automata import (accepts, degrees, equivalent, high_degree_example,
                      make_2_nfa, minimize_dfa, thompson, to_dfa)
from export_results import save_machine, stats


REQUIRED_REGEX = "(a|b)c(a|b)(a|b)(a|b)"


def check_conversion(original, converted):
    incoming, outgoing = degrees(converted)
    if any(incoming[q] > 2 or outgoing[q] > 2 for q in converted.states):
        raise ValueError("A state has more than 2 incoming or outgoing edges")
    same, witness = equivalent(original, converted)
    if not same:
        raise ValueError(f"Language changed! Counterexample: {witness!r}")


def main():
    parser = argparse.ArgumentParser(description="Simple bounded-NFA assignment experiment")
    parser.add_argument("--regex", default=REQUIRED_REGEX)
    parser.add_argument("--output", default="results")
    args = parser.parse_args()
    folder = Path(args.output)
    folder.mkdir(parents=True, exist_ok=True)

    original = thompson(args.regex)
    bounded = make_2_nfa(original)
    dfa, _ = to_dfa(original)
    minimal = minimize_dfa(dfa)
    demo = high_degree_example()
    demo_bounded = make_2_nfa(demo)

    check_conversion(original, bounded)
    check_conversion(demo, demo_bounded)
    for machine in (dfa, minimal):
        if not equivalent(original, machine)[0]:
            raise ValueError("A DFA does not accept the same language as the NFA")

    machines = [
        ("thompson_nfa", original, "Thompson NFA", None),
        ("two_nfa", bounded, "Converted 2-NFA", len(original.states)),
        ("subset_dfa", dfa, "Complete subset DFA", None),
        ("minimal_dfa", minimal, "Minimal complete DFA", None),
        ("demo_before", demo, "High-degree example: before", None),
        ("demo_after", demo_bounded, "High-degree example: after", len(demo.states)),
    ]
    summary = {}
    print(f"Regular expression: {args.regex}\n")
    print(f"{'Machine':<28} {'States':>7} {'Edges':>7} {'Max in':>8} {'Max out':>8}")
    for name, machine, title, original_count in machines:
        info = stats(machine)
        summary[name] = info
        print(f"{title:<28} {info['states']:>7} {info['transitions']:>7} "
              f"{info['max_in_degree']:>8} {info['max_out_degree']:>8}")
        save_machine(machine, folder, name, title, original_count)

    report = [f"# Results for `{args.regex}`", "",
              "| Machine | States | Edges | ε edges | Max in | Max out |",
              "|---|---:|---:|---:|---:|---:|"]
    for name, _, title, _ in machines:
        info = summary[name]
        report.append(f"| {title} | {info['states']} | {info['transitions']} | "
                      f"{info['epsilon_transitions']} | {info['max_in_degree']} | {info['max_out_degree']} |")
    report += ["", "All language-equivalence checks passed.",
               "DFA counts include the dead state.",
               "The high-degree example accepts only `ab` and shows routing states being added."]

    if args.regex == REQUIRED_REGEX:
        words = [a + "c" + "".join(tail)
                 for a in "ab" for tail in product("ab", repeat=3)]
        if not all(accepts(bounded, word) for word in words):
            raise ValueError("The 2-NFA rejects one of the expected words")
        report += ["", f"Accepted words ({len(words)}): " + ", ".join(words)]

    (folder / "RESULTS.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\nExact language checks: passed")
    print(f"Tables and diagrams saved in: {folder.resolve()}")


if __name__ == "__main__":
    main()
