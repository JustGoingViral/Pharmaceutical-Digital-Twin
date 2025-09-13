"""Simplified quantum scenario simulator avoiding heavy external dependencies."""

from __future__ import annotations

from typing import Dict, List
import numpy as np


class QuantumScenarioSimulator:
    """Lightweight stand-in for quantum simulations.

    The original implementation relied on qiskit. To keep tests lightweight and
    self-contained, this version generates pseudo-random measurement counts
    without executing a real quantum circuit.
    """

    def __init__(self, num_qubits: int = 4, shots: int = 1024):
        if num_qubits <= 0:
            raise ValueError("num_qubits must be positive")
        if shots <= 0:
            raise ValueError("shots must be positive")
        self.num_qubits = num_qubits
        self.shots = shots

    def run_simulation(self, parameters: List[float]) -> Dict[str, int]:
        """Produce deterministic counts based on supplied parameters.

        Args:
            parameters: List of floats representing adjustable parameters.
                        Length may differ from num_qubits; only the provided
                        values are used to seed the RNG.

        Returns:
            Mapping from bitstring state to integer counts that sum to `shots`.
        """
        # Deterministic seed based on rounded parameters to stabilize across platforms
        seed = hash(tuple(round(float(p), 6) for p in parameters)) & 0xFFFFFFFF
        rng = np.random.default_rng(seed=seed)

        # Enumerate computational basis states
        states = [format(i, f"0{self.num_qubits}b") for i in range(2 ** self.num_qubits)]

        # Random probability simplex and multinomial sampling to ensure sum == shots
        probs = rng.dirichlet(np.ones(len(states)))
        counts_array = rng.multinomial(self.shots, probs)

        return {state: int(count) for state, count in zip(states, counts_array)}


if __name__ == "__main__":  # pragma: no cover
    sim = QuantumScenarioSimulator(num_qubits=2, shots=1024)
    params = list(np.random.uniform(0, np.pi, 2))
    print(sim.run_simulation(params))
