"""
run_models.py

Runs a list of models for a list of scenarios.
"""
import requests
import json
from country_metadata import get_countries_by_tags
SCENARIO_MAPPING = {
    "baseline": {},
    "null": {},
    "cr1": {},
    "cr3": {}
}


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
    ...


def main():
    countries = get_countries_by_tags("appendix_3")["1"]
    with open("asthma_baseline.json", "r") as f:
        botech = json.load(f)
    for country in countries:
        change_country(botech, country.alpha3)
        convert_scenario(botech, "baseline")
        convert_scenario(botech, "null")
        convert_scenario(botech, "cr1")
        convert_scenario(botech, "cr3")


if __name__ == "__main__":
    main()
