# ============================================================
#   
#   Stage 3 - K-Map Simplification
#
#   This is where we actually simplify the Boolean equation.
#   Instead of doing it algebraically, we use a grid (K-Map)
#   to find patterns visually.
#
#   The grid uses a specific column order (00, 01, 11, 10)
#   instead of normal binary order. The reason is that each
#   adjacent cell in the grid should only differ by one variable.
#   Normal binary order doesnt guarantee that, so we use this
#   ordering instead. It keeps the grouping logic clean.
#
#   Groups must be powers of 2 (1, 2, 4, 8...)
#   The bigger the group, the more variables cancel out.
#   What doesnt cancel is what ends up in the simplified equation.
# ============================================================

from utils import input_labels


# ------------------------------------------------------------
# GRAY CODE ORDER
# this is the column/row order the k-map uses
# each step only changes one bit, which is exactly what we need
# for adjacent cells to be logically "next to" each other
# ------------------------------------------------------------

# for 2 variable k-map (2x2 grid)
gray_2 = [0, 1]

# for 3 variable k-map (2x4 grid)
# columns follow gray code: 00, 01, 11, 10
gray_4 = [0, 1, 3, 2]


# ------------------------------------------------------------
# HELPER - get the k-map grid layout
# returns a 2D list of minterm indices in k-map order
# this is basically the blank k-map before we fill in values
# ------------------------------------------------------------
def get_kmap_grid(num_vars):
    """
    Returns the k-map grid as a 2D list of minterm indices.
    Layout depends on number of variables.
    """

    if num_vars == 2:
        # 2 variable k-map is a simple 2x2 grid
        # rows = A, columns = B
        grid = []
        for row in gray_2:
            current_row = []
            for col in gray_2:
                # minterm index = row bit concat with col bit
                minterm_index = (row << 1) | col
                current_row.append(minterm_index)
            grid.append(current_row)
        return grid

    elif num_vars == 3:
        # 3 variable k-map is a 2x4 grid
        # rows = A, columns = BC in gray code order
        grid = []
        for row in gray_2:
            current_row = []
            for col in gray_4:
                # minterm index = row bit concat with 2 col bits
                minterm_index = (row << 2) | col
                current_row.append(minterm_index)
            grid.append(current_row)
        return grid

    elif num_vars == 4:
        # 4 variable k-map is a 4x4 grid
        # rows = AB in gray code order, columns = CD in gray code order
        grid = []
        for row in gray_4:
            current_row = []
            for col in gray_4:
                # minterm index = row bits concat with col bits
                minterm_index = (row << 2) | col
                current_row.append(minterm_index)
            grid.append(current_row)
        return grid

    else:
        # shouldnt happen since we validate n earlier but just in case
        return []


# ------------------------------------------------------------
# HELPER - print the k-map so user can see it
# just a visual display, not used for the actual simplification
# ------------------------------------------------------------
def print_kmap(grid, minterm_indices, num_vars):
    """
    Prints the k-map grid with 1s and 0s filled in.
    """
    labels = input_labels[:num_vars]

    print("\n  K-Map:")
    print()

    if num_vars == 2:
        # header row
        print("          B=0   B=1")
        for row_index in range(len(grid)):
            row_label = "  A=" + str(row_index) + "  "
            row_str = row_label
            for minterm_index in grid[row_index]:
                if minterm_index in minterm_indices:
                    row_str = row_str + "[  1  ]"
                else:
                    row_str = row_str + "[  0  ]"
            print(row_str)

    elif num_vars == 3:
        # header row for 3 variable k-map
        print("          BC=00  BC=01  BC=11  BC=10")
        for row_index in range(len(grid)):
            row_label = "  A=" + str(row_index) + "  "
            row_str = row_label
            for minterm_index in grid[row_index]:
                if minterm_index in minterm_indices:
                    row_str = row_str + "[  1  ]"
                else:
                    row_str = row_str + "[  0  ]"
            print(row_str)

    elif num_vars == 4:
        # header row for 4 variable k-map
        print("            CD=00  CD=01  CD=11  CD=10")
        row_headers = ["AB=00", "AB=01", "AB=11", "AB=10"]
        for row_index in range(len(grid)):
            row_label = "  " + row_headers[row_index] + "  "
            row_str = row_label
            for minterm_index in grid[row_index]:
                if minterm_index in minterm_indices:
                    row_str = row_str + "[  1  ]"
                else:
                    row_str = row_str + "[  0  ]"
            print(row_str)

    print()


# ------------------------------------------------------------
# FIND GROUPS
# this is the heart of the k-map simplification
# we look for rectangular groups of 1s on the grid
# groups must be powers of 2 in size (1, 2, 4, 8, 16)
# we want the biggest groups possible to cancel the most variables
# ------------------------------------------------------------
def find_groups(minterm_indices, num_vars):
    """
    Finds all valid groups of 1s on the k-map.
    Returns a list of groups, where each group is a list of minterm indices.
    """
    grid = get_kmap_grid(num_vars)
    num_rows = len(grid)
    num_cols = len(grid[0])

    # collect all valid groups we find
    all_groups = []

    # try every possible rectangle size (height x width)
    # height and width must both be powers of 2
    height = 1
    while height <= num_rows:
        width = 1
        while width <= num_cols:

            # try placing this rectangle at every position on the grid
            for start_row in range(num_rows):
                for start_col in range(num_cols):

                    # collect all minterm indices inside this rectangle
                    group = []
                    all_ones = True

                    for row_offset in range(height):
                        for col_offset in range(width):
                            # wrap around edges using modulo (k-map wraps!)
                            actual_row = (start_row + row_offset) % num_rows
                            actual_col = (start_col + col_offset) % num_cols
                            minterm_index = grid[actual_row][actual_col]
                            group.append(minterm_index)

                            # if any cell in the group is 0, this group is invalid
                            if minterm_index not in minterm_indices:
                                all_ones = False
                                break

                        if not all_ones:
                            break

                    # only keep the group if every cell was a 1
                    if all_ones and len(group) > 0:
                        # sort so we can check for duplicates easily
                        sorted_group = sorted(group)
                        if sorted_group not in all_groups:
                            all_groups.append(sorted_group)

            width = width * 2
        height = height * 2

    return all_groups


# ------------------------------------------------------------
# FIND ESSENTIAL GROUPS
# not every group we found is necessary
# we only keep groups that cover at least one minterm
# that no other group covers - those are the essential ones
# ------------------------------------------------------------
def find_essential_groups(all_groups, minterm_indices):
    """
    Picks the minimum set of groups needed to cover all minterms.
    Returns the essential groups list.
    """
    # start with nothing covered
    covered = []
    essential_groups = []

    # sort groups by size descending so we grab biggest first
    # bigger groups = more variables cancelled = simpler expression
    sorted_groups = sorted(all_groups, key=len, reverse=True)

    for group in sorted_groups:
        # check if this group covers anything not already covered
        adds_new_coverage = False
        for minterm_index in group:
            if minterm_index not in covered:
                adds_new_coverage = True
                break

        if adds_new_coverage:
            essential_groups.append(group)
            for minterm_index in group:
                if minterm_index not in covered:
                    covered.append(minterm_index)

        # stop early if everything is covered
        if len(covered) == len(minterm_indices):
            break

    return essential_groups


# ------------------------------------------------------------
# SIMPLIFY GROUP - turn one group into a Boolean term
# look at each variable across all minterms in the group
# if the variable is always 0 -> use complemented form (A')
# if the variable is always 1 -> use normal form (A)
# if it changes between 0 and 1 -> it cancels out, skip it
# ------------------------------------------------------------
def simplify_group(group, num_vars):
    """
    Takes one group of minterms and returns the simplified term string.
    """
    labels = input_labels[:num_vars]
    simplified_term = ""

    for var_index in range(num_vars):
        # collect what this variable is across every minterm in the group
        bit_values = []
        for minterm_index in group:
            # extract the bit for this variable from the minterm index
            # shift right by the right amount and mask to get just that bit
            bit_position = num_vars - 1 - var_index
            bit_value = (minterm_index >> bit_position) & 1
            bit_values.append(bit_value)

        # check if all values in the group are 0
        all_zeros = True
        for bit in bit_values:
            if bit != 0:
                all_zeros = False
                break
        
        # check if all values in the group are 1
        all_ones = True
        for bit in bit_values:
             if bit != 1:
                all_ones = False
                break


        if all_zeros:
            # variable is always 0 in this group so it stays complemented
            simplified_term = simplified_term + labels[var_index] + "'"

        elif all_ones:
            # variable is always 1 in this group so it stays normal
            simplified_term = simplified_term + labels[var_index]

        # if neither, the variable changes so it cancels out
        # we just dont add it to the term

    # if everything cancelled out it means output is always 1
    if simplified_term == "":
        simplified_term = "1"

    return simplified_term


# ------------------------------------------------------------
# MAIN KMAP FUNCTION - ties everything together
# called from task2_eden_mckenzie.py
# ------------------------------------------------------------
def run_kmap(truth_table, minterm_indices, num_vars):
    """
    Runs the full k-map process:
    build grid -> print k-map -> find groups -> simplify -> return result
    """
    # build and print the k-map grid first so user can see it
    grid = get_kmap_grid(num_vars)
    print_kmap(grid, minterm_indices, num_vars)

    # find all valid groups of 1s on the grid
    all_groups = find_groups(minterm_indices, num_vars)

    # narrow down to just the essential groups we need
    essential_groups = find_essential_groups(all_groups, minterm_indices)

    # turn each essential group into a simplified Boolean term
    simplified_terms = []
    for group in essential_groups:
        term = simplify_group(group, num_vars)
        simplified_terms.append(term)

    # join all simplified terms with + to get the final expression
    simplified_expression = ""
    for term_index in range(len(simplified_terms)):
        if term_index > 0:
            simplified_expression = simplified_expression + " + "
        simplified_expression = simplified_expression + simplified_terms[term_index]

    # print the groups we found so user can see the grouping
    print("  K-Map Groups Found:")
    for group in essential_groups:
        group_str = ""
        for idx in range(len(group)):
            if idx > 0:
                group_str = group_str + ", "
            group_str = group_str + "m" + str(group[idx])
        print("    Group: {" + group_str + "}")

    print()
    print("  Simplified Expression: " + simplified_expression)

    return simplified_expression