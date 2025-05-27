#!/bin/bash

# Pharmaceutical Digital Twin Factory - Local Simulation Runner
# This script runs a local simulation of the digital twin system

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Pharmaceutical Digital Twin Factory ===${NC}"
echo -e "${GREEN}Starting local simulation environment...${NC}\n"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import numpy" 2>/dev/null; then
    echo -e "${YELLOW}Dependencies not installed. Installing...${NC}"
    pip install -r requirements.txt
fi

# Set environment variables for simulation mode
export PDTF_MODE="simulation"
export PDTF_LOG_LEVEL="INFO"
export PDTF_DB_HOST="localhost"
export PDTF_DB_PORT="5432"
export PDTF_DB_NAME="pharma_twin_sim"

# Create necessary directories
mkdir -p logs
mkdir -p data/simulations
mkdir -p output/documents
mkdir -p output/reports

# Run the simulation
echo -e "\n${GREEN}Starting Digital Twin simulation...${NC}"
echo -e "${YELLOW}Mode: Local Simulation${NC}"
echo -e "${YELLOW}Quantum Backend: NumPy Simulator${NC}"
echo -e "${YELLOW}AI Models: Ensemble${NC}\n"

# Run the main orchestrator in simulation mode
python -c "
import asyncio
import logging
from src.core.digital_twin_orchestrator import (
    DigitalTwinOrchestrator, 
    SystemConfiguration, 
    SystemMode
)
from src.quantum.production_simulator import QuantumBackend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/simulation.log'),
        logging.StreamHandler()
    ]
)

async def run_simulation():
    # System configuration for local simulation
    config = SystemConfiguration(
        mode=SystemMode.SIMULATION,
        company_name='SimulationCorp',
        facility_id='SIM-FACILITY-001',
        quantum_backend=QuantumBackend.NUMPY_SIMULATOR,
        ai_model_type='ensemble',
        regulatory_frameworks=['FDA', 'EMA', 'ICH'],
        data_refresh_interval=10,  # 10 seconds for simulation
        prediction_horizon_days=30,
        enable_real_time_monitoring=True,
        enable_quantum_optimization=True,
        database_config={
            'host': 'localhost',
            'port': '5432',
            'database': 'pharma_twin_sim'
        },
        api_endpoints={}
    )
    
    # Initialize orchestrator
    print('Initializing Digital Twin System...')
    orchestrator = DigitalTwinOrchestrator(config)
    await orchestrator.initialize_system()
    
    # Create a sample batch
    print('\\nCreating sample batch twin...')
    batch_config = {
        'batch_number': 'SIM-BATCH-001',
        'product_id': 'IBU-001',
        'product_name': 'Ibuprofen 200mg Tablets (Simulation)',
        'batch_size': 100,
        'materials': [
            {
                'name': 'Ibuprofen API',
                'code': 'API-001',
                'quantity': 20,
                'unit': 'kg',
                'smiles': 'CC(C)CC1=CC=C(C=C1)C(C)C(=O)O',
                'lot_number': 'SIM-API-001',
                'manufacturer': 'Simulation Supplier',
                'expiry_date': '2025-12-31'
            },
            {
                'name': 'Microcrystalline Cellulose',
                'code': 'EXC-001',
                'quantity': 60,
                'unit': 'kg',
                'lot_number': 'SIM-EXC-001'
            },
            {
                'name': 'Croscarmellose Sodium',
                'code': 'EXC-002',
                'quantity': 5,
                'unit': 'kg',
                'lot_number': 'SIM-EXC-002'
            },
            {
                'name': 'Magnesium Stearate',
                'code': 'EXC-003',
                'quantity': 2,
                'unit': 'kg',
                'lot_number': 'SIM-EXC-003'
            }
        ],
        'process_steps': [
            {'operation': 'Dispensing', 'parameters': {'temperature': 22, 'humidity': 45}, 'duration': 30},
            {'operation': 'Blending', 'parameters': {'speed': 200, 'time': 15}, 'duration': 15, 'critical': True},
            {'operation': 'Granulation', 'parameters': {'liquid_amount': 10, 'spray_rate': 50}, 'duration': 45, 'critical': True},
            {'operation': 'Drying', 'parameters': {'temperature': 60, 'time': 120}, 'duration': 120, 'critical': True},
            {'operation': 'Sizing', 'parameters': {'mesh_size': 20}, 'duration': 30},
            {'operation': 'Compression', 'parameters': {'force': 15, 'speed': 30}, 'duration': 180, 'critical': True},
            {'operation': 'Coating', 'parameters': {'spray_rate': 100, 'temperature': 40}, 'duration': 90}
        ],
        'quality_targets': {
            'yield': 0.95,
            'purity': 0.995,
            'dissolution': 0.85,
            'hardness': 8.0,
            'friability': 0.5
        },
        'timeline_days': 3
    }
    
    batch_id = await orchestrator.create_batch_twin(batch_config)
    print(f'Created batch twin: {batch_id}')
    
    # Run quantum simulation
    print('\\nRunning quantum production simulation...')
    quantum_result = await orchestrator.run_quantum_simulation(batch_id)
    advantage = quantum_result.get('quantum_advantage_metrics', {}).get('overall_quantum_advantage', 0)
    print(f'Quantum simulation complete!')
    print(f'Quantum advantage achieved: {advantage:.1%}')
    
    # Simulate some processing time
    print('\\nSimulating manufacturing process...')
    await asyncio.sleep(5)
    
    # Get batch status
    status = orchestrator.get_batch_status(batch_id)
    print(f'\\nBatch Status:')
    print(f'  - Status: {status[\"status\"]}')
    print(f'  - Process data points: {status[\"process_data_points\"]}')
    print(f'  - Predictions made: {status[\"predictions_count\"]}')
    print(f'  - Documents generated: {len(status[\"documents_generated\"])}')
    
    # Generate batch record
    print('\\nGenerating batch manufacturing record...')
    from src.regulatory.document_generator import DocumentType
    document = await orchestrator.generate_document(batch_id, DocumentType.BATCH_RECORD)
    print(f'Generated document: {document[\"metadata\"][\"document_id\"]}')
    print(f'Files created: {list(document.get(\"generated_files\", {}).keys())}')
    
    # Get system metrics
    print('\\n=== System Metrics ===')
    metrics = orchestrator.get_system_metrics()
    for key, value in metrics['metrics'].items():
        print(f'  {key}: {value}')
    
    print('\\n✓ Simulation completed successfully!')
    print('\\nCheck the following directories for output:')
    print('  - logs/          : System logs')
    print('  - output/        : Generated documents')
    print('  - data/          : Simulation data')
    
    # Keep running for a bit to show real-time monitoring
    print('\\nReal-time monitoring active for 30 seconds...')
    await asyncio.sleep(30)
    
    # Shutdown
    print('\\nShutting down...')
    await orchestrator.shutdown()

# Run the simulation
asyncio.run(run_simulation())
"

# Check if simulation completed successfully
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Simulation completed successfully!${NC}"
    echo -e "${GREEN}Check the output directory for generated documents.${NC}"
else
    echo -e "\n${RED}✗ Simulation failed. Check logs/simulation.log for details.${NC}"
    exit 1
fi

# Deactivate virtual environment
deactivate

echo -e "\n${GREEN}=== Simulation Complete ===${NC}"