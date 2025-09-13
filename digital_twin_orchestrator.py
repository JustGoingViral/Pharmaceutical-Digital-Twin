"""
Pharmaceutical Digital Twin Orchestrator
Main system coordinator that integrates all components
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd

from external_data_ingestion import (
    fetch_openprescribing,
    fetch_openfda,
    map_prescribing_data,
    map_fda_data,
    schedule_sync,
)
from scenario_ui import ScenarioToggle
from report_exporter import export_fda_report

# Import all digital twin components
from models.molecule_twin import MoleculeTwin, ProcessConditions, MolecularState
from quantum.production_simulator import (
    QuantumProductionSimulator, 
    ProductionScenario,
    QuantumBackend
)
from ai.quality_forecasting import (
    QualityForecastingEngine,
    QualityMetrics,
    ProcessParameters,
    EnvironmentalData
)
from regulatory.document_generator import (
    RegulatoryDocumentGenerator,
    DocumentType
)
from simulation_report import export_fda_simulation_report

logger = logging.getLogger(__name__)

class SystemMode(Enum):
    """Operating modes for the digital twin system"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    VALIDATION = "validation"
    SIMULATION = "simulation"
    REAL_TIME = "real_time"

@dataclass
class SystemConfiguration:
    """System-wide configuration"""
    mode: SystemMode
    company_name: str
    facility_id: str
    quantum_backend: QuantumBackend
    ai_model_type: str
    regulatory_frameworks: List[str]
    data_refresh_interval: int  # seconds
    prediction_horizon_days: int
    enable_real_time_monitoring: bool
    enable_quantum_optimization: bool
    database_config: Dict[str, str]
    api_endpoints: Dict[str, str]
    prescribing_sync_interval: int = 24 * 3600
    fda_sync_interval: int = 7 * 24 * 3600
    scenario_inputs: Optional[Dict[str, bool]] = None

class DigitalTwinOrchestrator:
    """Main orchestrator for the Pharmaceutical Digital Twin system"""
    
    def __init__(self, config: SystemConfiguration):
        self.config = config
        self.molecule_twins: Dict[str, MoleculeTwin] = {}
        self.quantum_simulator = QuantumProductionSimulator(config.quantum_backend)
        self.quality_engines: Dict[str, QualityForecastingEngine] = {}
        self.doc_generator = RegulatoryDocumentGenerator(
            config.company_name,
            config.facility_id
        )
        self.active_batches: Dict[str, Dict] = {}
        self.scenario_toggle = ScenarioToggle(**(config.scenario_inputs or {}))
        self.external_data: List[Dict[str, Any]] = []
        self.system_metrics = {
            "batches_processed": 0,
            "predictions_made": 0,
            "documents_generated": 0,
            "quantum_simulations_run": 0
        }
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._running = False
        
    async def initialize_system(self):
        """Initialize all system components"""
        logger.info(f"Initializing Digital Twin System in {self.config.mode.value} mode")
        
        # Load existing molecule library
        await self._load_molecule_library()
        
        # Initialize quality models
        await self._initialize_quality_models()
        
        # Connect to data sources
        await self._connect_data_sources()
        
        # Start monitoring if enabled
        if self.config.enable_real_time_monitoring:
            asyncio.create_task(self._monitoring_loop())
        
        self._running = True
        logger.info("Digital Twin System initialized successfully")
    
    async def _load_molecule_library(self):
        """Load molecule library from database"""
        # In production, this would load from a chemical database
        # For now, create some example molecules
        example_molecules = [
            ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", "Ibuprofen", "15687-27-1"),
            ("CC(=O)NC1=CC=C(C=C1)O", "Acetaminophen", "103-90-2"),
            ("CC(C)(C)NCC(C1=CC(=C(C=C1)O)O)O", "Salbutamol", "18559-94-9")
        ]
        
        for smiles, name, cas in example_molecules:
            twin = MoleculeTwin(smiles, name, cas)
            self.molecule_twins[twin.id] = twin
            
        logger.info(f"Loaded {len(self.molecule_twins)} molecules into library")
    
    async def _initialize_quality_models(self):
        """Initialize AI quality forecasting models"""
        # In production, would load pre-trained models
        # For now, create engines for common products
        products = ["IBU-001", "ACET-001", "SALB-001"]
        
        for product_id in products:
            engine = QualityForecastingEngine(product_id, self.config.ai_model_type)
            self.quality_engines[product_id] = engine
            
        logger.info(f"Initialized {len(self.quality_engines)} quality forecasting engines")
    
    async def _connect_data_sources(self):
        """Connect to real-time data sources"""
        # Connect to:
        # - Manufacturing Execution System (MES)
        # - Laboratory Information Management System (LIMS)
        # - Enterprise Resource Planning (ERP)
        # - IoT sensors
        # - Quality Management System (QMS)
        # Schedule external data synchronisation
        try:
            schedule_sync(
                timedelta(seconds=self.config.prescribing_sync_interval),
                fetch_openprescribing,
                map_prescribing_data,
                self._handle_external_data,
                self.config.api_endpoints.get("openprescribing_ccg", "10Q"),
                self.config.api_endpoints.get("openprescribing_measure", "quantity"),
            )
            schedule_sync(
                timedelta(seconds=self.config.fda_sync_interval),
                fetch_openfda,
                map_fda_data,
                self._handle_external_data,
                self.config.api_endpoints.get("openfda_drug", "ibuprofen"),
            )
        except Exception as exc:
            logger.warning(f"Failed to schedule external data sync: {exc}")

        logger.info("Connected to data sources")

    def _handle_external_data(self, payload: Dict[str, Any]) -> None:
        """Store mapped external data payloads."""

        self.external_data.append(payload)

    def toggle_scenario_input(self, key: str) -> None:
        """Toggle scenario inputs such as pricing, utilization or policy."""

        self.scenario_toggle.toggle(key)

    def export_simulation_report(self, data: Dict[str, Any], path: str) -> Dict[str, str]:
        """Export simulation results in FDA-friendly formats."""

        return export_fda_report(data, path)
    
    async def create_batch_twin(self, batch_config: Dict[str, Any]) -> str:
        """Create a new batch digital twin"""
        batch_id = batch_config.get('batch_number')
        product_id = batch_config.get('product_id')
        
        logger.info(f"Creating digital twin for batch {batch_id}")
        
        # Initialize batch twin
        batch_twin = {
            "batch_id": batch_id,
            "product_id": product_id,
            "status": "initialized",
            "created_at": datetime.utcnow(),
            "molecule_twins": [],
            "process_data": {},
            "quality_data": {},
            "predictions": {},
            "documents": {}
        }
        
        # Create molecule twins for batch components
        for material in batch_config.get('materials', []):
            if material.get('smiles'):
                mol_twin = MoleculeTwin(
                    material['smiles'],
                    material['name'],
                    material.get('cas_number')
                )
                batch_twin['molecule_twins'].append(mol_twin.id)
                self.molecule_twins[mol_twin.id] = mol_twin
        
        # Store batch twin
        self.active_batches[batch_id] = batch_twin
        
        # Start monitoring
        if self.config.enable_real_time_monitoring:
            asyncio.create_task(self._monitor_batch(batch_id))
        
        self.system_metrics["batches_processed"] += 1
        
        return batch_id
    
    async def _monitor_batch(self, batch_id: str):
        """Monitor a batch in real-time"""
        batch = self.active_batches.get(batch_id)
        if not batch:
            return
        
        while batch['status'] not in ['completed', 'failed', 'cancelled']:
            try:
                # Collect real-time data
                process_data = await self._collect_process_data(batch_id)
                environmental_data = await self._collect_environmental_data(batch_id)
                
                # Update batch twin
                batch['process_data'].update(process_data)
                
                # Run quality predictions
                if batch['product_id'] in self.quality_engines:
                    prediction = await self._run_quality_prediction(
                        batch_id,
                        process_data,
                        environmental_data
                    )
                    batch['predictions'][datetime.utcnow().isoformat()] = prediction
                
                # Check for deviations
                deviations = await self._check_deviations(batch_id, process_data)
                if deviations:
                    await self._handle_deviations(batch_id, deviations)
                
                # Wait for next cycle
                await asyncio.sleep(self.config.data_refresh_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring batch {batch_id}: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_process_data(self, batch_id: str) -> Dict:
        """Collect real-time process data"""
        # In production, this would interface with MES/SCADA systems
        # Simulate data collection
        return {
            "temperature": np.random.normal(25, 0.5),
            "pressure": np.random.normal(1.0, 0.02),
            "humidity": np.random.normal(45, 2),
            "mixing_speed": np.random.normal(200, 5),
            "ph": np.random.normal(7.0, 0.1),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _collect_environmental_data(self, batch_id: str) -> EnvironmentalData:
        """Collect environmental monitoring data"""
        # Simulate environmental data
        return EnvironmentalData(
            room_temperature=np.random.normal(22, 0.5),
            room_humidity=np.random.normal(40, 2),
            room_pressure_differential=np.random.normal(15, 1),
            particulate_count_05um=int(np.random.normal(1000, 100)),
            particulate_count_5um=int(np.random.normal(10, 2)),
            air_changes_per_hour=np.random.normal(20, 1),
            operator_count=np.random.randint(2, 6),
            shift="day"
        )
    
    async def _run_quality_prediction(self, batch_id: str, 
                                    process_data: Dict,
                                    environmental_data: EnvironmentalData) -> Dict:
        """Run AI quality prediction"""
        batch = self.active_batches[batch_id]
        engine = self.quality_engines.get(batch['product_id'])
        
        if not engine or not engine.is_trained:
            # Train model if needed (in production, models would be pre-trained)
            historical_data = await self._get_historical_data(batch['product_id'])
            if len(historical_data) > 100:
                specs = await self._get_quality_specifications(batch['product_id'])
                engine.train(historical_data, specs)
        
        # Prepare process parameters
        process_params = ProcessParameters(
            temperature=process_data.get('temperature', 25),
            pressure=process_data.get('pressure', 1.0),
            humidity=process_data.get('humidity', 45),
            mixing_speed=process_data.get('mixing_speed', 200),
            mixing_time=process_data.get('mixing_time', 30),
            drying_temperature=process_data.get('drying_temperature', 60),
            drying_time=process_data.get('drying_time', 120),
            granulation_liquid_amount=process_data.get('granulation_liquid', 10),
            compression_force=process_data.get('compression_force', 15),
            coating_spray_rate=process_data.get('coating_spray_rate', 50),
            air_flow_rate=process_data.get('air_flow_rate', 1000)
        )
        
        # Get current quality if available
        current_quality = None
        if batch.get('quality_data'):
            latest_quality = batch['quality_data'].get('latest')
            if latest_quality:
                current_quality = QualityMetrics(**latest_quality)
        
        # Run prediction
        prediction = engine.predict(
            process_params,
            environmental_data,
            current_quality,
            self.config.prediction_horizon_days
        )
        
        self.system_metrics["predictions_made"] += 1
        
        return prediction
    
    async def run_quantum_simulation(self, batch_id: str, 
                                   simulation_params: Optional[Dict] = None) -> Dict:
        """Run quantum simulation for production optimization"""
        batch = self.active_batches.get(batch_id)
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")
        
        logger.info(f"Running quantum simulation for batch {batch_id}")
        
        # Prepare production scenario
        scenario = ProductionScenario(
            batch_size=batch.get('batch_size', 100),
            target_molecule=batch.get('product_name', 'Unknown'),
            starting_materials=[
                {"name": mat['name'], "quantity": mat['quantity']}
                for mat in batch.get('materials', [])
            ],
            process_steps=batch.get('process_steps', []),
            equipment_constraints=batch.get('equipment_constraints', {}),
            quality_targets=batch.get('quality_targets', {
                "yield": 0.95,
                "purity": 0.99,
                "dissolution": 0.85
            }),
            regulatory_requirements=["FDA", "cGMP", "ICH"],
            timeline_days=batch.get('timeline_days', 3)
        )
        
        # Run quantum simulation
        if self.config.enable_quantum_optimization:
            simulation_result = self.quantum_simulator.simulate_production_scenario(
                scenario,
                num_shots=simulation_params.get('num_shots', 1000) if simulation_params else 1000
            )

            # Store results
            batch['quantum_simulation'] = simulation_result

            # Export FDA-friendly report
            try:
                report_prefix = os.path.join("output", "reports", f"quantum_sim_{batch_id}")
                report_files = export_fda_simulation_report(simulation_result, report_prefix)
                simulation_result["fda_report_files"] = report_files
            except Exception as exc:
                logger.error(f"Failed to export simulation report: {exc}")

            # Apply optimizations if quantum advantage achieved
            if simulation_result['quantum_advantage_metrics']['achieves_quantum_advantage']:
                await self._apply_quantum_optimizations(batch_id, simulation_result)
            
            self.system_metrics["quantum_simulations_run"] += 1
        else:
            simulation_result = {
                "status": "Quantum optimization disabled",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return simulation_result
    
    async def _apply_quantum_optimizations(self, batch_id: str, simulation_result: Dict):
        """Apply optimizations from quantum simulation"""
        batch = self.active_batches[batch_id]
        recommendations = simulation_result.get('production_recommendations', [])
        
        for rec in recommendations:
            if rec['priority'] == 'high':
                logger.info(f"Applying quantum optimization: {rec['recommendation']}")
                # In production, this would interface with MES to adjust parameters
                
                # Log optimization
                batch.setdefault('optimizations_applied', []).append({
                    "source": "quantum_simulation",
                    "recommendation": rec['recommendation'],
                    "applied_at": datetime.utcnow().isoformat(),
                    "expected_improvement": rec.get('expected_improvement')
                })
    
    async def _check_deviations(self, batch_id: str, process_data: Dict) -> List[Dict]:
        """Check for process deviations"""
        deviations = []
        
        # Define acceptable ranges
        limits = {
            "temperature": (20, 30),
            "pressure": (0.9, 1.1),
            "humidity": (30, 60),
            "ph": (6.5, 7.5)
        }
        
        for param, (min_val, max_val) in limits.items():
            value = process_data.get(param)
            if value and (value < min_val or value > max_val):
                deviations.append({
                    "parameter": param,
                    "value": value,
                    "limit_low": min_val,
                    "limit_high": max_val,
                    "severity": "critical" if abs(value - (min_val + max_val)/2) > (max_val - min_val) else "minor",
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return deviations
    
    async def _handle_deviations(self, batch_id: str, deviations: List[Dict]):
        """Handle detected deviations"""
        batch = self.active_batches[batch_id]
        
        for deviation in deviations:
            logger.warning(f"Deviation detected in batch {batch_id}: {deviation}")
            
            # Store deviation
            batch.setdefault('deviations', []).append(deviation)
            
            # Generate deviation report if critical
            if deviation['severity'] == 'critical':
                doc = await self.generate_document(
                    batch_id,
                    DocumentType.DEVIATION_REPORT,
                    {"deviation": deviation}
                )
                
                # Trigger alerts
                await self._send_alert(batch_id, deviation)
    
    async def generate_document(self, batch_id: str, 
                              doc_type: DocumentType,
                              additional_data: Optional[Dict] = None) -> Dict:
        """Generate regulatory document"""
        batch = self.active_batches.get(batch_id)
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")
        
        logger.info(f"Generating {doc_type.value} for batch {batch_id}")
        
        # Prepare document data
        doc_data = {
            "batch_number": batch_id,
            "product_name": batch.get('product_name', 'Unknown'),
            "product_code": batch.get('product_id'),
            "batch_size": batch.get('batch_size', 100),
            "batch_size_unit": "kg",
            "manufacturing_date": batch.get('created_at', datetime.utcnow()),
            "materials": batch.get('materials', []),
            "process_steps": batch.get('process_steps', []),
            "in_process_controls": batch.get('in_process_controls', []),
            "quality_tests": batch.get('quality_tests', []),
            "actual_yield": batch.get('actual_yield', 0),
            "theoretical_yield": batch.get('theoretical_yield', 100),
            "deviations": batch.get('deviations', [])
        }
        
        if additional_data:
            doc_data.update(additional_data)
        
        # Generate document based on type
        if doc_type == DocumentType.BATCH_RECORD:
            document = self.doc_generator.generate_batch_record(doc_data)
        elif doc_type == DocumentType.DEVIATION_REPORT:
            document = self.doc_generator.generate_deviation_report(doc_data)
        elif doc_type == DocumentType.STABILITY_REPORT:
            document = self.doc_generator.generate_stability_report(doc_data)
        else:
            raise ValueError(f"Document type {doc_type} not implemented")
        
        # Store document reference
        batch.setdefault('documents', {})[doc_type.value] = {
            "document_id": document['metadata']['document_id'],
            "generated_at": datetime.utcnow().isoformat(),
            "files": document.get('generated_files', {})
        }
        
        self.system_metrics["documents_generated"] += 1
        
        return document
    
    async def _get_historical_data(self, product_id: str) -> pd.DataFrame:
        """Get historical batch data for training"""
        # In production, this would query historical database
        # Generate synthetic data for demonstration
        
        num_batches = 500
        dates = pd.date_range(end=datetime.utcnow(), periods=num_batches, freq='D')
        
        data = {
            'timestamp': dates,
            'batch_id': [f"BATCH-{i:05d}" for i in range(num_batches)],
            'temperature': np.random.normal(25, 0.5, num_batches),
            'pressure': np.random.normal(1.0, 0.02, num_batches),
            'humidity': np.random.normal(45, 2, num_batches),
            'mixing_speed': np.random.normal(200, 5, num_batches),
            'mixing_time': np.random.normal(30, 2, num_batches),
            'drying_temperature': np.random.normal(60, 2, num_batches),
            'drying_time': np.random.normal(120, 5, num_batches),
            'granulation_liquid_amount': np.random.normal(10, 0.5, num_batches),
            'compression_force': np.random.normal(15, 0.5, num_batches),
            'coating_spray_rate': np.random.normal(50, 2, num_batches),
            'air_flow_rate': np.random.normal(1000, 20, num_batches),
            'room_temperature': np.random.normal(22, 0.5, num_batches),
            'room_humidity': np.random.normal(40, 2, num_batches),
            'room_pressure_differential': np.random.normal(15, 1, num_batches),
            'particulate_count_05um': np.random.normal(1000, 100, num_batches),
            'particulate_count_5um': np.random.normal(10, 2, num_batches),
            'air_changes_per_hour': np.random.normal(20, 1, num_batches),
            'operator_count': np.random.randint(2, 6, num_batches),
            'day': [d.day for d in dates],
            'month': [d.month for d in dates],
            'weekday': [d.weekday() for d in dates],
            'hour': np.random.randint(0, 24, num_batches),
            'quality_purity': np.random.normal(99.5, 0.2, num_batches),
            'quality_potency': np.random.normal(100, 1, num_batches),
            'quality_dissolution_rate': np.random.normal(85, 2, num_batches),
            'quality_moisture_content': np.random.normal(2, 0.2, num_batches),
            'quality_particle_size_d50': np.random.normal(100, 5, num_batches),
            'quality_particle_size_d90': np.random.normal(200, 10, num_batches),
            'quality_impurity_total': np.random.normal(0.5, 0.1, num_batches),
            'quality_ph': np.random.normal(7.0, 0.1, num_batches)
        }
        
        return pd.DataFrame(data)
    
    async def _get_quality_specifications(self, product_id: str) -> Dict[str, Tuple[float, float]]:
        """Get quality specifications for product"""
        # In production, this would come from product master data
        return {
            "purity": (98.0, 100.0),
            "potency": (95.0, 105.0),
            "dissolution_rate": (80.0, 100.0),
            "moisture_content": (0.0, 4.0),
            "particle_size_d50": (50.0, 150.0),
            "particle_size_d90": (100.0, 300.0),
            "impurity_total": (0.0, 2.0),
            "ph": (6.5, 7.5)
        }
    
    async def _send_alert(self, batch_id: str, deviation: Dict):
        """Send alert for critical deviations"""
        alert_message = f"""
        CRITICAL DEVIATION ALERT
        
        Batch: {batch_id}
        Parameter: {deviation['parameter']}
        Value: {deviation['value']}
        Limits: {deviation['limit_low']} - {deviation['limit_high']}
        Time: {deviation['timestamp']}
        
        Immediate action required.
        """
        
        # In production, this would send emails, SMS, or push notifications
        logger.critical(alert_message)
    
    async def _monitoring_loop(self):
        """Main monitoring loop for real-time operations"""
        while self._running:
            try:
                # Monitor system health
                await self._check_system_health()
                
                # Process pending tasks
                await self._process_pending_tasks()
                
                # Generate periodic reports
                if datetime.utcnow().hour == 0:  # Daily reports at midnight
                    await self._generate_daily_reports()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _check_system_health(self):
        """Check overall system health"""
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_batches": len(self.active_batches),
            "system_metrics": self.system_metrics,
            "component_status": {
                "quantum_simulator": "online" if self.quantum_simulator else "offline",
                "quality_engines": f"{len(self.quality_engines)} active",
                "document_generator": "online" if self.doc_generator else "offline"
            }
        }
        
        logger.debug(f"System health: {health_status}")
    
    async def _process_pending_tasks(self):
        """Process any pending system tasks"""
        # Check for batches needing document generation
        for batch_id, batch in self.active_batches.items():
            if batch['status'] == 'completed' and DocumentType.BATCH_RECORD.value not in batch.get('documents', {}):
                await self.generate_document(batch_id, DocumentType.BATCH_RECORD)
    
    async def _generate_daily_reports(self):
        """Generate daily summary reports"""
        logger.info("Generating daily reports")
        
        # Collect daily metrics
        daily_summary = {
            "date": datetime.utcnow().date().isoformat(),
            "batches_active": len(self.active_batches),
            "batches_completed": sum(1 for b in self.active_batches.values() if b['status'] == 'completed'),
            "predictions_made": self.system_metrics["predictions_made"],
            "documents_generated": self.system_metrics["documents_generated"],
            "quantum_simulations": self.system_metrics["quantum_simulations_run"],
            "critical_deviations": sum(
                len([d for d in b.get('deviations', []) if d['severity'] == 'critical'])
                for b in self.active_batches.values()
            )
        }
        
        # Store or send daily report
        logger.info(f"Daily summary: {daily_summary}")
    
    def get_batch_status(self, batch_id: str) -> Dict:
        """Get current status of a batch"""
        batch = self.active_batches.get(batch_id)
        if not batch:
            return {"error": f"Batch {batch_id} not found"}
        
        return {
            "batch_id": batch_id,
            "status": batch['status'],
            "created_at": batch['created_at'].isoformat(),
            "molecule_count": len(batch['molecule_twins']),
            "process_data_points": len(batch.get('process_data', {})),
            "predictions_count": len(batch.get('predictions', {})),
            "documents_generated": list(batch.get('documents', {}).keys()),
            "deviations_count": len(batch.get('deviations', [])),
            "quantum_optimization": "applied" if batch.get('quantum_simulation') else "not applied"
        }
    
    def get_system_metrics(self) -> Dict:
        """Get overall system metrics"""
        return {
            "system_mode": self.config.mode.value,
            "uptime": "active" if self._running else "stopped",
            "metrics": self.system_metrics,
            "active_batches": len(self.active_batches),
            "molecule_library_size": len(self.molecule_twins),
            "quality_models_count": len(self.quality_engines)
        }
    
    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("Shutting down Digital Twin System")
        self._running = False
        
        # Save state
        await self._save_system_state()
        
        # Close connections
        self.executor.shutdown(wait=True)
        
        logger.info("Digital Twin System shutdown complete")
    
    async def _save_system_state(self):
        """Save current system state"""
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_batches": {
                batch_id: {
                    "status": batch['status'],
                    "created_at": batch['created_at'].isoformat()
                }
                for batch_id, batch in self.active_batches.items()
            },
            "system_metrics": self.system_metrics
        }
        
        # In production, this would save to persistent storage
        with open('system_state.json', 'w') as f:
            json.dump(state, f, indent=2)


async def main():
    """Example usage of the Digital Twin System"""
    
    # System configuration
    config = SystemConfiguration(
        mode=SystemMode.SIMULATION,
        company_name="PharmaCorp",
        facility_id="FACILITY-001",
        quantum_backend=QuantumBackend.NUMPY_SIMULATOR,
        ai_model_type="ensemble",
        regulatory_frameworks=["FDA", "EMA", "ICH"],
        data_refresh_interval=30,  # 30 seconds
        prediction_horizon_days=30,
        enable_real_time_monitoring=True,
        enable_quantum_optimization=True,
        database_config={
            "host": "localhost",
            "port": "5432",
            "database": "pharma_twin"
        },
        api_endpoints={
            "mes": "http://mes.internal/api",
            "lims": "http://lims.internal/api",
            "erp": "http://erp.internal/api"
        }
    )
    
    # Initialize orchestrator
    orchestrator = DigitalTwinOrchestrator(config)
    await orchestrator.initialize_system()
    
    # Create a batch twin
    batch_config = {
        "batch_number": "BATCH-2024-001",
        "product_id": "IBU-001",
        "product_name": "Ibuprofen 200mg Tablets",
        "batch_size": 100,
        "materials": [
            {
                "name": "Ibuprofen API",
                "code": "API-001",
                "quantity": 20,
                "unit": "kg",
                "smiles": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
                "lot_number": "API-LOT-2024-001",
                "manufacturer": "API Supplier Inc",
                "expiry_date": "2025-12-31"
            },
            {
                "name": "Microcrystalline Cellulose",
                "code": "EXC-001",
                "quantity": 60,
                "unit": "kg",
                "lot_number": "EXC-LOT-2024-001"
            }
        ],
        "process_steps": [
            {
                "operation": "Dispensing",
                "parameters": {"temperature": 22, "humidity": 45},
                "duration": 30,
                "critical": False
            },
            {
                "operation": "Blending",
                "parameters": {"speed": 200, "time": 15},
                "duration": 15,
                "critical": True
            },
            {
                "operation": "Granulation",
                "parameters": {"liquid_amount": 10, "spray_rate": 50},
                "duration": 45,
                "critical": True
            },
            {
                "operation": "Drying",
                "parameters": {"temperature": 60, "time": 120},
                "duration": 120,
                "critical": True
            },
            {
                "operation": "Compression",
                "parameters": {"force": 15, "speed": 30},
                "duration": 180,
                "critical": True
            }
        ],
        "quality_targets": {
            "yield": 0.95,
            "purity": 0.995,
            "dissolution": 0.85
        },
        "timeline_days": 3
    }
    
    batch_id = await orchestrator.create_batch_twin(batch_config)
    print(f"Created batch twin: {batch_id}")
    
    # Run quantum simulation
    quantum_result = await orchestrator.run_quantum_simulation(batch_id)
    print(f"Quantum simulation complete: {quantum_result.get('quantum_advantage_metrics', {}).get('overall_quantum_advantage', 0):.2%} advantage")
    
    # Simulate some processing time
    await asyncio.sleep(5)
    
    # Get batch status
    status = orchestrator.get_batch_status(batch_id)
    print(f"Batch status: {status}")
    
    # Get system metrics
    metrics = orchestrator.get_system_metrics()
    print(f"System metrics: {metrics}")
    
    # Generate batch record
    document = await orchestrator.generate_document(batch_id, DocumentType.BATCH_RECORD)
    print(f"Generated document: {document['metadata']['document_id']}")
    
    # Shutdown
    await orchestrator.shutdown()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the example
    asyncio.run(main())