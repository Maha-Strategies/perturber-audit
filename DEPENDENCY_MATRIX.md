# Dependency Matrix

This document lists the status (AVAILABLE / FAILED) of all tools, libraries, and compilers required for this research replication.

## 1. Python Stack
* **Python Interpreter**: AVAILABLE (`/opt/homebrew/bin/python3`, version 3.14.4)
* **numpy**: AVAILABLE (version 2.4.6)
* **scipy**: AVAILABLE (version 1.17.1)
* **astropy**: AVAILABLE (version 7.2.0)
* **matplotlib**: AVAILABLE (version 3.10.9)
* **pandas**: AVAILABLE (version 3.0.3)

## 2. Build Tools & Compilers
* **git**: AVAILABLE (`/usr/bin/git`)
* **cc/clang/gcc**: AVAILABLE (`/usr/bin/cc`, `/usr/bin/clang`, `/usr/bin/gcc`)
* **gfortran**: FAILED (command not found on host environment)
* **f2py**: FAILED (command not found on host environment)

## 3. OSSOS Survey Simulator Repository
* **Repository Cloning**: AVAILABLE (cloned from `https://github.com/OSSOS/SurveySimulator`)
* **Fortran Component Build**: FAILED (missing `gfortran` compiler)
* **Python Wrapper Build (`pip install -e .`)**: FAILED (fails when invoking subprocess `make` for Fortran modules: `make: gfortran: No such file or directory`)
* **Status**: **FALLBACK ENGAGED** — Implementing survey selection function filtering directly in Python as an **`[ILLUSTRATIVE-PIPELINE]`** based on the survey pointing history and detection efficiency files.

## 4. Literature Retrieval
* **arXiv API / Web Search**: AVAILABLE (via standard Python HTTP clients and environment search tools)
