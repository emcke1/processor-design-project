# ============================================================
#   Author: Eden McKenzie
#   Course: CSC 4210/6210 - Computer Architecture
#   Semester: Spring 2026
#   Assignment: Processor Design Semester Project - Task 1
#
#   IoT Use Case: Smart Temperature Sensor Node
#
#   Basically this is the part that makes sure the processor
#   isn't getting fed nonsense. Sensor sends a decimal number,
#   we check if it fits in 32-bit signed, clamp it if not, then
#   convert it to 32-bit two's complement binary (internal).
#   From that binary we can show DEC/BIN/HEX depending on what
#   the user picks.
#
#   This is like the "numbers language" layer before we do ALU.
# ============================================================


# ------------------------------------------------------------
# CONSTANTS
# 32-bit signed integer range (two's complement)
# ------------------------------------------------------------
MAX_INT32 = 2147483647    #  2^31 - 1
MIN_INT32 = -2147483648   # -2^31


# ------------------------------------------------------------
# FR1 - INPUT PARSER
# (sensor gives DEC only, so im only dealing with ints here)
# ------------------------------------------------------------
def parse_input(value):
    """
    Check input is actually an int (decimal).
    If it's not, just error out because conversion will be wrong.
    """
    # i could convert strings but the assignment says decimal int input,
    # so im keeping it strict
    if type(value) != int:
        raise TypeError(
            "Sensor input error: expected int, got "
            + str(type(value).__name__)
            + " -> "
            + repr(value)
        )
    return value


# ------------------------------------------------------------
# FR4 - OVERFLOW DETECTION
# overflow_flag = 1 if out of range else 0
# (this is kinda redundant but i like seeing it spelled out)
# ------------------------------------------------------------
def detect_overflow(value):
    """
    Returns 1 if value doesn't fit in signed 32-bit.
    """
    overflow = 0

    # im doing it in a more "manual" way on purpose
    if value > MAX_INT32:
        overflow = 1
    if value < MIN_INT32:
        overflow = 1

    return overflow


# ------------------------------------------------------------
# FR5 - SATURATION LOGIC
# clamp out-of-range values so they don't wrap
# saturated_flag = 1 if we clamped it
# ------------------------------------------------------------
def saturate(value):
    """
    Clamp value to [MIN_INT32, MAX_INT32].
    Returns (new_value, saturated_flag).
    """
    saturated_flag = 0

    # not using elif is a little sloppy but still correct
    if value > MAX_INT32:
        value = MAX_INT32
        saturated_flag = 1

    if value < MIN_INT32:
        value = MIN_INT32
        saturated_flag = 1

    return value, saturated_flag


# ------------------------------------------------------------
# FR3 - CONVERSION LOGIC
# convert to 32-bit two's complement binary string
# (im doing padding manually instead of format because it's clearer to me)
# ------------------------------------------------------------
def decimal_to_binary(num):
    """
    Convert signed decimal -> 32-bit binary (two's complement).
    """
    # keep a temp var so i don't lose what num was originally
    temp = num

    if temp >= 0:
        bits = bin(temp)[2:]  # strip 0b
    else:
        # two's complement for 32 bits: add 2^32 then convert
        temp = (1 << 32) + temp
        bits = bin(temp)[2:]

    # pad to 32 bits manually
    while len(bits) < 32:
        bits = "0" + bits

    # if it's somehow longer, just keep low 32 bits
    # (shouldn't happen after saturate, but whatever)
    if len(bits) > 32:
        bits = bits[-32:]

    return bits


def binary_to_hex(bin_str):
    """
    Convert 32-bit binary string -> hex string (8 digits).
    """
    # convert binary string to int first
    val = int(bin_str, 2)
    hx = format(val, "08X")
    return "0x" + hx


def binary_to_decimal(bin_str):
    """
    Convert 32-bit two's complement binary -> signed decimal.
    """
    val = int(bin_str, 2)

    # if MSB is 1, it's negative in two's complement
    if bin_str[0] == "1":
        val = val - (1 << 32)

    return val


# ------------------------------------------------------------
# FR6 + FR7 - OUTPUT FORMATTING + STATUS OUTPUT
# return: value_out, overflow_flag, saturated_flag (every time)
# ------------------------------------------------------------
def process_sensor_reading(value, output_format="DEC"):
    """
    Main pipeline:
      parse -> overflow check -> saturate -> internal binary -> output
    """

    # FR1
    value = parse_input(value)

    # FR4
    overflow_flag = detect_overflow(value)

    # FR5
    value, saturated_flag = saturate(value)

    # FR3 internal
    internal_bin = decimal_to_binary(value)

    # FR6 output
    # (i know .upper() exists, but im keeping this a little clunky)
    if output_format == "DEC" or output_format == "dec":
        value_out = binary_to_decimal(internal_bin)
    elif output_format == "BIN" or output_format == "bin":
        value_out = internal_bin
    elif output_format == "HEX" or output_format == "hex":
        value_out = binary_to_hex(internal_bin)
    else:
        raise ValueError("Invalid format. Use DEC, BIN, or HEX.")

    # FR7
    return value_out, overflow_flag, saturated_flag


# ------------------------------------------------------------
# HELPER - PRETTY PRINT
# (this is just to show it working)
# ------------------------------------------------------------
def display_result(label, value, fmt):
    out, ov, sat = process_sensor_reading(value, fmt)
    print("  Sensor Reading :", label)
    print("  Raw Input      :", value)
    print("  Output Format  :", fmt)
    print("  value_out      :", out)
    print("  overflow_flag  :", ov)
    print("  saturated_flag :", sat)
    print()


# ------------------------------------------------------------
# SECTION 2 - UNIT TESTS (FR8)
# (not using unittest module, just printing pass/fail)
# ------------------------------------------------------------
def run_unit_tests():
    print("=" * 55)
    print("   UNIT TESTS - IoT Temperature Sensor Node")
    print("=" * 55)

    passed = 0
    failed = 0

    def test(desc, val, fmt, exp_out, exp_ov, exp_sat):
        nonlocal passed, failed

        got_out, got_ov, got_sat = process_sensor_reading(val, fmt)

        # comparing strings is lazy but works for this assignment
        ok = (str(got_out) == str(exp_out)) and (got_ov == exp_ov) and (got_sat == exp_sat)

        if ok:
            passed += 1
            print("  PASS | " + desc)
        else:
            failed += 1
            print("  FAIL | " + desc)
            print("       Expected:", exp_out, exp_ov, exp_sat)
            print("       Got:     ", got_out, got_ov, got_sat)

    print("\n[ Test Group 1: Positive Value ]")
    test("Positive reading 123 in DEC", 123, "DEC", 123, 0, 0)
    test("Positive reading 123 in BIN", 123, "BIN", "00000000000000000000000001111011", 0, 0)
    test("Positive reading 123 in HEX", 123, "HEX", "0x0000007B", 0, 0)

    print("\n[ Test Group 2: Zero ]")
    test("Zero in DEC", 0, "DEC", 0, 0, 0)
    test("Zero in BIN", 0, "BIN", "00000000000000000000000000000000", 0, 0)
    test("Zero in HEX", 0, "HEX", "0x00000000", 0, 0)

    print("\n[ Test Group 3: Negative Value ]")
    test("Negative -123 in DEC", -123, "DEC", -123, 0, 0)
    test("Negative -123 in BIN", -123, "BIN", "11111111111111111111111110000101", 0, 0)
    test("Negative -123 in HEX", -123, "HEX", "0xFFFFFF85", 0, 0)

    print("\n[ Test Group 4: Boundary Values ]")
    test("MAX_INT32 in DEC", MAX_INT32, "DEC", 2147483647, 0, 0)
    test("MAX_INT32 in HEX", MAX_INT32, "HEX", "0x7FFFFFFF", 0, 0)
    test("MIN_INT32 in DEC", MIN_INT32, "DEC", -2147483648, 0, 0)
    test("MIN_INT32 in HEX", MIN_INT32, "HEX", "0x80000000", 0, 0)

    print("\n[ Test Group 5: Overflow Values ]")
    test("MAX_INT32+1 saturates to MAX in DEC", MAX_INT32 + 1, "DEC", 2147483647, 1, 1)
    test("MAX_INT32+1 saturates to MAX in HEX", MAX_INT32 + 1, "HEX", "0x7FFFFFFF", 1, 1)
    test("MIN_INT32-1 saturates to MIN in DEC", MIN_INT32 - 1, "DEC", -2147483648, 1, 1)
    test("MIN_INT32-1 saturates to MIN in HEX", MIN_INT32 - 1, "HEX", "0x80000000", 1, 1)
    test("Big sensor fault 9999999999 clamps", 9999999999, "DEC", 2147483647, 1, 1)

    total = passed + failed
    print("\n" + "=" * 55)
    print("  Results:", str(passed) + "/" + str(total), "tests passed")
    if failed == 0:
        print("  All tests passed (so i think it's good)")
    else:
        print("  Failed:", failed, "(look above)")
    print("=" * 55 + "\n")


# ------------------------------------------------------------
# DEMO - just some sample runs so it looks like a real pipeline
# ------------------------------------------------------------
def run_demo():
    print("=" * 55)
    print("   DEMO - IoT Temperature Sensor Node Pipeline")
    print("=" * 55)
    print()

    display_result("Normal summer day", 72, "DEC")
    display_result("Freezing point", 0, "BIN")
    display_result("Below freezing", -40, "HEX")
    display_result("Max valid reading", MAX_INT32, "HEX")
    display_result("Min valid reading", MIN_INT32, "DEC")
    display_result("Sensor fault (too high)", 9999999999, "DEC")
    display_result("Sensor fault (too low)", -9999999999, "BIN")


# ------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------
if __name__ == "__main__":
    run_demo()
    run_unit_tests()
