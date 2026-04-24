# ============================================================
#   Author: Eden McKenzie
#   Course: CSC 4210/6210 - Computer Architecture
#   Semester: Spring 2026
#   Assignment: Processor Design Semester Project - Task 4
#
#   Single-Cycle Processor — AND / OR
#
#   Target computation: Y = A·B + C'·D
#
#   The processor executes exactly three instructions to get there:
#
#     and t4, t0, t1   ->  t4 = A & B
#     and t6, t5, t3   ->  t6 = (~C) & D   (invert_a flag set)
#     or  t0, t4, t6   ->  t0 = Y
#
#   NOT is not its own instruction — the control unit sets an
#   inversion flag in the function field and the ALU flips the
#   first operand before doing the AND.
#
#   This is the main entry point. It ties together all the stages:
#
#   Stage 1 - register_file.py  — 32-bit register file
#   Stage 2 - alu.py            — ALU (AND / OR + inversion)
#   Stage 3 - mux.py            — multiplexer for inversion path
#   Stage 4 - control_unit.py   — instruction decoder / signal gen
#   Stage 5 - datapath.py       — single-cycle datapath
#
#   Run this file and pick demo or interactive mode.
# ============================================================

from datapath      import Datapath
from control_unit  import FUNC_AND, FUNC_AND_NOT, FUNC_OR, OPCODE_RTYPE
from alu           import OP_AND, OP_OR


# ------------------------------------------------------------
# INSTRUCTION ENCODING
# builds a 32-bit R-type instruction word from its fields
# format: [31:26] opcode | [25:21] rs | [20:16] rt | [15:11] rd
#         [7:6] func | [5] inv_a
# ------------------------------------------------------------
def encode_rtype(rs, rt, rd, func, inv_a):
    word  = (OPCODE_RTYPE & 0x3F) << 26
    word |= (rs            & 0x1F) << 21
    word |= (rt            & 0x1F) << 16
    word |= (rd            & 0x1F) << 11
    word |= (func          & 0x03) <<  6
    word |= (int(inv_a)    & 0x01) <<  5
    return word


# ------------------------------------------------------------
# PRINT TRACE
# shows the instruction execution trace with control signals
# and register state after each instruction
# ------------------------------------------------------------
def print_trace(trace):
    for entry in trace:
        signals  = entry["signals"]
        op_name  = "AND" if signals.alu_op == OP_AND else "OR"
        inv_str  = " [invert_a=1]" if signals.invert_a else ""

        # label the inverted operand with a prime (') in the output
        rs_label = "t" + str(entry["rs"]) + ("'" if signals.invert_a else "")
        rt_label = "t" + str(entry["rt"])
        rd_label = "t" + str(entry["rd"])

        print("\n  Cycle " + str(entry["cycle"]) + ": " + entry["mnemonic"])
        print("  " + "-" * 58)
        print("  Control signals : alu_op=" + op_name + inv_str + ", reg_write=" + str(signals.reg_write))
        print("  Operands        : " + rs_label + " = " + fmt(entry["data_rs"]) + ",  " + rt_label + " = " + fmt(entry["data_rt"]))
        print("  Result          : " + rd_label + " <- " + fmt(entry["result"]))
        print("  Register state  :")
        for idx, val in sorted(entry["reg_state"].items()):
            marker = " <" if idx == entry["rd"] else ""
            print("      t" + str(idx) + " = " + fmt(val) + marker)


# ------------------------------------------------------------
# PRINT FINAL RESULTS
# shows t4, t6, and the final Y alongside expected value
# ------------------------------------------------------------
def print_final(trace, A, B, C, D):
    final_regs = trace[-1]["reg_state"]
    t4 = final_regs[4]
    t6 = final_regs[6]
    t0 = final_regs[0]

    # compute expected result the normal way to verify
    expected = int(bool(A & B) or bool(((~C) & 1) & D))
    y_bit    = t0 & 1

    print("\n" + "=" * 60)
    print("  FINAL RESULTS")
    print("=" * 60)
    print("  Inputs         : A=" + str(A) + "  B=" + str(B) + "  C=" + str(C) + "  D=" + str(D))
    print("  t4  (A & B)    = " + fmt(t4))
    print("  t6  (~C & D)   = " + fmt(t6))
    print("  Y   (t0)       = " + fmt(t0))
    print()
    print("  Single-bit Y   = " + str(y_bit))
    print("  Expected Y     = " + str(expected))
    result = "PASS" if y_bit == expected else "FAIL"
    print("  Validation     : " + result)
    print("=" * 60 + "\n")


# ------------------------------------------------------------
# HELPER - value formatter
# prints both decimal and hex so its easier to read
# ------------------------------------------------------------
def fmt(val):
    return str(val) + " (0x" + format(val, "08X") + ")"


# ------------------------------------------------------------
# RUN PROCESSOR
# sets up the datapath, loads registers, and runs all three
# instructions for a given set of inputs
# ------------------------------------------------------------
def run_processor(A, B, C, D):
    print("\n" + "=" * 60)
    print("  Single-Cycle Processor  |  A=" + str(A) + " B=" + str(B) + " C=" + str(C) + " D=" + str(D))
    print("=" * 60)

    dp = Datapath()

    # register layout:
    #   t0=A, t1=B, t2=C (preserved), t3=D
    #   t5=C (the copy we actually feed into the AND-not ALU operation)
    #   t4, t6 are scratch — will be written during execution
    dp.load_registers({
        0: A,
        1: B,
        2: C,
        3: D,
        5: C,   # t5 is the source for instruction 2 (gets inverted by ALU)
    })

    # instruction 1: and t4, t0, t1  ->  t4 = A & B
    i1 = encode_rtype(rs=0, rt=1, rd=4, func=FUNC_AND, inv_a=False)
    dp.execute_instruction(i1, mnemonic="and t4, t0, t1   ; t4 = A & B")

    # instruction 2: and t6, t5, t3  ->  t6 = (~C) & D
    # inv_a=True tells the control unit to set the inversion flag
    # the mux flips t5 before it hits the ALU — no NOT instruction needed
    i2 = encode_rtype(rs=5, rt=3, rd=6, func=FUNC_AND_NOT, inv_a=True)
    dp.execute_instruction(i2, mnemonic="and t6, t5, t3   ; t6 = (~C) & D")

    # instruction 3: or t0, t4, t6  ->  t0 = t4 | t6 = Y
    i3 = encode_rtype(rs=4, rt=6, rd=0, func=FUNC_OR, inv_a=False)
    dp.execute_instruction(i3, mnemonic="or  t0, t4, t6   ; t0 = Y")

    print("\n  --- Instruction Execution Trace ---")
    print_trace(dp.trace)
    print_final(dp.trace, A, B, C, D)


# ------------------------------------------------------------
# DEMO MODE
# runs all 16 combinations of A, B, C, D and checks each one
# good for seeing the truth table at a glance
# ------------------------------------------------------------
def run_demo():
    print("\n" + "=" * 60)
    print("   DEMO — Single-Cycle Processor  Y = A·B + C'·D")
    print("   All 16 input combinations")
    print("=" * 60 + "\n")

    all_pass = True
    results  = []

    for combo in range(16):
        A = (combo >> 3) & 1
        B = (combo >> 2) & 1
        C = (combo >> 1) & 1
        D =  combo       & 1

        expected = int(bool(A & B) or bool(((~C) & 1) & D))

        dp = Datapath()
        dp.load_registers({0: A, 1: B, 2: C, 3: D, 5: C})

        dp.execute_instruction(encode_rtype(0, 1, 4, FUNC_AND, False),     "and t4,t0,t1")
        dp.execute_instruction(encode_rtype(5, 3, 6, FUNC_AND_NOT, True),  "and t6,t5,t3")
        dp.execute_instruction(encode_rtype(4, 6, 0, FUNC_OR, False),      "or  t0,t4,t6")

        y  = dp.trace[-1]["reg_state"][0] & 1
        ok = y == expected

        if not ok:
            all_pass = False

        results.append((A, B, C, D, expected, y, ok))

    print("  " + "{:>2}  {:>2}  {:>2}  {:>2} | {:>4}  {:>4}   Status".format("A","B","C","D","Exp","Got"))
    print("  " + "-" * 44)
    for A, B, C, D, exp, got, ok in results:
        status = "PASS" if ok else "FAIL"
        print("  " + "{:>2}  {:>2}  {:>2}  {:>2} | {:>4}  {:>4}   {}".format(A, B, C, D, exp, got, status))

    print()
    if all_pass:
        print("  All 16 combinations passed.")
    else:
        print("  Some combinations failed — check above.")
    print()


# ------------------------------------------------------------
# INTERACTIVE MODE
# user types in A, B, C, D and sees the full execution trace
# ------------------------------------------------------------
def run_interactive():
    print("\n" + "=" * 60)
    print("   INTERACTIVE MODE — Single-Cycle Processor")
    print("=" * 60 + "\n")
    print("  Enter single-bit values (0 or 1) for each input.\n")

    A = get_bit("  A = ")
    B = get_bit("  B = ")
    C = get_bit("  C = ")
    D = get_bit("  D = ")

    run_processor(A, B, C, D)


# ------------------------------------------------------------
# HELPER - safe single-bit input
# keeps asking until the user gives a 0 or 1
# ------------------------------------------------------------
def get_bit(prompt):
    while True:
        raw = input(prompt).strip()
        if raw == "0" or raw == "1":
            return int(raw)
        print("  Please enter 0 or 1.")


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Task 4 — Single-Cycle Processor (AND / OR)")
    print("  Target: Y = A·B + C'·D")
    print("=" * 60)
    print("  1) Interactive  (enter your own A, B, C, D)")
    print("  2) Demo         (all 16 input combinations)")

    choice = input("\n  Choose (1 or 2): ").strip()

    if choice == "1":
        run_interactive()
    elif choice == "2":
        run_demo()
    else:
        print("  Invalid choice. Running demo by default.")
        run_demo()
