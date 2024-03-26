import pandas as pd

INPUT_FILEPATH = "./data/asthma_avenir_results.csv"
OUTPUT_FILEPATH = "./data/asthma_avenir_results_formatted.json"


def main():
    df = pd.read_csv(INPUT_FILEPATH, skiprows=[0])
    required_columns = [2, 13, 14, 15]

    records = []
    scenarios = ['CRNullAsthma', 'CR1', 'CR3']

    for _, row in df.iterrows():
        if not isinstance(row[2], float):
            for index, scenario in enumerate(scenarios, start=1):
                records.append({
                    'ISO3': row[2],
                    'scenario': scenario,
                    'HYL': row[required_columns[index]],
                } 
            )

    clean_data = pd.DataFrame(records)
    clean_data.to_json(OUTPUT_FILEPATH, orient='records', indent=4)


if __name__ == "__main__":
    main()
