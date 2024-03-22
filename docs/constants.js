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


export const CR1_COVERAGE_CHANGES = {
    'AsthmaOralPrednisolone': 0.95,
};

export const CR3_COVERAGE_CHANGES = {
    'LowDoseBeclom': 0.95,
    'HighDoseBeclom': 0.95,
    'InhaledShortActingBeta': 0.95,
};
