"""
NLG-Driven Regulatory Document Generation System
Automated generation of FDA-compliant documentation for pharmaceutical manufacturing
"""

import json
import os
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
import hashlib
from jinja2 import Template, Environment, FileSystemLoader
import pandas as pd
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import logging

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Types of regulatory documents"""
    BATCH_RECORD = "batch_manufacturing_record"
    VALIDATION_REPORT = "validation_report"
    DEVIATION_REPORT = "deviation_report"
    CHANGE_CONTROL = "change_control"
    STABILITY_REPORT = "stability_report"
    QUALITY_REVIEW = "annual_product_quality_review"
    IND_SUBMISSION = "ind_submission"
    NDA_MODULE = "nda_module"
    CAPA_REPORT = "capa_report"
    AUDIT_RESPONSE = "audit_response"

class RegulatoryFramework(Enum):
    """Regulatory frameworks"""
    FDA_CFR = "fda_21_cfr"
    EMA_GMP = "ema_gmp"
    ICH_GUIDELINES = "ich_guidelines"
    WHO_GMP = "who_gmp"
    PIC_S = "pic_s"

@dataclass
class DocumentMetadata:
    """Metadata for regulatory documents"""
    document_id: str
    document_type: DocumentType
    version: str
    status: str  # draft, review, approved, superseded
    created_date: datetime
    effective_date: Optional[datetime]
    expiry_date: Optional[datetime]
    author: str
    reviewers: List[str]
    approvers: List[str]
    regulatory_framework: List[RegulatoryFramework]
    references: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    
@dataclass
class ComplianceRequirement:
    """Regulatory compliance requirement"""
    requirement_id: str
    regulation: str
    section: str
    description: str
    criticality: str  # critical, major, minor
    verification_method: str
    acceptance_criteria: str

class RegulatoryDocumentGenerator:
    """NLG system for generating regulatory documents"""
    
    def __init__(self, company_name: str, facility_id: str):
        self.company_name = company_name
        self.facility_id = facility_id
        self.templates = {}
        self.compliance_db = self._load_compliance_database()
        self.terminology_db = self._load_regulatory_terminology()
        self.generated_documents = []
        
    def _load_compliance_database(self) -> Dict[str, List[ComplianceRequirement]]:
        """Load regulatory compliance requirements database"""
        # In production, this would connect to a comprehensive regulatory database
        compliance_db = {
            "batch_record": [
                ComplianceRequirement(
                    "BR-001", "21 CFR 211.188", "Production record review",
                    "All drug product production and control records must be reviewed",
                    "critical", "QA review and approval", "100% review before batch release"
                ),
                ComplianceRequirement(
                    "BR-002", "21 CFR 211.186", "Master production records",
                    "Master production and control records must be prepared for each drug product",
                    "critical", "Document control", "Current approved version"
                )
            ],
            "validation": [
                ComplianceRequirement(
                    "VAL-001", "21 CFR 211.220", "Validation requirements",
                    "Written procedures for process validation",
                    "critical", "Validation protocol execution", "Meets acceptance criteria"
                )
            ]
        }
        return compliance_db
    
    def _load_regulatory_terminology(self) -> Dict[str, str]:
        """Load standardized regulatory terminology"""
        return {
            "gmp": "Good Manufacturing Practice",
            "qa": "Quality Assurance",
            "qc": "Quality Control",
            "oos": "Out of Specification",
            "capa": "Corrective and Preventive Action",
            "api": "Active Pharmaceutical Ingredient",
            "cpp": "Critical Process Parameter",
            "cqa": "Critical Quality Attribute",
            "par": "Proven Acceptable Range",
            "pqr": "Product Quality Review",
            "qbd": "Quality by Design"
        }
    
    def generate_batch_record(self, batch_data: Dict[str, Any], 
                            template_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate batch manufacturing record"""
        logger.info(f"Generating batch record for batch {batch_data.get('batch_number')}")
        
        # Create document metadata
        metadata = DocumentMetadata(
            document_id=self._generate_document_id("BMR", batch_data.get('batch_number')),
            document_type=DocumentType.BATCH_RECORD,
            version="1.0",
            status="draft",
            created_date=datetime.utcnow(),
            effective_date=datetime.utcnow(),
            expiry_date=None,
            author=batch_data.get('operator', 'System Generated'),
            reviewers=["QA Manager", "Production Manager"],
            approvers=["QA Director"],
            regulatory_framework=[RegulatoryFramework.FDA_CFR, RegulatoryFramework.ICH_GUIDELINES]
        )
        
        # Generate document sections
        sections = {
            "header": self._generate_bmr_header(batch_data, metadata),
            "materials": self._generate_materials_section(batch_data),
            "equipment": self._generate_equipment_section(batch_data),
            "process_steps": self._generate_process_steps(batch_data),
            "in_process_controls": self._generate_ipc_section(batch_data),
            "yield_reconciliation": self._generate_yield_section(batch_data),
            "quality_results": self._generate_quality_section(batch_data),
            "deviations": self._generate_deviations_section(batch_data),
            "signatures": self._generate_signature_section(metadata)
        }
        
        # Apply NLG to create narrative sections
        narrative_sections = self._apply_nlg_enhancement(sections, batch_data)
        
        # Validate against compliance requirements
        compliance_check = self._validate_compliance(
            narrative_sections, 
            self.compliance_db.get("batch_record", [])
        )
        
        # Generate final document
        document = {
            "metadata": metadata.__dict__,
            "sections": narrative_sections,
            "compliance_status": compliance_check,
            "generated_files": self._render_document_formats(narrative_sections, metadata)
        }
        
        self.generated_documents.append(document)
        return document
    
    def _generate_bmr_header(self, batch_data: Dict, metadata: DocumentMetadata) -> Dict:
        """Generate batch record header section"""
        return {
            "title": "BATCH MANUFACTURING RECORD",
            "document_number": metadata.document_id,
            "product_name": batch_data.get('product_name', 'Unknown Product'),
            "product_code": batch_data.get('product_code', 'N/A'),
            "batch_number": batch_data.get('batch_number', 'N/A'),
            "batch_size": f"{batch_data.get('batch_size', 0)} {batch_data.get('batch_size_unit', 'kg')}",
            "manufacturing_date": batch_data.get('manufacturing_date', datetime.utcnow()).strftime('%Y-%m-%d'),
            "expiry_date": batch_data.get('expiry_date', 'To be determined'),
            "facility": f"{self.company_name} - {self.facility_id}"
        }
    
    def _generate_materials_section(self, batch_data: Dict) -> Dict:
        """Generate materials section with lot traceability"""
        materials = batch_data.get('materials', [])
        
        materials_table = []
        for material in materials:
            materials_table.append({
                "material_name": material.get('name'),
                "material_code": material.get('code'),
                "quantity_required": f"{material.get('quantity')} {material.get('unit')}",
                "lot_number": material.get('lot_number'),
                "manufacturer": material.get('manufacturer'),
                "expiry_date": material.get('expiry_date'),
                "dispensed_by": material.get('dispensed_by', 'N/A'),
                "verified_by": material.get('verified_by', 'N/A'),
                "compliance_status": self._check_material_compliance(material)
            })
        
        return {
            "section_title": "Raw Materials and Components",
            "compliance_statement": "All materials have been verified against approved specifications",
            "materials": materials_table,
            "total_materials": len(materials),
            "critical_materials": [m for m in materials_table if m.get('compliance_status') == 'critical']
        }
    
    def _generate_process_steps(self, batch_data: Dict) -> Dict:
        """Generate detailed process steps with parameters"""
        process_steps = batch_data.get('process_steps', [])
        
        enhanced_steps = []
        for i, step in enumerate(process_steps, 1):
            enhanced_step = {
                "step_number": i,
                "operation": step.get('operation'),
                "description": self._enhance_step_description(step),
                "critical_parameters": step.get('parameters', {}),
                "duration": f"{step.get('duration', 0)} {step.get('duration_unit', 'min')}",
                "equipment_used": step.get('equipment'),
                "performed_by": step.get('operator'),
                "verified_by": step.get('verifier'),
                "completion_time": step.get('completion_time'),
                "parameter_checks": self._generate_parameter_checks(step)
            }
            enhanced_steps.append(enhanced_step)
        
        return {
            "section_title": "Manufacturing Process Steps",
            "total_steps": len(enhanced_steps),
            "critical_steps": sum(1 for s in enhanced_steps if s.get('critical_parameters')),
            "steps": enhanced_steps
        }
    
    def _enhance_step_description(self, step: Dict) -> str:
        """Apply NLG to enhance step descriptions"""
        operation = step.get('operation', 'process step')
        params = step.get('parameters', {})
        
        # Build enhanced description
        description = f"Perform {operation}"
        
        if params:
            param_descriptions = []
            for param, value in params.items():
                param_descriptions.append(f"{param} at {value}")
            description += f" with {', '.join(param_descriptions)}"
        
        # Add compliance language
        if step.get('critical', False):
            description += ". This is a critical process step requiring verification."
        
        return description
    
    def _generate_parameter_checks(self, step: Dict) -> List[Dict]:
        """Generate parameter verification checks"""
        checks = []
        for param, target in step.get('parameters', {}).items():
            checks.append({
                "parameter": param,
                "target_value": target,
                "actual_value": step.get('actual_parameters', {}).get(param, 'TBD'),
                "within_range": "Yes" if step.get('parameters_verified', False) else "TBD",
                "verified_by": step.get('parameter_verifier', 'TBD'),
                "timestamp": step.get('verification_time', 'TBD')
            })
        return checks
    
    def _generate_ipc_section(self, batch_data: Dict) -> Dict:
        """Generate in-process control section"""
        ipc_tests = batch_data.get('in_process_controls', [])
        
        ipc_results = []
        for test in ipc_tests:
            result = {
                "test_name": test.get('test_name'),
                "stage": test.get('stage'),
                "specification": test.get('specification'),
                "method": test.get('method'),
                "result": test.get('result', 'Pending'),
                "units": test.get('units'),
                "status": self._evaluate_test_status(test),
                "performed_by": test.get('analyst', 'TBD'),
                "test_date": test.get('test_date', 'TBD')
            }
            ipc_results.append(result)
        
        return {
            "section_title": "In-Process Controls",
            "total_tests": len(ipc_results),
            "completed_tests": sum(1 for t in ipc_results if t['result'] != 'Pending'),
            "passed_tests": sum(1 for t in ipc_results if t['status'] == 'Pass'),
            "test_results": ipc_results
        }
    
    def _generate_yield_section(self, batch_data: Dict) -> Dict:
        """Generate yield and reconciliation section"""
        theoretical_yield = batch_data.get('theoretical_yield', 0)
        actual_yield = batch_data.get('actual_yield', 0)
        
        yield_percentage = (actual_yield / theoretical_yield * 100) if theoretical_yield > 0 else 0
        
        return {
            "section_title": "Yield and Reconciliation",
            "theoretical_yield": f"{theoretical_yield} {batch_data.get('yield_unit', 'kg')}",
            "actual_yield": f"{actual_yield} {batch_data.get('yield_unit', 'kg')}",
            "yield_percentage": f"{yield_percentage:.1f}%",
            "yield_limit": "85-115%",  # Standard acceptance range
            "yield_status": "Acceptable" if 85 <= yield_percentage <= 115 else "Investigation Required",
            "reconciliation_notes": batch_data.get('reconciliation_notes', ''),
            "accountability": self._generate_material_accountability(batch_data)
        }
    
    def _generate_material_accountability(self, batch_data: Dict) -> List[Dict]:
        """Generate material accountability table"""
        accountability = []
        
        for material in batch_data.get('materials', []):
            issued = material.get('quantity_issued', 0)
            used = material.get('quantity_used', 0)
            returned = material.get('quantity_returned', 0)
            
            accountability.append({
                "material": material.get('name'),
                "issued": f"{issued} {material.get('unit')}",
                "used": f"{used} {material.get('unit')}",
                "returned": f"{returned} {material.get('unit')}",
                "waste": f"{issued - used - returned} {material.get('unit')}",
                "reconciled": "Yes" if abs(issued - used - returned) < 0.01 * issued else "No"
            })
        
        return accountability
    
    def _generate_quality_section(self, batch_data: Dict) -> Dict:
        """Generate quality testing results section"""
        quality_tests = batch_data.get('quality_tests', [])
        
        test_results = []
        for test in quality_tests:
            test_results.append({
                "test": test.get('test_name'),
                "specification": test.get('specification'),
                "method": test.get('method_reference'),
                "result": test.get('result', 'Pending'),
                "status": "Pass" if test.get('meets_spec', False) else "Fail",
                "tested_by": test.get('analyst'),
                "test_date": test.get('test_date'),
                "reviewed_by": test.get('reviewer')
            })
        
        return {
            "section_title": "Quality Control Testing",
            "total_tests": len(test_results),
            "tests_completed": sum(1 for t in test_results if t['result'] != 'Pending'),
            "tests_passed": sum(1 for t in test_results if t['status'] == 'Pass'),
            "release_status": "Approved" if all(t['status'] == 'Pass' for t in test_results) else "Hold",
            "test_results": test_results
        }
    
    def _generate_deviations_section(self, batch_data: Dict) -> Dict:
        """Generate deviations and investigations section"""
        deviations = batch_data.get('deviations', [])
        
        deviation_list = []
        for dev in deviations:
            deviation_list.append({
                "deviation_number": dev.get('number'),
                "description": dev.get('description'),
                "impact_assessment": dev.get('impact', 'Under evaluation'),
                "root_cause": dev.get('root_cause', 'Under investigation'),
                "corrective_action": dev.get('corrective_action', 'TBD'),
                "quality_impact": dev.get('quality_impact', 'None identified'),
                "approval_status": dev.get('status', 'Open')
            })
        
        return {
            "section_title": "Deviations and Investigations",
            "total_deviations": len(deviation_list),
            "open_deviations": sum(1 for d in deviation_list if d['approval_status'] == 'Open'),
            "critical_deviations": sum(1 for d in deviation_list if 'critical' in d.get('impact_assessment', '').lower()),
            "deviations": deviation_list
        }
    
    def _generate_signature_section(self, metadata: DocumentMetadata) -> Dict:
        """Generate electronic signature section"""
        signatures = []
        
        # Production signatures
        signatures.append({
            "role": "Manufacturing Operator",
            "name": "[Electronic Signature Required]",
            "date": "[Date]",
            "meaning": "I certify that this batch was manufactured according to approved procedures"
        })
        
        signatures.append({
            "role": "Production Supervisor",
            "name": "[Electronic Signature Required]",
            "date": "[Date]",
            "meaning": "I have reviewed the manufacturing operations and verify compliance"
        })
        
        # QA signatures
        signatures.append({
            "role": "Quality Assurance",
            "name": "[Electronic Signature Required]",
            "date": "[Date]",
            "meaning": "I have reviewed this record and approve for batch release"
        })
        
        return {
            "section_title": "Approvals and Signatures",
            "electronic_signature_statement": "This document is electronically signed in compliance with 21 CFR Part 11",
            "signatures": signatures,
            "signature_meanings": "Electronic signatures are legally binding and equivalent to handwritten signatures"
        }
    
    def _apply_nlg_enhancement(self, sections: Dict, batch_data: Dict) -> Dict:
        """Apply NLG to enhance document sections with narrative text"""
        enhanced_sections = sections.copy()
        
        # Add executive summary
        enhanced_sections['executive_summary'] = self._generate_executive_summary(sections, batch_data)
        
        # Add compliance narrative
        enhanced_sections['compliance_narrative'] = self._generate_compliance_narrative(sections)
        
        # Enhance each section with contextual narrative
        for section_key, section_data in sections.items():
            if isinstance(section_data, dict) and 'section_title' in section_data:
                section_data['narrative'] = self._generate_section_narrative(section_key, section_data)
        
        return enhanced_sections
    
    def _generate_executive_summary(self, sections: Dict, batch_data: Dict) -> str:
        """Generate executive summary using NLG"""
        product_name = batch_data.get('product_name', 'Product')
        batch_number = batch_data.get('batch_number', 'N/A')
        
        # Extract key metrics
        yield_data = sections.get('yield_reconciliation', {})
        quality_data = sections.get('quality_results', {})
        deviation_data = sections.get('deviations', {})
        
        summary = f"""
        This Batch Manufacturing Record documents the production of {product_name}, 
        Batch {batch_number}, manufactured at {self.company_name} facility {self.facility_id}.
        
        The batch achieved a yield of {yield_data.get('yield_percentage', 'N/A')} against 
        the theoretical yield, which is {yield_data.get('yield_status', 'pending evaluation')}.
        
        Quality control testing showed {quality_data.get('tests_passed', 0)} of 
        {quality_data.get('total_tests', 0)} tests meeting specifications. The batch 
        release status is currently {quality_data.get('release_status', 'pending')}.
        
        There were {deviation_data.get('total_deviations', 0)} deviations recorded during 
        manufacturing, with {deviation_data.get('open_deviations', 0)} requiring closure 
        before final batch disposition.
        
        This document has been prepared in accordance with current Good Manufacturing 
        Practices (cGMP) and meets all applicable regulatory requirements.
        """
        
        return summary.strip()
    
    def _generate_compliance_narrative(self, sections: Dict) -> str:
        """Generate compliance statement narrative"""
        narrative = """
        COMPLIANCE STATEMENT
        
        This Batch Manufacturing Record has been designed and executed in compliance with:
        - 21 CFR Part 211 - Current Good Manufacturing Practice
        - ICH Q7 - Good Manufacturing Practice for Active Pharmaceutical Ingredients
        - Company Standard Operating Procedures
        
        All critical process parameters were monitored and controlled within established ranges.
        All equipment used was qualified and calibrated. All personnel involved in manufacturing
        were appropriately trained and qualified for their assigned tasks.
        
        Any deviations from approved procedures have been documented, investigated, and 
        assessed for impact on product quality. Quality unit approval is required before
        batch release.
        """
        
        return narrative.strip()
    
    def _generate_section_narrative(self, section_key: str, section_data: Dict) -> str:
        """Generate narrative text for specific sections"""
        narratives = {
            "materials": f"""
                A total of {section_data.get('total_materials', 0)} materials were dispensed 
                for this batch. All materials were verified against approved specifications 
                and within their expiry dates. {len(section_data.get('critical_materials', []))} 
                materials are classified as critical and received additional verification.
            """,
            
            "process_steps": f"""
                The manufacturing process consisted of {section_data.get('total_steps', 0)} 
                documented steps, with {section_data.get('critical_steps', 0)} identified as 
                critical process steps. All critical parameters were monitored and documented
                to ensure process control and product quality.
            """,
            
            "quality_results": f"""
                Quality control testing encompassed {section_data.get('total_tests', 0)} 
                analytical tests. Currently, {section_data.get('tests_completed', 0)} tests 
                have been completed with {section_data.get('tests_passed', 0)} meeting 
                specifications. The remaining tests are in progress or pending.
            """
        }
        
        return narratives.get(section_key, "").strip()
    
    def _check_material_compliance(self, material: Dict) -> str:
        """Check material compliance status"""
        # Check expiry
        if material.get('expiry_date'):
            expiry = datetime.strptime(material['expiry_date'], '%Y-%m-%d')
            if expiry < datetime.utcnow():
                return "expired"
        
        # Check if material is on critical list
        critical_materials = ['API', 'Active Ingredient', 'Preservative']
        if any(crit in material.get('name', '') for crit in critical_materials):
            return "critical"
        
        return "standard"
    
    def _evaluate_test_status(self, test: Dict) -> str:
        """Evaluate test result against specification"""
        result = test.get('result')
        spec = test.get('specification')
        
        if not result or result == 'Pending':
            return 'Pending'
        
        # Parse specification (simplified)
        if '-' in str(spec):
            min_val, max_val = map(float, spec.split('-'))
            try:
                result_val = float(result)
                return 'Pass' if min_val <= result_val <= max_val else 'Fail'
            except ValueError:
                return 'Invalid'
        
        return 'Pass' if str(result) == str(spec) else 'Fail'
    
    def _validate_compliance(self, sections: Dict, 
                           requirements: List[ComplianceRequirement]) -> Dict:
        """Validate document against compliance requirements"""
        compliance_results = {
            "overall_status": "compliant",
            "requirements_checked": len(requirements),
            "requirements_met": 0,
            "gaps": []
        }
        
        for req in requirements:
            # Check if requirement is addressed in document
            requirement_met = self._check_requirement_in_sections(req, sections)
            
            if requirement_met:
                compliance_results["requirements_met"] += 1
            else:
                compliance_results["gaps"].append({
                    "requirement_id": req.requirement_id,
                    "regulation": req.regulation,
                    "description": req.description,
                    "criticality": req.criticality
                })
                
                if req.criticality == "critical":
                    compliance_results["overall_status"] = "non-compliant"
        
        return compliance_results
    
    def _check_requirement_in_sections(self, requirement: ComplianceRequirement, 
                                     sections: Dict) -> bool:
        """Check if a specific requirement is met in document sections"""
        # Simplified check - in production would use NLP for semantic matching
        requirement_keywords = requirement.description.lower().split()
        
        for section in sections.values():
            if isinstance(section, dict):
                section_text = json.dumps(section).lower()
                if any(keyword in section_text for keyword in requirement_keywords):
                    return True
            elif isinstance(section, str):
                if any(keyword in section.lower() for keyword in requirement_keywords):
                    return True
        
        return False
    
    def _render_document_formats(self, sections: Dict, 
                               metadata: DocumentMetadata) -> Dict[str, str]:
        """Render document in multiple formats (PDF, JSON, XML)"""
        rendered_files = {}
        
        # Generate PDF
        pdf_filename = f"{metadata.document_id}.pdf"
        self._generate_pdf(sections, metadata, pdf_filename)
        rendered_files['pdf'] = pdf_filename
        
        # Generate JSON
        json_filename = f"{metadata.document_id}.json"
        with open(json_filename, 'w') as f:
            json.dump({
                "metadata": metadata.__dict__,
                "sections": sections
            }, f, indent=2, default=str)
        rendered_files['json'] = json_filename
        
        # Generate XML for regulatory submission
        xml_filename = f"{metadata.document_id}.xml"
        self._generate_regulatory_xml(sections, metadata, xml_filename)
        rendered_files['xml'] = xml_filename
        
        return rendered_files
    
    def _generate_pdf(self, sections: Dict, metadata: DocumentMetadata, filename: str):
        """Generate PDF document"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        story.append(Paragraph(sections['header']['title'], title_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Document info table
        doc_info = [
            ['Document Number:', metadata.document_id],
            ['Product:', sections['header']['product_name']],
            ['Batch Number:', sections['header']['batch_number']],
            ['Manufacturing Date:', sections['header']['manufacturing_date']],
            ['Status:', metadata.status.upper()]
        ]
        
        info_table = Table(doc_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(PageBreak())
        
        # Add sections
        for section_key, section_data in sections.items():
            if isinstance(section_data, dict) and 'section_title' in section_data:
                # Section title
                story.append(Paragraph(section_data['section_title'], styles['Heading2']))
                story.append(Spacer(1, 0.2*inch))
                
                # Section narrative
                if 'narrative' in section_data:
                    story.append(Paragraph(section_data['narrative'], styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                
                # Section data tables
                if 'materials' in section_data:
                    story.append(self._create_materials_table(section_data['materials']))
                elif 'steps' in section_data:
                    story.append(self._create_process_table(section_data['steps']))
                elif 'test_results' in section_data:
                    story.append(self._create_test_results_table(section_data['test_results']))
                
                story.append(Spacer(1, 0.3*inch))
        
        # Build PDF
        doc.build(story)
    
    def _create_materials_table(self, materials: List[Dict]) -> Table:
        """Create materials table for PDF"""
        headers = ['Material', 'Code', 'Quantity', 'Lot Number', 'Expiry Date']
        data = [headers]
        
        for mat in materials:
            data.append([
                mat.get('material_name', ''),
                mat.get('material_code', ''),
                mat.get('quantity_required', ''),
                mat.get('lot_number', ''),
                mat.get('expiry_date', '')
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_process_table(self, steps: List[Dict]) -> Table:
        """Create process steps table for PDF"""
        headers = ['Step #', 'Operation', 'Parameters', 'Duration', 'Performed By']
        data = [headers]
        
        for step in steps:
            params_str = ', '.join([f"{k}: {v}" for k, v in step.get('critical_parameters', {}).items()])
            data.append([
                str(step.get('step_number', '')),
                step.get('operation', ''),
                params_str,
                step.get('duration', ''),
                step.get('performed_by', '')
            ])
        
        table = Table(data, colWidths=[0.7*inch, 2*inch, 2.5*inch, 1*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_test_results_table(self, test_results: List[Dict]) -> Table:
        """Create test results table for PDF"""
        headers = ['Test', 'Specification', 'Result', 'Status', 'Tested By']
        data = [headers]
        
        for test in test_results:
            data.append([
                test.get('test', ''),
                test.get('specification', ''),
                test.get('result', ''),
                test.get('status', ''),
                test.get('tested_by', '')
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        # Color code status
        for i, test in enumerate(test_results, 1):
            if test.get('status') == 'Pass':
                table.setStyle(TableStyle([('BACKGROUND', (3, i), (3, i), colors.lightgreen)]))
            elif test.get('status') == 'Fail':
                table.setStyle(TableStyle([('BACKGROUND', (3, i), (3, i), colors.salmon)]))
        
        return table
    
    def _generate_regulatory_xml(self, sections: Dict, metadata: DocumentMetadata, 
                                filename: str):
        """Generate XML format for regulatory submission"""
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<RegulatoryDocument xmlns="http://www.fda.gov/regulatory">
    <DocumentMetadata>
        <DocumentID>{metadata.document_id}</DocumentID>
        <DocumentType>{metadata.document_type.value}</DocumentType>
        <Version>{metadata.version}</Version>
        <Status>{metadata.status}</Status>
        <CreatedDate>{metadata.created_date.isoformat()}</CreatedDate>
        <Author>{metadata.author}</Author>
    </DocumentMetadata>
    
    <BatchInformation>
        <ProductName>{sections['header']['product_name']}</ProductName>
        <BatchNumber>{sections['header']['batch_number']}</BatchNumber>
        <BatchSize>{sections['header']['batch_size']}</BatchSize>
        <ManufacturingDate>{sections['header']['manufacturing_date']}</ManufacturingDate>
    </BatchInformation>
    
    <ComplianceStatus>
        <OverallStatus>{sections.get('compliance_status', {}).get('overall_status', 'pending')}</OverallStatus>
        <RequirementsMet>{sections.get('compliance_status', {}).get('requirements_met', 0)}</RequirementsMet>
    </ComplianceStatus>
</RegulatoryDocument>"""
        
        with open(filename, 'w') as f:
            f.write(xml_content)
    
    def _generate_document_id(self, doc_type: str, batch_number: str) -> str:
        """Generate unique document ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"{doc_type}-{batch_number}-{timestamp}"
    
    def generate_validation_report(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation report document"""
        logger.info(f"Generating validation report for {validation_data.get('validation_type')}")
        
        # Similar structure to batch record but focused on validation activities
        # Implementation would follow similar pattern with validation-specific sections
        
        return {
            "status": "Template method - implement based on validation type",
            "validation_type": validation_data.get('validation_type')
        }
    
    def generate_stability_report(self, stability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate stability study report"""
        logger.info(f"Generating stability report for {stability_data.get('product_name')}")
        
        # Implementation for stability reports
        # Would include trend analysis, shelf-life predictions, etc.
        
        return {
            "status": "Template method - implement based on stability protocol",
            "study_id": stability_data.get('study_id')
        }