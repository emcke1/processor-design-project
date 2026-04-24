# ============================================================
#
#   datapath.py - Single-cycle datapath
#
#   This is what wires all the components together.
#   Each call to execute_instruction() does the full
#   Fetch -> Decode -> Execute -> Write-back in one shot.
#
#   Components used:
#     register_file.py  — reads source regs, writes result
#     alu.py            — does the actual AND / OR / AND-not
#     mux.py            — routes the inversion signal into ALU input A
#     control_unit.py   — decodes the instruction word
#
# ============================================================

from register_file import RegisterFile
from alu           import ALU
from mux           import mux2
from control_unit  import ControlUnit

WORD_MASK = 0xFFFFFFFF


class Datapath:

    def __init__(self):
        self.reg_file   = RegisterFile()
        self.alu        = ALU()
        self.control    = ControlUnit()
        self.cycle      = 0
        self.trace      = []    # list of dicts, one per instruction

    # --------------------------------------------------------
    # LOAD REGISTERS
    # called before execution to set initial register values
    # --------------------------------------------------------
    def load_registers(self, values):
        self.reg_file.load(values)

    # --------------------------------------------------------
    # EXECUTE INSTRUCTION
    # runs one instruction through the full pipeline
    # mnemonic is just a label for the trace output
    # returns the result that was written to rd
    # --------------------------------------------------------
    def execute_instruction(self, instruction, mnemonic=""):
        self.cycle += 1

        # FETCH — instruction word is already provided
        # in a real processor this would go to memory, but
        # here we just hand it in directly

        # DECODE
        rs, rt, rd, signals = self.control.decode(instruction)

        # EXECUTE
        data_rs, data_rt = self.reg_file.read(rs, rt)

        # the mux in front of ALU input A picks between
        # the raw value and its inverse based on invert_a
        alu_in_a = mux2(data_rs, (~data_rs) & WORD_MASK, int(signals.invert_a))
        alu_in_b = data_rt

        # invert_a was already handled by the mux, so pass False here
        result = self.alu.execute(alu_in_a, alu_in_b, signals.alu_op, False)

        # WRITE-BACK
        self.reg_file.write(rd, result, signals.reg_write)

        # save everything for the trace printer
        self.trace.append({
            "cycle":     self.cycle,
            "mnemonic":  mnemonic,
            "rs":        rs,
            "rt":        rt,
            "rd":        rd,
            "data_rs":   data_rs,
            "data_rt":   data_rt,
            "signals":   signals,
            "result":    result,
            "reg_state": self.reg_file.dump(),
        })

        return result
