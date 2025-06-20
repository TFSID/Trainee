"""
CVE Analyst API module
"""
import sqlite3
import logging
from typing import Optional
import torch


from config.settings import CVEConfig
from database.models import CVEDatabase
from transformers.utils import logging as hf_logging

logger = logging.getLogger(__name__)
hf_logging.set_verbosity_info()
info_logger = hf_logging.get_logger("transformers")

class CVEAnalystAPI:
    """API untuk CVE analysis menggunakan trained model"""
    
    def __init__(self, config: CVEConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.db = CVEDatabase()
        self.load_model()
    
    def load_model(self):
        """Load trained model"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            model_path = self.config.model_dir / "cve-analyst-model"
            
            if model_path.exists():
                self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                self.model = AutoModelForCausalLM.from_pretrained(
                    str(model_path),
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                logger.info("Trained model loaded successfully")
            else:
                info_logger.info("Trained model not found, loading base model")
                logger.warning("Trained model not found, using base model")
                # Load the base model
                self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(self.config.model_name)

                # Create the model directory if it doesn't exist
                model_path.mkdir(parents=True, exist_ok=True)

                # Save the base model and tokenizer to the new path
                self.tokenizer.save_pretrained(str(model_path))
                self.model.save_pretrained(str(model_path))
                
        except ImportError:
            logger.error("Transformers library not available")
            self.model = None
            self.tokenizer = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.tokenizer = None
    
    def analyze_cve(self, cve_id: str, instruction: str = "Analyze this CVE") -> str:
        """Analyze CVE using trained model"""
        if not self.model or not self.tokenizer:
            return "Model not available. Please check model installation."
        
        # Get CVE data from database
        cve_data = self.db.get_cve(cve_id)
        
        if not cve_data:
            return f"CVE {cve_id} not found in database"
        
        # Format prompt
        prompt = f"""### Instruction:
{instruction}

### Input:
CVE ID: {cve_data['cve_id']}
Description: {cve_data['description']}
Severity: {cve_data['severity']}
CWE: {cve_data['cwe_id']}

### Response:
"""
        
        try:
            # Generate response
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the generated part
            response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error during inference: {e}")
            return f"Error analyzing CVE: {str(e)}"
    
    def get_cve_info(self, cve_id: str) -> Optional[dict]:
        """Get CVE information from database"""
        return self.db.get_cve(cve_id)
    
    def get_recent_cves(self, limit: int = 10) -> list:
        """Get recent CVEs"""
        return self.db.get_recent_cves(limit=limit)
