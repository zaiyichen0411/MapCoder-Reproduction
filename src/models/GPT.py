import openai
import os

class GPT:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = self.api_key

    def prompt(self, prompt_text: str, **kwargs):
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt_text}],
                **kwargs
            )
            content = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            return content, prompt_tokens, completion_tokens
        except Exception as e:
            print(f"An error occurred during OpenAI API call: {e}")
            # In case of an API error, we'll return None and 0 tokens
            # The calling function should handle this case.
            return None, 0, 0