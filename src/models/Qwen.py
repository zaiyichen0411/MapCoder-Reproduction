from models.OpenAI import OpenAIModel
import os

class QwenCoderTurbo(OpenAIModel):
    def prompt(self, processed_input: list[dict], **kwargs):
        # 使用 OpenAI 兼容接口，优先采用专用 TURBO 环境变量；不可用或返回空内容时降级到后备模型。
        model_id = os.environ.get("QWEN_CODER_TURBO_MODEL") or os.environ.get("OPENAI_MODEL") or "qwen-coder-turbo"
        self.model_params["model"] = model_id
        try:
            content, pt, ct = super().prompt(processed_input, **kwargs)
            if not content or (isinstance(content, str) and not content.strip()):
                fallback = os.environ.get("QWEN_TURBO_FALLBACK_MODEL") or "qwen-32b-chat"
                self.model_params["model"] = fallback
                return super().prompt(processed_input, **kwargs)
            return content, pt, ct
        except Exception as e:
            msg = str(e)
            if "no available channels for model" in msg or "model not found" in msg or "invalid_request_error" in msg:
                fallback = os.environ.get("QWEN_TURBO_FALLBACK_MODEL") or "qwen-32b-chat"
                self.model_params["model"] = fallback
                return super().prompt(processed_input, **kwargs)
            raise


class TongyiQianwenCoder(OpenAIModel):
    def prompt(self, processed_input: list[dict], **kwargs):
        self.model_params["model"] = "qwen-32b-chat"
        return super().prompt(processed_input, **kwargs)


class QwenCoder480b(OpenAIModel):
    def prompt(self, processed_input: list[dict], **kwargs):
        # Allow overriding model id via environment variable to avoid 404s.
        # Prefer a dedicated env var, then fall back to OPENAI_MODEL, then a safe default.
        model_id = os.environ.get("QWEN_CODER_480B_MODEL") or os.environ.get("OPENAI_MODEL") or "qwen-coder-turbo"
        self.model_params["model"] = model_id
        return super().prompt(processed_input, **kwargs)