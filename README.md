# Saarthi-Axiom: Subprocess Execution Harness & Diagnostic Triage for Lean 4

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Lean 4](https://img.shields.io/badge/Lean%204-v4.6.0-blue)](https://leanprover.github.io/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-green)](https://www.python.org/)

**Saarthi-Axiom** is an asynchronous execution harness designed to evaluate, sandbox, and extract diagnostics from AI-generated formal proofs inside the [Lean 4](https://leanprover.github.io/) interactive theorem prover.

Language models frequently propose proof steps that fail to compile due to type mismatches, unknown lemmas, or syntax errors. Saarthi-Axiom eliminates pipeline deadlocks by providing an isolated, resource-bounded execution environment that maps compiler diagnostics directly to structured fault categories.

---

## Architecture Overview

```
[ LLM / Tactic Generator ]
│  (Tactic Sequence)
▼
┌───────────────────────────────────────┐
│     Saarthi Subprocess Sandbox        │
│  - Asynchronous timeout enforcement   │
│  - Ephemeral scratchpad management    │
│  - Process isolation                  │
└───────────────────┬───────────────────┘
│  lake env lean
▼
┌───────────────────────────────────────┐
│         Lean 4 Kernel & Lake          │
│   (Mathlib4 Dependent Type Checker)   │
└───────────────────┬───────────────────┘
│
┌───────┴───────┐
(Exit Code 0)    (Compiler Output)
│               │
▼               ▼
[ SUCCESS_QED ]   [ Typed Diagnostic Triage ]
```

---

## Key Features

- **Asynchronous Process Isolation:** Executes `lake env lean` within non-blocking subprocesses with strict wall-clock timeout thresholds.
- **Structured Diagnostic Extraction:** Converts compiler standard error streams into typed Pydantic models with line/column coordinates and categorized error types (`TypeMismatch`, `UnknownIdentifier`, `TacticFailure`, `UnsolvedGoals`).
- **Benchmark Manifest Pipeline:** Ingests international competition suites like [miniF2F](https://github.com/openai/miniF2F) and outputs standardized JSONL task records.
- **Compilation-Verified Reference Proofs:** Ships with certified, `sorry`-free proofs across discrete math induction, ring normalization, and kernel security properties.

---

## Reference Formalizations

| Benchmark | Domain | Key Tactics | File |
| :--- | :--- | :--- | :--- |
| **Sum of Natural Numbers** | Induction | `induction`, `ring` | `benchmarks/DiscreteMath.lean` |
| **Microkernel Isolation** | Systems Security | `unfold`, `simp` | `benchmarks/KernelSecurity.lean` |
| **RBF Kernel Symmetry** | Functional Analysis | `ring`, `rw` | `benchmarks/AlgebraBasics.lean` |
| **Linear Systems** | Real Arithmetic | `linarith` | `benchmarks/AlgebraBasics.lean` |

---

## Installation & Usage

### 1. Prerequisites
Install Lean 4 via `elan`:
```bash
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh
source $HOME/.elan/env
```

### 2. Python Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Test Suite
```bash
pytest tests/
```

### 4. Extract miniF2F Benchmarks
```bash
python3 -m src.saarthi.minif2f_parser --data-dir path/to/miniF2F --output data/minif2f_manifest.jsonl
```

---

## Academic R&D & Funding Alignment

Saarthi-Axiom is aligned with Scottish academic enterprise initiatives (Interface / Scottish Funding Council Innovation Vouchers). We collaborate with Scottish research laboratories specializing in Dependent Type Theory, Interactive Theorem Proving (Lean 4 / Mathlib4), and Automated Reasoning.

For technical collaboration or grant inquiries: sanesystems.ai@gmail.com.

---

## License

This project is licensed under the MIT License. See LICENSE for details.
