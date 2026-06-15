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
* **gfortran**: AVAILABLE (`/opt/homebrew/bin/gfortran`, GCC version 14.1.0 via Homebrew)
* **f2py**: AVAILABLE (numpy f2py interface)

## 3. OSSOS Survey Simulator Repository
* **Repository Cloning**: AVAILABLE (cloned from `https://github.com/OSSOS/SurveySimulator`)
* **Fortran Component Build**: AVAILABLE (compiled native `Driver` binary with `ReadModelFromFile` module successfully using GCC/gfortran 14.1.0)
* **Python Wrapper Build (`pip install -e .`)**: AVAILABLE (compiled and wrapper available)
* **Status**: **FULLY BENCHMARKED AND CO-VALIDATED** — Executed side-by-side benchmarks showing excellent physical agreement between Python (`[ILLUSTRATIVE-PIPELINE]`) and official Fortran implementations, and computed official simulator p-values on a 10M candidate pool.

## 4. Literature Retrieval
* **arXiv API / Web Search**: AVAILABLE (via standard Python HTTP clients and environment search tools)
