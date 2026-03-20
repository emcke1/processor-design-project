# ============================================================
#   
#   Stage 2 - Boolean Expression & Simplification
#
#   This is where the truth table actually becomes something useful.
#   User picks SOP or POS, and we build the canonical equation
#   and list out the minterms or maxterms.
#
#   SOP = Sum of Products (rows where output is 1)
#   POS = Product of Sums (rows where output is 0)
#
#   Think of it like this:
#   SOP asks "when is the output ON?" and builds from there
#   POS asks "when is the output OFF?" and builds from there
# ============================================================

from utils import input_labels


# ------------------------------------------------------------
# HELPER - build one minterm (used in SOP)
#
# minterms come from rows where output = 1
# the rule is:
#   if the variable is 0 in that row -> complement it (add ')
#   if the variable is 1 in that row -> leave it alone
#
# example:
#   row A=0, B=1 -> A is 0 so flip it, B is 1 so keep it
#   result: A'B
# ------------------------------------------------------------
def build_minterm(input_combination, num_vars):
    """
    Takes one row's input combo and returns the minterm string.
    """
    # only grab as many labels as we have variables
    labels = input_labels[:num_vars]

    # start with empty string and build it up character by character
    minterm = ""

    for var_index in range(num_vars):

        # if this variable is 0 in the row, we complement it
        # complementing means adding a ' after the label
        if input_combination[var_index] == 0:
            minterm = minterm + labels[var_index] + "'"

        # if its 1, we just add the label with nothing after it
        else:
            minterm = minterm + labels[var_index]

    return minterm


# ------------------------------------------------------------
# HELPER - build one maxterm (used in POS)
#
# maxterms come from rows where output = 0
# the rule is the OPPOSITE of minterms:
#   if the variable is 1 in that row -> complement it (add ')
#   if the variable is 0 in that row -> leave it alone
#
# example:
#   row A=0, B=1 -> A is 0 so keep it, B is 1 so flip it
#   result: (A + B')
#
# also notice maxterms are wrapped in parentheses and use +
# thats what makes it a "sum" term in Product of Sums
# ------------------------------------------------------------
def build_maxterm(input_combination, num_vars):
    """
    Takes one row's input combo and returns the maxterm string.
    """
    # only grab as many labels as we have variables
    labels = input_labels[:num_vars]

    # collect each piece of the maxterm in a list first
    # then we'll join them into a string at the end
    term_list = []

    for var_index in range(num_vars):

        # opposite of minterm logic - we flip the 1s, not the 0s
        if input_combination[var_index] == 1:
            term_list.append(labels[var_index] + "'")

        # 0 stays as is in POS
        else:
            term_list.append(labels[var_index])

    # now join everything with + signs inside parentheses
    # doing it manually instead of join() so its clear whats happening
    inside = ""
    for term_index in range(len(term_list)):
        if term_index > 0:
            inside = inside + " + "
        inside = inside + term_list[term_index]

    # wrap the whole thing in parentheses to complete the maxterm
    maxterm = "(" + inside + ")"
    return maxterm


# ------------------------------------------------------------
# ASK USER - SOP or POS
# we need to know which form they want before we can generate
# anything - so this runs first before all the other functions
# ------------------------------------------------------------
def get_equation_type():
    """
    Ask user to pick SOP or POS.
    Keep asking until they give something valid.
    """
    while True:
        user_choice = input("\nChoose equation type - SOP or POS: ").strip().upper()

        # .upper() handles lowercase input so "sop" works too
        # but we still need to check its actually one of the two options
        if user_choice != "SOP" and user_choice != "POS":
            print("  Error: please type SOP or POS.")
            continue

        return user_choice


# ------------------------------------------------------------
# GENERATE SOP
#
# go through every row in the truth table
# find the ones where output = 1 (those are our minterms)
# build a minterm string for each one
# join them all with + to get the full canonical SOP equation
#
# example result: A'B + AB'
# ------------------------------------------------------------
def generate_sop(truth_table, num_vars):
    """
    Builds the canonical SOP equation from the truth table.
    Returns the equation string and list of minterm row numbers.
    """
    # these will hold the minterm strings and their row numbers
    minterm_list = []
    minterm_indices = []

    for row_index in range(len(truth_table)):

        # pull out the input combo and output value for this row
        input_combination = truth_table[row_index][0]
        output_value = truth_table[row_index][1]

        # SOP only cares about rows where output is 1
        # skip anything that is 0
        if output_value == 1:
            minterm = build_minterm(input_combination, num_vars)
            minterm_list.append(minterm)

            # save the row number so we can list minterms like m(1, 2, 3)
            minterm_indices.append(row_index)

    # edge case - if no rows were 1, the whole function is just 0
    if len(minterm_list) == 0:
        equation = "0"
        return equation, minterm_indices

    # join all the minterms with + to get the full SOP equation
    # doing it manually so its obvious whats happening
    equation = ""
    for term_index in range(len(minterm_list)):
        if term_index > 0:
            equation = equation + " + "
        equation = equation + minterm_list[term_index]

    return equation, minterm_indices


# ------------------------------------------------------------
# GENERATE POS
#
# go through every row in the truth table
# find the ones where output = 0 (those are our maxterms)
# build a maxterm string for each one
# join them all together to get the full canonical POS equation
#
# example result: (A + B')(A' + B)
# ------------------------------------------------------------
def generate_pos(truth_table, num_vars):
    """
    Builds the canonical POS equation from the truth table.
    Returns the equation string and list of maxterm row numbers.
    """
    # these will hold the maxterm strings and their row numbers
    maxterm_list = []
    maxterm_indices = []

    for row_index in range(len(truth_table)):

        # pull out the input combo and output value for this row
        input_combination = truth_table[row_index][0]
        output_value = truth_table[row_index][1]

        # POS only cares about rows where output is 0
        # skip anything that is 1
        if output_value == 0:
            maxterm = build_maxterm(input_combination, num_vars)
            maxterm_list.append(maxterm)

            # save the row number so we can list maxterms like M(0, 3)
            maxterm_indices.append(row_index)

    # edge case - if no rows were 0, the whole function is just 1
    if len(maxterm_list) == 0:
        equation = "1"
        return equation, maxterm_indices

    # join all the maxterms together for the full POS equation
    # no + between maxterms - in POS the multiplication is implied
    equation = ""
    for term_index in range(len(maxterm_list)):
        if term_index > 0:
            equation = equation + " · "
        equation = equation + maxterm_list[term_index]

    return equation, maxterm_indices


# ------------------------------------------------------------
# MAIN FUNCTION - ties it all together
#
# this is the only function that gets called from outside
# it runs get_equation_type first, then calls either
# generate_sop or generate_pos depending on what user picked
# then prints the results and returns everything stage 3 needs
# ------------------------------------------------------------
def get_boolean_equation(truth_table, num_vars):
    """
    Ask SOP or POS, generate the equation, print the results.
    Returns everything the next stages need.
    """
    # find out which form the user wants first
    equation_type = get_equation_type()

    # run the right generator based on their choice
    if equation_type == "SOP":
        equation, term_indices = generate_sop(truth_table, num_vars)
        term_label = "Minterms"
    else:
        equation, term_indices = generate_pos(truth_table, num_vars)
        term_label = "Maxterms"

    # print the canonical equation so user can see it
    print("\n" + "=" * 55)
    print("  Canonical " + equation_type + ": " + equation)

    # build the term index string manually for clean printing
    # this gives us something like m(1, 2, 3)
    index_str = ""
    for idx in range(len(term_indices)):
        if idx > 0:
            index_str = index_str + ", "
        index_str = index_str + str(term_indices[idx])

    print("  " + term_label + ": m(" + index_str + ")")
    print("=" * 55)

    # return everything stage 3 (kmap.py) will need
    return equation_type, equation, term_indices