import {
    DISEASE_NAME,
    INTERVENTIONS,
    DEFAULT_COVERAGE,
    NULL_COVERAGE_CHANGES,
    CR1_COVERAGE_CHANGES,
    CR3_COVERAGE_CHANGES
} from './constants.js'


function populateCoverageOptions() {
    const coverageOptions = document.getElementById('coverageOptions');
    INTERVENTIONS.forEach(intervention => {
        const div = document.createElement('div');
        div.classList.add('form-group');
        
        const label = document.createElement('label');
        label.textContent = intervention;
        div.appendChild(label);

        const starting_input = document.createElement('input');
        starting_input.type = 'number';
        starting_input.classList.add('form-control', 'coverage-value');
        starting_input.id = `${intervention}-starting`;
        starting_input.value = DEFAULT_COVERAGE;
        starting_input.step = "0.01";
        starting_input.min = "0";
        starting_input.max = "1";
        starting_input.readOnly = true;
        div.appendChild(starting_input);

        const target_input = document.createElement('input');
        target_input.type = 'number';
        target_input.classList.add('form-control', 'coverage-value');
        target_input.id = `${intervention}-target`;
        target_input.value = DEFAULT_COVERAGE;
        target_input.step = "0.01";
        target_input.min = "0";
        target_input.max = "1";
        target_input.readOnly = true;
        div.appendChild(target_input);

        coverageOptions.appendChild(div);
    });
}


function handleInterventionChange() {
    const interventionSelection = document.querySelector('input[name="interventionOptions"]:checked').value;
    resetCoverages();
    if (interventionSelection == "NULL") {
        applyCoverageChanges(NULL_COVERAGE_CHANGES);
    } else if (interventionSelection === 'CR1') {
        applyCoverageChanges(CR1_COVERAGE_CHANGES);
    } else if (interventionSelection === 'CR3') {
        applyCoverageChanges(CR3_COVERAGE_CHANGES);
    };
    toggleFormDisable();
}

function toggleFormDisable(){
    const interventionSelection = document.querySelector('input[name="interventionOptions"]:checked').value;
    INTERVENTIONS.forEach(intervention => {
        const startId = `${intervention}-starting`
        const targetId = `${intervention}-target`
        if (interventionSelection === 'custom') {
            document.getElementById(startId).readOnly = false
            document.getElementById(targetId).readOnly = false
        } else {
            document.getElementById(startId).readOnly = true
            document.getElementById(targetId).readOnly = true
        }
    });
};


function resetCoverages() {
    INTERVENTIONS.forEach(intervention => {
        const targetNode = `${intervention}-target`;
        document.getElementById(targetNode).value = DEFAULT_COVERAGE;
    });
}

function applyCoverageChanges(changes) {
    Object.keys(changes).forEach(intervention => {
        const interventionID = `${intervention}-target`;
        document.getElementById(interventionID).value = changes[intervention];
    });
}

window.runModel = function() {
    const iso3 = document.getElementById('selectCountry').value
    fetch('asthma_baseline.json')
        .then(response => response.json())
        .then(data => {
            const botech = data;
            updateTimeHorizon(botech)
            changeCountry(botech, iso3)
            updateCoverages(botech)
            console.log(botech)
            postBotech(botech)
        })
}

function updateTimeHorizon(botech){
    let startTime = document.getElementById("startTime").value
    let endTime = document.getElementById("endTime").value
    startTime = parseInt(startTime, 10)
    endTime = parseInt(endTime, 10)
    botech.runtime.startYear = startTime
    botech.runtime.endYear = endTime
};

function changeCountry(modelData, newCountryISO3) {
    if (modelData.nodes) {
        modelData.nodes.forEach(node => {
            if (node.generate_array && node.generate_array.parameters) {
                if ('country' in node.generate_array.parameters) {
                    node.generate_array.parameters.country = newCountryISO3;
                }
            }
        });
    }

    if (modelData.links) {
        modelData.links.forEach(link => {
            if (link.generate_array && link.generate_array.parameters) {
                if ('country' in link.generate_array.parameters) {
                    link.generate_array.parameters.country = newCountryISO3;
                }
            }
        });
    }
}


function updateCoverages(botech) {
    INTERVENTIONS.forEach(
        function(element) {

            const sourceLabel = `${element}-starting`;
            let sourceValue = document.getElementById(sourceLabel).value
            sourceValue = parseInt(sourceValue, 10)
            const sourceNodeLabel = `${element}_StartingCoverage`

            const targetLabel = `${element}-target`;
            let targetValue = document.getElementById(targetLabel).value
            targetValue = parseInt(targetValue, 10)
            const targetNodeLabel = `${element}_Coverage`

            botech.nodes.forEach(
                function(node) {
                    if (node.label == sourceNodeLabel) {
                        node.generate_array.parameters.value = sourceValue;
                    } else if (node.label == targetNodeLabel) {
                        node.generate_array.parameters.value = targetValue;
                    }
                }
            )
        }
    )
};

function generateFileID() {
    const iso3 = document.getElementById('selectCountry').value
    const scenario = document.querySelector('input[name="interventionOptions"]:checked').value;
    const fileID = `${DISEASE_NAME}-${scenario}-${iso3}`
    return fileID
};

function postBotech(botech) {
  const file_id = generateFileID()
  const url = "https://api.forecasthealth.org/run/appendix_3"
  const requestBody = {
    data: botech,
    store: false,
    file_id: file_id
  };

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(requestBody)
  })
  .then(response => {
    if (response.ok) {
      return response.text();
    }
    throw new Error('Network response was not ok.');
  })
  .then(csvText => {
    console.log(csvText.split("\n").slice(0, 5).join("\n"))
  })
  .catch(error => {
    console.error('There has been a problem with your fetch operation:', error);
  });
}


fetch('metadata.json')
.then(response => response.json())
.then(data => {
    const selectCountry = document.getElementById('selectCountry');
    data.forEach(country => {
        let option = new Option(country.name, country.code);
        selectCountry.add(option);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    populateCoverageOptions();
    document.querySelectorAll('input[type=radio]').forEach(input => {
        input.addEventListener('change', handleInterventionChange);
    });
});


