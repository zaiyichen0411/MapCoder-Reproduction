from models.Gemini import Gemini
from models.OpenAI import ChatGPT, GPT4
from models.Qwen import QwenCoderTurbo, TongyiQianwenCoder, QwenCoder480b
from models.Minimax import MinimaxM2


class ModelFactory:
    @staticmethod
    def get_model_class(model_name):
        if model_name == "Gemini":
            return Gemini
        elif model_name == "ChatGPT":
            return ChatGPT
        elif model_name == "GPT4":
            return GPT4
        elif model_name == "QwenCoderTurbo":
            return QwenCoderTurbo
        elif model_name == "TongyiQianwenCoder":
            return TongyiQianwenCoder
        elif model_name == "QwenCoder480b":
            return QwenCoder480b
        elif model_name == "MinimaxM2":
            return MinimaxM2
        else:
            raise Exception(f"Unknown model name {model_name}")
