import streamlit as st
from pyswip import Prolog, Functor, Variable, Query

# --- Configuration ---
PROLOG_RULES_FILE = "rules.pl"
APPLICANT_ID = "applicant" # Consistent identifier used in Prolog facts

# --- Helper Functions ---

def check_eligibility(prolog_instance, applicant_details):
    """
    Asserts facts into Prolog, queries eligibility, and retracts facts.

    Args:
        prolog_instance: An initialized pyswip Prolog object.
        applicant_details (dict): A dictionary containing the applicant's info.

    Returns:
        bool: True if eligible, False otherwise.
        list: A list of asserted facts (for potential debugging/display).
    """
    asserted_facts = []
    # Convert boolean inputs to lowercase strings 'true'/'false' for Prolog
    prolog_bool = {True: 'true', False: 'false'}

    try:
        # 1. Assert facts dynamically based on input
        # Use a consistent applicant ID
        nationality_fact = f"nationality({APPLICANT_ID}, '{applicant_details['nationality'].lower()}')"
        prolog_instance.assertz(nationality_fact)
        asserted_facts.append(nationality_fact)

        job_offer_fact = f"has_job_offer({APPLICANT_ID}, {prolog_bool[applicant_details['has_job_offer']]})"
        prolog_instance.assertz(job_offer_fact)
        asserted_facts.append(job_offer_fact)

        salary_fact = f"salary_meets_minimum({APPLICANT_ID}, {prolog_bool[applicant_details['salary_meets_minimum']]})"
        prolog_instance.assertz(salary_fact)
        asserted_facts.append(salary_fact)

        skills_fact = f"has_required_skills({APPLICANT_ID}, {prolog_bool[applicant_details['has_required_skills']]})"
        prolog_instance.assertz(skills_fact)
        asserted_facts.append(skills_fact)

        record_fact = f"has_clean_record({APPLICANT_ID}, {prolog_bool[applicant_details['has_clean_record']]})"
        prolog_instance.assertz(record_fact)
        asserted_facts.append(record_fact)

        # Example Age Check (derived from input age)
        is_age_eligible = 18 <= applicant_details['age'] <= 60
        age_fact = f"age_eligible({APPLICANT_ID}, {prolog_bool[is_age_eligible]})"
        prolog_instance.assertz(age_fact)
        asserted_facts.append(age_fact)

        print("\n--- Asserted Facts ---")
        for fact in asserted_facts:
            print(fact)
        print("----------------------\n")


        # 2. Query the main eligibility rule
        query_string = f"is_eligible({APPLICANT_ID})"
        print(f"--- Running Query --- \n{query_string}\n---------------------")
        result = list(prolog_instance.query(query_string))
        print(f"--- Query Result --- \n{result}\n--------------------")


        # 3. Retract facts to clean up for the next check
        # Use _ as a wildcard to retract regardless of the second argument's value
        prolog_instance.retractall(f"nationality({APPLICANT_ID}, _)")
        prolog_instance.retractall(f"has_job_offer({APPLICANT_ID}, _)")
        prolog_instance.retractall(f"salary_meets_minimum({APPLICANT_ID}, _)")
        prolog_instance.retractall(f"has_required_skills({APPLICANT_ID}, _)")
        prolog_instance.retractall(f"has_clean_record({APPLICANT_ID}, _)")
        prolog_instance.retractall(f"age_eligible({APPLICANT_ID}, _)")

        return bool(result), asserted_facts # Eligible if the query succeeded (result list is not empty)

    except Exception as e:
        st.error(f"An error occurred during Prolog interaction: {e}")
        # Ensure cleanup happens even if there's an error during query
        try:
            prolog_instance.retractall(f"nationality({APPLICANT_ID}, _)")
            prolog_instance.retractall(f"has_job_offer({APPLICANT_ID}, _)")
            prolog_instance.retractall(f"salary_meets_minimum({APPLICANT_ID}, _)")
            prolog_instance.retractall(f"has_required_skills({APPLICANT_ID}, _)")
            prolog_instance.retractall(f"has_clean_record({APPLICANT_ID}, _)")
            prolog_instance.retractall(f"age_eligible({APPLICANT_ID}, _)")
        except Exception as cleanup_e:
            st.warning(f"Error during cleanup: {cleanup_e}") # Log or warn about cleanup issues
        return False, asserted_facts


# --- Streamlit User Interface ---

st.set_page_config(page_title="Legal Eligibility Checker", layout="centered")
st.title("📜 Legal Rule-Based Eligibility Checker")
st.markdown("Enter the applicant's details to check their eligibility based on predefined Prolog rules.")
st.markdown("_(Example: Simplified Work Visa)_")

with st.sidebar:
    st.image('vcet-logo@2x.png')
    
# --- Initialize Prolog ---
try:
    prolog = Prolog()
    prolog.consult(PROLOG_RULES_FILE)
    st.sidebar.success(f"Prolog engine initialized and rules loaded from '{PROLOG_RULES_FILE}'.")
    # Print available predicates (optional debug)
    # print("--- Loaded Predicates ---")
    # for pred in prolog.query("current_predicate(P/A)"):
    #    print(f"{pred['P']}/{pred['A']}")
    # print("-----------------------")

except Exception as e:
    st.error(f"Fatal Error: Could not initialize Prolog or load rules file '{PROLOG_RULES_FILE}'.")
    st.error(f"Details: {e}")
    st.error("Please ensure SWI-Prolog is installed and accessible, and the rules file exists.")
    st.stop() # Stop execution if Prolog setup fails


# --- Input Fields ---
with st.form("eligibility_form"):
    st.subheader("Applicant Information")

    nationality = st.text_input("Nationality", "CountryX")
    age = st.number_input("Age", min_value=0, max_value=120, value=30, step=1)

    st.markdown("**Conditions:**")
    has_job_offer = st.radio("Has a valid job offer?", (True, False), format_func=lambda x: 'Yes' if x else 'No', key='job')
    salary_meets_minimum = st.radio("Does the salary meet the minimum requirement?", (True, False), format_func=lambda x: 'Yes' if x else 'No', key='salary')
    has_required_skills = st.radio("Possesses the required skills/qualifications?", (True, False), format_func=lambda x: 'Yes' if x else 'No', key='skills')
    has_clean_record = st.radio("Has a clean criminal record?", (True, False), format_func=lambda x: 'Yes' if x else 'No', key='record')

    submitted = st.form_submit_button("Check Eligibility")

# --- Processing and Output ---
if submitted:
    applicant_data = {
        "nationality": nationality.strip(), # Basic sanitization
        "age": age,
        "has_job_offer": has_job_offer,
        "salary_meets_minimum": salary_meets_minimum,
        "has_required_skills": has_required_skills,
        "has_clean_record": has_clean_record
    }

    st.info("Checking eligibility against Prolog rules...")

    is_eligible, facts = check_eligibility(prolog, applicant_data)

    if is_eligible:
        st.success("✅ Eligible!")
        st.balloons()
    else:
        st.error("❌ Not Eligible.")
        st.markdown("The applicant did not meet all the required criteria defined in the Prolog rules.")

    # Optional: Display asserted facts for debugging/transparency
    with st.expander("Show Details (Prolog Facts Asserted for this Check)"):
        st.code("\n".join(facts), language="prolog")

st.sidebar.markdown("---")
st.sidebar.markdown("**About:** This app uses SWI-Prolog via `pyswip` to evaluate eligibility based on rules defined in `rules.pl`.")
