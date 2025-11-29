from models.OpenAI import OpenAIModel
import os

class MinimaxM2(OpenAIModel):
    def prompt(self, processed_input: list[dict], **kwargs):
        model_id = os.environ.get("OPENAI_MODEL") or "minimax/minimax-m2"
        self.model_params["model"] = model_id
        return super().prompt(processed_input, **kwargs)