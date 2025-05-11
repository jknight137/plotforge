import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import HfFolder

class AIModelold:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"[Model] Loading: {model_name}")
        print(f"[Model] Using device: {self.device}")

        token = HfFolder.get_token()
        if token is None:
            raise RuntimeError("Hugging Face token not found. Run 'huggingface-cli login' first.")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, token=token, trust_remote_code=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
            device_map="auto",
            token=token,
            trust_remote_code=True
        )

        self.model.eval()

    def generate(self, prompt: str, min_words=5000, max_new_tokens=4000, retries=3):
        total_text = ""
        attempts = 0
        start_time = time.time()

        while len(total_text.split()) < min_words and attempts < retries:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.95,
                    top_k=50,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            total_text += " " + text
            prompt = "Continue the above, adding more detail until reaching 5000 words:\n\n" + text
            attempts += 1

        elapsed_time = round(time.time() - start_time, 2)
        word_count = len(total_text.split())

        return total_text.strip(), word_count, elapsed_time
