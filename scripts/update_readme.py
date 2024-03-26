"""
update_readme.py

Take the results in JSON format,
render them as a markdown table,
append that table to the bottom of the README.md
"""
import json

def main():
    with open('results.json', 'r') as file:
        data = json.load(file)

    markdown_table = "# Test Results\n\n| Country | Scenario  | STATUS_CODE | HYL          |\n|---------|-----------|-------------|--------------|\n"
    for result in data:
        country = result["country"]
        for scenario, details in result["scenarios"].items():
            markdown_table += f"| {country} | {scenario} | {details['STATUS_CODE']} | {details['HYL']:.2f} |\n"

    with open('README.md', 'r') as file:
        readme_content = file.read()

    header_index = readme_content.find("# Test Results")
    if header_index != -1:
        readme_content = readme_content[:header_index]
    readme_content += markdown_table

    with open('README.md', 'w') as file:
        file.write(readme_content)


if __name__ == "__main__":
    main()
