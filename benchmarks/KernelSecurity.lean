structure MemoryRegion where
  ownerId : ℕ
  isKernelSpace : Bool

structure KernelState where
  currentDomain : ℕ
  regions : ℕ → MemoryRegion

def writeToAddress (state : KernelState) (addr : ℕ) (caller : ℕ) : Option KernelState :=
  let target := state.regions addr
  if target.isKernelSpace = true ∧ state.currentDomain ≠ 0 then none
  else some state

theorem write_kernel_space_denied (s : KernelState) (addr : ℕ)
    (h1 : s.currentDomain ≠ 0) (h2 : (s.regions addr).isKernelSpace = true) :
    writeToAddress s addr s.currentDomain = none := by
  unfold writeToAddress
  simp [h1, h2]
