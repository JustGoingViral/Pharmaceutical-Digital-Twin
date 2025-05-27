"""Tests for the Molecule Twin module"""

import pytest
import numpy as np
from datetime import datetime

from src.models.molecule_twin import (
    MoleculeTwin,
    MolecularState,
    MolecularProperty,
    ProcessConditions
)


class TestMoleculeTwin:
    """Test cases for MoleculeTwin class"""
    
    @pytest.fixture
    def ibuprofen_twin(self):
        """Create an ibuprofen molecule twin for testing"""
        return MoleculeTwin(
            smiles="CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
            name="Ibuprofen",
            cas_number="15687-27-1"
        )
    
    @pytest.fixture
    def standard_conditions(self):
        """Standard process conditions for testing"""
        return ProcessConditions(
            temperature=25.0,
            pressure=1.0,
            ph=7.0,
            humidity=45.0,
            light_exposure=100.0,
            oxygen_level=21.0,
            mixing_speed=200.0,
            reaction_time=30.0
        )
    
    def test_molecule_initialization(self, ibuprofen_twin):
        """Test proper initialization of molecule twin"""
        assert ibuprofen_twin.name == "Ibuprofen"
        assert ibuprofen_twin.smiles == "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
        assert ibuprofen_twin.cas_number == "15687-27-1"
        assert ibuprofen_twin.state == MolecularState.RAW_MATERIAL
        assert isinstance(ibuprofen_twin.id, str)
        assert len(ibuprofen_twin.id) == 16
        assert isinstance(ibuprofen_twin.properties, MolecularProperty)
    
    def test_process_simulation(self, ibuprofen_twin, standard_conditions):
        """Test process step simulation"""
        initial_purity = ibuprofen_twin.quality_metrics.get("purity", 99.9)
        
        # Run simulation
        result = ibuprofen_twin.simulate_process_step(standard_conditions, duration=60)
        
        # Check result structure
        assert "timestamp" in result
        assert "conditions" in result
        assert "duration_minutes" in result
        assert "quality_metrics" in result
        assert "degradation_rate" in result
        
        # Check quality metrics
        assert "purity" in result["quality_metrics"]
        assert "yield" in result["quality_metrics"]
        assert "stability_index" in result["quality_metrics"]
        
        # Purity should decrease slightly
        assert result["quality_metrics"]["purity"] <= initial_purity
        assert result["quality_metrics"]["purity"] > 95.0  # Should still be high quality
        
        # Check process history
        assert len(ibuprofen_twin.process_history) == 1
        assert ibuprofen_twin.process_history[0] == result
    
    def test_degradation_calculation(self, ibuprofen_twin, standard_conditions):
        """Test degradation rate calculations"""
        # Test at reference conditions
        ref_degradation = ibuprofen_twin._calculate_degradation_rate(standard_conditions)
        assert 0 < ref_degradation < 0.1  # Should be low at standard conditions
        
        # Test at elevated temperature
        hot_conditions = ProcessConditions(
            temperature=60.0,  # Much higher temperature
            pressure=standard_conditions.pressure,
            ph=standard_conditions.ph,
            humidity=standard_conditions.humidity,
            light_exposure=standard_conditions.light_exposure,
            oxygen_level=standard_conditions.oxygen_level,
            mixing_speed=standard_conditions.mixing_speed,
            reaction_time=standard_conditions.reaction_time
        )
        hot_degradation = ibuprofen_twin._calculate_degradation_rate(hot_conditions)
        assert hot_degradation > ref_degradation  # Should degrade faster at higher temp
        
        # Test at extreme pH
        extreme_ph_conditions = ProcessConditions(
            temperature=standard_conditions.temperature,
            pressure=standard_conditions.pressure,
            ph=2.0,  # Very acidic
            humidity=standard_conditions.humidity,
            light_exposure=standard_conditions.light_exposure,
            oxygen_level=standard_conditions.oxygen_level,
            mixing_speed=standard_conditions.mixing_speed,
            reaction_time=standard_conditions.reaction_time
        )
        ph_degradation = ibuprofen_twin._calculate_degradation_rate(extreme_ph_conditions)
        assert ph_degradation > ref_degradation  # Should degrade faster at extreme pH
    
    def test_shelf_life_prediction(self, ibuprofen_twin, standard_conditions):
        """Test shelf life prediction"""
        acceptance_criteria = {
            "min_purity": 95.0,
            "min_potency": 90.0
        }
        
        shelf_life_months, stability_profile = ibuprofen_twin.predict_shelf_life(
            standard_conditions,
            acceptance_criteria
        )
        
        # Check shelf life is reasonable
        assert 0 < shelf_life_months < 60  # Between 0 and 5 years
        
        # Check stability profile structure
        assert "predicted_shelf_life_months" in stability_profile
        assert "degradation_rate_per_month" in stability_profile
        assert "stability_index" in stability_profile
        assert "critical_quality_attributes" in stability_profile
        assert "storage_recommendations" in stability_profile
        
        # Check storage recommendations
        assert isinstance(stability_profile["storage_recommendations"], dict)
        assert "temperature" in stability_profile["storage_recommendations"]
        assert "humidity" in stability_profile["storage_recommendations"]
    
    def test_process_efficiency(self, ibuprofen_twin, standard_conditions):
        """Test process efficiency calculations"""
        # Optimal conditions should give high efficiency
        optimal_efficiency = ibuprofen_twin._calculate_process_efficiency(standard_conditions)
        assert 0.9 < optimal_efficiency <= 1.0
        
        # Sub-optimal conditions
        suboptimal_conditions = ProcessConditions(
            temperature=5.0,  # Too cold
            pressure=0.5,  # Too low
            ph=4.0,  # Too acidic
            humidity=90.0,  # Too humid
            light_exposure=1000.0,  # Too bright
            oxygen_level=21.0,
            mixing_speed=50.0,  # Too slow
            reaction_time=30.0
        )
        suboptimal_efficiency = ibuprofen_twin._calculate_process_efficiency(suboptimal_conditions)
        assert suboptimal_efficiency < optimal_efficiency
        assert 0.3 < suboptimal_efficiency < 0.9  # Should still be somewhat functional
    
    def test_stability_index(self, ibuprofen_twin, standard_conditions):
        """Test stability index calculation"""
        stability_index = ibuprofen_twin._calculate_stability_index(standard_conditions)
        
        # Should be high for good conditions
        assert 80 < stability_index <= 100
        
        # Test with poor conditions
        poor_conditions = ProcessConditions(
            temperature=80.0,  # Very hot
            pressure=2.0,  # High pressure
            ph=12.0,  # Very basic
            humidity=95.0,  # Very humid
            light_exposure=10000.0,  # Intense light
            oxygen_level=30.0,  # High oxygen
            mixing_speed=1000.0,  # Very fast mixing
            reaction_time=30.0
        )
        poor_stability = ibuprofen_twin._calculate_stability_index(poor_conditions)
        assert poor_stability < 50  # Should indicate poor stability
    
    def test_chemical_transformation(self, ibuprofen_twin, standard_conditions):
        """Test chemical transformation to create new molecule twin"""
        reagents = ["NaOH", "H2O"]
        
        new_twin = ibuprofen_twin.apply_transformation(
            "hydrolysis",
            reagents,
            standard_conditions
        )
        
        # Check new twin properties
        assert isinstance(new_twin, MoleculeTwin)
        assert new_twin.id != ibuprofen_twin.id
        assert new_twin.state == MolecularState.INTERMEDIATE
        assert "hydrolysis" in new_twin.name
        assert new_twin.properties.molecular_weight > ibuprofen_twin.properties.molecular_weight
        assert len(new_twin.process_history) == 1
        
        # Check transformation record
        transformation = new_twin.process_history[0]
        assert transformation["parent_id"] == ibuprofen_twin.id
        assert transformation["reaction_type"] == "hydrolysis"
        assert transformation["reagents"] == reagents
    
    def test_serialization(self, ibuprofen_twin, standard_conditions):
        """Test molecule twin serialization"""
        # Run some operations first
        ibuprofen_twin.simulate_process_step(standard_conditions, 30)
        
        # Serialize
        data = ibuprofen_twin.to_dict()
        
        # Check structure
        assert isinstance(data, dict)
        assert data["id"] == ibuprofen_twin.id
        assert data["smiles"] == ibuprofen_twin.smiles
        assert data["name"] == ibuprofen_twin.name
        assert data["cas_number"] == ibuprofen_twin.cas_number
        assert data["state"] == ibuprofen_twin.state.value
        assert "properties" in data
        assert "quality_metrics" in data
        assert "process_history" in data
        assert "timestamp" in data
        
        # Check properties are serialized
        assert isinstance(data["properties"], dict)
        assert "molecular_weight" in data["properties"]
        assert "melting_point" in data["properties"]
        assert "solubility" in data["properties"]
    
    def test_multiple_process_steps(self, ibuprofen_twin):
        """Test running multiple process steps"""
        conditions_list = [
            ProcessConditions(temperature=25, pressure=1.0, ph=7.0, humidity=45,
                            light_exposure=100, oxygen_level=21, mixing_speed=200, reaction_time=30),
            ProcessConditions(temperature=30, pressure=1.1, ph=6.5, humidity=50,
                            light_exposure=200, oxygen_level=21, mixing_speed=250, reaction_time=45),
            ProcessConditions(temperature=60, pressure=0.9, ph=7.5, humidity=30,
                            light_exposure=0, oxygen_level=5, mixing_speed=100, reaction_time=120),
        ]
        
        initial_purity = 99.9
        
        for i, conditions in enumerate(conditions_list):
            result = ibuprofen_twin.simulate_process_step(conditions, duration=60)
            
            # Purity should generally decrease
            current_purity = result["quality_metrics"]["purity"]
            assert current_purity <= initial_purity
            
            # Process history should accumulate
            assert len(ibuprofen_twin.process_history) == i + 1
        
        # Final quality should still be acceptable
        final_purity = ibuprofen_twin.quality_metrics["purity"]
        assert final_purity > 90.0  # Still pharmaceutical grade


class TestMolecularProperty:
    """Test cases for MolecularProperty dataclass"""
    
    def test_property_initialization(self):
        """Test MolecularProperty initialization"""
        props = MolecularProperty(
            molecular_weight=206.28,
            melting_point=76.0,
            solubility={"water": 0.021, "ethanol": 200.0},
            stability_profile={"25C_60RH": 8760},  # 1 year
            pka_values=[4.91],
            logp=3.97,
            bioavailability=0.8,
            toxicity_profile={"hERG": 10.5},
            synthesis_complexity=3
        )
        
        assert props.molecular_weight == 206.28
        assert props.melting_point == 76.0
        assert props.solubility["water"] == 0.021
        assert props.solubility["ethanol"] == 200.0
        assert props.pka_values == [4.91]
        assert props.logp == 3.97
        assert props.bioavailability == 0.8
        assert props.synthesis_complexity == 3
    
    def test_property_dict_conversion(self):
        """Test converting properties to dictionary"""
        props = MolecularProperty(
            molecular_weight=206.28,
            melting_point=76.0,
            solubility={"water": 0.021},
            stability_profile={"25C_60RH": 8760},
            pka_values=[4.91],
            logp=3.97,
            bioavailability=0.8,
            toxicity_profile={"hERG": 10.5},
            synthesis_complexity=3
        )
        
        props_dict = props.to_dict()
        assert isinstance(props_dict, dict)
        assert props_dict["molecular_weight"] == 206.28
        assert props_dict["melting_point"] == 76.0
        assert "solubility" in props_dict


class TestProcessConditions:
    """Test cases for ProcessConditions dataclass"""
    
    def test_conditions_initialization(self):
        """Test ProcessConditions initialization"""
        conditions = ProcessConditions(
            temperature=25.0,
            pressure=1.0,
            ph=7.0,
            humidity=45.0,
            light_exposure=100.0,
            oxygen_level=21.0,
            mixing_speed=200.0,
            reaction_time=30.0
        )
        
        assert conditions.temperature == 25.0
        assert conditions.pressure == 1.0
        assert conditions.ph == 7.0
        assert conditions.humidity == 45.0
        assert conditions.light_exposure == 100.0
        assert conditions.oxygen_level == 21.0
        assert conditions.mixing_speed == 200.0
        assert conditions.reaction_time == 30.0
    
    def test_extreme_conditions(self):
        """Test with extreme process conditions"""
        extreme_conditions = ProcessConditions(
            temperature=150.0,  # Very high
            pressure=10.0,  # High pressure
            ph=14.0,  # Maximum pH
            humidity=100.0,  # Saturated
            light_exposure=100000.0,  # Intense UV
            oxygen_level=100.0,  # Pure oxygen
            mixing_speed=10000.0,  # Ultra high speed
            reaction_time=1440.0  # 24 hours
        )
        
        # Should initialize without errors
        assert extreme_conditions.temperature == 150.0
        assert extreme_conditions.ph == 14.0
        assert extreme_conditions.oxygen_level == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])