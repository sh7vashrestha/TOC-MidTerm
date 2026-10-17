# Degree-2 NFA

Turns the regex `(a|b)c(a|b)(a|b)(a|b)` into a Thompson NFA, converts it to a
2-NFA (no state has more than 2 incoming or outgoing edges), and compares it
with the DFA. Uses only the Python standard library.

## Run

```sh
./run.sh                   # paper results -> outputs/main, demo -> outputs/demo
python3 -m unittest -v     # runs the tests
```

`run.sh` just runs `python3 main.py --output outputs/main` and
`python3 main.py --demo --output outputs/demo`. To try another regex:

```sh
python3 main.py --regex '(a|b)*abb' --output outputs/other
```

Supported: letters/digits, `|`, `*`, parentheses, `ε`, `∅`.

## Expected results

| Machine | States | Edges | Max in | Max out |
|---|---:|---:|---:|---:|
| Thompson NFA | 26 | 29 | 2 | 2 |
| 2-NFA | 26 | 29 | 2 | 2 |
| Subset DFA | 11 | 33 | 19 | 3 |
| Minimal DFA | 7 | 21 | 12 | 3 |
| Demo (ε-free `(a\|b\|c\|d)x`) before | 6 | 8 | 4 | 4 |
| Demo after | 10 | 12 | 2 | 2 |

The Thompson NFA already meets the limit, so the 2-NFA is the same machine.
The demo removes the ε-edges from the Thompson NFA of `(a|b|c|d)x`; that NFA has
states with 4 edges, and the algorithm adds 4 states to fix them.

## Files

- `automata.py`: the algorithms (Thompson, 2-NFA conversion, DFA, minimization).
- `main.py`: runs the regex (or `--demo`) and writes the tables and diagrams.
- `export_results.py`: writes the CSV tables and SVG diagrams.
- `test_automata.py`: tests.
- `outputs/main/RESULTS.md`: summary table and the 16 accepted words.
  `outputs/demo/RESULTS.md`: the high-degree example. Each machine also has a
  `.svg` diagram, `_transitions.csv` and `_degrees.csv`.
- `output/pdf/bounded_nfa_paper.pdf`: the paper. See `paper/README.md` to rebuild it.
