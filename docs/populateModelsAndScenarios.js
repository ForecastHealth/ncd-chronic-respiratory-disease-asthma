document.addEventListener('DOMContentLoaded', function() {
    const modelSelect = document.getElementById('model');
    const modelDescriptionElement = document.getElementById('modelDescription');
    const scenarioSelect = document.getElementById('scenario');
    const scenarioDescriptionElement = document.getElementById('scenarioDescription');
    const entrypointsSection = document.getElementById('entrypointsSection');
    const entrypointsTable = document.getElementById('entrypointsTable');
    const startYearInput = document.getElementById('startYear');
    const endYearInput = document.getElementById('endYear');
    const countrySelect = document.getElementById('country');  // Country select dropdown

    function updateScenarios(selectedModelPath) {
        if (!scenarioSelect) {
            console.error('Scenario select element not found in the DOM');
            return;
        }

        const selectedModelName = selectedModelPath.split('/').pop();  // Extract filename
        fetch('./list_of_scenarios.json')
            .then(response => response.json())
            .then(data => {
                const scenarios = data[selectedModelName] || [];
                scenarioSelect.innerHTML = '';  // Clear existing options
                
                // Add other scenarios
                scenarios.forEach(scenario => {
                    const option = document.createElement('option');
                    option.value = scenario.path;
                    option.text = scenario.name;
                    scenarioSelect.appendChild(option);
                });
                
                // Add Custom scenario
                const customOption = document.createElement('option');
                customOption.value = 'custom';
                customOption.text = 'Custom';
                scenarioSelect.appendChild(customOption);

                // Fetch description for the first scenario if available
                if (scenarios.length > 0) {
                    fetchScenarioDescription(scenarios[0].path);
                    handleScenarioLockYears(scenarios[0].path);
                    updateEntrypoints(selectedModelPath, scenarios[0].path);
                }
            })
            .catch(error => console.error('Error fetching scenario list:', error));
    }

    function fetchModelDescription(modelPath) {
        if (!modelDescriptionElement) {
            console.warn('Model description element not found in the DOM');
            return;
        }

        fetch(modelPath)
            .then(response => response.json())
            .then(data => {
                const description = data.metadata && data.metadata.description 
                    ? data.metadata.description 
                    : "No description available";
                modelDescriptionElement.textContent = description;
            })
            .catch(error => {
                console.error('Error fetching model description:', error);
                modelDescriptionElement.textContent = "No description available";
            });
    }

    function updateYears(modelPath) {
        fetch(modelPath)
            .then(response => response.json())
            .then(data => {
                const startYear = data.runtime.startYear;
                const endYear = data.runtime.endYear;
                startYearInput.value = startYear;
                endYearInput.value = endYear;
            })
            .catch(error => {
                console.error('Error fetching model description:', error);
                modelDescriptionElement.textContent = "No description available";
            });
    }

    function fetchScenarioDescription(scenarioPath) {
        if (!scenarioDescriptionElement) {
            console.warn('Scenario description element not found in the DOM');
            return;
        }

        if (scenarioPath === 'custom') {
            scenarioDescriptionElement.textContent = "Custom scenario with all editable entrypoints.";
            return;
        }

        fetch(scenarioPath)
            .then(response => response.json())
            .then(data => {
                const description = data.description || "No description available";
                scenarioDescriptionElement.textContent = description;
            })
            .catch(error => {
                console.error('Error fetching scenario description:', error);
                scenarioDescriptionElement.textContent = "No description available";
            });
    }

    function updateEntrypoints(modelPath, scenarioPath) {
        fetch(modelPath)
            .then(response => response.json())
            .then(modelData => {
                if (modelData.entrypoints && modelData.entrypoints.length > 0) {
                    const entrypoints = modelData.entrypoints.filter(entry => entry.id !== "COUNTRY");
                    
                    fetch(scenarioPath)
                        .then(response => response.json())
                        .then(scenarioData => {
                            const selectedCountry = countrySelect ? countrySelect.value : '';
                            const appliedScenario = getAppliedScenario(scenarioData, selectedCountry);
                            renderEntrypoints(entrypoints, appliedScenario);
                        })
                        .catch(error => {
                            console.error('Error fetching scenario data:', error);
                            renderEntrypoints(entrypoints);
                        });
                    
                    entrypointsSection.style.display = 'block';
                } else {
                    entrypointsSection.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error fetching model data:', error);
                entrypointsSection.style.display = 'none';
            });
    }

    function getAppliedScenario(scenarioData, country) {
        // Check country_overrides
        if (scenarioData.country_overrides && scenarioData.country_overrides[country]) {
            return { ...scenarioData.defaults, ...scenarioData.country_overrides[country] };
        }
        
        // Check scenario_groups
        for (const group in scenarioData.scenario_groups) {
            if (scenarioData.scenario_groups[group].countries.includes(country)) {
                return { ...scenarioData.defaults, ...scenarioData.scenario_groups[group].parameters };
            }
        }
        
        // Use defaults
        return scenarioData.defaults;
    }

    function renderEntrypoints(entrypoints, appliedScenario) {
        const tbody = entrypointsTable.querySelector('tbody');
        tbody.innerHTML = ''; // Clear existing rows

        entrypoints.forEach(entry => {
            const row = document.createElement('tr');
            
            // ID cell
            const idCell = document.createElement('td');
            idCell.textContent = entry.id;
            row.appendChild(idCell);

            // Description cell
            const descCell = document.createElement('td');
            descCell.textContent = entry.description || '';
            row.appendChild(descCell);

            // Value cell
            const valueCell = document.createElement('td');
            const valueInput = document.createElement('input');
            valueInput.type = 'text';
            
            valueInput.value = appliedScenario[entry.id] || entry.value;
            valueInput.disabled = appliedScenario.hasOwnProperty(entry.id);
            
            valueInput.addEventListener('change', function() {
                console.log(`Updated ${entry.id} to ${this.value}`);
            });
            valueCell.appendChild(valueInput);
            row.appendChild(valueCell);

            tbody.appendChild(row);
        });
    }

    function handleScenarioLockYears(scenarioPath) {
        if (scenarioPath === 'custom') {
            startYearInput.disabled = false;
            endYearInput.disabled = false;
            return;
        }

        fetch(scenarioPath)
            .then(response => response.json())
            .then(data => {
                const lockYears = data.lock_years || false;
                startYearInput.disabled = lockYears;
                endYearInput.disabled = lockYears;
            })
            .catch(error => {
                console.error('Error fetching scenario data:', error);
                startYearInput.disabled = false;
                endYearInput.disabled = false;
            });
    }

    function fetchModelsAndScenarios() {
        if (!modelSelect) {
            console.error('Model select element not found in the DOM');
            return;
        }

        fetch('./list_of_models.json')
            .then(response => response.json())
            .then(data => {
                const models = data.models;
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.path;
                    option.text = model.name;
                    modelSelect.appendChild(option);
                });

                if (models.length > 0) {
                    modelSelect.value = models[0].path;
                    updateYears(models[0].path);
                    updateScenarios(models[0].path);
                    fetchModelDescription(models[0].path);
                }
            })
            .catch(error => console.error('Error fetching model list:', error));
    }

    // Event listener for model selection change
    if (modelSelect) {
        modelSelect.addEventListener('change', function() {
            const selectedModelPath = this.value;
            updateYears(selectedModelPath);
            updateScenarios(selectedModelPath);
            fetchModelDescription(selectedModelPath);
        });
    } else {
        console.error('Model select element not found in the DOM');
    }

    // Event listener for scenario selection change
    if (scenarioSelect) {
        scenarioSelect.addEventListener('change', function() {
            const selectedScenarioPath = this.value;
            fetchScenarioDescription(selectedScenarioPath);
            updateEntrypoints(modelSelect.value, selectedScenarioPath);
            handleScenarioLockYears(selectedScenarioPath);
        });
    } else {
        console.error('Scenario select element not found in the DOM');
    }

    // Event listener for country selection change
    if (countrySelect) {
        countrySelect.addEventListener('change', function() {
            const selectedModelPath = modelSelect ? modelSelect.value : '';
            const selectedScenarioPath = scenarioSelect ? scenarioSelect.value : '';
            
            // Update the entrypoints based on the selected country
            updateEntrypoints(selectedModelPath, selectedScenarioPath);
        });
    } else {
        console.error('Country select element not found in the DOM');
    }

    // Handle generate button click
    const generateButton = document.getElementById('generate');
    if (generateButton) {
        generateButton.addEventListener('click', function() {
            const selectedModelPath = modelSelect ? modelSelect.value : '';
            const selectedScenarioPath = scenarioSelect ? scenarioSelect.value : '';
            console.log('Generate button clicked');
            console.log('Selected model:', selectedModelPath);
            console.log('Selected scenario:', selectedScenarioPath);
        });
    } else {
        console.error('Generate button not found in the DOM');
    }

    // Fetch models and scenarios on initial load
    fetchModelsAndScenarios();
});
