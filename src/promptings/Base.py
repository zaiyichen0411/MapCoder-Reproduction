from typing import List
import tiktoken
import os
import copy
import time

from models.Base import BaseModel
from datasets.Dataset import Dataset
from results.Results import Results
from utils.parse import parse_response


class BaseStrategy(object):
    def __init__(
        self,
        model: BaseModel,
        data: Dataset,
        language: str,
        pass_at_k: int,
        results: Results,
        verbose: bool = True,
    ):
        self.model = model
        self.data = data
        self.pass_at_k = pass_at_k
        self.results = results
        self.language = language
        self.verbose = verbose
        self.out_path = self.results.result_path

    def gpt_chat(self, prompt, temperature=0.0, top_p=1.0):
        # print("Inside BaseStrategy.gpt_chat", flush=True)
        # print(prompt, flush=True)
        kwargs = {"temperature": temperature, "top_p": top_p}
        if ("QwenCoderTurbo" in self.model.__class__.__name__) or ("QwenCoder480b" in self.model.__class__.__name__):
            kwargs.pop("temperature", None)
            kwargs.pop("top_p", None)
        return self.model.prompt(prompt, **kwargs)

    def run(self):
        num_items = len(self.data)
        num_success = 0

        # Build a lookup by task_id for existing results to support sliced runs
        existing_by_task_id = {}
        try:
            for res in getattr(self.results, "results", []):
                tid = res.get("task_id")
                if tid is not None:
                    existing_by_task_id[tid] = res
        except Exception:
            existing_by_task_id = {}

        for i, item in enumerate(self.data):
            print("", flush=True, end="")

            # if i < len(self.results):
            #     is_passing = self.results[i]["is_solved"]
            #     """
            #     if not is_passing:
            #         for response in self.results[i]["source_codes"]:
            #             cur_imp = response
            #             # parse_response(
            #             #     response,
            #             #     item["entry_point"]
            #             # )
            #             is_passing = self.data.evaluate(
            #                 item=item,
            #                 cur_imp=cur_imp,
            #                 language=self.language
            #             )
            #             if is_passing:
            #                 break
            #     """
            #     if is_passing:
            #         num_success += 1

            #     if self.verbose:
            #         print(f'completed {i+1}/{num_items}, Solved: {is_passing}, number of success = {num_success}/{i+1}, acc = {round(num_success/(i+1)*100, 2)}')

            #     continue

            # Align results by task_id rather than index to support dataset slices
            tid = item.get(self.data.id_key, None)
            prior = existing_by_task_id.get(tid) if tid is not None else None

            if prior is not None:
                item = copy.deepcopy(prior)
                cur_pass = len(item.get("source_codes", []))
                is_solved = item.get("is_solved", False)
                cur_imp = item["source_codes"][-1] if item.get("source_codes") else ""
            else:
                item = copy.deepcopy(item)
                item["source_codes"] = []
                item["responses"] = []
                item["prompt_tokens"] = []
                item["completion_tokens"] = []
                item["no_of_try"] = 0

                cur_pass = 0
                is_solved = False
                cur_imp = ""

            while cur_pass < self.pass_at_k and not is_solved:
                response = None
                # try:
                #     response, prompt_tokens, completion_tokens = self.run_single_pass(
                #         item)
                # except Exception as e:
                #     print(f"An error occurred: {e}")
                #     break

                if hasattr(self, "run_single_pass"):
                    try:
                        response, prompt_tokens, completion_tokens = self.run_single_pass(
                            item)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        # 写入一个失败结果占位，确保该样本被记录
                        item["responses"].append(str(e))
                        item["source_codes"].append("")
                        item["prompt_tokens"].append(0)
                        item["completion_tokens"].append(0)
                        item["no_of_try"] += 1

                        item["is_solved"] = False
                        item["language"] = self.language
                        item["task_id"] = item[self.data.id_key]

                        # Update or add by task_id
                        updated = False
                        if item["task_id"] in existing_by_task_id:
                            # find the index to update
                            for idx, res in enumerate(self.results.results):
                                if res.get("task_id") == item["task_id"]:
                                    self.results.results[idx] = item
                                    updated = True
                                    break
                            self.results.save_results()
                        if not updated:
                            self.results.add_result(item)
                        # Keep the lookup in sync for subsequent passes within the same run
                        existing_by_task_id[item["task_id"]] = item
                        break
                else:
                    raise NotImplementedError("run_single_pass is not implemented in the derived class")

                if hasattr(self, "parse_code"):
                    cur_imp = self.parse_code(response)
                else:
                    cur_imp = parse_response(response)
                    # cur_imp = parse_response(response, item.get("entry_point", None))

                item["source_codes"].append(cur_imp)
                item["responses"].append(response)
                item["prompt_tokens"].append(prompt_tokens)
                item["completion_tokens"].append(completion_tokens)
                item["no_of_try"] += 1

                is_solved = self.data.evaluate(
                    item=item,
                    cur_imp=cur_imp,
                    language=self.language
                )

                cur_pass += 1

                if is_solved:
                    num_success += 1

                item["is_solved"] = is_solved
                item["language"] = self.language
                item["task_id"] = item[self.data.id_key]

                # Update or add by task_id
                updated = False
                if item["task_id"] in existing_by_task_id:
                    # find the index to update
                    for idx, res in enumerate(self.results.results):
                        if res.get("task_id") == item["task_id"]:
                            self.results.results[idx] = item
                            updated = True
                            break
                    self.results.save_results()
                if not updated:
                    self.results.add_result(item)
                # Keep the lookup in sync for subsequent passes within the same run
                existing_by_task_id[item["task_id"]] = item

                if self.verbose:
                    print(
                        f'completed {i+1}/{num_items}, Solved: {item["is_solved"]}, number of success = {num_success}/{i+1}, acc = {round(num_success/(i+1)*100, 2)}')

                # break
