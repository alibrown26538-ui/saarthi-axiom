from __future__ import annotations

import asyncio
import os
import re
import time
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class DiagnosticSeverity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ProofStatus(str, Enum):
    SUCCESS_QED = "SUCCESS_QED"
    OPEN_GOAL_SORRY = "OPEN_GOAL_SORRY"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    TIMEOUT = "TIMEOUT"
    PROCESS_FAILURE = "PROCESS_FAILURE"


class LeanDiagnostic(BaseModel):
    file_path: str
    line: int
    column: int
    severity: DiagnosticSeverity
    message: str
    error_class: Optional[str] = None


class VerificationResult(BaseModel):
    trajectory_id: str
    status: ProofStatus
    wall_clock_ms: float
    diagnostics: List[LeanDiagnostic] = Field(default_factory=list)
    raw_stdout: str = ""
    raw_stderr: str = ""
    lean_code_evaluated: str = ""


class LeanEnvironmentRunner:
    """Manages asynchronous subprocess execution and diagnostic extraction for Lean 4."""

    DIAGNOSTIC_REGEX = re.compile(
        r"^(?P<file>[^:\n]+):(?P<line>\d+):(?P<col>\d+):\s+(?P<severity>error|warning|info):\s+(?P<msg>.+)$",
        re.MULTILINE,
    )

    def __init__(self, workspace_dir: str | Path, default_timeout_sec: float = 15.0):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.default_timeout_sec = default_timeout_sec
        self.scratch_dir = self.workspace_dir / ".saarthi_scratch"
        self.scratch_dir.mkdir(parents=True, exist_ok=True)

    def _parse_diagnostics(self, output: str) -> List[LeanDiagnostic]:
        diagnostics = []
        for match in self.DIAGNOSTIC_REGEX.finditer(output):
            sev_str = match.group("severity").upper()
            sev = DiagnosticSeverity[sev_str] if sev_str in DiagnosticSeverity.__members__ else DiagnosticSeverity.ERROR
            msg = match.group("msg").strip()

            error_class = None
            msg_lower = msg.lower()
            if "type mismatch" in msg_lower:
                error_class = "TypeMismatch"
            elif "unknown identifier" in msg_lower:
                error_class = "UnknownIdentifier"
            elif "unsolved goals" in msg_lower:
                error_class = "UnsolvedGoals"
            elif "tactic" in msg_lower and "failed" in msg_lower:
                error_class = "TacticFailure"

            diagnostics.append(
                LeanDiagnostic(
                    file_path=match.group("file"),
                    line=int(match.group("line")),
                    column=int(match.group("col")),
                    severity=sev,
                    message=msg,
                    error_class=error_class,
                )
            )
        return diagnostics

    async def verify_proof_script(
        self,
        trajectory_id: str,
        lean_code: str,
        timeout_sec: Optional[float] = None,
    ) -> VerificationResult:
        timeout = timeout_sec or self.default_timeout_sec
        scratch_file = self.scratch_dir / f"Scratch_{int(time.time() * 1000)}.lean"
        scratch_file.write_text(lean_code, encoding="utf-8")

        cmd = ["lake", "env", "lean", str(scratch_file)]
        start_time = time.perf_counter()

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.workspace_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
                stdout = stdout_b.decode("utf-8", errors="replace")
                stderr = stderr_b.decode("utf-8", errors="replace")
                raw_combined = f"{stdout}\n{stderr}".strip()
                duration_ms = (time.perf_counter() - start_time) * 1000

                diagnostics = self._parse_diagnostics(raw_combined)
                has_error = any(d.severity == DiagnosticSeverity.ERROR for d in diagnostics)
                has_sorry = "declaration uses 'sorry'" in raw_combined or "sorry" in lean_code

                if process.returncode == 0 and not has_error:
                    status = ProofStatus.OPEN_GOAL_SORRY if has_sorry else ProofStatus.SUCCESS_QED
                else:
                    status = ProofStatus.COMPILATION_ERROR

                return VerificationResult(
                    trajectory_id=trajectory_id,
                    status=status,
                    wall_clock_ms=round(duration_ms, 2),
                    diagnostics=diagnostics,
                    raw_stdout=stdout,
                    raw_stderr=stderr,
                    lean_code_evaluated=lean_code,
                )

            except asyncio.TimeoutError:
                try:
                    process.kill()
                    await process.wait()
                except ProcessLookupError:
                    pass
                duration_ms = (time.perf_counter() - start_time) * 1000
                return VerificationResult(
                    trajectory_id=trajectory_id,
                    status=ProofStatus.TIMEOUT,
                    wall_clock_ms=round(duration_ms, 2),
                    diagnostics=[
                        LeanDiagnostic(
                            file_path=str(scratch_file),
                            line=0,
                            column=0,
                            severity=DiagnosticSeverity.ERROR,
                            message=f"Lean compiler timed out after {timeout} seconds.",
                            error_class="Timeout",
                        )
                    ],
                    lean_code_evaluated=lean_code,
                )

        finally:
            if scratch_file.exists():
                try:
                    scratch_file.unlink()
                except OSError:
                    pass
