import json
from pathlib import Path
from src.legal_text import get_obligation_provision


BASE_DIR = Path(__file__).resolve().parent.parent
RULES_PATH = BASE_DIR / "data" / "processed" / "compliance_rules.json"


def load_rules():
    """Load compliance decision rules."""
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ask_single_choice(question_data):
    """Ask a single-choice question."""
    options = list(question_data["options"].items())

    for number, (_, option_data) in enumerate(options, start=1):
        print(f"{number}. {option_data['label']}")

    while True:
        choice = input("\nSelect an option: ").strip()

        try:
            number = int(choice)

            if 1 <= number <= len(options):
                return [options[number - 1]]

        except ValueError:
            pass

        print("Please enter a valid number.")


def ask_multiple_choice(question_data):
    """Ask a multiple-choice question."""
    options = list(question_data["options"].items())

    for number, (_, option_data) in enumerate(options, start=1):
        print(f"{number}. {option_data['label']}")

    while True:
        raw = input(
            "\nSelect one or more options separated by commas: "
        ).strip()

        try:
            numbers = [int(x.strip()) for x in raw.split(",")]

            if all(1 <= n <= len(options) for n in numbers):
                selected = [options[n - 1] for n in numbers]

                # "None of the above" cannot be combined with another answer.
                keys = [key for key, _ in selected]

                if "none" in keys and len(keys) > 1:
                    print(
                        "'None of the above' cannot be selected "
                        "with another option."
                    )
                    continue

                return selected

        except ValueError:
            pass

        print("Please enter valid option numbers.")


def ask_question(question_id, rules, state):
    """Display and ask one questionnaire node."""
    question_data = rules[question_id]

    if question_id in ("S1", "R4"):
        current_entity = state["current_entity"]

        filtered_options = {
            key: option_data
            for key, option_data in question_data["options"].items()
            if "applies_to" not in option_data
            or current_entity in option_data["applies_to"]
        }

        question_data = question_data.copy()
        question_data["options"] = filtered_options

    print(f"\n--- {question_id}: {question_data['section']} ---")
    print(f"\n{question_data['question']}\n")

    if question_data["type"] == "single_choice":
        return ask_single_choice(question_data)

    if question_data["type"] == "multiple_choice":
        return ask_multiple_choice(question_data)

    raise ValueError(
        f"Unsupported question type: {question_data['type']}"
    )


def update_state(question_id, selected, rules, state):
    """Store answers, obligations, status changes and legal references."""
    state["answers"][question_id] = [
        key for key, _ in selected
    ]

    if question_id == "E1":

        entity_key = selected[0][0]
        state["original_entity"] = entity_key
        state["current_entity"] = entity_key

    if question_id == "E2":
        selected_keys = [key for key, _ in selected]
        has_modification = "none" not in selected_keys

        if has_modification:
            if state["current_entity"] == "provider":
                if "Handover" not in state["obligations"]:
                    state["obligations"].append("Handover")
            else:
                state["current_entity"] = "provider"

                if "AI Literacy" not in state["obligations"]:
                    state["obligations"].append("AI Literacy")

    if question_id == "HR1":
        selected_keys = [key for key, _ in selected]
        is_high_risk = "none" not in selected_keys

        if is_high_risk and state["current_entity"] != "provider":
            state["current_entity"] = "provider"

            if "Become a Provider" not in state["status_changes"]:
                state["status_changes"].append("Become a Provider")

            if "AI Literacy" not in state["obligations"]:
                state["obligations"].append("AI Literacy")

    if question_id == "HR3":
        selected_keys = [key for key, _ in selected]
        is_high_risk = "yes" in selected_keys

        if is_high_risk and state["current_entity"] != "provider":
            state["current_entity"] = "provider"

            if "Become a Provider" not in state["status_changes"]:
                state["status_changes"].append("Become a Provider")

            if "AI Literacy" not in state["obligations"]:
                state["obligations"].append("AI Literacy")

    for _, option_data in selected:
        if "set_entity" in option_data:
            state["current_entity"] = option_data["set_entity"]

        # Add obligations
        for obligation in option_data.get("obligations", []):
            # Article 6(4) obligations apply only to Providers at HR5.
            provider_only_hr5_obligations = {
                "Document Non-High-Risk Assessment",
                "Register in EU Database",
            }

            if (
                question_id == "HR5"
                and obligation in provider_only_hr5_obligations
                and state["current_entity"] != "provider"
            ):
                continue

            if obligation not in state["obligations"]:
                state["obligations"].append(obligation)

        # Add status changes
        for status_change in option_data.get("status_changes", []):
            # An original Provider does not "Become a Provider" at E2.
            if (
                question_id == "E2"
                and status_change == "Become a Provider"
                and state["original_entity"] == "provider"
            ):
                continue

            if status_change not in state["status_changes"]:
                state["status_changes"].append(status_change)

    # Add legal references
    for source in rules[question_id].get("legal_basis", []):
        if source not in state["legal_basis"]:
            state["legal_basis"].append(source)


def determine_next(question_id, selected, state):
    """Determine the next questionnaire node."""

    # After R4, only high-risk Deployers continue to R5.
    if question_id == "R4":
        is_high_risk = "High risk" in state["status_changes"]
        is_deployer = state["current_entity"] == "deployer"

        if is_high_risk and is_deployer:
            return "R5"

        return "END"

    # At S1, the GPAI branch takes precedence because it must first
    # pass through the systemic-risk assessment at R1.
    if question_id == "S1":
        selected_keys = [key for key, _ in selected]

        if "gpai_eu_market" in selected_keys:
            hr2_answers = state["answers"].get("HR2", [])
            hr6_answers = state["answers"].get("HR6", [])

            matched_hr2 = (
                bool(hr2_answers)
                and "none" not in hr2_answers
            )
            matched_hr6 = (
                bool(hr6_answers)
                and "none" not in hr6_answers
            )

            if matched_hr2 or matched_hr6:
                if (
                    "High risk Exception"
                    not in state["status_changes"]
                ):
                    state["status_changes"].append(
                        "High risk Exception"
                    )
                return "END"

            return "R1"

        if "none" in selected_keys:
            return "END"

        return "R2"

    # At R2, complete scope exclusions take precedence over
    # exclusions that still proceed to the prohibited-practices check.
    if question_id == "R2":
        selected_keys = [key for key, _ in selected]

        if (
            "military" in selected_keys
            or "third_country_public_authorities" in selected_keys
        ):
            return "END"

        return "R3"

    for _, option_data in selected:
        if "next" in option_data:
            next_question = option_data["next"]

            # Only Providers and Deployers proceed to R4.
            if next_question == "R4":
                if state["current_entity"] not in ("provider", "deployer"):
                    return "END"

            return next_question

    return None


def print_state(state):
    """Show the current assessment state."""
    print("\n--- Current assessment ---")

    print(f"\nOriginal entity: {state['original_entity']}")
    print(f"Current entity: {state['current_entity']}")

    print("Answers:")
    for question_id, answers in state["answers"].items():
        print(f"- {question_id}: {', '.join(answers)}")

    if state["status_changes"]:
        print("\nStatus changes:")
        for status_change in state["status_changes"]:
            print(f"- {status_change}")

    if state["obligations"]:
        print("\nObligations:")

        for obligation in state["obligations"]:
            print(f"\n- {obligation}")

            provision = get_obligation_provision(obligation)

            if provision is not None:
                print(f"  Legal provision: {provision['reference']}")
                print("  Relevant text:")
                print(provision["text"])

    if state["legal_basis"]:
        print("\nRelevant legal references:")
        for source in state["legal_basis"]:
            print(f"- {source}")


def main():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": None,
        "current_entity": None,
        "status_changes": [],
        "obligations": [],
        "legal_basis": []
    }

    current_question = "E1"

    while current_question != "END":
        selected = ask_question(current_question, rules, state)

        update_state(
            current_question,
            selected,
            rules,
            state
        )

        next_question = determine_next(current_question, selected, state)

        if next_question is None:
            print(
                "\nThis branch is not implemented yet."
            )
            break

        if next_question != "END" and next_question not in rules:
            print(
                f"\nNext question is {next_question}, "
                "but it has not been implemented yet."
            )
            break

        current_question = next_question

    print_state(state)


if __name__ == "__main__":
    main()
