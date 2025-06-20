"""
Training dataset generation module
"""
import json
import pandas as pd
from typing import Dict, List
import logging

from database.models import CVEDatabase
from config.settings import CVEConfig

logger = logging.getLogger(__name__)

class DatasetGenerator:
    """Generate training dataset dalam format instruction"""
    
    def __init__(self, config: CVEConfig):
        self.config = config
        self.db = CVEDatabase()
    
    def generate_instruction_dataset(self) -> List[Dict]:
        """Generate dataset dalam format instruction-input-output"""
        logger.info("Generating instruction dataset")
        
        # Get recent CVEs from database
        recent_cves = self.db.get_recent_cves(limit=1000)
        
        dataset = []
        
        # CVE Analysis Instructions
        for cve_data in recent_cves:
            # Basic CVE analysis
            dataset.append({
                "instruction": "Analyze this CVE and provide a security assessment",
                "input": f"CVE ID: {cve_data['cve_id']}\nDescription: {cve_data['description']}\nSeverity: {cve_data['severity']}",
                "output": self._generate_cve_analysis(cve_data),
                "category": "cve_analysis"
            })
            
            # Risk assessment
            dataset.append({
                "instruction": "Provide a risk assessment for this vulnerability",
                "input": f"CVE: {cve_data['cve_id']}\nCVSS Score: {cve_data['severity']}\nCWE: {cve_data['cwe_id']}",
                "output": self._generate_risk_assessment(cve_data),
                "category": "risk_assessment"
            })
            
            # Mitigation recommendations
            dataset.append({
                "instruction": "Suggest mitigation strategies for this vulnerability",
                "input": f"Vulnerability: {cve_data['description']}\nCWE Type: {cve_data['cwe_id']}",
                "output": self._generate_mitigation_advice(cve_data),
                "category": "mitigation"
            })
        
        # Add threat intelligence and detection rules
        dataset.extend(self._generate_threat_intel_instructions())
        dataset.extend(self._generate_detection_rules_instructions())
        
        logger.info(f"Generated {len(dataset)} instruction samples")
        return dataset
    
    def _generate_cve_analysis(self, cve_data: Dict) -> str:
        """Generate CVE analysis output"""
        severity_level = self._get_severity_level(cve_data['severity'])
        
        return f"""**CVE Analysis for {cve_data['cve_id']}**

**Severity Level**: {severity_level} (CVSS: {cve_data['severity']})

**Summary**: This vulnerability has been classified as {severity_level.lower()} priority based on its CVSS score of {cve_data['severity']}.

**Technical Details**: {cve_data['description'][:200]}...

**Weakness Classification**: {cve_data['cwe_id']}

**Exploitation Risk**: {'High - Exploit code available' if cve_data['exploit_available'] else 'Medium - No public exploits detected'}

**Recommended Actions**:
1. Apply security patches immediately if {severity_level.lower()} priority
2. Monitor for suspicious activity
3. Review system configurations
4. Update detection rules"""
    
    def _generate_risk_assessment(self, cve_data: Dict) -> str:
        """Generate risk assessment"""
        risk_level = self._get_severity_level(cve_data['severity'])
        
        return f"""**Risk Assessment**

**Overall Risk**: {risk_level}
**CVSS Base Score**: {cve_data['severity']}/10.0

**Risk Factors**:
- Severity Score: {cve_data['severity']}
- Exploit Availability: {'Yes' if cve_data['exploit_available'] else 'No'}
- Weakness Type: {cve_data['cwe_id']}

**Business Impact**: 
{risk_level} risk to confidentiality, integrity, and availability of affected systems.

**Likelihood of Exploitation**: 
{'High' if cve_data['exploit_available'] and cve_data['severity'] >= 7.0 else 'Medium' if cve_data['severity'] >= 7.0 else 'Low'}

**Recommendations**:
1. Prioritize patching for {risk_level.lower()} risk vulnerabilities
2. Implement compensating controls if patching is delayed
3. Monitor for indicators of compromise"""
    
    def _generate_mitigation_advice(self, cve_data: Dict) -> str:
        """Generate mitigation advice"""
        return f"""**Mitigation Strategies**

**Immediate Actions**:
1. Apply vendor security patches
2. Implement workarounds if patches unavailable
3. Increase monitoring and logging

**Detection Measures**:
1. Deploy network monitoring rules
2. Update IDS/IPS signatures
3. Enable detailed logging for affected services

**Preventive Controls**:
1. Regular vulnerability scanning
2. Security configuration reviews
3. Access control validation
4. Network segmentation

**Long-term Strategy**:
1. Establish patch management process
2. Implement defense-in-depth architecture
3. Regular security assessments
4. Threat intelligence integration

**Specific Recommendations for {cve_data['cwe_id']}**:
- Implement input validation controls
- Review authentication mechanisms
- Validate access controls
- Monitor for anomalous behavior"""
    
    def _generate_threat_intel_instructions(self) -> List[Dict]:
        """Generate threat intelligence instruction samples"""
        return [
            {
                "instruction": "Analyze this threat intelligence report and extract IOCs",
                "input": "Threat actors are exploiting CVE-2024-XXXX using malicious domains example[.]com and IP 192.168.1.100",
                "output": "**Indicators of Compromise (IOCs)**:\n- Domain: example[.]com\n- IP Address: 192.168.1.100\n- CVE: CVE-2024-XXXX\n\n**Threat Assessment**: Active exploitation detected\n**Recommended Actions**: Block IOCs, monitor for similar patterns",
                "category": "threat_intel"
            },
            {
                "instruction": "Map this attack technique to MITRE ATT&CK framework",
                "input": "Attackers using PowerShell to download and execute malicious payloads",
                "output": "**MITRE ATT&CK Mapping**:\n- Tactic: Execution (TA0002)\n- Technique: PowerShell (T1059.001)\n- Sub-technique: Command and Scripting Interpreter\n\n**Detection Opportunities**: Monitor PowerShell execution, network connections, file creation",
                "category": "attack_mapping"
            }
        ]
    
    def _generate_detection_rules_instructions(self) -> List[Dict]:
        """Generate detection rules instruction samples"""
        return [
            {
                "instruction": "Create a Sigma rule for detecting this attack pattern",
                "input": "SQL injection attempts targeting web applications",
                "output": """title: SQL Injection Detection
id: 12345678-1234-1234-1234-123456789012
status: experimental
description: Detects potential SQL injection attempts
logsource:
    category: webserver
detection:
    selection:
        request|contains:
            - "' OR '1'='1"
            - "UNION SELECT"
            - "'; DROP TABLE"
    condition: selection
falsepositives:
    - Legitimate database queries
level: high""",
                "category": "detection_rules"
            }
        ]
    
    def _get_severity_level(self, severity: float) -> str:
        """Get severity level from CVSS score"""
        if severity >= 9.0:
            return "Critical"
        elif severity >= 7.0:
            return "High"
        elif severity >= 4.0:
            return "Medium"
        else:
            return "Low"
    
    def save_dataset(self, dataset: List[Dict], filename: str = "cve_training_dataset.json"):
        """Save dataset to file"""
        filepath = self.config.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        logger.info(f"Dataset saved to {filepath}")
