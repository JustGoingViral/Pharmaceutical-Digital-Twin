"""Simplified quantum scenario simulator avoiding heavy external dependencies."""

from __future__ import annotations

import numpy as np


class QuantumScenarioSimulator:
    """Lightweight stand-in for quantum simulations.

    The original implementation relied on qiskit. To keep tests lightweight and
    self-contained, this version generates pseudo-random measurement counts
    without executing a real quantum circuit.
    """

    def __init__(self, num_qubits: int = 4):
        self.num_qubits = num_qubits

    def run_simulation(self, parameters: list) -> dict:
        """Produce deterministic counts based on supplied parameters."""
        rng = np.random.default_rng(seed=sum(int(p * 1000) for p in parameters))
        states = [format(i, f"0{self.num_qubits}b") for i in range(2 ** self.num_qubits)]
        probs = rng.dirichlet(np.ones(len(states)))
        counts = {state: int(p * 1024) for state, p in zip(states, probs)}
        return counts


if __name__ == "__main__":  # pragma: no cover
    sim = QuantumScenarioSimulator(num_qubits=2)
    params = list(np.random.uniform(0, np.pi, 2))
    print(sim.run_simulation(params))
