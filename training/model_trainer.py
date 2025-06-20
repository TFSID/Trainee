"""
Model training module using QLoRA fine-tuning
"""
import json
import logging
from typing import List, Dict, Tuple
from pathlib import Path

from config.settings import CVEConfig

logger = logging.getLogger(__name__)

class CVEModelTrainer:
    """Fine-tune DeepSeek-Coder menggunakan QLoRA"""
    
    def __init__(self, config: CVEConfig):
        self.config = config
        
    def prepare_model_and_tokenizer(self):
        """Setup model dan tokenizer untuk fine-tuning"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            from peft import LoraConfig, TaskType, get_peft_model
            import torch
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model dengan quantization
            model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                load_in_4bit=True
            )
            
            # Setup LoRA config
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=16,
                lora_alpha=32,
                lora_dropout=0.1,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
            )
            
            # Apply LoRA
            model = get_peft_model(model, lora_config)
            
            return model, tokenizer
            
        except ImportError as e:
            logger.error(f"Required libraries not installed: {e}")
            raise
    
    def format_training_data(self, dataset: List[Dict]) -> List[str]:
        """Format data untuk training"""
        formatted_data = []
        
        for item in dataset:
            # Format: Instruction + Input + Output
            prompt = f"""### Instruction:
{item['instruction']}

### Input:
{item['input']}

### Response:
{item['output']}"""
            
            formatted_data.append(prompt)
        
        return formatted_data
    
    def train_model(self, dataset: List[Dict]):
        """Train model dengan dataset"""
        try:
            from datasets import Dataset
            from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
            
            logger.info("Starting model training")
            
            # Prepare model and tokenizer
            model, tokenizer = self.prepare_model_and_tokenizer()
            
            # Format training data
            formatted_data = self.format_training_data(dataset)
            
            # Create dataset
            train_dataset = Dataset.from_dict({"text": formatted_data})
            
            def tokenize_function(examples):
                return tokenizer(
                    examples["text"],
                    truncation=True,
                    padding=True,
                    max_length=self.config.max_length
                )
            
            tokenized_dataset = train_dataset.map(tokenize_function, batched=True)
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=str(self.config.model_dir / "checkpoints"),
                overwrite_output_dir=True,
                num_train_epochs=3,
                per_device_train_batch_size=self.config.batch_size,
                save_steps=500,
                save_total_limit=2,
                prediction_loss_only=True,
                learning_rate=self.config.learning_rate,
                warmup_steps=100,
                logging_steps=50,
                fp16=True,
                dataloader_drop_last=True
            )
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                data_collator=data_collator,
                train_dataset=tokenized_dataset,
            )
            
            # Start training
            trainer.train()
            
            # Save model
            model_save_path = self.config.model_dir / "cve-analyst-model"
            trainer.save_model(str(model_save_path))
            tokenizer.save_pretrained(str(model_save_path))
            
            logger.info(f"Model saved to {model_save_path}")
            
        except ImportError as e:
            logger.error(f"Training libraries not available: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during training: {e}")
            raise
    
    def load_dataset_from_file(self, filepath: str) -> List[Dict]:
        """Load dataset from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
