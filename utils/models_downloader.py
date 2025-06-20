import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.utils import logging as hf_logging

def download_model(model_name: str, cache_dir: str = None):
    hf_logging.set_verbosity_info()
    logger = hf_logging.get_logger("transformers")

    print(f"Downloading model: {model_name}")
    if cache_dir:
        print(f"Using custom cache directory: {cache_dir}")

    # Download tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    print("✅ Tokenizer downloaded.")

    # Download model
    model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=cache_dir)
    print("✅ Model downloaded.")

    print("🎉 Model and tokenizer successfully downloaded and cached.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and cache Hugging Face model")
    parser.add_argument("--model", required=True, help="Model name or path on Hugging Face Hub (e.g., 'mistralai/Mistral-7B-v0.1')")
    parser.add_argument("--cache-dir", default=None, help="Optional custom cache directory")

    args = parser.parse_args()

    download_model(args.model, args.cache_dir)
