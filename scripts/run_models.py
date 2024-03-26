"""
run_models.py

Runs a list of models for a list of scenarios.
"""
import requests
import json
from country_metadata import get_countries_by_tags


def change_country(botech: dict, iso3: str):
    for node in botech["nodes"]:
        generate_array = node.get("generate_array")
        if generate_array:
            parameters = generate_array.get("parameters", {})
            if "country" in parameters.keys():
                parameters["country"] = iso3

    for edge in botech["links"]:
        generate_array = edge.get("generate_array")
        if generate_array:
            parameters = generate_array.get("parameters", {})
            if "country" in parameters.keys():
                parameters["country"] = iso3


def convert_scenario(botech: dict, scenario: str):
    if scenario == "baseline":
        for node in botech["nodes"]:
            if node["id"] == "LowDoseBeclom_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.05
            if node["id"] == "HighDoseBeclom_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.05
            if node["id"] == "AsthmaOralPrednisolone_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.05
            if node["id"] == "InhaledShortActingBeta_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.05

    elif scenario == "null":
        for node in botech["nodes"]:
            if node["id"] == "LowDoseBeclom_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.00
            if node["id"] == "HighDoseBeclom_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.00
            if node["id"] == "AsthmaOralPrednisolone_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.00
            if node["id"] == "InhaledShortActingBeta_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.00

    elif scenario == "cr1":
        for node in botech["nodes"]:
            if node["id"] == "LowDoseBeclom_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.05
            if node["id"] == "HighDoseBeclom_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.05
            if node["id"] == "AsthmaOralPrednisolone_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.95
            if node["id"] == "InhaledShortActingBeta_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.05

    elif scenario == "cr3":
        for node in botech["nodes"]:
            if node["id"] == "LowDoseBeclom_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.95
            if node["id"] == "HighDoseBeclom_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.95
            if node["id"] == "AsthmaOralPrednisolone_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.05
            if node["id"] == "InhaledShortActingBeta_Coverage":
                node["generate_array"]["parameters"]["value"] = 0.95

    else:
        raise KeyError(f"{scenario} is not recognised")


def change_time_horizon(botech: dict, start_year: int, end_year: int):
    botech["runtime"]["startYear"] = start_year
    botech["runtime"]["endYear"] = end_year


def make_api_request(session, botech: dict, scenario: str, iso3: str):
    URL = "https://api.forecasthealth.org/run/appendix_3"
    request = {
        "data": botech,
        "store": False,
        "file_id": f"test_{scenario}_{iso3}"
    }
    response = session.post(url=URL, json=request)
    return response


def main():
    results = []
    countries = get_countries_by_tags("appendix_3")["1"]
    with open("asthma_baseline.json", "r") as f:
        botech = json.load(f)

    with requests.Session() as session:
        for country in countries:
            change_country(botech, country.alpha3)
            change_time_horizon(botech, 2020, 2021)
            country_results = []
            country_results.append(country.alpha3)
            for scenario in ["baseline", "null", "cr1", "cr3"]:
                print(f"Working on {country.alpha3} - {scenario}")
                convert_scenario(botech, scenario)
                response = make_api_request(session, botech, scenario, country.alpha3)
                country_results.append(response.status_code)
            results.append(tuple(country_results))
            with open("results.json", "w") as file:
                json.dump(results, file, indent=4)


if __name__ == "__main__":
    main()
