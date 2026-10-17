# Custom Syms

A small solver for linear equations, written from scratch in plain Python (only `re`, no sympy or numpy). You type the equations as text, like `2x + 4y = 8`, and it finds the value of every variable.

## Why I made it

It started with the Truss calculator. My first idea there was to mark each unknown force as `"undefined"`, write the equations anyway, and then solve them by working on the left and right sides as strings. The truss project ended up using sympy instead. This project is me working out how that kind of solving can be done by hand, to see the logic behind it.

## How to run

```bash
python3 Custom_syms.py
```

```
How many equations: 2
Equation 1: 2x + 4y = 8
Equation 2: x - y + 2 = 0
x = 0.0
y = 2.0
```

## How it works

### 1. Read the equations: `equationSet()`
Asks how many equations there are, then reads them one by one. It keeps asking until it gets a positive number.

### 2. Split each equation into terms: `split_equation()`
- Removes spaces and splits at `=` into a left side and a right side.
- Splits each side into terms with a regex. Each term keeps its own sign.
- Drops the `+` signs and keeps the `-` attached to its term, so `2x - 4y` and `2x + 4y` stay different.

`2x + 4y = 8` becomes `[['2x', '4y'], ['8']]`.

### 3. Split each term into a number and a variable: `split_term()`
| Term | Result |
|---|---|
| `2x` | `(2.0, 'x')` |
| `-y` | `(-1.0, 'y')` |
| `3.5F1` | `(3.5, 'F1')` |
| `8` | `(8.0, None)` (a constant) |

### 4. Build the matrix: `setMatrix()`
- **Pass 1:** every unique variable gets its own column number (`x → 0`, `y → 1`, ...) in a dictionary.
- **Pass 2:** each equation becomes one row. The last slot of every row holds the constant.
- Anything that crosses `=` changes sign:
  - a constant on the **left** is multiplied by −1 and moved to the last slot;
  - a variable on the **right** is multiplied by −1 and moved into its column.
- A variable that is missing from an equation gets a 0 in that row.
- A variable that appears twice in one equation is added up (`2x + x` → `3x`).

`2x + 4y = 8` and `x - y + 2 = 0` become:
```
[2,  4,  8]
[1, -1, -2]
```

### 5. Gaussian elimination (recursive): `gauss()`
- `k` is the current pivot, starting at 0. The matrix never gets smaller. `k` marks where the part still being worked on starts.
- If the pivot is 0, it swaps in the row below with the largest value in that column. This is what makes `y = 3` work as the first equation.
- Makes every value below the pivot 0, then calls itself with `k + 1`.
- Stops when `k` reaches the number of rows.

### 6. Back substitution (recursive): `back_sub()`
Starts from the last row, which now has only one unknown. It solves that one, then moves up a row at a time, using the values it has already found.

## Error messages

| Input | Message |
|---|---|
| No `=` or more than one `=` | `'x+2' must have exactly one '='` |
| `2*x`, `x^2` | `Can't read term '2*x' (write it like 2x, -3.5y or 7)` |
| Equations that repeat or contradict each other | `No unique solution ...` |
| Fewer equations than variables | `Need as many equations as variables ...` |

## What it can't do yet

- Only linear equations: no `x*y`, `x^2`, brackets, or `*` between a number and its variable.
- Uses floats, so answers can show rounding like `2.0000000000000004`.
- Needs exactly as many equations as variables.

## Where the real sympy goes further

My `setMatrix` + `gauss` + `back_sub` match sympy's `linear_eq_to_matrix` + `linsolve`. Sympy also:
- stores an unknown as an object (`Symbol`) instead of a string, so `2*x + 4` builds an expression directly with no text parsing;
- stores expressions as trees, which allows brackets, powers and products;
- uses exact fractions and can simplify, expand and solve nonlinear equations.

Possible next step: a small `Sym` class with `__add__` / `__mul__`, so the variable works as a real "undefined" value.
