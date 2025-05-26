"""
Molecule-Level Digital Twin Model
Handles molecular structure simulation and property prediction
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import hashlib
import json
from datetime import datetime

class MolecularState(Enum):
    """Possible states of a molecule in the manufacturing process"""
    RAW_MATERIAL = "raw_material"
    INTERMEDIATE = "intermediate"
    ACTIVE_PHARMACEUTICAL_INGREDIENT = "api"
    EXCIPIENT = "excipient"
    FINAL_PRODUCT = "final_product"
    DEGRADED = "degraded"

@dataclass
class MolecularProperty:
    """Properties of a molecule relevant to pharmaceutical manufacturing"""
    molecular_weight: float
    melting_point: float  # Celsius
    solubility: Dict[str, float]  # Solvent -> g/L
    stability_profile: Dict[str, float]  # Condition -> half-life in hours
    pka_values: List[float]
    logp: float  # Partition coefficient
    bioavailability: float  # 0-1 scale
    toxicity_profile: Dict[str, float]  # Target -> IC50
    synthesis_complexity: int  # 1-10 scale

@dataclass
class ProcessConditions:
    """Manufacturing process conditions"""
    temperature: float  # Celsius
    pressure: float  # Bar
    ph: float
    humidity: float  # Percentage
    light_exposure: float  # Lux
    oxygen_level: float  # Percentage
    mixing_speed: float  # RPM
    reaction_time: float  # Minutes

class MoleculeTwin:
    """Digital twin for pharmaceutical molecules"""
    
    def __init__(self, smiles: str, name: str, cas_number: Optional[str] = None):
        self.smiles = smiles
        self.name = name
        self.cas_number = cas_number
        self.id = self._generate_id()
        self.state = MolecularState.RAW_MATERIAL
        self.properties = self._initialize_properties()
        self.process_history: List[Dict] = []
        self.quality_metrics: Dict[str, float] = {}
        self.stability_data: List[Dict] = []
        
    def _generate_id(self) -> str:
        """Generate unique ID for the molecule twin"""
        data = f"{self.smiles}_{self.name}_{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _initialize_properties(self) -> MolecularProperty:
        """Initialize molecular properties (in real implementation, would use cheminformatics)"""
        # Placeholder - in production, integrate with RDKit or similar
        return MolecularProperty(
            molecular_weight=np.random.uniform(150, 500),
            melting_point=np.random.uniform(50, 250),
            solubility={"water": np.random.uniform(0.1, 100), "ethanol": np.random.uniform(1, 500)},
            stability_profile={"25C_60RH": np.random.uniform(720, 8760)},  # hours
            pka_values=[np.random.uniform(2, 12) for _ in range(np.random.randint(1, 3))],
            logp=np.random.uniform(-2, 5),
            bioavailability=np.random.uniform(0.1, 0.9),
            toxicity_profile={"hERG": np.random.uniform(0.1, 100)},
            synthesis_complexity=np.random.randint(1, 10)
        )
    
    def simulate_process_step(self, conditions: ProcessConditions, duration: float) -> Dict:
        """Simulate the effect of a process step on the molecule"""
        initial_purity = self.quality_metrics.get("purity", 99.9)
        initial_yield = self.quality_metrics.get("yield", 100.0)
        
        # Stability-based degradation model
        degradation_rate = self._calculate_degradation_rate(conditions)
        purity_loss = degradation_rate * duration / 60  # Convert to hours
        
        # Process efficiency model
        efficiency = self._calculate_process_efficiency(conditions)
        yield_factor = efficiency * (1 - purity_loss / 100)
        
        # Update quality metrics
        self.quality_metrics["purity"] = max(0, initial_purity - purity_loss)
        self.quality_metrics["yield"] = initial_yield * yield_factor
        self.quality_metrics["stability_index"] = self._calculate_stability_index(conditions)
        
        # Log process step
        process_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "conditions": conditions.__dict__,
            "duration_minutes": duration,
            "quality_metrics": self.quality_metrics.copy(),
            "degradation_rate": degradation_rate
        }
        self.process_history.append(process_record)
        
        return process_record
    
    def _calculate_degradation_rate(self, conditions: ProcessConditions) -> float:
        """Calculate degradation rate based on Arrhenius equation and stress factors"""
        # Simplified Arrhenius model
        reference_temp = 25.0  # Celsius
        activation_energy = 80000  # J/mol (typical for drug degradation)
        gas_constant = 8.314  # J/(mol·K)
        
        # Temperature factor
        temp_k = conditions.temperature + 273.15
        ref_temp_k = reference_temp + 273.15
        temp_factor = np.exp(activation_energy / gas_constant * (1/ref_temp_k - 1/temp_k))
        
        # pH factor (assuming optimal pH of 7)
        ph_factor = 1 + 0.1 * abs(conditions.ph - 7)
        
        # Humidity factor
        humidity_factor = 1 + 0.01 * (conditions.humidity - 60) if conditions.humidity > 60 else 1
        
        # Light factor
        light_factor = 1 + 0.0001 * conditions.light_exposure
        
        # Combined degradation rate (% per hour)
        base_rate = 0.01  # 0.01% per hour at reference conditions
        return base_rate * temp_factor * ph_factor * humidity_factor * light_factor
    
    def _calculate_process_efficiency(self, conditions: ProcessConditions) -> float:
        """Calculate process efficiency based on conditions"""
        # Optimal ranges for pharmaceutical processing
        optimal_ranges = {
            "temperature": (20, 25),
            "pressure": (0.9, 1.1),
            "ph": (6.5, 7.5),
            "humidity": (40, 60),
            "mixing_speed": (100, 300)
        }
        
        efficiency = 1.0
        
        # Temperature efficiency
        if not optimal_ranges["temperature"][0] <= conditions.temperature <= optimal_ranges["temperature"][1]:
            temp_deviation = min(
                abs(conditions.temperature - optimal_ranges["temperature"][0]),
                abs(conditions.temperature - optimal_ranges["temperature"][1])
            )
            efficiency *= max(0.5, 1 - 0.02 * temp_deviation)
        
        # pH efficiency
        if not optimal_ranges["ph"][0] <= conditions.ph <= optimal_ranges["ph"][1]:
            ph_deviation = min(
                abs(conditions.ph - optimal_ranges["ph"][0]),
                abs(conditions.ph - optimal_ranges["ph"][1])
            )
            efficiency *= max(0.6, 1 - 0.1 * ph_deviation)
        
        # Mixing efficiency
        if conditions.mixing_speed < optimal_ranges["mixing_speed"][0]:
            efficiency *= 0.8
        elif conditions.mixing_speed > optimal_ranges["mixing_speed"][1]:
            efficiency *= 0.9
        
        return efficiency
    
    def _calculate_stability_index(self, conditions: ProcessConditions) -> float:
        """Calculate stability index (0-100) based on current conditions"""
        degradation_rate = self._calculate_degradation_rate(conditions)
        
        # Convert degradation rate to stability index
        # 0.01% per hour = stability index of 95
        # 0.1% per hour = stability index of 50
        # 1% per hour = stability index of 0
        if degradation_rate <= 0.01:
            return 95 + 5 * (0.01 - degradation_rate) / 0.01
        elif degradation_rate <= 0.1:
            return 50 + 45 * (0.1 - degradation_rate) / 0.09
        else:
            return max(0, 50 * (1 - degradation_rate) / 0.9)
    
    def predict_shelf_life(self, storage_conditions: ProcessConditions, 
                          acceptance_criteria: Dict[str, float]) -> Tuple[float, Dict]:
        """Predict shelf life based on storage conditions and acceptance criteria"""
        current_purity = self.quality_metrics.get("purity", 99.9)
        min_acceptable_purity = acceptance_criteria.get("min_purity", 95.0)
        
        degradation_rate = self._calculate_degradation_rate(storage_conditions)
        
        # Calculate time to reach minimum acceptable purity
        if degradation_rate > 0:
            shelf_life_hours = (current_purity - min_acceptable_purity) / degradation_rate
            shelf_life_months = shelf_life_hours / (24 * 30)
        else:
            shelf_life_months = 36  # Maximum 3 years if no degradation
        
        # Generate stability profile
        stability_profile = {
            "predicted_shelf_life_months": round(shelf_life_months, 1),
            "degradation_rate_per_month": degradation_rate * 24 * 30,
            "stability_index": self._calculate_stability_index(storage_conditions),
            "critical_quality_attributes": {
                "purity": {
                    "initial": current_purity,
                    "predicted_at_expiry": min_acceptable_purity,
                    "rate_of_change": -degradation_rate
                }
            },
            "storage_recommendations": self._generate_storage_recommendations(storage_conditions)
        }
        
        return shelf_life_months, stability_profile
    
    def _generate_storage_recommendations(self, conditions: ProcessConditions) -> Dict:
        """Generate storage recommendations based on stability data"""
        recommendations = {
            "temperature": "Store at 2-8°C" if conditions.temperature > 25 else "Store at controlled room temperature",
            "humidity": "Store in tight container" if conditions.humidity > 60 else "Normal storage",
            "light": "Protect from light" if conditions.light_exposure > 100 else "No special light protection needed",
            "packaging": "Use moisture-barrier packaging" if conditions.humidity > 70 else "Standard packaging acceptable"
        }
        return recommendations
    
    def to_dict(self) -> Dict:
        """Convert molecule twin to dictionary for serialization"""
        return {
            "id": self.id,
            "smiles": self.smiles,
            "name": self.name,
            "cas_number": self.cas_number,
            "state": self.state.value,
            "properties": {
                "molecular_weight": self.properties.molecular_weight,
                "melting_point": self.properties.melting_point,
                "solubility": self.properties.solubility,
                "stability_profile": self.properties.stability_profile,
                "pka_values": self.properties.pka_values,
                "logp": self.properties.logp,
                "bioavailability": self.properties.bioavailability,
                "toxicity_profile": self.properties.toxicity_profile,
                "synthesis_complexity": self.properties.synthesis_complexity
            },
            "quality_metrics": self.quality_metrics,
            "process_history": self.process_history[-10:],  # Last 10 process steps
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def apply_transformation(self, reaction_type: str, reagents: List[str], 
                           conditions: ProcessConditions) -> 'MoleculeTwin':
        """Apply chemical transformation and create new molecule twin"""
        # In production, this would use reaction prediction models
        # For now, create a modified version
        new_smiles = f"{self.smiles}_modified_{reaction_type}"
        new_name = f"{self.name}_{reaction_type}_product"
        
        new_twin = MoleculeTwin(new_smiles, new_name)
        new_twin.state = MolecularState.INTERMEDIATE
        
        # Transfer some properties with modifications
        new_twin.properties.molecular_weight = self.properties.molecular_weight * 1.1
        new_twin.properties.synthesis_complexity = min(10, self.properties.synthesis_complexity + 1)
        
        # Log transformation
        transformation_record = {
            "parent_id": self.id,
            "reaction_type": reaction_type,
            "reagents": reagents,
            "conditions": conditions.__dict__,
            "timestamp": datetime.utcnow().isoformat()
        }
        new_twin.process_history.append(transformation_record)
        
        return new_twin