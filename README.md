# Minesweeper Solver (Rule-Based, Vision + Automation)

A rule-based Minesweeper solver that plays directly on a live game using **screen reading + mouse automation**.

This project focuses on:
- accurate **pixel-based board parsing**
- clean separation between **vision**, **logic**, and **execution**
- a **deterministic solver** that stops correctly when guessing is required

No internal game state, no APIs — everything is inferred from the screen.

---

## Features

- **Rule-based solver**
  - Implements the two fundamental Minesweeper rules:
    - If remaining mines = unknown neighbors → all are mines
    - If remaining mines = 0 → all unknown neighbors are safe
  - Solves most boards without guessing
  - Correctly stops when no deterministic move exists

- **Pixel-based board reading**
  - Detects numbers, flags, unknown tiles, win & loss states from screen pixels
  - Robust against animations and timing issues
  - Works on Minesweeper Online (browser-based)

- **Direct mouse control**
  - Uses `pyautogui` to perform left/right clicks
  - Actions are decided first, then executed (no mid-logic IO)

- **Stable architecture**
  - Clear separation:
    - Vision (read board)
    - Solver (decide actions)
    - Executor (click)
  - Full board remap after actions to ensure state consistency

---

## How the Solver Works

At a high level:

1. Read the entire board from screen pixels
2. For each numbered cell:
   - Count known mines and unknown neighbors
   - Compute remaining mines
3. Apply deterministic rules:
   - All remaining unknowns are mines → flag them
   - No remaining mines → click all unknowns
4. Execute all actions
5. Remap the board
6. Repeat until:
   - The game is won
   - Or no further deterministic move is possible

If the solver stops with unrevealed tiles remaining, the position is **logically ambiguous** (true 50/50 or guessing required).

---

## Limitations

- This solver is **deterministic only**
- It does **not** guess or brute-force ambiguous positions
- Some boards will require guessing by design (this is expected behavior)
- Local brute-force on frontier regions
- Slow

Future improvements could include:
- Probability-based guessing
- SAT/CSP-based solving

---

## Usage

1. Open a Minesweeper game (e.g. Minesweeper Online)
2. Ensure the board is fully visible on screen
3. Adjust TILES_X_START, TILES_Y_START, and offsets if needed
4. Run the script
5. The solver will:
  - Perform initial clicks
  - Solve deterministically
  - Stop when no safe move exists

---

## Project Goals

This project was built to:
- Learn how to combine computer vision, automation, and logical reasoning
- Explore solver architecture and constraint-based reasoning
- Understand the limits of rule-based approaches in Minesweeper
It is intentionally written without using any game internals.

---

## Notes

- Screen coordinates and colors may vary by system or browser theme
- Timing values (sleep) may need small adjustments
- Designed for learning and experimentation, not speedrunning

---

## Versions

Currently in v3:
- v1: Vision and board mapping
- v2: Basic rule-based solver
- v3: Solver with Brute-forcing
- v4: Optimization

---
