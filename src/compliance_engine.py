import json
from pathlib import Path


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


def ask_question(question_id, rules):
    """Display and ask one questionnaire node."""
    question_data = rules[question_id]

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

    for _, option_data in selected:
        # Add obligations
        for obligation in option_data.get("obligations", []):
            if obligation not in state["obligations"]:
                state["obligations"].append(obligation)

        # Add status changes
        for status_change in option_data.get("status_changes", []):
            if status_change not in state["status_changes"]:
                state["status_changes"].append(status_change)

    # Add legal references
    for source in rules[question_id].get("legal_basis", []):
        if source not in state["legal_basis"]:
            state["legal_basis"].append(source)


def determine_next(selected):
    """Determine the next questionnaire node."""
    for _, option_data in selected:
        if "next" in option_data:
            return option_data["next"]

    return None


def print_state(state):
    """Show the current assessment state."""
    print("\n--- Current assessment ---")

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
            print(f"- {obligation}")

    if state["legal_basis"]:
        print("\nRelevant legal references:")
        for source in state["legal_basis"]:
            print(f"- {source}")


def main():
    rules = load_rules()

    state = {
        "answers": {},
        "status_changes": [],
        "obligations": [],
        "legal_basis": []
    }

    current_question = "E1"

    while current_question != "END":
        selected = ask_question(current_question, rules)

        update_state(
            current_question,
            selected,
            rules,
            state
        )

        next_question = determine_next(selected)

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
