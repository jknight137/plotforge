import time
import ollama

class AIModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        print(f"[Ollama] Using model: {model_name}")

    def generate(self, prompt: str, min_words=1000, max_tokens=1024, tail_words=300):
        """
        Generates ~1000 words from a prompt. If previous content is passed, appends a continuation request
        using only the last tail_words of context.
        """
        start_time = time.time()

        if prompt.strip().endswith("### CONTINUE"):
            # Continuation mode: only include the last 300 words
            body = prompt.replace("### CONTINUE", "").strip()
            context = self._get_tail(body, tail_words)
            full_prompt = (
                f"The current story is continuing. Recent context:\n\n"
                f"{context}\n\n"
                "Continue writing the next section of the chapter, keeping style, tone, and narrative flow consistent."
            )
        else:
            # Initial generation
            full_prompt = (
                "You are an expert fiction author. Write the beginning of a novel chapter in a compelling, immersive style.\n\n"
                f"{prompt}"
            )

        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                stream=False,
                options={"num_predict": max_tokens}
            )
            text = response.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"[Ollama Error] Generation failed: {e}")

        elapsed = round(time.time() - start_time, 2)
        word_count = len(text.split())

        if word_count < min_words:
            print(f"[Warning] Only {word_count} words generated (target was {min_words})")

        return text, word_count, elapsed

    def _get_tail(self, text, word_limit):
        words = text.split()
        return " ".join(words[-word_limit:]) if len(words) > word_limit else text
