from pydantic import BaseModel, Field
from typing import List, Optional
import json

class Atom(BaseModel):
    element: str
    x: float
    y: float
    z: float

class Bond(BaseModel):
    atom1: int
    atom2: int
    type: str

class Molecule(BaseModel):
    name: str
    formula: str
    molecular_weight: float
    atoms: List[Atom]
    bonds: List[Bond]
    batch_id: Optional[str] = Field(default=None, description="Production batch identifier")
    timestamp: Optional[str] = Field(default=None, description="Production or simulation timestamp")

    def to_json(self) -> str:
        return self.json()

    @classmethod
    def from_json(cls, json_str: str):
        return cls.parse_raw(json_str)

# Example usage:
if __name__ == "__main__":
    mol = Molecule(
        name="Aspirin",
        formula="C9H8O4",
        molecular_weight=180.16,
        atoms=[
            Atom(element="C", x=0.0, y=0.0, z=0.0),
            Atom(element="O", x=1.0, y=0.0, z=0.0)
        ],
        bonds=[
            Bond(atom1=0, atom2=1, type="single")
        ],
        batch_id="BATCH20250525"
    )
    print(mol.to_json())
