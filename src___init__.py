"""
Pharmaceutical Digital Twin Factory
AI + Quantum-powered digital twin platform for pharmaceutical manufacturing
"""

__version__ = "0.1.0"
__author__ = "PDTF Team"
__email__ = "team@pdtf.ai"

# Import main components for easier access
from .core.digital_twin_orchestrator import (
    DigitalTwinOrchestrator,
    SystemConfiguration,
    SystemMode
)

from .models.molecule_twin import (
    MoleculeTwin,
    MolecularProperty,
    ProcessConditions,
    MolecularState
)

from .quantum.production_simulator import (
    QuantumProductionSimulator,
    ProductionScenario,
    QuantumBackend,
    QuantumState
)

from .ai.quality_forecasting import (
    QualityForecastingEngine,
    QualityMetrics,
    ProcessParameters,
    EnvironmentalData
)

from .regulatory.document_generator import (
    RegulatoryDocumentGenerator,
    DocumentType,
    RegulatoryFramework,
    DocumentMetadata
)

__all__ = [
    # Core
    "DigitalTwinOrchestrator",
    "SystemConfiguration",
    "SystemMode",
    
    # Models
    "MoleculeTwin",
    "MolecularProperty",
    "ProcessConditions",
    "MolecularState",
    
    # Quantum
    "QuantumProductionSimulator",
    "ProductionScenario",
    "QuantumBackend",
    "QuantumState",
    
    # AI
    "QualityForecastingEngine",
    "QualityMetrics",
    "ProcessParameters",
    "EnvironmentalData",
    
    # Regulatory
    "RegulatoryDocumentGenerator",
    "DocumentType",
    "RegulatoryFramework",
    "DocumentMetadata",
]