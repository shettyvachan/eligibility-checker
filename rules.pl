% --- Simplified Work Visa Eligibility Rules ---

% Define dynamic predicates for facts that will be asserted from Python.
% These represent the applicant's details.
:- dynamic nationality/2.       % nationality(applicant, Country)
:- dynamic has_job_offer/2.     % has_job_offer(applicant, boolean)
:- dynamic salary_meets_minimum/2. % salary_meets_minimum(applicant, boolean)
:- dynamic has_required_skills/2. % has_required_skills(applicant, boolean)
:- dynamic has_clean_record/2.  % has_clean_record(applicant, boolean)
:- dynamic age_eligible/2.      % age_eligible(applicant, boolean) % Example: age between 18 and 60

% --- Eligibility Rule ---
% An applicant is eligible if they meet all the necessary conditions.

is_eligible(Applicant) :-
    write_ln('Checking eligibility rules...'), % Debugging output
    has_job_offer(Applicant, true),
    write_ln('  - Job offer check: PASSED'),
    salary_meets_minimum(Applicant, true),
    write_ln('  - Salary check: PASSED'),
    has_required_skills(Applicant, true),
    write_ln('  - Skills check: PASSED'),
    has_clean_record(Applicant, true),
    write_ln('  - Criminal record check: PASSED'),
    age_eligible(Applicant, true),
    write_ln('  - Age check: PASSED'),
    nationality_permits_visa(Applicant), % Check if nationality is generally allowed
    write_ln('  - Nationality check: PASSED'),
    write_ln('Eligibility Check Successful!'). % Final success message

% Rule for specific nationalities (example)
% This could be expanded with many more rules or data lookups.
nationality_permits_visa(Applicant) :-
    nationality(Applicant, Country),
    \+ restricted_nationality(Country). % Succeeds if the country is NOT restricted

% Define restricted nationalities (example)
restricted_nationality('CountryZ').
% restricted_nationality('CountryW').

% --- Helper rule for debugging/showing failure points ---
% (Optional: More complex to implement fully with pyswip feedback)
% You could define specific failure rules, but simply checking the main
% rule's success/failure is often sufficient for basic use cases.