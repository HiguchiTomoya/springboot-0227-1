import re
import json
import sys

# Remove all reviews not within changed lines of files.
# Compare the 'git diff' result & the review comments from te OpenAI.
# If a comment is not in the git diff, the comment will be removed from the output.
# Unless so, GithubAPI would reject the request.
def filter_comments_by_diff(diff_path, result_path):
    with open(diff_path, 'r') as file:
        diff_text = file.read()

    with open(result_path, 'r') as file:
        result_data = file.read()

    # list all chaged lines of code and paths from the diff. 
    changed_files = {}
    for match in re.finditer(r'^\+\+\+ b/(.+)$\n@@ -\d+,\d+ \+(\d+),(\d+) @@', diff_text, re.MULTILINE):
        file_path = match.group(1)
        start_line = int(match.group(2))
        num_lines = int(match.group(3))
        end_line = start_line + num_lines - 1
        if file_path not in changed_files:
            changed_files[file_path] = []
        changed_files[file_path].append((start_line, end_line))
    

    result_json = json.loads(result_data)

    # keep all reviews within the changed_files.
    filtered_comments = []
    for comment in result_json:
        file_path = comment['file_path']
        if file_path in changed_files:
            comment_line = comment['line']
            for start_line, end_line in changed_files[file_path]:
                if start_line <= comment_line <= end_line:
                    filtered_comments.append(comment)
                    break

    result_json = filtered_comments

    return json.dumps(result_json, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) < 3:
        print("Usage: python validate_review_json.py <diff_file> <result_file>")
        sys.exit(1)

    diff_path = sys.argv[1]
    result_path = sys.argv[2]
    filtered_result = filter_comments_by_diff(diff_path, result_path)
    print(filtered_result)

if __name__ == '__main__':
    main()
