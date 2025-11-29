import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from promptings.MapCoder import MapCoder
from results.Results import Results


class DummyModel:
    def prompt(self, prompt, **kwargs):
        text = "\n".join([m.get("content", "") for m in prompt if isinstance(m, dict)])
        if "Please provide a knowledge base" in text:
            return (
                "<response>\n"
                "  <knowledge_base>math, iteration</knowledge_base>\n"
                "  <exemplars><![CDATA[example]]></exemplars>\n"
                "</response>\n",
                10,
                10,
            )
        if "Create a plan" in text:
            return (
                "<response>\n"
                "  <plan>step1; step2</plan>\n"
                "  <test_cases><![CDATA[cases]]></test_cases>\n"
                "</response>\n",
                10,
                10,
            )
        if "Check correctness and adequacy" in text:
            return ("CORRECT", 2, 1)
        if "Return only the solution code inside a fenced code block" in text:
            if "Style:" in text and "robust" in text:
                code = """```python
def add_one(x):
    return x + 1
```"""
                return (code, 20, 50)
            code = """```python
def wrong():
    return 0
```"""
            return (code, 20, 50)
        return ("", 0, 0)


class DummyData:
    id_key = "task_id"
    def get_prompt(self, item: dict) -> str:
        return "Implement add_one(x) returning x+1."


def main():
    model = DummyModel()
    data = DummyData()
    results = Results(result_path=os.path.join("results", "sanity2.jsonl"), discard_previous_run=True)
    strategy = MapCoder(model=model, data=data, language="Python3", pass_at_k=1, results=results, verbose=False)
    item = {
        "task_id": "sanity_2",
        "entry_point": "add_one",
        "test": "def check(f):\n    assert f(1) == 2",
    }
    code, pr_tok, com_tok = strategy.run_single_pass(item)
    print(code)
    print(pr_tok, com_tok)


if __name__ == "__main__":
    main()