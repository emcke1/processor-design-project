# ============================================================
#   
#   Shared utilities used across all stages
#
#   Keeping shared stuff in one place so i dont have to
#   redefine it in every file. If something needs to change
#   i only have to change it here.
# ============================================================


# ------------------------------------------------------------
# INPUT LABELS
# standard variable names used in logic (A, B, C, D)
# only supporting up to 4 because k-map only works for 2-4 vars
# we slice this list depending on how many vars the user picked
# e.g. 2 vars = ["A", "B"], 3 vars = ["A", "B", "C"]
# ------------------------------------------------------------
input_labels = ["A", "B", "C", "D"]


# ------------------------------------------------------------
# HELPER - print a section divider
# just a visual separator so the output doesnt look like a wall of text
# same idea as the = lines in task 1
# ------------------------------------------------------------
def print_divider():
    print("=" * 55)


# ------------------------------------------------------------
# HELPER - print a section title
# used at the start of each stage output so its clear
# what part of the pipeline we're looking at
# ------------------------------------------------------------
def print_section(title):
    print_divider()
    print("  " + title)
    print_divider()