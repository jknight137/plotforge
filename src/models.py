from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from huggingface_hub import HfFolder

class AIModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"Loading model: {model_name}")
        print(f"Using device: {self.device}")

        # Retrieve the token from the Hugging Face CLI
        token = HfFolder.get_token()
        if token is None:
            raise RuntimeError("Hugging Face token not found. Please run 'huggingface-cli login'.")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                token=token,
                trust_remote_code=True
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto",
                token=token,
                trust_remote_code=True
            )

            self.model.eval()
        except Exception as e:
            raise RuntimeError(f"Failed to load model '{model_name}': {e}")
