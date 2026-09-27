import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.Ring

def sumFirstN : ℕ → ℕ
  | 0 => 0
  | n + 1 => (n + 1) + sumFirstN n

theorem sum_first_n_eq (n : ℕ) : 2 * sumFirstN n = n * (n + 1) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    dsimp [sumFirstN]
    have h : 2 * (n + 1 + sumFirstN n) = 2 * (n + 1) + 2 * sumFirstN n := by ring
    rw [h, ih]
    ring
