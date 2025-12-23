from collections import deque

def ac3(csp):
    """
    AC-3 algorithm for enforcing arc consistency in a CSP.
    :param csp: A dictionary with 'variables', 'domains', and 'constraints'
    :return: True if arc consistent, False if any domain is empty
    """
    queue = deque([(xi, xj) for xi in csp['variables'] for xj in csp['neighbors'][xi]])

    while queue:
        xi, xj = queue.popleft()
        if revise(csp, xi, xj):
            if not csp['domains'][xi]:
                return False  # Domain wiped out
            for xk in csp['neighbors'][xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True

def revise(csp, xi, xj):
    """
    Revise domain of xi to enforce consistency with xj.
    :return: True if domain of xi was revised
    """
    revised = False
    for x in csp['domains'][xi][:]:
        if not any(csp['constraints'](xi, x, xj, y) for y in csp['domains'][xj]):
            csp['domains'][xi].remove(x)
            revised = True
    return revised

# Example CSP: 3 variables with binary inequality constraints
# csp = {
#     'variables': ['A', 'B', 'C'],
#     'domains': {
#         'A': [1, 2, 3],
#         'B': [1, 2, 3],
#         'C': [2, 3]
#     },
#     'neighbors': {
#         'A': ['B', 'C'],
#         'B': ['A', 'C'],
#         'C': ['A', 'B']
#     },
#     'constraints': lambda xi, x, xj, y: x != y  # All variables must differ
# }

csp = {
    'variables': ['A', 'B', 'C'],
    'domains': {
        'A': [1, 2, 3],
        'B': [1, 2, 3],
        'C': [2, 3]
    },
    'neighbors': {
        'A': ['B'],
        'B': ['A', 'C'],
        'C': ['B']
    },
    'constraints': None
}

def constraint(xi, x, xj, y):
    # B = A + 1
    if xi == 'B' and xj == 'A':
        return x == y + 1
    if xi == 'A' and xj == 'B':
        return x + 1 == y
    # C != B
    if (xi == 'C' and xj == 'B') or (xi == 'B' and xj == 'C'):
        return x != y
    # No constraint between other pairs
    return True

csp['constraints'] = constraint

# Run AC-3
result = ac3(csp)
print("Arc Consistent:", result)
print("Reduced Domains:", csp['domains'])