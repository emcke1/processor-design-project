# Processor Design Semester Project
**Course:** CSC 4210/6210 - Computer Architecture  
**Semester:** Spring 2026  
**Author:** Eden McKenzie  
**IoT Use Case:** Smart Temperature Sensor Node

---

## Overview

This project is a three-part processor design simulation built in Python.
The goal is to understand how a processor handles data and makes decisions
at the hardware level — from raw number representation and combinational
logic design all the way up to memory hierarchy simulation.

All tasks are connected to the same IoT use case: a Smart Temperature
Sensor Node. Task 1 handles how the sensor's data gets validated and
represented internally. Task 2 handles the logic design that would live
inside the chip itself. Task 3 models the full memory subsystem that
feeds instructions to the CPU.

---

## Project Structure
```
processor-design-project/
├── task1/
│   └── task1_eden_mckenzie.py
├── task2/
│   ├── task2_eden_mckenzie.py
│   ├── boolean_logic.py
│   ├── kmap.py
│   ├── validator.py
│   └── utils.py
├── task3/
│   ├── task3_eden_mckenzie.py
│   ├── config.py
│   ├── memory_level.py
│   ├── hierarchy.py
│   └── output.py
├── visuals/
│   └── (worksheets and diagrams)
└── README.md
```

---

## Task 1 — Input Parser & Number Representation

Task 1 is the "front door" of the processor. Before any data gets
processed, it needs to be validated and converted into a format the
hardware understands.

The program takes a decimal integer from the sensor, checks if it fits
in a 32-bit signed integer range, clamps it if it doesn't (saturation
logic), converts it to 32-bit two's complement binary internally, and
outputs it in whatever format the user requests.

**How to run:**
```bash
python3 task1/task1_eden_mckenzie.py
```

**Features:**
- Input parsing and type validation
- 32-bit signed integer overflow detection
- Saturation logic (clamps instead of wrapping)
- Conversion to 32-bit two's complement binary
- Output in DEC, BIN, or HEX format
- Status flags: overflow_flag, saturated_flag
- Built-in unit tests

**Example output:**
```
Sensor Reading : Sensor fault (too high)
Raw Input      : 9999999999
Output Format  : DEC
value_out      : 2147483647
overflow_flag  : 1
saturated_flag : 1
```

---

## Task 2 — Truth Table → Boolean Equation → K-Map Simplification

Task 2 is about combinational logic design. This is how the logic
inside a processor chip gets designed — starting from a truth table
and working down to the simplest possible Boolean expression.

The program takes a truth table from the user, generates the canonical
Boolean equation in SOP or POS form, simplifies it using a Karnaugh Map,
and validates the result against the original truth table.

**How to run:**
```bash
python3 task2/task2_eden_mckenzie.py
```

**Features:**
- Supports 2 to 4 input variables
- Interactive truth table input with validation
- Canonical SOP and POS equation generation
- Minterm and maxterm listing
- K-Map construction and grouping (Gray code ordering)
- Automatic simplification via K-Map group analysis
- Validation against original truth table (PASS / FAIL)

**Example output:**
```
Canonical SOP: A'B' + A'B
Minterms: m(0, 1)

K-Map:
        B=0   B=1
A=0  [  1  ][  1  ]
A=1  [  0  ][  0  ]

K-Map Groups Found:
  Group: {m0, m1}

Simplified Expression: A'

Validation Result: PASS
```

---

---

## Task 3 — Memory Hierarchy Simulation (SSD → DRAM → Cache → CPU)

Task 3 models the memory subsystem of the processor. Instructions must
travel through the full hierarchy — no skipping levels. This is how a
real CPU is fed data in hardware.

The simulator uses a clock-driven model. Each transfer between levels
costs clock cycles (student-defined latency). An LRU replacement policy
handles cache evictions, and evicted blocks are written back down the
chain (write-back policy).

**How to run:**
```bash
python3 task3/task3_eden_mckenzie.py
```

Choose **1** for a pre-built demo, or **2** for interactive mode where
you configure the hierarchy, load instructions, and issue your own`read` / `write` commands.

**Features:**
- Five memory levels: SSD, DRAM, L3, L2, L1
- Configurable capacity per level (in 32-bit instructions)
- Enforced hierarchy: SSD > DRAM > L3 > L2 > L1
- Clock-driven model with per-transfer latency
- Strict no-skip data flow: SSD → DRAM → L3 → L2 → L1 → CPU
- Read: miss propagates down until found, loads back through all levels
- Write: write-back with write-allocate, evictions propagate downward
- LRU cache replacement policy (bonus)
- Full access trace with cycle timestamps
- Cache hit / miss statistics per level
- Final state dump for every memory level

**Example output (abridged):**
```
[Cycle     0] READ  addr=0x00000000
[Cycle     0]   L1 MISS
[Cycle     0]   L2 MISS
[Cycle     0]   L3 MISS
[Cycle     0]   DRAM MISS
[Cycle     0]   SSD HIT  → val=0xa0010001
[Cycle    10]   SSD → DRAM | addr=0x00000000 val=0xa0010001 | latency=10 cycles
...
[Cycle    84] READ  addr=0x00000000
[Cycle    85]   L1 HIT  → val=0xa0010001 | total latency=1 cycle

Cache hit rate — L1: 30.8%  |  Total cycles: 186
```

---

## Visuals

The `visuals/` folder contains hand-drawn worksheets showing the full
engineering process before it was coded — truth tables, K-Map grids,
grouping analysis, and simplified expressions worked out by hand.

![K-Map Worksheet](visuals/kmap_worksheet.jpg)

---

## How to Run

Make sure you have Python 3 installed. Clone the repo and run either task:
```bash
git clone https://github.com/emcke1/processor-design-project.git
cd processor-design-project

# Run Task 1
python3 task1/task1_eden_mckenzie.py

# Run Task 2
python3 task2/task2_eden_mckenzie.py

# Run Task 3
python3 task3/task3_eden_mckenzie.py
```

No external libraries needed. All programs run on standard Python 3.

---

## Notes

- Task 2 K-Map simplification supports SOP only for 2-4 variables
- POS generates the canonical equation but skips K-Map simplification
- Variable names follow standard logic convention: A, B, C, D