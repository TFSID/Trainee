"""
Database models and operations for CVE data
"""
import sqlite3
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class CVEDatabase:
    """SQLite database untuk menyimpan data CVE dan metadata"""
    
    def __init__(self, db_path: str = "cve_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # CVE Data Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cve_data (
                    cve_id TEXT PRIMARY KEY,
                    description TEXT,
                    severity REAL,
                    cvss_vector TEXT,
                    published_date TEXT,
                    modified_date TEXT,
                    cwe_id TEXT,
                    references_list TEXT,
                    exploit_available INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Exploits Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exploits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cve_id TEXT,
                    exploit_title TEXT,
                    exploit_code TEXT,
                    source TEXT,
                    date_added TEXT,
                    FOREIGN KEY (cve_id) REFERENCES cve_data (cve_id)
                )
            """)
            
            # Training Data Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    instruction TEXT,
                    input_text TEXT,
                    output_text TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def insert_cve(self, cve_data: Dict):
        """Insert CVE data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO cve_data 
                (cve_id, description, severity, cvss_vector, published_date, 
                 modified_date, cwe_id, references_list, exploit_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cve_data.get('cve_id'),
                cve_data.get('description'),
                cve_data.get('severity'),
                cve_data.get('cvss_vector'),
                cve_data.get('published_date'),
                cve_data.get('modified_date'),
                cve_data.get('cwe_id'),
                json.dumps(cve_data.get('references_list', [])),
                cve_data.get('exploit_available', 0)
            ))
            conn.commit()
    
    def get_cve(self, cve_id: str) -> Optional[Dict]:
        """Get CVE data by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cve_data WHERE cve_id = ?", (cve_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_recent_cves(self, limit: int = 100) -> List[Dict]:
        """Get recent CVEs"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM cve_data 
                ORDER BY published_date DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def insert_exploit(self, exploit_data: Dict):
        """Insert exploit data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO exploits 
                (cve_id, exploit_title, exploit_code, source, date_added)
                VALUES (?, ?, ?, ?, ?)
            """, (
                exploit_data.get('cve_id'),
                exploit_data.get('exploit_title'),
                exploit_data.get('exploit_code'),
                exploit_data.get('source'),
                exploit_data.get('date_added')
            ))
            conn.commit()
    
    def insert_training_data(self, training_data: Dict):
        """Insert training data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO training_data 
                (instruction, input_text, output_text, category)
                VALUES (?, ?, ?, ?)
            """, (
                training_data.get('instruction'),
                training_data.get('input'),
                training_data.get('output'),
                training_data.get('category')
            ))
            conn.commit()
    
    def get_training_data(self) -> pd.DataFrame:
        """Get all training data as DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("SELECT * FROM training_data", conn)
