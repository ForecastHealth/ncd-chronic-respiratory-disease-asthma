export const DISEASE_NAME = "asthma"

export const INTERVENTIONS = [
    'LowDoseBeclom',
    'HighDoseBeclom',
    'AsthmaOralPrednisolone',
    'InhaledShortActingBeta'
];

export const TARGET_COVERAGES = {
    'LowDoseBeclom': 'LowDoseBeclom_Coverage',
    'HighDoseBeclom': 'HighDoseBeclom_Coverage',
    'AsthmaOralPrednisolone': 'AsthmaOralPrednisolone_Coverage',
    'InhaledShortActingBeta': 'InhaledShortActingBeta_Coverage'
};

export const STARTING_COVERAGES = {
    'LowDoseBeclom': 'LowDoseBeclom_StartingCoverage',
    'HighDoseBeclom': 'HighDoseBeclom_StartingCoverage',
    'AsthmaOralPrednisolone': 'AsthmaOralPrednisolone_StartingCoverage',
    'InhaledShortActingBeta': 'InhaledShortActingBeta_StartingCoverage'
};

export const DEFAULT_COVERAGE = 0.05;

export const NULL_COVERAGE_CHANGES = {
    'AsthmaOralPrednisolone': 0.00,
    'LowDoseBeclom': 0.00,
    'HighDoseBeclom': 0.00,
    'InhaledShortActingBeta': 0.00,
}

export const CR1_COVERAGE_CHANGES = {
    'AsthmaOralPrednisolone': 0.95,
};

export const CR3_COVERAGE_CHANGES = {
    'LowDoseBeclom': 0.95,
    'HighDoseBeclom': 0.95,
    'InhaledShortActingBeta': 0.95,
};

export const RESULTS_QUERY = `
SELECT strftime('%Y', timestamp) AS year,
       element_label,
       AVG(value) AS "AVG(value)"
FROM results
WHERE event_type IN ('BALANCE_SET')
AND element_label IN ('DsFreeSus', 'DsFreeSus -> AsthmaEpsd', 'AsthmaEpsd',
                      'AsthmaEpsd -> AsthmaEpsd Mortality', 'Deceased',
                      'DsFreeSus -> DsFreeSus HYL', 'AsthmaEpsd -> AsthmaEpsd HYL')
GROUP BY strftime('%Y', timestamp), element_label
ORDER BY "AVG(value)" DESC
`
