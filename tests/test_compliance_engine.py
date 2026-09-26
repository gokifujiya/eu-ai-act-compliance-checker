import json

from src.compliance_engine import determine_next, print_state, update_state


def load_rules():
    with open(
        "data/processed/compliance_rules.json",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def test_s1_gpai_precedence_is_order_independent():
    rules = load_rules()
    options = rules["S1"]["options"]

    state = {
        "answers": {},
        "original_entity": "provider",
        "current_entity": "provider",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    ai_system = (
        "ai_system_eu_market",
        options["ai_system_eu_market"],
    )
    gpai = (
        "gpai_eu_market",
        options["gpai_eu_market"],
    )

    assert determine_next(
        "S1",
        [ai_system, gpai],
        state,
    ) == "R1"

    assert determine_next(
        "S1",
        [gpai, ai_system],
        state,
    ) == "R1"


def test_r2_complete_exclusion_precedence_is_order_independent():
    rules = load_rules()
    options = rules["R2"]["options"]

    state = {
        "answers": {},
        "original_entity": "provider",
        "current_entity": "provider",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    open_source = (
        "open_source",
        options["open_source"],
    )
    military = (
        "military",
        options["military"],
    )

    assert determine_next(
        "R2",
        [open_source, military],
        state,
    ) == "END"

    assert determine_next(
        "R2",
        [military, open_source],
        state,
    ) == "END"


def test_hr5_high_risk_deployer_remains_deployer():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [
        (
            "yes",
            rules["HR5"]["options"]["yes"],
        )
    ]

    update_state("HR5", selected, rules, state)

    assert state["current_entity"] == "deployer"
    assert "High risk" in state["status_changes"]
    assert "Become a Provider" not in state["status_changes"]
    assert state["obligations"] == ["AI Literacy"]


def test_hr6_none_preserves_product_manufacturer():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "product_manufacturer",
        "current_entity": "product_manufacturer",
        "status_changes": [],
        "obligations": [],
        "legal_basis": [],
    }

    selected = [
        (
            "none",
            rules["HR6"]["options"]["none"],
        )
    ]

    update_state("HR6", selected, rules, state)

    assert state["current_entity"] == "product_manufacturer"
    assert state["status_changes"] == []
    assert state["obligations"] == ["Product Manufacturer"]
    assert determine_next("HR6", selected, state) == "END"


def test_r4_only_high_risk_deployer_continues_to_r5():
    rules = load_rules()

    selected = [
        (
            "deepfake",
            rules["R4"]["options"]["deepfake"],
        )
    ]

    high_risk_state = {
        "answers": {},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": ["High risk"],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    update_state("R4", selected, rules, high_risk_state)

    assert (
        "Transparency: Content Resemblance"
        in high_risk_state["obligations"]
    )
    assert determine_next(
        "R4",
        selected,
        high_risk_state,
    ) == "R5"

    non_high_risk_state = {
        "answers": {},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    update_state("R4", selected, rules, non_high_risk_state)

    assert (
        "Transparency: Content Resemblance"
        in non_high_risk_state["obligations"]
    )
    assert determine_next(
        "R4",
        selected,
        non_high_risk_state,
    ) == "END"


def test_hr3_yes_converts_deployer_to_provider():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [
        (
            "yes",
            rules["HR3"]["options"]["yes"],
        )
    ]

    update_state("HR3", selected, rules, state)

    assert state["current_entity"] == "provider"
    assert "High risk" in state["status_changes"]
    assert "Become a Provider" in state["status_changes"]
    assert "AI Literacy" in state["obligations"]
    assert determine_next("HR3", selected, state) == "S1"


def test_hr1_high_risk_converts_deployer_to_provider():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [
        (
            "civil_aviation",
            rules["HR1"]["options"]["civil_aviation"],
        )
    ]

    update_state("HR1", selected, rules, state)

    assert state["current_entity"] == "provider"
    assert "High risk" in state["status_changes"]
    assert "Become a Provider" in state["status_changes"]
    assert "AI Literacy" in state["obligations"]
    assert determine_next("HR1", selected, state) == "S1"


def test_e2_provider_modification_requires_handover():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "provider",
        "current_entity": "provider",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [
        (
            "different_name_or_trademark",
            rules["E2"]["options"]["different_name_or_trademark"],
        )
    ]

    update_state("E2", selected, rules, state)

    assert state["current_entity"] == "provider"
    assert "Handover" in state["obligations"]
    assert "AI Literacy" in state["obligations"]
    assert "Become a Provider" not in state["status_changes"]
    assert determine_next("E2", selected, state) == "HR1"


def test_e2_deployer_modification_becomes_provider():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [
        (
            "different_name_or_trademark",
            rules["E2"]["options"]["different_name_or_trademark"],
        )
    ]

    update_state("E2", selected, rules, state)

    assert state["current_entity"] == "provider"
    assert "Become a Provider" in state["status_changes"]
    assert "AI Literacy" in state["obligations"]
    assert "Handover" not in state["obligations"]
    assert determine_next("E2", selected, state) == "HR1"


def test_high_risk_exception_blocks_r1_after_hr2_match():
    rules = load_rules()

    state = {
        "answers": {
            "HR2": ["medical_devices"],
        },
        "original_entity": "provider",
        "current_entity": "provider",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [
        (
            "gpai_eu_market",
            rules["S1"]["options"]["gpai_eu_market"],
        )
    ]

    assert determine_next("S1", selected, state) == "END"
    assert "High risk Exception" in state["status_changes"]


def test_high_risk_exception_blocks_r1_after_hr6_match():
    rules = load_rules()

    state = {
        "answers": {
            "HR6": ["medical_devices"],
        },
        "original_entity": "product_manufacturer",
        "current_entity": "provider",
        "status_changes": ["High risk", "Become a Provider"],
        "obligations": [],
        "legal_basis": [],
    }

    selected = [
        (
            "gpai_eu_market",
            rules["S1"]["options"]["gpai_eu_market"],
        )
    ]

    assert determine_next("S1", selected, state) == "END"
    assert "High risk Exception" in state["status_changes"]


def test_provider_normal_path_reaches_r4():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "provider",
        "current_entity": "provider",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    # E2: no modification
    selected = [("none", rules["E2"]["options"]["none"])]
    update_state("E2", selected, rules, state)
    assert determine_next("E2", selected, state) == "HR1"

    # HR1: no Annex I Section B category
    selected = [("none", rules["HR1"]["options"]["none"])]
    update_state("HR1", selected, rules, state)
    assert determine_next("HR1", selected, state) == "HR2"

    # HR2: no Annex I Section A category
    selected = [("none", rules["HR2"]["options"]["none"])]
    update_state("HR2", selected, rules, state)
    assert determine_next("HR2", selected, state) == "HR4"

    # HR4: no Annex III category
    selected = [("none", rules["HR4"]["options"]["none"])]
    update_state("HR4", selected, rules, state)
    assert determine_next("HR4", selected, state) == "S1"

    # S1: provider places an AI system on the EU market
    selected = [
        (
            "ai_system_eu_market",
            rules["S1"]["options"]["ai_system_eu_market"],
        )
    ]
    update_state("S1", selected, rules, state)
    assert determine_next("S1", selected, state) == "R2"

    # R2: no exclusion
    selected = [("none", rules["R2"]["options"]["none"])]
    update_state("R2", selected, rules, state)
    assert determine_next("R2", selected, state) == "R3"

    # R3: no prohibited practice
    selected = [("none", rules["R3"]["options"]["none"])]
    update_state("R3", selected, rules, state)
    assert determine_next("R3", selected, state) == "R4"


def test_high_risk_deployer_path_reaches_r5():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": ["High risk"],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    # S1: deployer is established in the EU
    selected = [
        (
            "deployer_established_eu",
            rules["S1"]["options"]["deployer_established_eu"],
        )
    ]
    update_state("S1", selected, rules, state)
    assert determine_next("S1", selected, state) == "R2"

    # R2: no exclusion
    selected = [("none", rules["R2"]["options"]["none"])]
    update_state("R2", selected, rules, state)
    assert determine_next("R2", selected, state) == "R3"

    # R3: no prohibited practice
    selected = [("none", rules["R3"]["options"]["none"])]
    update_state("R3", selected, rules, state)
    assert determine_next("R3", selected, state) == "R4"

    # R4: deployer uses emotion recognition / biometric categorisation
    selected = [
        (
            "emotion_or_biometric",
            rules["R4"]["options"]["emotion_or_biometric"],
        )
    ]
    update_state("R4", selected, rules, state)

    assert determine_next("R4", selected, state) == "R5"
    assert "Transparency: Emotion & Biometric" in state["obligations"]


def test_product_manufacturer_medical_device_becomes_provider():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "product_manufacturer",
        "current_entity": "product_manufacturer",
        "status_changes": [],
        "obligations": [],
        "legal_basis": [],
    }

    # HR6: AI system is a safety component of a medical device
    selected = [
        (
            "medical_devices",
            rules["HR6"]["options"]["medical_devices"],
        )
    ]
    update_state("HR6", selected, rules, state)

    assert state["current_entity"] == "provider"
    assert "High risk" in state["status_changes"]
    assert "Become a Provider" in state["status_changes"]
    assert determine_next("HR6", selected, state) == "S1"

    # S1 now uses Provider scope options
    selected = [
        (
            "ai_system_eu_market",
            rules["S1"]["options"]["ai_system_eu_market"],
        )
    ]
    update_state("S1", selected, rules, state)

    assert determine_next("S1", selected, state) == "R2"


def test_gpai_systemic_risk_path_continues_through_rules():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "provider",
        "current_entity": "provider",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    # S1: Provider places a GPAI model on the EU market
    selected = [
        (
            "gpai_eu_market",
            rules["S1"]["options"]["gpai_eu_market"],
        )
    ]
    update_state("S1", selected, rules, state)
    assert determine_next("S1", selected, state) == "R1"

    # R1: GPAI model has high-impact capabilities
    selected = [
        (
            "high_impact_capabilities",
            rules["R1"]["options"]["high_impact_capabilities"],
        )
    ]
    update_state("R1", selected, rules, state)

    assert "GPAI with systemic risk" in state["status_changes"]
    assert determine_next("R1", selected, state) == "R2"

    # R2: no exclusion
    selected = [("none", rules["R2"]["options"]["none"])]
    update_state("R2", selected, rules, state)
    assert determine_next("R2", selected, state) == "R3"

    # R3: no prohibited practice
    selected = [("none", rules["R3"]["options"]["none"])]
    update_state("R3", selected, rules, state)
    assert determine_next("R3", selected, state) == "R4"

    # R4: no transparency category
    selected = [("none", rules["R4"]["options"]["none"])]
    update_state("R4", selected, rules, state)
    assert determine_next("R4", selected, state) == "END"


def test_prohibited_ai_practice_terminates_at_r3():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "provider",
        "current_entity": "provider",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [
        (
            "social_scoring",
            rules["R3"]["options"]["social_scoring"],
        )
    ]
    update_state("R3", selected, rules, state)

    assert "Prohibited AI Practice" in state["status_changes"]
    assert determine_next("R3", selected, state) == "END"


def test_hr5_non_high_risk_provider_gets_article_6_4_obligations():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "provider",
        "current_entity": "provider",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [("no", rules["HR5"]["options"]["no"])]

    update_state("HR5", selected, rules, state)

    assert "Document Non-High-Risk Assessment" in state["obligations"]
    assert "Register in EU Database" in state["obligations"]
    assert "Article 6 point 3" in state["legal_basis"]
    assert "Article 6 point 4" in state["legal_basis"]


def test_hr5_non_high_risk_deployer_does_not_get_provider_obligations():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [("no", rules["HR5"]["options"]["no"])]

    update_state("HR5", selected, rules, state)

    assert "Document Non-High-Risk Assessment" not in state["obligations"]
    assert "Register in EU Database" not in state["obligations"]
    assert "Article 6 point 3" in state["legal_basis"]
    assert "Article 6 point 4" in state["legal_basis"]


def test_hr5_high_risk_yes_does_not_add_article_6_4():
    rules = load_rules()

    state = {
        "answers": {},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": [],
        "obligations": ["AI Literacy"],
        "legal_basis": [],
    }

    selected = [("yes", rules["HR5"]["options"]["yes"])]

    update_state("HR5", selected, rules, state)

    assert "High risk" in state["status_changes"]
    assert "Article 6 point 3" in state["legal_basis"]
    assert "Article 6 point 4" not in state["legal_basis"]


def test_print_state_shows_precise_legal_provision(capsys):
    state = {
        "answers": {"R4": ["emotion_or_biometric"]},
        "original_entity": "deployer",
        "current_entity": "deployer",
        "status_changes": [],
        "obligations": ["Transparency: Emotion & Biometric"],
        "legal_basis": ["Article 50"],
    }

    print_state(state)

    output = capsys.readouterr().out

    assert "Transparency: Emotion & Biometric" in output
    assert "Legal provision: Article 50(3)" in output
    assert "emotion recognition system" in output


def test_s1_distributor_has_article_2_1_d_scope():
    rules = load_rules()

    option = rules["S1"]["options"]["distributor_scope"]

    assert "distributor" in option["applies_to"]
    assert "Article 2 point 1(d)" in option["legal_basis"]
    assert option["next"] == "R2"


def test_s1_output_used_eu_does_not_apply_to_distributor():
    rules = load_rules()

    option = rules["S1"]["options"]["output_used_eu"]

    assert "provider" in option["applies_to"]
    assert "deployer" in option["applies_to"]
    assert "distributor" not in option["applies_to"]


def test_s1_operator_scope_routes_exist():
    rules = load_rules()
    options = rules["S1"]["options"]

    expected = {
        "importer_scope": ("importer", "Article 2 point 1(d)"),
        "distributor_scope": ("distributor", "Article 2 point 1(d)"),
        "product_manufacturer_scope": (
            "product_manufacturer",
            "Article 2 point 1(e)",
        ),
        "authorised_representative_scope": (
            "authorised_representative",
            "Article 2 point 1(f)",
        ),
    }

    for option_key, (entity, legal_basis) in expected.items():
        option = options[option_key]

        assert entity in option["applies_to"]
        assert legal_basis in option["legal_basis"]
        assert option["next"] == "R2"
