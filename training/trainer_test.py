import os
import time
import threading
from datetime import datetime
import logging

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    TrainerCallback,
    DataCollatorForLanguageModeling,
)

# Assume these classes are defined elsewhere in your project
# from your_models_file import Job, ModelInfo, YourConfig

# Configure a basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingManager:
    """
    A class to manage the lifecycle of model training jobs.
    Replace this with your actual class structure.
    """
    def __init__(self, config):
        # In a real app, these would be loaded from a persistent state file
        self.training_jobs = {}
        self.trained_models = {}
        self.active_jobs = 0
        self.config = config # Should contain paths like models_directory
        # self._load_state() # Method to load jobs and models from disk

    def _save_state(self):
        # A placeholder for saving the state of jobs and models
        print("State saved (simulation).")
        pass

    def _start_real_training(self, job_id: str):
        """
        Starts a real model training process in a background thread
        using the Hugging Face Transformers library.
        """
        
        # --- Custom Callback to bridge Trainer with our Job Management System ---
        class JobProgressCallback(TrainerCallback):
            def __init__(self, job):
                self.job = job
                self.job.logs.append("Training callback initialized.")

            def on_train_begin(self, args, state, control, **kwargs):
                self.job.status = 'training'
                self.job.logs.append("Hugging Face Trainer has started the training run.")

            def on_step_begin(self, args, state, control, **kwargs):
                # Check for cancellation signal from the main application
                if self.job.status == 'cancelled':
                    self.job.logs.append("Cancellation signal received. Stopping training.")
                    control.should_training_stop = True

            def on_log(self, args, state, control, logs=None, **kwargs):
                # This is called at each logging step defined in TrainingArguments
                if state.is_local_process_zero:
                    # Update progress percentage
                    progress = (state.global_step / state.max_steps) * 100
                    self.job.progress = int(progress)
                    
                    # Append new logs from the trainer
                    log_entry = f"Step {state.global_step}/{state.max_steps}"
                    if 'loss' in logs:
                        log_entry += f" - Loss: {logs['loss']:.4f}"
                    if 'learning_rate' in logs:
                        log_entry += f" - LR: {logs['learning_rate']:.2e}"
                    self.job.logs.append(log_entry)


        def training_worker():
            """The actual training logic that runs in the background thread."""
            job = self.training_jobs.get(job_id)
            if not job:
                logger.error(f"Job {job_id} not found for training.")
                return

            try:
                # --- 1. SETUP AND INITIALIZATION ---
                job.status = 'initializing'
                job.logs.append("Initializing training environment...")
                self._save_state()

                # Define model output directory
                model_output_dir = os.path.join(self.config.models_directory, job.model_name)
                os.makedirs(model_output_dir, exist_ok=True)

                # --- 2. LOAD TOKENIZER AND MODEL ---
                job.logs.append(f"Loading base model and tokenizer: {job.base_model}...")
                tokenizer = AutoTokenizer.from_pretrained(job.base_model)
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                    
                model = AutoModelForCausalLM.from_pretrained(
                    job.base_model,
                    # For memory efficiency on GPUs, consider quantization:
                    # load_in_8bit=True,
                    # device_map="auto",
                )
                
                # --- 3. LOAD AND PREPARE DATASET ---
                job.logs.append(f"Loading and processing dataset: {job.dataset_path}...")
                
                # Load from the CSV generated earlier
                raw_dataset = load_dataset('csv', data_files={'train': job.dataset_path})['train']

                # Format and tokenize the dataset
                def preprocess_function(examples):
                    # Combine instruction, input, and response into a single string for training
                    formatted_texts = []
                    for instr, inp, resp in zip(examples['Instruction'], examples['Input'], examples['Response']):
                        # Standard Alpaca-style prompt format
                        text = f"### Instruction:\n{instr}\n\n### Input:\n{inp}\n\n### Response:\n{resp}"
                        formatted_texts.append(text)
                    return tokenizer(formatted_texts, truncation=True, padding='max_length', max_length=512)

                tokenized_dataset = raw_dataset.map(preprocess_function, batched=True, remove_columns=raw_dataset.column_names)
                
                # Split into training and validation sets
                train_val_split = tokenized_dataset.train_test_split(test_size=0.1, seed=42)
                train_dataset = train_val_split["train"]
                eval_dataset = train_val_split["test"]

                job.logs.append(f"Dataset processed. Training samples: {len(train_dataset)}, Validation samples: {len(eval_dataset)}")
                
                # --- 4. CONFIGURE TRAINING ARGUMENTS ---
                training_args = TrainingArguments(
                    output_dir=model_output_dir,
                    num_train_epochs=job.epochs,
                    per_device_train_batch_size=4, # Lower this if you run out of VRAM
                    per_device_eval_batch_size=4,  # Lower this if you run out of VRAM
                    gradient_accumulation_steps=2, # Effectively increases batch size
                    warmup_steps=50,
                    weight_decay=0.01,
                    learning_rate=2e-5,
                    logging_dir=os.path.join(model_output_dir, 'logs'),
                    logging_strategy="steps",
                    logging_steps=10, # Log progress every 10 steps
                    evaluation_strategy="epoch", # Evaluate at the end of each epoch
                    save_strategy="epoch",       # Save a checkpoint at the end of each epoch
                    fp16=torch.cuda.is_available(), # Use mixed-precision if a GPU is available
                    load_best_model_at_end=True, # Load the best model based on validation loss
                    metric_for_best_model="loss",
                    report_to="none", # Disable reporting to external services like W&B/TensorBoard
                )
                
                # Data collator for language modeling prepares batches for training
                data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

                trainer = Trainer(
                    model=model,
                    args=training_args,
                    train_dataset=train_dataset,
                    eval_dataset=eval_dataset,
                    tokenizer=tokenizer,
                    data_collator=data_collator,
                    callbacks=[JobProgressCallback(job=job)], # Add our custom callback
                )
                
                # --- 5. START TRAINING ---
                trainer.train()

                # --- 6. FINALIZE, EVALUATE, AND SAVE ---
                job.logs.append("Training process finished. Evaluating final model...")
                final_metrics = trainer.evaluate()
                
                job.logs.append(f"Final evaluation metrics: {final_metrics}")
                job.status = 'completed'
                job.end_time = datetime.now().isoformat()
                job.progress = 100

                # Save the final, best-performing model
                trainer.save_model(model_output_dir)
                job.logs.append(f"Model saved successfully to {model_output_dir}")

                # Create and save final model metadata
                # model_info = ModelInfo(...) # Assuming you have a ModelInfo class
                # self.trained_models[job.model_name] = model_info

            except Exception as e:
                # Handle all exceptions, including cancellation which raises an error
                if job.status == 'cancelled':
                    job.logs.append("Training run was successfully cancelled by the user.")
                else:
                    error_msg = f"Training failed unexpectedly: {str(e)}"
                    job.status = 'failed'
                    job.error_message = str(e)
                    job.logs.append(error_msg)
                    logger.exception(f"Training failed for job {job_id}")

            finally:
                # This block always runs, whether training succeeded, failed, or was cancelled
                self.active_jobs -= 1
                if not job.end_time:
                    job.end_time = datetime.now().isoformat()
                self._save_state()

        # --- Start the worker in a background thread ---
        thread = threading.Thread(target=training_worker)
        thread.daemon = True # Allows the main program to exit even if the thread is running
        thread.start()

