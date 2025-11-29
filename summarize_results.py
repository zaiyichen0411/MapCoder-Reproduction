import json

def summarize_results(file_path):
    """
    Parses a .jsonl result file and prints a formatted summary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            results = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file '{file_path}'. It might be empty or corrupted.")
        return

    if not results:
        print("The result file is empty. No summary to display.")
        return

    total_problems = len(results)
    solved_problems = sum(1 for r in results if r.get('is_solved', False))
    
    print("-" * 50)
    print(f"{'Task ID':<15} | {'Solved?':<10} | {'Tries':<5}")
    print("-" * 50)

    for result in results:
        task_id = result.get('task_id', 'N/A')
        is_solved = 'Yes' if result.get('is_solved', False) else 'No'
        tries = result.get('no_of_try', 0)
        print(f"{task_id:<15} | {is_solved:<10} | {tries:<5}")

    print("-" * 50)
    print("\n--- Overall Summary ---")
    print(f"Total Problems Processed: {total_problems}")
    print(f"Problems Solved: {solved_problems}")
    if total_problems > 0:
        success_rate = (solved_problems / total_problems) * 100
        print(f"Success Rate: {success_rate:.2f}%")
    print("-" * 25)

if __name__ == "__main__":
    # The script will target the specific result file we've been working with.
    result_file = 'results/QwenCoderTurbo-MapCoder-HumanEval-Python3-0-1.jsonl'
    summarize_results(result_file)