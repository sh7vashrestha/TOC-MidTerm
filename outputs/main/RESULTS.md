# Regular expression: `(a|b)c(a|b)(a|b)(a|b)`

| Machine | States | Edges | ε edges | Max in | Max out |
|---|---:|---:|---:|---:|---:|
| Thompson NFA | 26 | 29 | 20 | 2 | 2 |
| Converted 2-NFA | 26 | 29 | 20 | 2 | 2 |
| ε-free NFA | 10 | 14 | 0 | 2 | 2 |
| Complete subset DFA | 11 | 33 | 0 | 19 | 3 |
| Minimal complete DFA | 7 | 21 | 0 | 12 | 3 |

All language-equivalence checks passed.
DFA counts include the dead state.

Accepted words (16): acaaa, acaab, acaba, acabb, acbaa, acbab, acbba, acbbb, bcaaa, bcaab, bcaba, bcabb, bcbaa, bcbab, bcbba, bcbbb
