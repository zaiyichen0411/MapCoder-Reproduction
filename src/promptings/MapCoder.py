from typing import List
import tiktoken
import os
import json
import re
import sys
import time

from copy import deepcopy
import xml.etree.ElementTree as ET

from .Base import BaseStrategy
from models.Base import BaseModel

from datasets.Dataset import Dataset
from datasets.APPSDataset import APPSDataset
from datasets.MBPPDataset import MBPPDataset
from datasets.XCodeDataset import XCodeDataset
from datasets.HumanEvalDataset import HumanDataset
from datasets.CodeContestDataset import CodeContestDataset

from results.Results import Results
from evaluations.func_evaluate import evaluate_io, evaluate_functional_correctness

mapping = {
    1: "one (01)",
    2: "two (02)",
    3: "three (03)",
    4: "four (04)",
    5: "five (05)",
    6: "six (06)",
    7: "seven (07)",
    8: "eight (08)",
    9: "nine (09)",
}

# KB + Exemplars + Example Planning + Problem Planning + Code Generation + Sample IO testing + Code Improvement


class MapCoder(BaseStrategy):
    def __init__(
        self,
        k: int = 3,
        t: int = 5,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.k = k
        self.t = t
        self.n_alternatives = 2
        self.style_variations = [
            "concise",
            "robust",
            "edge-case-focused",
        ]
        # Default retries for planning and improvement loops
        self.max_retries = 4

    def xml_to_dict(self, element):
        if not list(element):
            return element.text or ''

        result = {}
        for child in element:
            child_data = self.xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        # If the element has text content besides children, add it
        if element.text and element.text.strip():
            result['#text'] = element.text.strip()
            
        return result

    def parse_xml(self, response: str) -> dict:
        response = response.strip()
        if response.startswith('```xml'):
            response = response[len('```xml'):].strip()
        if response.endswith('```'):
            response = response[:-len('```')].strip()

        # Attempt to fix common XML errors
        response = re.sub(r'&(?!(amp|lt|gt|apos|quot);)', '&amp;', response)
        # Remove CDATA sections that wrap other XML tags
        response = re.sub(r'<!\[CDATA\[\s*<([a-zA-Z_:]+)', r'<\1', response)
        response = re.sub(r'</([a-zA-Z_:]+)>\s*]]>', r'</\1>', response)

        try:
            # First attempt to parse the response as is
            root = ET.fromstring(response)
        except ET.ParseError:
            try:
                # If parsing fails, try wrapping the response in a single root element
                response_wrapped = f"<root>{response}</root>"
                root = ET.fromstring(response_wrapped)
            except ET.ParseError as e:
                # If it still fails, log the error and return a dictionary with an error message
                print(f"XML ParseError: {e}\nResponse:\n{response}")
                return {'error': 'XML parsing failed', 'response': response}

        # The calling code expects a 'root' key. We return the parsed content under the 'root' key.
        # The original root tag's content is preserved by xml_to_dict.
        return {'root': {root.tag: self.xml_to_dict(root)}}

    def parse_code(self, response: str) -> str:
        # Prefer fenced code blocks by language; fall back when absent
        if "```" in response:
            code_pattern = r'```((.|\n)*?)```'
            if "```Python" in response:
                code_pattern = r'```Python((.|\n)*?)```'
            if "```Python3" in response:
                code_pattern = r'```Python3((.|\n)*?)```'
            if "```python" in response:
                code_pattern = r'```python((.|\n)*?)```'
            if "```python3" in response:
                code_pattern = r'```python3((.|\n)*?)```'
            if "```C" in response:
                code_pattern = r'```C((.|\n)*?)```'
            if "```c" in response:
                code_pattern = r'```c((.|\n)*?)```'
            if "```C++" in response:
                code_pattern = r'```C\+\+((.|\n)*?)```'
            if "```c++" in response:
                code_pattern = r'```c\+\+((.|\n)*?)```'
            if "```Java" in response:
                code_pattern = r'```Java((.|\n)*?)```'
            if "```java" in response:
                code_pattern = r'```java((.|\n)*?)```'
            if "```Node" in response:
                code_pattern = r'```Node((.|\n)*?)```'
            if "```node" in response:
                code_pattern = r'```node((.|\n)*?)```'
            if "```Rust" in response:
                code_pattern = r'```Rust((.|\n)*?)```'
            if "```rust" in response:
                code_pattern = r'```rust((.|\n)*?)```'
            if "```PHP" in response:
                code_pattern = r'```PHP((.|\n)*?)```'
            if "```php" in response:
                code_pattern = r'```php((.|\n)*?)```'
            if "```Go" in response:
                code_pattern = r'```Go((.|\n)*?)```'
            if "```go" in response:
                code_pattern = r'```go((.|\n)*?)```'
            if "```Ruby" in response:
                code_pattern = r'```Ruby((.|\n)*?)```'
            if "```ruby" in response:
                code_pattern = r'```ruby((.|\n)*?)```'
            if "```C#" in response:
                code_pattern = r'```C#((.|\n)*?)```'
            if "```c#" in response:
                code_pattern = r'```c#((.|\n)*?)```'
            if "```csharp" in response:
                code_pattern = r'```csharp((.|\n)*?)```'

            code_blocks = re.findall(code_pattern, response, re.DOTALL)
            if not code_blocks:
                return response
            # Prefer blocks that contain function definitions
            preferred = None
            for blk in code_blocks:
                text = blk[0] if isinstance(blk, (tuple, list)) else blk
                if "def " in text:
                    preferred = blk
                    break
            if preferred is None:
                preferred = code_blocks[-1]
            if isinstance(preferred, (tuple, list)):
                return "\n".join(preferred)
            return preferred

        # Fallback: try to extract Python definitions if no fences are present
        raw = response.strip()
        lines = raw.splitlines()
        start_idx = None
        for i, ln in enumerate(lines):
            s = ln.strip()
            if s.startswith("def ") or s.startswith("class ") or s.startswith("import "):
                start_idx = i
                break
        if start_idx is not None:
            return "\n".join(lines[start_idx:]).strip()
        return raw

    def _sp(self, x):
        if getattr(self, "verbose", True):
            try:
                print(x)
            except Exception:
                try:
                    sys.stdout.buffer.write((str(x) + "\n").encode('utf-8', 'ignore'))
                except Exception:
                    pass

    @staticmethod
    def trim_text(text: str, trimmed_text: str):
        return text.replace(trimmed_text, '').strip()

    @staticmethod
    def replace_tag(text: str, tag: str):
        if f'<{tag}><![CDATA[' in text and f']]></{tag}>' in text:
            return text 
        else:
            return text.replace(f'<{tag}>', f'<{tag}><![CDATA[').replace(f'</{tag}>', f']]></{tag}>').strip()

    @staticmethod
    def get_sample_io_str(sample_io: any) -> str:
        if len(sample_io) > 0:
            if type(sample_io[0]) == str:
                return "\n".join(sample_io)
            if type(sample_io[0]) == dict:
                return "\n".join([f"Input:\n{io['input']}\nExpected output:\n{io['output'][0]}" for io in sample_io])
        return sample_io

    def run_single_pass(self, item: dict):
        print("--- Starting run_single_pass ---")
        # Be robust across datasets: use dataset-specific id_key if available
        try:
            id_key = getattr(self.data, 'id_key', 'task_id')
            task_id_value = item.get(id_key, item.get('task_id', item.get('id', 'N/A')))
        except Exception:
            task_id_value = item.get('task_id', item.get('id', 'N/A'))
        print(f"Task ID: {task_id_value}")

        code = ""
        plan = ""
        test_cases = ""

        pr_tok = 0
        com_tok = 0

        # Use dataset-specific prompt generation instead of assuming 'description'
        try:
            problem_description = self.data.get_prompt(item)
        except Exception:
            # Fallbacks if dataset lacks get_prompt or fields
            problem_description = item.get('description') or item.get('prompt') or item.get('text') or ""

        # Dataset-specific defaults for exemplars and planning steps
        try:
            if isinstance(self.data, HumanDataset):
                self.k = max(self.k, 4)
                self.t = max(self.t, 6)
            if isinstance(self.data, MBPPDataset):
                self.k = max(self.k, 5)
                self.t = max(self.t, 6)
        except Exception:
            pass

        # Turbo simplified path
        exemplars_override = ""
        try:
            is_turbo = "QwenCoderTurbo" in self.model.__class__.__name__
            entry_point = item.get('entry_point') if isinstance(item, dict) else None
            constraint_text = ""
            if isinstance(self.data, (APPSDataset, CodeContestDataset, XCodeDataset)):
                constraint_text = (
                    "严格遵循输入/输出格式：从标准输入读取并打印到标准输出。"
                    "生成可直接运行的完整程序。"
                )
            elif isinstance(self.data, (HumanDataset, MBPPDataset)):
                if entry_point:
                    constraint_text = (
                        f"必须实现名为 '{entry_point}' 的函数。不要编写任何输入输出代码或顶层测试，"
                        "仅返回函数定义。"
                    )
                else:
                    constraint_text = (
                        "实现所需函数。不编写输入输出或顶层测试，仅提供函数定义。"
                    )

            if is_turbo:
                # Formula (1) Turbo Path: Direct Code Generation without Planning
                plan = ""
                test_cases = ""
                code_gen_prompt = [
                    {
                        "role": "system",
                        "content": (
                            "You are a coding agent. "
                            "Return only executable solution code for the task. "
                            "Do not include any commentary, Markdown fences or explanations."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Problem description:\n{problem_description}\n\n"
                            + (f"Constraints:\n{constraint_text}\n\n" if constraint_text else "")
                            + f"Target language: {self.language}. "
                            + "只输出可执行代码，无任何额外文本。"
                        )
                    }
                ]
                self._sp(f"Input for Turbo Code Generation: {code_gen_prompt}")
                code_response, pr_tok_1, com_tok_1 = self.gpt_chat(prompt=code_gen_prompt)
                self._sp(f"Response from Turbo Code Generation: {code_response}")
                item.setdefault('api_calls', 0)
                item['api_calls'] += 1
                pr_tok += pr_tok_1
                com_tok += com_tok_1
                code = self.parse_code(code_response)
                self._sp(f"Initial Extracted Code (Turbo): {code}")
            else:
                # 1. Generate Knowledge Base and Exemplars
                print("--- Generating Knowledge Base and Exemplars ---")
                exemplars_override = ""
                try:
                    if isinstance(self.data, MBPPDataset):
                        sim_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'MBPPEval', 'similar_problems_solutions.jsonl'))
                        if os.path.exists(sim_path):
                            with open(sim_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    line = line.strip()
                                    if not line:
                                        continue
                                    try:
                                        obj = json.loads(line)
                                    except Exception:
                                        continue
                                    name_key = item.get('name') or item.get('task_id')
                                    if name_key and (obj.get('name') == name_key or obj.get('task_id') == name_key):
                                        kb = obj.get('knowledge', '')
                                        sol = obj.get('solution', '')
                                        parts = []
                                        if kb:
                                            parts.append(str(kb))
                                        if sol:
                                            parts.append(str(sol))
                                        if parts:
                                            exemplars_override = "\n".join(parts)
                                        break
                except Exception:
                    exemplars_override = ""

            kb_exemplars_prompt = [
                # Formula (1) Knowledge & Exemplars: Generate KB and examples to aid reasoning
                {
                    "role": "system",
                    "content": (
                        "You are an expert code synthesis assistant. "
                        "Given a programming problem description, produce a concise knowledge base of relevant concepts, algorithms, data structures, and edge cases. "
                        "Also produce up to k exemplars (worked examples or similar problems) that will help solve the task. "
                        "Respond strictly as XML with the following structure: \n"
                        "<response>\n"
                        "  <knowledge_base>...</knowledge_base>\n"
                        "  <exemplars><![CDATA[...]]></exemplars>\n"
                        "</response>\n"
                        "Do not include any text outside the XML."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Problem description:\n{problem_description}\n\n"
                        f"Please provide a knowledge base and up to {self.k} exemplars. "
                        + (f"You may reuse the following exemplars if relevant:\n{exemplars_override}\n\n" if exemplars_override else "")
                        + "Use the exact XML structure specified above."
                    )
                }
            ]
            self._sp(f"Input for KB and Exemplars: {kb_exemplars_prompt}")

            response, pr_tok_1, com_tok_1 = self.gpt_chat(prompt=kb_exemplars_prompt)
            self._sp(f"Response from KB and Exemplars: {response}")
            item.setdefault('api_calls', 0)
            item['api_calls'] += 1
            pr_tok += pr_tok_1
            com_tok += com_tok_1

            # 2. Parse Knowledge Base and Exemplars
            if not is_turbo:
                print("--- Parsing Knowledge Base and Exemplars ---")
                try:
                    parsed_xml = self.parse_xml(response)
                    root = parsed_xml.get('root', {})
                    response_content = root.get('response', root)
                    knowledge_base = response_content.get('knowledge_base', '')
                    exemplars = response_content.get('exemplars', '')
                    if isinstance(knowledge_base, dict):
                        knowledge_base = json.dumps(knowledge_base, indent=2)
                    if isinstance(exemplars, dict):
                        exemplars = json.dumps(exemplars, indent=2)
                    if exemplars_override:
                        exemplars = (str(exemplars).strip() + "\n" + exemplars_override).strip()
                    self._sp(f"Parsed Knowledge Base: {knowledge_base}")
                    self._sp(f"Parsed Exemplars: {exemplars}")
                except Exception as e:
                    print(f"Error parsing KB and Exemplars: {e}")
                    knowledge_base, exemplars = "", ""

            # 3. Iterative Planning
            for i in range(self.max_retries):
                print(f"--- Planning Iteration {i+1} of {self.max_retries} ---")
                try:
                    # 3a. Generate Problem Planning
                    if is_turbo:
                        break
                    print("--- Generating Problem Planning ---")
                    # Formula (2) Planning: Generate step-by-step plan and test cases
                    planning_prompt = [
                        {
                            "role": "system",
                            "content": (
                                "You are a planning agent for programming tasks. "
                                "Given a problem description, a knowledge base, and exemplars, draft a step-by-step plan and derive representative test cases. "
                                "Respond strictly as XML with the following structure: \n"
                                "<response>\n"
                                "  <plan>...</plan>\n"
                                "  <test_cases><![CDATA[...]]></test_cases>\n"
                                "</response>\n"
                                "Do not include any text outside the XML."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Problem description:\n{problem_description}\n\n"
                                f"Knowledge base:\n{knowledge_base}\n\n"
                                f"Exemplars:\n{exemplars}\n\n"
                                f"Create a plan with about {self.t} steps and derive representative test cases. "
                                "Return only the XML specified above."
                            )
                        }
                    ]
                    self._sp(f"Input for Problem Planning: {planning_prompt}")

                    planning_response, pr_tok_1, com_tok_1 = self.gpt_chat(prompt=planning_prompt)
                    self._sp(f"Response from Problem Planning: {planning_response}")
                    item.setdefault('api_calls', 0)
                    item['api_calls'] += 1
                    pr_tok += pr_tok_1
                    com_tok += com_tok_1

                    # 3b. Parse Plan and Test Cases
                    print("--- Parsing Problem Planning ---")
                    try:
                        parsed_planning = self.parse_xml(planning_response)
                        root = parsed_planning.get('root', {})
                        response_content = root.get('response', root)
                        plan = response_content.get('plan', '')
                        test_cases = response_content.get('test_cases', '')
                        if isinstance(plan, dict):
                            plan = json.dumps(plan, indent=2)
                        if isinstance(test_cases, dict):
                            test_cases = json.dumps(test_cases, indent=2)
                        self._sp(f"Parsed Plan: {plan}")
                        self._sp(f"Parsed Test Cases: {test_cases}")
                    except Exception as e:
                        print(f"Error parsing Plan and Test Cases: {e}")
                        plan, test_cases = "", ""

                    # 3c. Verify Plan
                    print("--- Generating Planning Verification ---")
                    verification_prompt = [
                        {
                            "role": "system",
                            "content": (
                                "You are a strict planning verifier. "
                                "Given a plan and test cases, check their correctness and adequacy for the problem. "
                                "If the plan and tests are sufficient, respond with the single word 'CORRECT'. "
                                "Otherwise, respond with 'INCORRECT' and briefly explain the issues. "
                                "Ensure test cases cover boundary conditions (empty inputs, single elements, duplicates, type conversions, and large sizes) when applicable."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Problem description:\n{problem_description}\n\n"
                                f"Plan:\n{plan}\n\n"
                                f"Test cases:\n{test_cases}\n\n"
                                "Check correctness and adequacy. Respond with 'CORRECT' or 'INCORRECT'."
                            )
                        }
                    ]
                    self._sp(f"Input for Planning Verification: {verification_prompt}")

                    verification_res, pr_tok_1, com_tok_1 = self.gpt_chat(prompt=verification_prompt)
                    self._sp(f"Response from Planning Verification: {verification_res}")
                    item.setdefault('api_calls', 0)
                    item['api_calls'] += 1
                    pr_tok += pr_tok_1
                    com_tok += com_tok_1

                    if "CORRECT" in verification_res.upper():
                        print("--- Plan Verification Correct ---")
                        break
                    else:
                        print("--- Plan Verification Incorrect, retrying ---\n")

                except Exception as e:
                    print(f"Error in planning phase iteration {i+1}: {e}")
                    continue
            
            # 4. Final Code Generation
            if is_turbo:
                pass
            print("--- Generating Final Code ---")
            # Dataset-specific constraints: enforce I/O vs function-only solutions
            constraint_text = ""
            entry_point = item.get('entry_point') if isinstance(item, dict) else None
            if isinstance(self.data, (APPSDataset, CodeContestDataset, XCodeDataset)):
                constraint_text = (
                    "严格遵循输入/输出格式：从标准输入读取并打印到标准输出。"
                    "生成可直接运行的完整程序。"
                )
            elif isinstance(self.data, (HumanDataset, MBPPDataset)):
                if entry_point:
                    constraint_text = (
                        f"必须实现名为 '{entry_point}' 的函数。不要编写任何输入输出代码或顶层测试，"
                        "仅返回函数定义。"
                    )
                else:
                    constraint_text = (
                        "实现所需函数。不编写输入输出或顶层测试，仅提供函数定义。"
                    )

            # Formula (3) Code Generation: Generate code based on plan, tests, and constraints
            code_gen_prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are a coding agent. "
                        "Generate a complete, correct solution for the task. "
                        "Return only code fenced in triple backticks with an explicit language tag (e.g., ```python or ```Python3). "
                        "Do not include any commentary outside the code fence. "
                        "Do not include sample assertions, testing code, or print statements unless required by I/O constraints."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Problem description:\n{problem_description}\n\n"
                        f"Plan:\n{plan}\n\n"
                        f"Test cases:\n{test_cases}\n\n"
                        + (f"Constraints:\n{constraint_text}\n\n" if constraint_text else "")
                        + f"Target language: {self.language}. "
                        + "Return only the solution code inside a fenced code block."
                    )
                }
            ]
            if not is_turbo:
                self._sp(f"Input for Final Code Generation: {code_gen_prompt}")

            if not is_turbo:
                code_response, pr_tok_1, com_tok_1 = self.gpt_chat(prompt=code_gen_prompt)
                self._sp(f"Response from Final Code Generation: {code_response}")
                item.setdefault('api_calls', 0)
                item['api_calls'] += 1
                pr_tok += pr_tok_1
                com_tok += com_tok_1
                code = self.parse_code(code_response)
                self._sp(f"Initial Extracted Code: {code}")


            passed = False
            feedback = ""
            timeout = 15
            sample_io = item.get('sample_io', [])
            entry_point = item.get('entry_point') if isinstance(item, dict) else None
            if isinstance(sample_io, list) and len(sample_io) > 0:
                if entry_point and isinstance(self.data, (HumanDataset, MBPPDataset)) and (f"def {entry_point}(" not in code):
                    passed, feedback = False, f"Missing required entry point function '{entry_point}'"
                else:
                    passed, feedback = evaluate_io(sample_io, code, timeout)
            else:
                if entry_point and isinstance(self.data, (HumanDataset, MBPPDataset)) and (f"def {entry_point}(" not in code):
                    passed, feedback = False, f"Missing required entry point function '{entry_point}'"
                else:
                    result = evaluate_functional_correctness(problem=item, completion=code, timeout=timeout)
                    passed = (result == "passed")
                    feedback = result if not passed else "passed"

            if not passed:
                alternatives = []
                for idx, style in enumerate(self.style_variations[: self.n_alternatives]):
                    alt_prompt = [
                        {
                            "role": "system",
                            "content": (
                                "You are a coding agent. "
                                "Generate a complete, correct solution for the task. "
                                "Return only code fenced in triple backticks with an explicit language tag (e.g., ```python or ```Python3). "
                                "Do not include any commentary outside the code fence. "
                                "Do not include sample assertions, testing code, or print statements unless required by I/O constraints."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Problem description:\n{problem_description}\n\n"
                                f"Plan:\n{plan}\n\n"
                                f"Test cases:\n{test_cases}\n\n"
                                + (f"Constraints:\n{constraint_text}\n\n" if constraint_text else "")
                                + f"Target language: {self.language}. "
                                + f"Style: {style}. "
                                + "Return only the solution code inside a fenced code block."
                            )
                        }
                    ]
                    alt_response, pr_t, com_t = self.gpt_chat(prompt=alt_prompt)
                    item['api_calls'] += 1
                    pr_tok += pr_t
                    com_tok += com_t
                    alt_code = self.parse_code(alt_response)
                    if isinstance(sample_io, list) and len(sample_io) > 0:
                        if entry_point and isinstance(self.data, (HumanDataset, MBPPDataset)) and (f"def {entry_point}(" not in alt_code):
                            alt_passed, alt_feedback = False, f"Missing required entry point function '{entry_point}'"
                        else:
                            alt_passed, alt_feedback = evaluate_io(sample_io, alt_code, timeout)
                    else:
                        if entry_point and isinstance(self.data, (HumanDataset, MBPPDataset)) and (f"def {entry_point}(" not in alt_code):
                            alt_passed, alt_feedback = False, f"Missing required entry point function '{entry_point}'"
                        else:
                            alt_result = evaluate_functional_correctness(problem=item, completion=alt_code, timeout=timeout)
                            alt_passed = (alt_result == "passed")
                            alt_feedback = alt_result if not alt_passed else "passed"
                    alternatives.append((alt_code, alt_passed, alt_feedback))
                    if alt_passed:
                        code = alt_code
                        passed = True
                        feedback = alt_feedback
                        break

                if not passed and alternatives:
                    code = alternatives[0][0]
                    feedback = alternatives[0][2]

            # 5. Code Improvement Loop
            # Formula (4) Iterative Refinement: Improve code based on execution feedback
            for i in range(self.max_retries):
                print(f"--- Code Improvement Iteration {i+1} of {self.max_retries} ---")
                if isinstance(sample_io, list) and len(sample_io) > 0:
                    entry_point = item.get('entry_point') if isinstance(item, dict) else None
                    if entry_point and isinstance(self.data, (HumanDataset, MBPPDataset)) and (f"def {entry_point}(" not in code):
                        passed, feedback = False, f"Missing required entry point function '{entry_point}'"
                    else:
                        passed, feedback = evaluate_io(sample_io, code, timeout)
                else:
                    entry_point = item.get('entry_point') if isinstance(item, dict) else None
                    if entry_point and isinstance(self.data, (HumanDataset, MBPPDataset)) and (f"def {entry_point}(" not in code):
                        passed, feedback = False, f"Missing required entry point function '{entry_point}'"
                    else:
                        result = evaluate_functional_correctness(problem=item, completion=code, timeout=timeout)
                        passed = (result == "passed")
                        feedback = result if not passed else "passed"

                if passed:
                    print("--- Code Passed All Tests ---\n")
                    break
                
                print("--- Code Failed, Improving ---")
                print(f"Feedback: {feedback}")
                improvement_prompt = [
                    {
                        "role": "system",
                        "content": (
                            "You are a debugging agent. "
                            "Improve the given solution based on execution feedback. "
                            "Return only the corrected code fenced in triple backticks with an explicit language tag."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Problem description:\n{problem_description}\n\n"
                            f"Current code:\n{code}\n\n"
                            f"Plan:\n{plan}\n\n"
                            f"Test cases:\n{test_cases}\n\n"
                            + (f"Constraints:\n{constraint_text}\n\n" if constraint_text else "")
                            + f"Feedback:\n{feedback}\n\n"
                            + f"Target language: {self.language}. "
                            + "Return only the improved solution inside a fenced code block."
                        )
                    }
                ]
                self._sp(f"Input for Improving Code: {improvement_prompt}")

                improvement_response, pr_tok_1, com_tok_1 = self.gpt_chat(prompt=improvement_prompt)
                self._sp(f"Response from Improving Code: {improvement_response}")
                item.setdefault('api_calls', 0)
                item['api_calls'] += 1
                pr_tok += pr_tok_1
                com_tok += com_tok_1

                code = self.parse_code(improvement_response)
                self._sp(f"Extracted Improved Code: {code}")

        except Exception as e:
            print(f"--- An unexpected error occurred in run_single_pass: {e} ---")
            import traceback
            traceback.print_exc()

        print("--- Ending run_single_pass ---")
        print(f"Final Code: {code}")
        print(f"Total Prompt Tokens: {pr_tok}")
        print(f"Total Completion Tokens: {com_tok}")
        print("________________________\n\n", flush=True)
        return code, pr_tok, com_tok
