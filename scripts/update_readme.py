"""
update_readme.py

Take the results in JSON format,
render them as a markdown table,
append that table to the bottom of the README.md
"""
import json

def load_avenir_results(filename):
    with open(filename, 'r') as file:
        avenir_data = json.load(file)
    avenir_results = {(d['ISO3'], d['scenario']): d['HYL'] for d in avenir_data}
    return avenir_results

def format_hyl(value):
    return "{:,}".format(int(value))

def main():
    avenir_results = load_avenir_results('data/asthma_avenir_results_formatted.json')

    with open('results.json', 'r') as file:
        data = json.load(file)

    markdown_table = "# Test Results\n\n| Country | Scenario  | STATUS_CODE | HYL          | Avenir HYL    | Ratio         |\n|---------|-----------|-------------|--------------|---------------|---------------|\n"
    for result in data:
        country = result["country"]
        for scenario, details in result["scenarios"].items():
            key = (country, scenario)
            if key in avenir_results:
                hyl_formatted = format_hyl(details['HYL'])
                avenir_hyl_formatted = format_hyl(avenir_results[key])
                ratio = "{:.2f}".format(details['HYL'] / avenir_results[key])
                markdown_table += f"| {country} | {scenario} | {details['STATUS_CODE']} | {hyl_formatted} | {avenir_hyl_formatted} | {ratio} |\n"

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
