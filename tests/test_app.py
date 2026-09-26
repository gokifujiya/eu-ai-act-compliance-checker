from app import (
    RULES,
    go_back,
    new_state,
    render_question,
    restart,
    submit_answer,
)


def option_label(question_id, option_key):
    """Return the UI label for a rule option."""
    return RULES[question_id]["options"][option_key]["label"]


def test_new_state_starts_at_e1_with_empty_history():
    state = new_state()

    assert state["current_question"] == "E1"
    assert state["history"] == []
    assert state["finished"] is False
    assert state["original_entity"] is None
    assert state["current_entity"] is None


def test_render_e1_uses_single_choice():
    state = new_state()

    heading, radio, checkboxes, button = render_question(state)

    assert "E1" in heading
    assert radio["visible"] is True
    assert checkboxes["visible"] is False
    assert button["visible"] is True


def test_deployer_e1_advances_and_creates_history():
    state = new_state()

    result = submit_answer(
        option_label("E1", "deployer"),
        [],
        state,
    )

    new_state_value = result[0]

    assert new_state_value["original_entity"] == "deployer"
    assert new_state_value["current_entity"] == "deployer"
    assert new_state_value["current_question"] == "E2"
    assert len(new_state_value["history"]) == 1

    # Back button update returned by submit_answer()
    assert result[5]["visible"] is True


def test_back_from_e2_restores_e1():
    state = new_state()

    result = submit_answer(
        option_label("E1", "deployer"),
        [],
        state,
    )
    state = result[0]

    result = go_back(state)
    state = result[0]

    assert state["current_question"] == "E1"
    assert state["history"] == []
    assert state["original_entity"] is None
    assert state["current_entity"] is None
    assert state["finished"] is False

    # Back must disappear at E1.
    assert result[5]["visible"] is False


def test_restart_from_e2_restores_clean_e1():
    state = new_state()

    result = submit_answer(
        option_label("E1", "deployer"),
        [],
        state,
    )
    state = result[0]

    result = restart()
    state = result[0]

    assert state["current_question"] == "E1"
    assert state["history"] == []
    assert state["original_entity"] is None
    assert state["current_entity"] is None
    assert state["status_changes"] == []
    assert state["obligations"] == []
    assert state["legal_basis"] == []
    assert state["finished"] is False

    # Back must disappear after Restart.
    assert result[5]["visible"] is False


def test_back_then_answer_again_works():
    state = new_state()

    # E1 -> E2
    result = submit_answer(
        option_label("E1", "deployer"),
        [],
        state,
    )
    state = result[0]

    # E2 -> E1
    result = go_back(state)
    state = result[0]

    # E1 -> E2 again
    result = submit_answer(
        option_label("E1", "deployer"),
        [],
        state,
    )
    state = result[0]

    assert state["current_question"] == "E2"
    assert state["original_entity"] == "deployer"
    assert state["current_entity"] == "deployer"
    assert len(state["history"]) == 1
    assert result[5]["visible"] is True
