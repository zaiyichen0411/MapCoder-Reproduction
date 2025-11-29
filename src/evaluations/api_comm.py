from dataclasses import dataclass, field

import requests
from .exec_outcome import ExecOutcome

@dataclass
class ExtendedUnittest:
    input: str
    output: list[str] = field(default_factory=list)
    result: str | None = None
    exec_outcome: ExecOutcome | None = None

    def json(self):
        _json = self.__dict__
        if self.exec_outcome is not None:
            _json["exec_outcome"] = self.exec_outcome.name

        return _json

    @classmethod
    def from_json(cls, _json):
        return cls(
            input=_json.get("input", ""),
            output=_json.get("output", list()),
            result=_json.get("result", None),
            exec_outcome=_json.get("exec_outcome", None),
        )


class EmptyValueError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EmptyUnittestError(EmptyValueError):
    pass


class EmptyLanguageError(EmptyValueError):
    pass


class EmptySourceCodeError(EmptyValueError):
    pass


class APICommunication:
    _session: requests.Session

    def __init__(self, server_url: str = "http://localhost:5000"):
        self._session = requests.Session()
        self.execute_code_url = f"{server_url}/api/execute_code"
        self.get_runtimes_url = f"{server_url}/api/all_runtimes"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._session.close()

    def get_runtimes(self):
        return self._session.get(self.get_runtimes_url).json()

    def execute_code(
        self,
        language: str,
        source_code: str,
        unittests: list[dict],
        limits: dict | None,
        block_network: bool = True,
        stop_on_first_fail: bool = True,
        use_sanitizer: bool = False,
        compiler_program_name: str | None = None,
        compiler_flags: str | None = None,
        interpreter_cmd: str | None = None,
        interpreter_flags: str | None = None,
        sample_id: int | None = None,
        task_id: str | int | None = None,
    ) -> tuple[list[ExtendedUnittest], int | None, str | int | None]:
        if language is None:
            raise EmptyLanguageError

        if source_code is None:
            raise EmptySourceCodeError

        if unittests is None or len(unittests) == 0:
            raise EmptyUnittestError

        # Prepare request body for remote executor
        request_body = dict(
            language=language,
            source_code=source_code,
            unittests=unittests,
            limits=limits if isinstance(limits, dict) else dict(),
            compile_cmd=compiler_program_name,
            compile_flags=compiler_flags,
            execute_cmd=interpreter_cmd,
            execute_flags=interpreter_flags,
            block_network=block_network,
            stop_on_first_fail=stop_on_first_fail,
            use_sanitizer=use_sanitizer,
        )

        # Try remote executor first; if unavailable, fall back to local Python runner for Python 3
        try:
            json_response = self._session.post(
                self.execute_code_url,
                json=request_body,
                headers={"Content-Type": "application/json"},
            ).json()

            if "data" not in json_response:
                return "error", sample_id, task_id

            return (
                json_response["data"],
                sample_id,
                task_id,
            )
        except Exception:
            # Remote executor not available; provide a minimal local fallback for Python 3
            if (language or "").lower() != "python 3":
                return "error", sample_id, task_id

            import tempfile
            import subprocess
            import os
            import textwrap
            from .exec_outcome import ExecOutcome

            # Write the source code to a temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
                tmp.write(textwrap.dedent(source_code))
                tmp_path = tmp.name

            results: list[dict] = []
            try:
                for ut in unittests:
                    test_input = ut.get("input", "")
                    expected_out = None
                    # expected may be list[str] or str
                    if isinstance(ut.get("output"), list) and ut.get("output"):
                        expected_out = str(ut["output"][0])
                    elif isinstance(ut.get("output"), str):
                        expected_out = ut.get("output")

                    try:
                        proc = subprocess.run(
                            ["python", tmp_path],
                            input=test_input,
                            capture_output=True,
                            text=True,
                            timeout=5,
                            cwd=os.path.dirname(tmp_path) or None,
                        )
                        stdout = proc.stdout.strip()
                        # Compare output; normalize expected as string
                        exp = ("" if expected_out is None else str(expected_out).strip())
                        outcome = ExecOutcome.PASSED.value if stdout == exp else ExecOutcome.WRONG_ANSWER.value
                        results.append({
                            "input": test_input,
                            "output": ut.get("output", []),
                            "result": stdout,
                            "exec_outcome": outcome,
                        })
                        if stop_on_first_fail and outcome != ExecOutcome.PASSED.value:
                            break
                    except subprocess.TimeoutExpired:
                        results.append({
                            "input": test_input,
                            "output": ut.get("output", []),
                            "result": "",
                            "exec_outcome": ExecOutcome.TIME_LIMIT_EXCEEDED.value,
                        })
                        if stop_on_first_fail:
                            break
                    except Exception:
                        results.append({
                            "input": test_input,
                            "output": ut.get("output", []),
                            "result": "",
                            "exec_outcome": ExecOutcome.RUNTIME_ERROR.value,
                        })
                        if stop_on_first_fail:
                            break
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

            return results, sample_id, task_id
