import time
import os
import ollama
import openai
from dotenv import load_dotenv
load_dotenv()

class AIModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.is_openai = model_name.startswith("gpt-")
        if self.is_openai:
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print(f"[Model] Using model: {model_name} ({'OpenAI' if self.is_openai else 'Ollama'})")

    def generate(self, prompt: str, min_words=1000, max_tokens=3072, tail_words=300):
        start_time = time.time()

        if prompt.strip().endswith("### CONTINUE"):
            body = prompt.replace("### CONTINUE", "").strip()
            context = self._get_tail(body, tail_words)
            full_prompt = (
                f"The current story is continuing. Recent context:\n\n"
                f"{context}\n\n"
                "Continue writing the next section of the chapter, keeping style, tone, and narrative flow consistent."
            )
        else:
            full_prompt = (
                "You are an expert fiction author. Write the beginning of a novel chapter in a compelling, immersive style.\n\n"
                f"{prompt}"
            )

        try:
            if self.is_openai:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a fiction-writing assistant."},
                        {"role": "user", "content": full_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.9
                )
                text = response.choices[0].message.content.strip()
                usage = response.usage
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens

                print(f"[OpenAI Usage] Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")
                with open("openai_usage.log", "a", encoding="utf-8") as log:
                    log.write(f"{time.ctime()} - {self.model_name} - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}\n")


            else:
                response = ollama.generate(
                    model=self.model_name,
                    prompt=full_prompt,
                    stream=False,
                    options={"num_predict": max_tokens}
                )
                text = response.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"[Model Error] Generation failed: {e}")

        elapsed = round(time.time() - start_time, 2)
        word_count = len(text.split())

        if word_count < min_words:
            print(f"[Warning] Only {word_count} words generated (target was {min_words})")

        return text, word_count, elapsed

    def _get_tail(self, text, word_limit):
        words = text.split()
        return " ".join(words[-word_limit:]) if len(words) > word_limit else text
