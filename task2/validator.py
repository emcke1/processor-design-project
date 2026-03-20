# ============================================================
#   
#   Stage 4 - Validation
#
#   This is the final check. We take the simplified expression
#   we got from the k-map and test it against every single row
#   in the original truth table.
#
#   If the simplified expression gives the same output as the
#   truth table for every input combination, we print PASS.
#   If even one row doesnt match, we print FAIL.
#
#   This is important because simplification can go wrong.
#   Having a validation step means we catch any mistakes
#   before they make it into actual hardware.
# ============================================================

from utils import input_labels


# ------------------------------------------------------------
# HELPER - evaluate one term
# a term is something like A'B or AB'C
# we check each variable in the term against the input combo
# if all variables match, the term evaluates to 1
# otherwise it evaluates to 0
# ------------------------------------------------------------
def evaluate_term(term, input_combination, num_vars):
    """
    Evaluates a single product term against one input combination.
    Returns 1 if the term is satisfied, 0 if not.
    """
    labels = input_labels[:num_vars]

    # go through each variable and check if the input matches
    term_index = 0
    while term_index < len(term):

        # figure out which variable this is
        current_char = term[term_index]

        # skip anything thats not a variable label
        if current_char not in labels:
            term_index = term_index + 1
            continue

        # find which variable index this label corresponds to
        var_index = labels.index(current_char)

        # check if the next character is a complement mark
        is_complemented = False
        if term_index + 1 < len(term):
            if term[term_index + 1] == "'":
                is_complemented = True
                term_index = term_index + 1

        # get the actual input value for this variable
        actual_value = input_combination[var_index]

        # if complemented, variable must be 0 to satisfy
        # if not complemented, variable must be 1 to satisfy
        if is_complemented:
            if actual_value != 0:
                return 0
        else:
            if actual_value != 1:
                return 0

        term_index = term_index + 1

    # if we made it through all variables without failing, term is satisfied
    return 1


# ------------------------------------------------------------
# HELPER - evaluate the full simplified expression
# the expression is made up of terms joined by +
# in SOP, if ANY term evaluates to 1, the whole expression is 1
# if ALL terms evaluate to 0, the whole expression is 0
# ------------------------------------------------------------
def evaluate_expression(simplified_expression, input_combination, num_vars):
    """
    Evaluates the full simplified SOP expression for one input combination.
    Returns 1 or 0.
    """
    # handle edge cases first
    if simplified_expression == "1":
        return 1
    if simplified_expression == "0":
        return 0

    # split the expression into individual terms by the + sign
    # doing it manually so its clear whats happening
    term_list = []
    current_term = ""

    for char_index in range(len(simplified_expression)):
        current_char = simplified_expression[char_index]

        if current_char == "+":
            # we hit a + so the current term is done
            # strip spaces and save it
            trimmed_term = current_term.strip()
            if trimmed_term != "":
                term_list.append(trimmed_term)
            current_term = ""
        else:
            current_term = current_term + current_char

    # dont forget the last term after the loop ends
    trimmed_term = current_term.strip()
    if trimmed_term != "":
        term_list.append(trimmed_term)

    # evaluate each term - if any is 1, whole expression is 1
    for term in term_list:
        term_result = evaluate_term(term, input_combination, num_vars)
        if term_result == 1:
            return 1

    # if none of the terms were 1, expression evaluates to 0
    return 0


# ------------------------------------------------------------
# MAIN VALIDATION FUNCTION
# go through every row in the truth table
# evaluate the simplified expression for that row
# compare to the original output
# if everything matches we pass, otherwise we fail
# ------------------------------------------------------------
def validate(truth_table, simplified_expression, num_vars):
    """
    Validates the simplified expression against the original truth table.
    Prints PASS or FAIL and returns True or False.
    """
    print("\n" + "=" * 55)
    print("  Validation")
    print("=" * 55)

    all_passed = True

    for row_index in range(len(truth_table)):
        input_combination = truth_table[row_index][0]
        expected_output = truth_table[row_index][1]

        # evaluate our simplified expression for this input combo
        actual_output = evaluate_expression(simplified_expression, input_combination, num_vars)

        # compare to what the truth table says it should be
        if actual_output != expected_output:
            all_passed = False

            # build the input label for printing like A=0, B=1
            labels = input_labels[:num_vars]
            row_label = ""
            for var_index in range(num_vars):
                if var_index > 0:
                    row_label = row_label + ", "
                row_label = row_label + labels[var_index] + "=" + str(input_combination[var_index])

            print("  MISMATCH at row " + str(row_index) + " (" + row_label + ")")
            print("    Expected: " + str(expected_output))
            print("    Got:      " + str(actual_output))

    # print final result
    print()
    if all_passed:
        print("  Validation Result: PASS")
        print("  Simplified expression matches the original truth table.")
    else:
        print("  Validation Result: FAIL")
        print("  Simplified expression does NOT match the truth table.")

    print("=" * 55)

    return all_passed