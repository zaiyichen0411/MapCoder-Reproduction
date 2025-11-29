@echo off

set "PYTHON_EXE=python"
set "MAIN_SCRIPT=src/main.py"
set "MODEL=QwenCoderTurbo"
set "DATASET=HumanEval"
set "STRATEGY=MapCoder"
set "LANGUAGE=Python3"

REM Kill any existing python processes to ensure a clean start
REM taskkill /F /IM python.exe

REM Start multiple processes in the background
start "Process 1" /B %PYTHON_EXE% %MAIN_SCRIPT% --model %MODEL% --dataset %DATASET% --strategy %STRATEGY% --language %LANGUAGE% --start-index 4 --end-index 40 > output_1.log 2>&1
start "Process 2" /B %PYTHON_EXE% %MAIN_SCRIPT% --model %MODEL% --dataset %DATASET% --strategy %STRATEGY% --language %LANGUAGE% --start-index 41 --end-index 81 > output_2.log 2>&1
start "Process 3" /B %PYTHON_EXE% %MAIN_SCRIPT% --model %MODEL% --dataset %DATASET% --strategy %STRATEGY% --language %LANGUAGE% --start-index 82 --end-index 122 > output_3.log 2>&1
start "Process 4" /B %PYTHON_EXE% %MAIN_SCRIPT% --model %MODEL% --dataset %DATASET% --strategy %STRATEGY% --language %LANGUAGE% --start-index 123 --end-index 164 > output_4.log 2>&1

echo All parallel processes have been started.
echo You can monitor their progress by checking the output_*.log files and the results file.