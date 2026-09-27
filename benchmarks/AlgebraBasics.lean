import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

open Real

theorem rbf_kernel_symmetry (x y : ℝ) :
    Real.exp (-(x - y)^2) = Real.exp (-(y - x)^2) := by
  have h : (x - y)^2 = (y - x)^2 := by ring
  rw [h]

theorem linear_algebra_goal (x y : ℝ) (h1 : x + y = 5) (h2 : y = 2) : x = 3 := by
  linarith
