from typing import Dict, List, Optional, Any, Tuple

# ==================================================
# CSP BACKTRACKING SOLVER (with Forward Checking)
# ==================================================


class CSP:
    def __init__(
        self,
        variables: List[Any],
        domains: Dict[Any, List[Any]],
        constraints: List[Tuple[Any, Any]],
    ):
        self.variables = variables
        self.domains = domains  # {var: [possible values]}
        self.constraints = (
            constraints  # List of (var1, var2) pairs that must differ or satisfy a rule
        )
        self.neighbors = self._build_neighbors()  # {var: [vars constrained with it]}

    def _build_neighbors(self) -> Dict[Any, List[Any]]:
        neighbors = {var: [] for var in self.variables}
        for v1, v2 in self.constraints:
            neighbors[v1].append(v2)
            neighbors[v2].append(v1)
        return neighbors


def backtrack(assignment: Dict[Any, Any], csp: CSP) -> Optional[Dict[Any, Any]]:
    # Base case: if assignment is complete
    if len(assignment) == len(csp.variables):
        return assignment

    # Select unassigned variable (using MRV heuristic)
    var = select_unassigned_variable(assignment, csp)
    for value in domain_values(var, assignment, csp):
        if is_consistent(var, value, assignment, csp):
            # Make assignment
            assignment[var] = value
            inferences = forward_checking(var, value, assignment, csp)
            if inferences is not None:
                result = backtrack(assignment, csp)
                if result is not None:
                    return result
            # Undo assignment and inferences
            remove_inference(var, value, inferences, assignment, csp)
            del assignment[var]
    return None  # failure


# ========================================
# Heuristics & Inference
# ========================================


def select_unassigned_variable(assignment: Dict, csp: CSP) -> Any:
    """MRV Heuristic: Minimum Remaining Values"""
    unassigned = [v for v in csp.variables if v not in assignment]
    return min(unassigned, key=lambda var: len(csp.domains[var]))


def domain_values(var: Any, assignment: Dict, csp: CSP) -> List[Any]:
    """Return current domain (may be pruned by forward checking)"""
    return csp.domains[var]


def is_consistent(var: Any, value: Any, assignment: Dict, csp: CSP) -> bool:
    """Check if value for var is consistent with current assignment"""
    for neighbor in csp.neighbors[var]:
        if neighbor in assignment and assignment[neighbor] == value:
            return False
    return True


def forward_checking(
    var: Any, value: Any, assignment: Dict, csp: CSP
) -> Optional[Dict[Any, List[Any]]]:
    """
    Remove 'value' from domains of unassigned neighbors.
    Return a dict of {neighbor: [removed values]} or None if conflict.
    """
    removed = {}
    for neighbor in csp.neighbors[var]:
        if neighbor not in assignment and value in csp.domains[neighbor]:
            csp.domains[neighbor].remove(value)
            removed[neighbor] = [value]
            if len(csp.domains[neighbor]) == 0:
                return None  # conflict
    return removed if removed else {}


def remove_inference(
    var: Any, value: Any, inferences: Dict, assignment: Dict, csp: CSP
):
    """Restore domains after backtracking"""
    if inferences is None:
        return
    for neighbor, values in inferences.items():
        for val in values:
            if val not in csp.domains[neighbor]:
                csp.domains[neighbor].append(val)
        csp.domains[neighbor].sort()  # optional: keep ordered


# ========================================
# SUDOKU EXAMPLE
# ========================================


def solve_sudoku(grid: List[List[int]]) -> Optional[List[List[int]]]:
    """Convert 9x9 Sudoku grid to CSP and solve"""
    variables = [(i, j) for i in range(9) for j in range(9)]
    domains = {}

    # Build initial domains
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                domains[(i, j)] = [grid[i][j]]
            else:
                domains[(i, j)] = list(range(1, 10))

    # Constraints: row, column, 3x3 box
    constraints = []
    # Row & column
    for i in range(9):
        for j1 in range(9):
            for j2 in range(j1 + 1, 9):
                constraints.append(((i, j1), (i, j2)))  # same row
                constraints.append(((j1, i), (j2, i)))  # same col

    # 3x3 boxes
    for box_i in range(0, 9, 3):
        for box_j in range(0, 9, 3):
            cells = [(box_i + di, box_j + dj) for di in range(3) for dj in range(3)]
            for k1 in range(len(cells)):
                for k2 in range(k1 + 1, len(cells)):
                    constraints.append((cells[k1], cells[k2]))

    csp = CSP(variables, domains, constraints)

    solution = backtrack({}, csp)
    if solution is None:
        return None

    # Convert back to grid
    result = [[0] * 9 for _ in range(9)]
    for (i, j), val in solution.items():
        result[i][j] = val
    return result


# ========================================
# TEST: Solve a Sudoku Puzzle
# ========================================

if __name__ == "__main__":
    # Example puzzle (0 = empty)
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    print("Puzzle:")
    for row in puzzle:
        print(row)

    solution = solve_sudoku(puzzle)

    print("\nSolution:")
    if solution:
        for row in solution:
            print(row)
    else:
        print("No solution exists.")
