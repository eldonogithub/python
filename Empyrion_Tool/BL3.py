# Define constants
EMPTY = 0
AMARA = 1
MOZE = 2
FL4K = 3
ZANE = 4

# Grid dimensions (12 rows x 15 columns)
# Populated manually based on the labeled image and user's clarification

# Main tile grid (each row is bottom-to-top)
# Note: Order is row-major: row[0] is the bottom row, row[11] is the top row
grid = [
    [ZANE, ZANE, ZANE, ZANE, ZANE, ZANE, ZANE, ZANE, ZANE, ZANE, ZANE, ZANE, ZANE, ZANE, ZANE],  # Row 1 (bottom)
    [AMARA, MOZE, MOZE, MOZE, MOZE, MOZE, MOZE, MOZE, FL4K, MOZE, ZANE, AMARA, MOZE, MOZE, FL4K, FL4K],  # Row 1 (bottom)
    [MOZE, FL4K, AMARA, FL4K, ZANE, FL4K, ZANE, MOZE, FL4K, ZANE, AMARA, FL4K, ZANE, ZANE, FL4K],     # Row 2
    [ZANE, MOZE, AMARA, ZANE, MOZE, FL4K, FL4K, AMARA, FL4K, MOZE, MOZE, MOZE, AMARA, AMARA, ZANE],   # Row 3
    [AMARA, ZANE, ZANE, AMARA, ZANE, AMARA, MOZE, ZANE, FL4K, FL4K, MOZE, AMARA, MOZE, ZANE, ZANE],   # Row 4
    [FL4K, AMARA, AMARA, MOZE, ZANE, ZANE, FL4K, FL4K, MOZE, MOZE, ZANE, FL4K, FL4K, MOZE, FL4K],     # Row 5
    [ZANE, FL4K, FL4K, ZANE, AMARA, MOZE, FL4K, ZANE, FL4K, AMARA, ZANE, ZANE, FL4K, MOZE, MOZE],     # Row 6
    [MOZE, FL4K, AMARA, MOZE, FL4K, AMARA, AMARA, FL4K, AMARA, ZANE, FL4K, ZANE, ZANE, FL4K, FL4K],   # Row 7
    [MOZE, MOZE, ZANE, ZANE, ZANE, MOZE, FL4K, MOZE, ZANE, AMARA, ZANE, AMARA, MOZE, ZANE, MOZE],     # Row 8
    [ZANE, FL4K, FL4K, AMARA, AMARA, FL4K, ZANE, ZANE, MOZE, FL4K, AMARA, ZANE, AMARA, AMARA, ZANE],  # Row 9
    [AMARA, AMARA, FL4K, FL4K, MOZE, AMARA, ZANE, MOZE, AMARA, FL4K, ZANE, FL4K, MOZE, FL4K, FL4K],   # Row10
    [MOZE, ZANE, MOZE, AMARA, FL4K, ZANE, MOZE, FL4K, ZANE, MOZE, FL4K, AMARA, AMARA, ZANE, AMARA],   # Row11
    [FL4K, AMARA, ZANE, ZANE, ZANE, ZANE, AMARA, FL4K, FL4K, AMARA, MOZE, FL4K, ZANE, FL4K, ZANE],    # Row12 (top)
]

# Guide per row on the left side
# Each entry is a list of acceptable tile types for that row (bottom to top)
guide = [
    [ZANE, FL4K], # Row 1 (bottom)
    [ZANE, FL4K], # Row 2
    [ZANE], # Row 3
    [AMARA, ZANE], # Row 4
    [AMARA, ZANE], # Row 5
    [FL4K], # Row 6
    [AMARA, MOZE], # Row 7
    [MOZE, FL4K], # Row 8
    [ZANE, AMARA], # Row 9
    [ZANE], # Row 10
    [FL4K], # Row 11
    [ZANE, FL4K], # Row 12 (top)
]

if __name__ == "__main__":
    grid, guide
