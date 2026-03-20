# ============================================================
#   Author: Eden McKenzie
#   Course: CSC 4210/6210 - Computer Architecture
#   Semester: Spring 2026
#   Assignment: Processor Design Semester Project - Task 2
#
#   IoT Use Case: Smart Temperature Sensor Node
#
#
#   This part handles combinational logic design.
#   User provides a truth table, we generate the canonical
#   Boolean equation (SOP or POS), simplify it using a K-Map,
#   and validate the result against the original truth table.
#
#   This is the main entry point for Task 2.
#   It ties together all the stages:
#
#   Stage 1 - get the truth table from the user
#   Stage 2 - generate the canonical Boolean equation (SOP or POS)
#   Stage 3 - simplify it using a K-Map
#   Stage 4 - validate the simplified expression against the truth table
#
#   Each stage lives in its own file to keep things organized.
#   This file just calls them in order.
# ============================================================

from utils import print_divider, print_section
from boolean_logic import get_boolean_equation
from kmap import run_kmap
from validator import validate


# ------------------------------------------------------------
# STAGE 1 - INPUT SYSTEM
# ask user for number of variables and collect the truth table
# doing input collection right here since its the entry point
# ------------------------------------------------------------
def get_num_variables():
    """
    Ask user for number of input variables (min 2).
    Keep asking until they give something valid.
    """
    while True:
        user_input = input("How many input variables? (minimum 2): ").strip()

        # make sure its actually a number before converting
        if not user_input.isdigit():
            print("  Error: please enter a whole number.")
            continue

        num_vars = int(user_input)

        # assignment says n >= 2, so anything below that is invalid
        if num_vars < 2:
            print("  Error: need at least 2 variables.")
            continue

        # k-map only works for up to 4 variables
        if num_vars > 4:
            print("  Error: maximum 4 variables supported for K-Map.")
            continue

        return num_vars


def get_truth_table(num_vars):
    """
    Collect output values (0 or 1) for all 2^n input combinations.
    Returns a list of (inputs_tuple, output) pairs.
    """
    from utils import input_labels

    # 2^n tells us exactly how many rows the truth table needs
    num_rows = 2 ** num_vars

    # grab only the labels we need
    labels = input_labels[:num_vars]

    # this will hold the full truth table when we're done
    truth_table = []

    print("\nEnter the output (0 or 1) for each input combination:")
    print()

    for row_index in range(num_rows):

        # each row index in binary gives us the input combination
        # e.g. row 2 with 2 vars = binary 10 = A=1, B=0
        binary_str = ""
        temp = row_index
        for bit_position in range(num_vars - 1, -1, -1):
            # shift right and mask to get each bit one at a time
            bit_value = (temp >> bit_position) & 1
            binary_str = binary_str + str(bit_value)

        # turn the binary string into a tuple so its easier to work with
        input_combination = tuple(int(bit) for bit in binary_str)

        # build a readable label for the prompt like "A=1, B=0"
        row_label = ""
        for var_index in range(num_vars):
            if var_index > 0:
                row_label = row_label + ", "
            row_label = row_label + labels[var_index] + "=" + str(input_combination[var_index])

        # keep asking until they give us a valid 0 or 1
        while True:
            output_input = input("  Row " + str(row_index) + " (" + row_label + "): ").strip()

            # anything other than 0 or 1 is invalid for a truth table
            if output_input != "0" and output_input != "1":
                print("  Error: output must be 0 or 1.")
                continue

            output_value = int(output_input)
            truth_table.append((input_combination, output_value))
            break

    return truth_table


def validate_truth_table(truth_table, num_vars):
    """
    Make sure the table has 2^n rows and no duplicate input combos.
    Returns True if valid, False if something is wrong.
    """
    num_rows = 2 ** num_vars

    # keep track of combos we've already seen to catch duplicates
    seen_combinations = []
    is_valid = True

    # first check - do we have the right number of rows?
    if len(truth_table) != num_rows:
        print("  Error: expected " + str(num_rows) + " rows, got " + str(len(truth_table)))
        is_valid = False
        return is_valid

    # second check - no input combination should appear more than once
    for input_combination, output_value in truth_table:
        if input_combination in seen_combinations:
            print("  Error: duplicate input combination found")
            is_valid = False
            return is_valid
        seen_combinations.append(input_combination)

    return is_valid


# ------------------------------------------------------------
# MAIN PIPELINE
# runs everything in order, stage by stage
# ------------------------------------------------------------
def main():

    print_divider()
    print("  Processor Design - Task 2")
    print("  Truth Table -> Boolean Equation -> K-Map -> Validate")
    print_divider()
    print()

    # stage 1 - get input from user
    print_section("Stage 1 - Input")
    num_vars = get_num_variables()
    truth_table = get_truth_table(num_vars)

    # validate the truth table before moving on
    is_valid = validate_truth_table(truth_table, num_vars)
    if not is_valid:
        print("  Truth table is invalid. Exiting.")
        return

    # print the truth table so user can see what they entered
    print()
    print_section("Truth Table")
    from utils import input_labels
    labels = input_labels[:num_vars]
    header = "  "
    for label in labels:
        header = header + label + "  "
    header = header + "| Output"
    print(header)
    print("  " + "-" * (num_vars * 3 + 10))
    for input_combination, output_value in truth_table:
        row_str = "  "
        for bit in input_combination:
            row_str = row_str + str(bit) + "  "
        row_str = row_str + "|   " + str(output_value)
        print(row_str)

    # stage 2 - generate boolean equation
    print()
    print_section("Stage 2 - Boolean Equation")
    equation_type, equation, term_indices = get_boolean_equation(truth_table, num_vars)

    # stage 3 - k-map simplification
    # kmap only works for SOP right now so we check for that
    print()
    print_section("Stage 3 - K-Map Simplification")
    if equation_type == "SOP":
        simplified_expression = run_kmap(truth_table, term_indices, num_vars)
    else:
        # for POS we skip the kmap and just use the canonical equation
        print("  K-Map simplification is only supported for SOP.")
        print("  Using canonical POS equation as the result.")
        simplified_expression = equation

    # stage 4 - validate
    print()
    validate(truth_table, simplified_expression, num_vars)


# ------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------
if __name__ == "__main__":
    main()