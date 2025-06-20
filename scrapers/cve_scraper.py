"""
CVE data scraping module
"""
import requests
import pandas as pd
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List
import logging

from database.models import CVEDatabase
from config.settings import CVEConfig

logger = logging.getLogger(__name__)

class CVEScraper:
    """Scraper untuk mengumpulkan data CVE dari berbagai sumber"""
    
    def __init__(self, config: CVEConfig):
        self.config = config
        self.db = CVEDatabase()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CVE-Analyst-Bot/1.0'
        })
    
    async def scrape_nvd_cves(self, days_back: int = 7) -> List[Dict]:
        """Scrape CVE data dari NVD"""
        logger.info(f"Scraping NVD CVEs for last {days_back} days")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        params = {
            'pubStartDate': start_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
            'pubEndDate': end_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
            'resultsPerPage': 2000
        }
        
        if self.config.nvd_api_key:
            self.session.headers['apiKey'] = self.config.nvd_api_key
        
        try:
            response = self.session.get(self.config.nvd_base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            cves = []
            for vuln in data.get('vulnerabilities', []):
                cve = vuln.get('cve', {})
                cve_data = {
                    'cve_id': cve.get('id'),
                    'description': self._extract_description(cve),
                    'severity': self._extract_severity(vuln),
                    'cvss_vector': self._extract_cvss_vector(vuln),
                    'published_date': cve.get('published'),
                    'modified_date': cve.get('lastModified'),
                    'cwe_id': self._extract_cwe(cve),
                    'references': self._extract_references(cve)
                }
                cves.append(cve_data)
                self.db.insert_cve(cve_data)
            
            logger.info(f"Scraped {len(cves)} CVEs from NVD")
            return cves
            
        except Exception as e:
            logger.error(f"Error scraping NVD: {e}")
            return []
    
    def scrape_exploit_db(self) -> List[Dict]:
        """Scrape exploit database"""
        logger.info("Scraping Exploit Database")
        
        try:
            response = self.session.get(self.config.exploit_db_url)
            response.raise_for_status()
            
            # Parse CSV content
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            exploits = []
            for _, row in df.iterrows():
                if pd.notna(row.get('cve')):
                    exploit_data = {
                        'cve_id': row.get('cve'),
                        'exploit_title': row.get('description'),
                        'exploit_code': row.get('file'),
                        'source': 'exploit-db',
                        'date_added': row.get('date')
                    }
                    exploits.append(exploit_data)
                    self.db.insert_exploit(exploit_data)
            
            logger.info(f"Scraped {len(exploits)} exploits")
            return exploits
            
        except Exception as e:
            logger.error(f"Error scraping Exploit DB: {e}")
            return []
    
    def scrape_mitre_attack(self) -> Dict:
        """Scrape MITRE ATT&CK framework data"""
        logger.info("Scraping MITRE ATT&CK data")
        
        attack_url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        
        try:
            response = self.session.get(attack_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error scraping MITRE ATT&CK: {e}")
            return {}
    
    def _extract_description(self, cve: Dict) -> str:
        """Extract description from CVE data"""
        descriptions = cve.get('descriptions', [])
        for desc in descriptions:
            if desc.get('lang') == 'en':
                return desc.get('value', '')
        return ''
    
    def _extract_severity(self, vuln: Dict) -> float:
        """Extract CVSS severity score"""
        metrics = vuln.get('metrics', {})
        for metric_type in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
            if metric_type in metrics:
                metric_data = metrics[metric_type][0]
                return metric_data.get('cvssData', {}).get('baseScore', 0.0)
        return 0.0
    
    def _extract_cvss_vector(self, vuln: Dict) -> str:
        """Extract CVSS vector string"""
        metrics = vuln.get('metrics', {})
        for metric_type in ['cvssMetricV31', 'cvssMetricV30']:
            if metric_type in metrics:
                metric_data = metrics[metric_type][0]
                return metric_data.get('cvssData', {}).get('vectorString', '')
        return ''
    
    def _extract_cwe(self, cve: Dict) -> str:
        """Extract CWE ID"""
        weaknesses = cve.get('weaknesses', [])
        for weakness in weaknesses:
            descriptions = weakness.get('description', [])
            for desc in descriptions:
                if desc.get('lang') == 'en':
                    return desc.get('value', '')
        return ''
    
    def _extract_references(self, cve: Dict) -> List[str]:
        """Extract reference URLs"""
        references = cve.get('references', [])
        return [ref.get('url', '') for ref in references]
