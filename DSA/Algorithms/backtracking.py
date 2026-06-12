# Backtracking Problem Template

def backtrack(path, choices, result):
    """
    Generic backtracking template
    
    Args:
        path: Current solution being built
        choices: Remaining options to explore
        result: List to store all valid solutions
    """
    # Base case: all choices have been made
    if not choices:
        result.append(path[:])  # Add a copy of the solution
        return
    
    # Recursive case: try each choice
    for i, choice in enumerate(choices):
        # Make a choice
        path.append(choice)
        
        # Explore with this choice
        remaining = choices[:i] + choices[i+1:]
        backtrack(path, remaining, result)
        
        # Undo the choice (backtrack)
        path.pop()
    
    return result


# Example: 8 Queens Problem
def solve_n_queens(n):
    """
    Solve the N-Queens problem.
    Returns all valid placements where queens don't attack each other.
    """
    result = []
    board = []
    
    def is_safe(row, col):
        """Check if placing a queen at (row, col) is safe"""
        for r, c in board:
            # Check same column or diagonal
            if c == col or abs(r - row) == abs(c - col):
                return False
        return True
    
    def backtrack_queens(row):
        """Place queens row by row"""
        if row == n:
            result.append(board[:])
            return
        
        for col in range(n):
            if is_safe(row, col):
                board.append((row, col))
                backtrack_queens(row + 1)
                board.pop()
    
    backtrack_queens(0)
    return result


# Usage example
if __name__ == "__main__":
    # Solve 8 Queens
    solutions = solve_n_queens(8)
    print(f"Found {len(solutions)} solutions for 8 Queens")
    
    # Print first solution
    if solutions:
        print("\nFirst solution:")
        for row, col in solutions[0]:
            print(f"Queen at row {row}, column {col}")