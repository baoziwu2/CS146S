# CS146S: The Modern Software Developer

This repository is a fork of the official [CS146S: The Modern Software Developer](https://themodernsoftware.dev/) assignments repo from Stanford University (Fall 2025).

It serves as a personal workspace for **meowl** to document progress, store completed assignments, and share study notes.

Updating...

## Repository Contents

- **Assignments:** Complete source code for all course projects.
- **Solutions:** My personal approach and walkthroughs for the problem sets.
- **Notes:** Summaries and takeaways from the lectures and readings.

## Setup & Installation

This project is built using **Python 3.12**. Follow these steps to replicate the environment:

### 1. Environment Management

It is recommended to use **Anaconda** to manage the Python environment:

1. [Download Anaconda](https://www.anaconda.com/download) and ensure `conda` is added to your `PATH`.

2. Create and activate the environment:

   Bash

   ```
   conda create -n cs146s python=3.12 -y
   conda activate cs146s
   ```

### 2. Dependency Management

We use **Poetry** for package management.

1. Install Poetry:

   ```bash
   curl -sSL https://install.python-poetry.org | python -
   ```

2. Install dependencies (ensure the `cs146s` conda env is active):

   ```bash
   poetry install --no-interaction
   ```

------

## Disclaimer

This repository is for educational purposes. If you are currently enrolled in CS146S, please ensure you follow Stanford's Honor Code regarding looking at existing solutions.
