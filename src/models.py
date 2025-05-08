from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class AIModel:
    def __init__(self, model_name):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )

    def generate(self, prompt, max_length=500):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_length, do_sample=True)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
