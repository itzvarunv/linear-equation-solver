import re

def equationSet():
    equations = []
    while True:
        try:
            n = int(input("How many equations: "))
            if n > 0:
                break
            else:
                print("Kindly enter a positive number")
        except ValueError:
            print("Try again")
    for i in range(n):
        eq = input(f"Equation {i + 1}: ")
        equations.append(eq)
    return equations


def split_equation(equations):
    wrap = []
    term = r'[+-]?[^+-]+'          # an optional sign, then everything up to the next + or -
    for eq in equations:
        eq = eq.replace(" ", "")
        if eq.count("=") != 1:
            raise ValueError(f"'{eq}' must have exactly one '='")
        left, right = eq.split("=")
        L = [t.lstrip('+') for t in re.findall(term, left)]
        R = [t.lstrip('+') for t in re.findall(term, right)]
        wrap.append([L, R])
    return wrap


def split_term(t):
    m = re.fullmatch(r'([+-]?\d*\.?\d*)([a-zA-Z]\w*)?', t)
    if m is None:
        raise ValueError(f"Can't read term '{t}' (write it like 2x, -3.5y or 7)")
    coef, var = m.groups()
    if coef in ("", "+"):
        coef = 1.0
    elif coef == "-":
        coef = -1.0
    else:
        try:
            coef = float(coef)
        except ValueError:
            raise ValueError(f"Can't read the number in term '{t}'")
    return coef, var               # var is None for a plain constant


def setMatrix(wrap):
    # Pass 1: give each unique variable its own column
    var_id = {}
    for L, R in wrap:
        for t in L + R:
            _, var = split_term(t)
            if var is not None and var not in var_id:
                var_id[var] = len(var_id)

    n = len(var_id)                # columns 0..n-1 are variables, column n is constants
    matrix = []

    # Pass 2: fill each row
    for L, R in wrap:
        row = [0.0] * (n + 1)
        for t in L:                # left side: variables stay, constants flip sign
            coef, var = split_term(t)
            if var is None:
                row[n] -= coef
            else:
                row[var_id[var]] += coef
        for t in R:                # right side: constants stay, variables flip sign
            coef, var = split_term(t)
            if var is None:
                row[n] += coef
            else:
                row[var_id[var]] -= coef
        matrix.append(row)

    return matrix, var_id

def gauss(matrix, k=0):
    n = len(matrix)
    if k == n:                              # base case: every pivot done
        return
    # If the pivot is 0 (or tiny) we can't divide by it, so swap in the
    # row below with the largest value in this column
    p = max(range(k, n), key=lambda i: abs(matrix[i][k]))
    if abs(matrix[p][k]) < 1e-12:
        raise ValueError("No unique solution (some equations repeat or contradict each other)")
    matrix[k], matrix[p] = matrix[p], matrix[k]

    # Make every entry below the pivot 0
    for i in range(k + 1, n):
        factor = matrix[i][k] / matrix[k][k]
        for j in range(k, len(matrix[0])):
            matrix[i][j] -= factor * matrix[k][j]

    gauss(matrix, k + 1)                    # same matrix, next pivot


def back_sub(matrix, k=None, x=None):
    n = len(matrix)
    if k is None:                           # first call: start at the last row
        k = n - 1
        x = [0.0] * n
    if k < 0:                               # base case: every variable solved
        return x

    s = sum(matrix[k][j] * x[j] for j in range(k + 1, n))
    x[k] = (matrix[k][-1] - s) / matrix[k][k]
    return back_sub(matrix, k - 1, x)


equations = equationSet()
try:
    wrap = split_equation(equations)
    matrix, var_id = setMatrix(wrap)
    if len(matrix) != len(var_id):
        print(f"Need as many equations as variables "
              f"(got {len(matrix)} equations, {len(var_id)} variables)")
    else:
        gauss(matrix)
        x = back_sub(matrix)
        for var, col in var_id.items():
            print(f"{var} = {x[col]}")
except ValueError as e:
    print(f"Error: {e}")
