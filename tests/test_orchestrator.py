import pytest
from pathlib import Path
from src.saarthi.orchestrator import LeanEnvironmentRunner, ProofStatus


@pytest.fixture
def runner(tmp_path):
    return LeanEnvironmentRunner(workspace_dir=tmp_path, default_timeout_sec=5.0)


@pytest.mark.asyncio
async def test_syntax_error_detection(runner):
    invalid_code = "theorem broken : 1 = 2 := by invalid_tactic"
    result = await runner.verify_proof_script("test_fail", invalid_code)
    assert result.status == ProofStatus.COMPILATION_ERROR
    assert len(result.diagnostics) > 0


@pytest.mark.asyncio
async def test_sorry_detection(runner):
    sorry_code = "theorem open_goal : 1 = 1 := by sorry"
    result = await runner.verify_proof_script("test_sorry", sorry_code)
    assert result.status == ProofStatus.OPEN_GOAL_SORRY


@pytest.mark.asyncio
async def test_valid_discharge(runner):
    valid_code = "theorem trivial_eq : 1 = 1 := by rfl"
    result = await runner.verify_proof_script("test_valid", valid_code)
    assert result.status == ProofStatus.SUCCESS_QED
    assert len(result.diagnostics) == 0
