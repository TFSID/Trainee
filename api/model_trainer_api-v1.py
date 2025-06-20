"""
API module for LLM Model Trainer operations
"""
import os
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import pandas as pd
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@dataclass
class APIResponse:
    success: bool
    message: str
    data: Optional[Dict] = None

@dataclass
class ValidationResponse(APIResponse):
    metadata: Optional[Dict] = None

@dataclass
class TrainingJob:
    """Training job data structure"""
    id: str
    model_name: str
    base_model: str
    dataset_path: str
    status: str  # pending, training, completed, failed, cancelled
    progress: int
    learning_rate: float
    batch_size: int
    epochs: int
    max_length: int
    start_time: str
    end_time: Optional[str] = None
    logs: List[str] = None
    error_message: Optional[str] = None
    model_path: Optional[str] = None
    metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []
        if self.metrics is None:
            self.metrics = {}

@dataclass
class ModelInfo:
    """Trained model information"""
    name: str
    base_model: str
    model_path: str
    training_job_id: str
    created_at: str
    dataset_info: Dict[str, Any]
    performance_metrics: Dict[str, float]
    model_size: int  # in bytes
    description: Optional[str] = None

class ModelTrainerAPI:
    """Main API class for model training operations"""
    
    def __init__(self, config):
        self.config = config
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.trained_models: Dict[str, ModelInfo] = {}
        self.active_jobs = 0
        
        # Load existing jobs and models
        self._load_state()
    
    def _load_state(self):
        """Load existing training jobs and models from disk"""
        try:
            jobs_file = os.path.join(self.config.logs_directory, "training_jobs.json")
            if os.path.exists(jobs_file):
                with open(jobs_file, 'r') as f:
                    jobs_data = json.load(f)
                    for job_data in jobs_data:
                        job = TrainingJob(**job_data)
                        self.training_jobs[job.id] = job
            
            models_file = os.path.join(self.config.models_directory, "trained_models.json")
            if os.path.exists(models_file):
                with open(models_file, 'r') as f:
                    models_data = json.load(f)
                    for model_data in models_data:
                        model = ModelInfo(**model_data)
                        self.trained_models[model.name] = model
                        
        except Exception as e:
            logger.error(f"Error loading state: {e}")
    
    def _save_state(self):
        """Save training jobs and models to disk"""
        try:
            # Save training jobs
            jobs_file = os.path.join(self.config.logs_directory, "training_jobs.json")
            jobs_data = [asdict(job) for job in self.training_jobs.values()]
            with open(jobs_file, 'w') as f:
                json.dump(jobs_data, f, indent=2)
            
            # Save trained models
            models_file = os.path.join(self.config.models_directory, "trained_models.json")
            models_data = [asdict(model) for model in self.trained_models.values()]
            with open(models_file, 'w') as f:
                json.dump(models_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def validate_dataset(self, file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate uploaded dataset and return metadata"""
        if not file_path or not os.path.exists(file_path):
            return False, "File does not exist", {}
        
        try:
            file_size = os.path.getsize(file_path)
            if file_size > self.config.max_file_size:
                return False, f"File too large. Max size: {self.config.max_file_size / 1024 / 1024:.1f}MB", {}
            
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.config.supported_formats:
                return False, f"Unsupported format. Supported: {', '.join(self.config.supported_formats)}", {}
            
            # Analyze dataset
            metadata = self._analyze_dataset(file_path, file_ext)
            
            return True, "Dataset validated successfully", metadata
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", {}
    
    def _analyze_dataset(self, file_path: str, file_ext: str) -> Dict[str, Any]:
        """Analyze dataset and extract metadata"""
        metadata = {
            'file_size': os.path.getsize(file_path),
            'file_format': file_ext,
            'num_samples': 0,
            'columns': [],
            'sample_data': []
        }
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path, nrows=1000)  # Sample first 1000 rows
                metadata['num_samples'] = len(df)
                metadata['columns'] = df.columns.tolist()
                metadata['sample_data'] = df.head(3).to_dict('records')
                
            elif file_ext in ['.json', '.jsonl']:
                with open(file_path, 'r') as f:
                    if file_ext == '.json':
                        data = json.load(f)
                        if isinstance(data, list):
                            metadata['num_samples'] = len(data)
                            metadata['sample_data'] = data[:3]
                    else:  # jsonl
                        lines = f.readlines()[:1000]
                        metadata['num_samples'] = len(lines)
                        sample_data = []
                        for line in lines[:3]:
                            try:
                                sample_data.append(json.loads(line.strip()))
                            except:
                                continue
                        metadata['sample_data'] = sample_data
                        
            elif file_ext == '.txt':
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    metadata['num_samples'] = len(lines)
                    metadata['sample_data'] = lines[:3]
                    
        except Exception as e:
            logger.error(f"Error analyzing dataset: {e}")
            
        return metadata
    
    def start_training(self, model_name: str, base_model: str, dataset_path: str,
                      learning_rate: float, batch_size: int, epochs: int,
                      max_length: int = 2048, description: str = "") -> Tuple[bool, str]:
        """Start model training"""
        
        # Validate inputs
        if not model_name.strip():
            return False, "Model name is required"
        
        if model_name in self.trained_models:
            return False, f"Model '{model_name}' already exists"
        
        if self.active_jobs >= self.config.max_concurrent_jobs:
            return False, f"Maximum concurrent jobs ({self.config.max_concurrent_jobs}) reached"
        
        # Validate dataset
        is_valid, message, dataset_metadata = self.validate_dataset(dataset_path)
        if not is_valid:
            return False, f"Dataset validation failed: {message}"
        
        # Create training job
        job_id = f"job_{int(time.time())}_{len(self.training_jobs)}"
        
        job = TrainingJob(
            id=job_id,
            model_name=model_name,
            base_model=base_model,
            dataset_path=dataset_path,
            status='pending',
            progress=0,
            learning_rate=learning_rate,
            batch_size=batch_size,
            epochs=epochs,
            max_length=max_length,
            start_time=datetime.now().isoformat()
        )
        
        job.logs.append(f"Training job created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        job.logs.append(f"Dataset: {os.path.basename(dataset_path)} ({dataset_metadata.get('num_samples', 0)} samples)")
        
        self.training_jobs[job_id] = job
        self.active_jobs += 1
        
        # Start training (simulate async training)
        self._simulate_training(job_id)
        
        self._save_state()
        
        return True, f"Training started successfully! Job ID: {job_id}"
    
    def _simulate_training(self, job_id: str):
        """Simulate training process (replace with actual training logic)"""
        def training_worker():
            job = self.training_jobs.get(job_id)
            if not job:
                return
            
            try:
                job.status = 'training'
                job.logs.append("Training started...")
                
                # Simulate training progress
                for epoch in range(job.epochs):
                    for step in range(10):  # 10 steps per epoch
                        if job.status == 'cancelled':
                            return
                        
                        time.sleep(0.5)  # Simulate training time
                        progress = ((epoch * 10 + step + 1) / (job.epochs * 10)) * 100
                        job.progress = int(progress)
                        
                        if step % 3 == 0:  # Log every 3 steps
                            job.logs.append(f"Epoch {epoch + 1}/{job.epochs}, Step {step + 1}/10 - Loss: {0.5 - progress/200:.4f}")
                
                # Complete training
                job.status = 'completed'
                job.end_time = datetime.now().isoformat()
                job.progress = 100
                job.logs.append("Training completed successfully!")
                
                # Create model info
                model_path = os.path.join(self.config.models_directory, f"{job.model_name}.model")
                
                model_info = ModelInfo(
                    name=job.model_name,
                    base_model=job.base_model,
                    model_path=model_path,
                    training_job_id=job_id,
                    created_at=job.end_time,
                    dataset_info={'path': job.dataset_path, 'samples': 1000},
                    performance_metrics={'accuracy': 0.95, 'loss': 0.05},
                    model_size=1024 * 1024 * 50,  # 50MB
                    description=f"Custom model trained on {os.path.basename(job.dataset_path)}"
                )
                
                self.trained_models[job.model_name] = model_info
                
                # Simulate saving model file
                with open(model_path, 'w') as f:
                    f.write(f"Model: {job.model_name}\nTrained: {job.end_time}")
                
            except Exception as e:
                job.status = 'failed'
                job.error_message = str(e)
                job.logs.append(f"Training failed: {str(e)}")
                logger.error(f"Training failed for job {job_id}: {e}")
            
            finally:
                self.active_jobs -= 1
                self._save_state()
        
        # Start training in background (in real implementation, use proper async/threading)
        import threading
        thread = threading.Thread(target=training_worker)
        thread.daemon = True
        thread.start()
    
    def get_training_status(self, job_id: Optional[str] = None) -> str:
        """Get training status for specific job or all jobs"""
        if job_id:
            job = self.training_jobs.get(job_id)
            if not job:
                return f"Job {job_id} not found"
            
            status_text = f"**Job {job_id} Status:**\n\n"
            status_text += f"Model: {job.model_name}\n"
            status_text += f"Status: {job.status.title()}\n"
            status_text += f"Progress: {job.progress}%\n"
            status_text += f"Base Model: {job.base_model}\n"
            status_text += f"Started: {job.start_time[:19]}\n"
            
            if job.end_time:
                status_text += f"Completed: {job.end_time[:19]}\n"
            
            if job.error_message:
                status_text += f"Error: {job.error_message}\n"
            
            if job.logs:
                status_text += f"\n**Recent Logs:**\n"
                for log in job.logs[-5:]:  # Show last 5 logs
                    status_text += f"- {log}\n"
            
            return status_text
        
        # Return all jobs status
        if not self.training_jobs:
            return "No training jobs found"
        
        status_text = "**All Training Jobs:**\n\n"
        
        for job in sorted(self.training_jobs.values(), key=lambda x: x.start_time, reverse=True):
            status_text += f"**{job.model_name}** (ID: {job.id})\n"
            status_text += f"- Status: {job.status.title()}\n"
            status_text += f"- Progress: {job.progress}%\n"
            status_text += f"- Base Model: {job.base_model}\n"
            status_text += f"- Started: {job.start_time[:19]}\n"
            
            if job.logs:
                status_text += f"- Latest: {job.logs[-1]}\n"
            
            status_text += "\n"
        
        return status_text
    
    def get_trained_models(self) -> str:
        """Get list of all trained models"""
        if not self.trained_models:
            return "No trained models available"
        
        models_text = "**Trained Models:**\n\n"
        
        for model in sorted(self.trained_models.values(), key=lambda x: x.created_at, reverse=True):
            models_text += f"**{model.name}**\n"
            models_text += f"- Base Model: {model.base_model}\n"
            models_text += f"- Created: {model.created_at[:19]}\n"
            models_text += f"- Size: {model.model_size / 1024 / 1024:.1f} MB\n"
            models_text += f"- Dataset: {os.path.basename(model.dataset_info.get('path', 'Unknown'))}\n"
            
            if model.performance_metrics:
                models_text += f"- Accuracy: {model.performance_metrics.get('accuracy', 0):.2%}\n"
            
            if model.description:
                models_text += f"- Description: {model.description}\n"
            
            models_text += "\n"
        
        return models_text
    
    def test_model(self, model_name: str, test_input: str) -> str:
        """Test a trained model with input"""
        if not model_name or not test_input:
            return "Please provide both model name and test input"
        
        model = self.trained_models.get(model_name)
        if not model:
            return f"Model '{model_name}' not found. Available models: {', '.join(self.trained_models.keys())}"
        
        if not os.path.exists(model.model_path):
            return f"Model file not found at {model.model_path}"
        
        # Simulate model inference
        response_templates = [
            f"Based on my training with {model.base_model}, here's my response to '{test_input}': This is a simulated response that would be generated by your custom trained model.",
            f"Using the patterns learned from your dataset, I interpret '{test_input}' as follows: [Simulated model output based on training data]",
            f"Model '{model_name}' response: Your trained model would process this input and generate contextually appropriate output based on the training data."
        ]
        
        import random
        response = random.choice(response_templates)
        
        result = f"**Model Response from '{model_name}':**\n\n"
        result += f"**Input:** {test_input}\n\n"
        result += f"**Output:** {response}\n\n"
        result += f"**Model Info:**\n"
        result += f"- Base Model: {model.base_model}\n"
        result += f"- Trained: {model.created_at[:19]}\n"
        result += f"- Accuracy: {model.performance_metrics.get('accuracy', 0):.2%}\n"
        
        return result
    
    def cancel_training(self, job_id: str) -> Tuple[bool, str]:
        """Cancel a training job"""
        job = self.training_jobs.get(job_id)
        if not job:
            return False, f"Job {job_id} not found"
        
        if job.status not in ['pending', 'training']:
            return False, f"Cannot cancel job with status: {job.status}"
        
        job.status = 'cancelled'
        job.logs.append(f"Training cancelled at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self._save_state()
        
        return True, f"Training job {job_id} cancelled successfully"
    
    def delete_model(self, model_name: str) -> Tuple[bool, str]:
        """Delete a trained model"""
        model = self.trained_models.get(model_name)
        if not model:
            return False, f"Model '{model_name}' not found"
        
        try:
            # Delete model file
            if os.path.exists(model.model_path):
                os.remove(model.model_path)
            
            # Remove from registry
            del self.trained_models[model_name]
            
            self._save_state()
            
            return True, f"Model '{model_name}' deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting model: {str(e)}"
    
    def export_model(self, model_name: str, export_format: str = 'zip') -> Tuple[bool, str]:
        """Export a trained model"""
        model = self.trained_models.get(model_name)
        if not model:
            return False, f"Model '{model_name}' not found"
        
        try:
            export_path = os.path.join(self.config.models_directory, f"{model_name}_export.{export_format}")
            
            # Simulate export process
            with open(export_path, 'w') as f:
                f.write(f"Exported model: {model_name}\n")
                f.write(f"Export time: {datetime.now().isoformat()}\n")
                f.write(f"Model info: {json.dumps(asdict(model), indent=2)}\n")
            
            return True, f"Model exported to: {export_path}"
            
        except Exception as e:
            return False, f"Export failed: {str(e)}"