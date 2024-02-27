import argparse
import fnmatch
import json
import os
import re
import subprocess
import requests

def read_gitignore_patterns(source_dir_path):
    gitignore_path = os.path.join(source_dir_path, '.gitignore')
    if not os.path.isfile(gitignore_path):
        return []

    with open(gitignore_path, 'r') as file:
        patterns = file.read().splitlines()
    return patterns

def should_ignore(file, ignore_patterns):
    return any(fnmatch.fnmatch(file, pattern) for pattern in ignore_patterns)

def log_prompt_to_file(prompt, log_file_path):
    with open(log_file_path, 'w') as file:
        file.write(prompt)

def extract_json_from_result(result):
    # Use regular expression to extract the JSON part from the result
    match = re.search(r'\[\s*{.+}\s*\]', result, re.DOTALL)
    if match:
        json_part = match.group(0)
        # Format the JSON string for pretty printing
        formatted_json = json.dumps(json.loads(json_part), indent=4)
        return formatted_json
    else:
        return "No JSON found in the result."

def is_valid_json_array(json_string):
    try:
        json_object = json.loads(json_string)
        return isinstance(json_object, list)
    except json.JSONDecodeError:
        return False

def is_in_allowed_directories(file_path, allowed_directories, root_dir):
    relative_file_path = os.path.relpath(file_path, root_dir)
    return any(relative_file_path.startswith(allowed_dir) for allowed_dir in allowed_directories)

def get_git_diff_output():
    try:
        # Run the git diff command to get changed files and their line ranges
        output = subprocess.check_output(
            ['git', 'diff', '--unified=0', 'main', 'HEAD'],
            text=True
        )
        changes = []
        current_file_path = None
        for line in output.splitlines():
            if line.startswith('+++ b/'):
                current_file_path = line[6:]
            elif line.startswith('@@'):
                line_numbers = re.search(r'@@ -\d+,\d+ \+(\d+),(\d+) @@', line)
                if line_numbers:
                    changed_lines_from = int(line_numbers.group(1))
                    num_lines = int(line_numbers.group(2))
                    changed_lines_to = changed_lines_from + num_lines - 1
                    changes.append({
                        'file_path': current_file_path,
                        'changed_lines_from': changed_lines_from,
                        'changed_lines_to': changed_lines_to
                    })
        return json.dumps(changes, indent=4)
    except subprocess.CalledProcessError:
        return "[]"

def get_prompt_text(source_dir_path, allowed_directories):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_template_path = os.path.join(script_dir, "prompt_template_py.txt")
    with open(prompt_template_path, 'r') as file:
        prompt_template = file.read()

    git_diff_output = get_git_diff_output()

    ignore_patterns = read_gitignore_patterns(source_dir_path)
    file_paths = []
    for root, _, files in os.walk(source_dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if should_ignore(filename, ignore_patterns) or not is_in_allowed_directories(file_path, allowed_directories, source_dir_path):
                continue
            if os.path.isfile(file_path):
                file_paths.append(file_path)

    return prompt_template, git_diff_output, file_paths

def analyze_code_with_gpt(source_dir_path, log_file_path=None, model="gpt-4-turbo-preview"):
    allowed_directories = ['src']
    prompt_template, git_diff_output, file_paths = get_prompt_text(source_dir_path, allowed_directories)

    max_files_per_request = 20
    all_responses = []

    total_files = len(file_paths)
    total_batches = (total_files + max_files_per_request - 1) // max_files_per_request

    print(f"Detected {total_files} files.")

    for i in range(0, total_files, max_files_per_request):
        batch_file_paths = file_paths[i:i + max_files_per_request]
        concatenated_code = ""
        for file_path in batch_file_paths:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                relative_path = os.path.relpath(file_path, source_dir_path)
                concatenated_code += f"\n# File: {relative_path}\n```\n"
                lines = file.readlines()
                for line_num, line in enumerate(lines, start=1):
                    concatenated_code += f"{line_num:>4} | {line}"
                concatenated_code += "```\n"

        prompt = prompt_template.replace('# placeholder_for_diff', git_diff_output)
        prompt = prompt.replace('# placeholder_for_codes', concatenated_code)

        batch_number = i // max_files_per_request + 1
        print(f"Requesting to OpenAI API({batch_number}/{total_batches})...")

        # Save the prompt to a file
        prompt_file_name = f"prompt_{batch_number}.txt"
        with open(prompt_file_name, 'w', encoding='utf-8') as prompt_file:
            prompt_file.write(prompt)

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + os.getenv('AZURE_OPENAI_API_KEY')
            }
            data = {
                "messages": [
                    {"role": "system", "content": "You are a coding problem quality evaluator."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
            }
            response = requests.post(
                "https://pino-aistudio-gpt4.openai.azure.com/openai/deployments/pino-gpt4-32k/chat/completions?api-version=2024-02-15-preview",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            completion = response.json()

            if not completion.get('choices') or not completion['choices'][0].get('message'):
                raise ValueError("Invalid response format from OpenAI API.")

            gpt_evaluation_response = completion['choices'][0]['message']['content']
            processed_response = extract_json_from_result(gpt_evaluation_response)

            if is_valid_json_array(processed_response):
                all_responses.extend(json.loads(processed_response))
        except Exception as e:
            print(f"An error occurred: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'content'):
                print("Response content:", e.response.content)

    return json.dumps(all_responses, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze code using GPT.")
    parser.add_argument("directory", help="Path to the directory containing code files for analysis.")
    parser.add_argument("--analysis_result_json_file", help="Path to the file where the analysis result JSON will be saved.", default=None)
    parser.add_argument("--dry_run_file", help="Optional path to dry-run by logging the prompt sent to GPT, and stopping.", default=None)
    args = parser.parse_args()

    result = analyze_code_with_gpt(args.directory, args.dry_run_file)
    
    if args.dry_run_file:
        print('Dry run complete. Prompt logged to file.')
    elif args.analysis_result_json_file:
        with open(args.analysis_result_json_file, 'w') as f:
            f.write(result)
    else:
        print(result)
    