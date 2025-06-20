from config.settings import ModelTrainerConfig
from api.model_trainer_api import ModelTrainerAPI
import gradio as gr
import os

def create_gradio_interface(config: ModelTrainerConfig):
    """Create Gradio interface"""
    api = ModelTrainerAPI(config)

    def validate_dataset_ui(uploaded_file):
        if uploaded_file is None:
            return "error", "No file provided", {}
        success, message, metadata = api.validate_dataset(uploaded_file.name)
        return success, message, metadata

    def start_training_ui(model_name, base_model, dataset_file, lr, batch_size, epochs, max_len, description):
        if None in [model_name, base_model, dataset_file]:
            return "error", "Model name, base model, and dataset are required"
        return api.start_training(
            model_name=model_name,
            base_model=base_model,
            dataset_path=dataset_file.name,
            learning_rate=lr,
            batch_size=batch_size,
            epochs=epochs,
            max_length=max_len,
            description=description or ""
        )

    
    def get_status_ui(job_id):
        return api.get_training_status(job_id)

    def list_models_ui():
        return api.get_trained_models()

    def test_model_ui(model_name, test_input):
        return api.test_model(model_name, test_input)

    def cancel_job_ui(job_id):
        success, msg = api.cancel_training(job_id)
        return msg

    def delete_model_ui(model_name):
        success, msg = api.delete_model(model_name)
        return msg

    def export_model_ui(model_name, export_format):
        success, msg = api.export_model(model_name, export_format)
        return msg

    with gr.Blocks(title="LLM Model Trainer") as demo:
        gr.Markdown("# 🧠 LLM Model Trainer Dashboard")

        with gr.Tab("Dataset Validation"):
            dataset_file = gr.File(label="Upload dataset")
            val_btn = gr.Button("Validate")
            val_status = gr.Label(label="Valid?")
            val_msg = gr.Textbox(label="Message")
            val_meta = gr.JSON(label="Metadata")
            val_btn.click(validate_dataset_ui, inputs=[dataset_file], outputs=[val_status, val_msg, val_meta])

        with gr.Tab("Start Training"):
            name = gr.Textbox(label="Model Name")
            base = gr.Textbox(label="Base Model")
            ds_file = gr.File(label="Dataset file")
            lr = gr.Number(label="Learning Rate", value=config.default_learning_rate)
            bs = gr.Number(label="Batch Size", value=config.default_batch_size)
            ep = gr.Number(label="Epochs", value=config.default_epochs)
            ml = gr.Number(label="Max Length", value=config.max_sequence_length)
            desc = gr.Textbox(label="Description")
            start_btn = gr.Button("Start")
            train_msg = gr.Textbox(label="Response")
            start_btn.click(start_training_ui, inputs=[name, base, ds_file, lr, bs, ep, ml, desc], outputs=[train_msg, train_msg])

        with gr.Tab("Training Status"):
            jid = gr.Textbox(label="Job ID (leave blank for all)")
            status_btn = gr.Button("Get Status")
            status_out = gr.Textbox(label="Status", lines=15)
            status_btn.click(get_status_ui, inputs=[jid], outputs=[status_out])

        with gr.Tab("Trained Models"):
            list_btn = gr.Button("List Models")
            list_out = gr.Textbox(label="Models", lines=15)
            list_btn.click(list_models_ui, inputs=None, outputs=[list_out])

        with gr.Tab("Test Model"):
            test_name = gr.Textbox(label="Model Name")
            test_in = gr.Textbox(label="Input to test")
            test_btn = gr.Button("Test")
            test_out = gr.Textbox(label="Output", lines=15)
            test_btn.click(test_model_ui, inputs=[test_name, test_in], outputs=[test_out])

        with gr.Tab("Manage Jobs/Models"):
            cancel_id = gr.Textbox(label="Cancel Job ID")
            cancel_btn = gr.Button("Cancel Job")
            cancel_out = gr.Textbox(label="Message")
            cancel_btn.click(cancel_job_ui, inputs=[cancel_id], outputs=[cancel_out])

            del_name = gr.Textbox(label="Model Name to delete")
            del_btn = gr.Button("Delete Model")
            del_out = gr.Textbox(label="Message")
            del_btn.click(delete_model_ui, inputs=[del_name], outputs=[del_out])

            exp_name = gr.Textbox(label="Model Name to export")
            exp_fmt = gr.Dropdown(label="Export format", choices=["zip", "tar"], value="zip")
            exp_btn = gr.Button("Export Model")
            exp_out = gr.Textbox(label="Message")
            exp_btn.click(export_model_ui, inputs=[exp_name, exp_fmt], outputs=[exp_out])

    return demo
