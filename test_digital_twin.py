import unittest
from molecule_model import Molecule, Atom, Bond
from quantum_engine import QuantumScenarioSimulator
import numpy as np

class TestMoleculeModel(unittest.TestCase):
    def test_molecule_serialization(self):
        molecule = Molecule(
            name="Aspirin",
            formula="C9H8O4",
            molecular_weight=180.16,
            atoms=[Atom(element="C", x=0.0, y=0.0, z=0.0)],
            bonds=[Bond(atom1=0, atom2=0, type="single")],
            batch_id="BATCH123"
        )
        json_data = molecule.to_json()
        deserialized = Molecule.from_json(json_data)
        self.assertEqual(deserialized.name, "Aspirin")
        self.assertEqual(deserialized.molecular_weight, 180.16)

class TestQuantumSimulator(unittest.TestCase):
    def test_run_simulation(self):
        simulator = QuantumScenarioSimulator(num_qubits=2)
        params = list(np.random.uniform(0, np.pi, 2))
        result = simulator.run_simulation(params)
        self.assertIsInstance(result, dict)
        self.assertTrue(all(isinstance(k, str) and isinstance(v, int) for k, v in result.items()))

if __name__ == "__main__":
    unittest.main()
