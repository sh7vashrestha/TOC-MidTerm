# Degree-2 NFA assignment

Turns the regex `(a|b)c(a|b)(a|b)(a|b)` into a Thompson NFA, converts it to a
2-NFA (no state has more than 2 incoming or outgoing edges), and compares it
with the DFA. Uses only the Python standard library.

## Run

```sh
python3 main.py            # builds everything into results/
python3 -m unittest -v     # runs the tests
```

To try another regex without overwriting `results/`:

```sh
python3 main.py --regex '(a|b)*abb' --output other_results
```

Supported: letters/digits, `|`, `*`, parentheses, `ε`, `∅`.

## Expected results

| Machine | States | Edges | Max in | Max out |
|---|---:|---:|---:|---:|
| Thompson NFA | 26 | 29 | 2 | 2 |
| 2-NFA | 26 | 29 | 2 | 2 |
| Subset DFA | 11 | 33 | 19 | 3 |
| Minimal DFA | 7 | 21 | 12 | 3 |
| Demo before | 11 | 16 | 4 | 4 |
| Demo after | 19 | 24 | 2 | 2 |

The Thompson NFA already meets the limit, so the 2-NFA is the same machine.
The demo shows the algorithm adding states when a state has too many edges.

## Files

- `automata.py`: the algorithms (Thompson, 2-NFA conversion, DFA, minimization).
- `main.py`: runs everything and writes `results/`.
- `export_results.py`: writes the CSV tables and SVG diagrams.
- `test_automata.py`: tests.
- `results/RESULTS.md`: summary table and the 16 accepted words. Each machine
  also has a `.svg` diagram, `_transitions.csv` and `_degrees.csv`.
- `output/pdf/bounded_nfa_paper.pdf`: the paper. See `paper/README.md` to rebuild it.
