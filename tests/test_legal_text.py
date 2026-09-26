from src.legal_text import find_article_page, get_article_text


def test_find_article_50_page():
    assert find_article_page(50) == 167


def test_get_article_50_complete():
    text = get_article_text(50)

    assert text is not None
    assert text.startswith("Article 50")
    assert "Transparency obligations" in text
    assert "4." in text
    assert "Article 51" not in text


def test_required_articles_can_be_extracted():
    required_articles = [4, 5, 6, 27, 49, 50, 51]

    for article_number in required_articles:
        text = get_article_text(article_number)

        assert text is not None
        assert text.startswith(f"Article {article_number}")


def test_missing_article_returns_none():
    assert get_article_text(999) is None

def test_get_article_50_paragraph_3():
    from src.legal_text import get_article_paragraph

    text = get_article_paragraph(50, 3)

    assert text is not None
    assert text.startswith("3.")
    assert "emotion recognition system" in text
    assert "biometric" in text
    assert "4." not in text


def test_page_number_artifact_is_removed():
    from src.legal_text import get_article_paragraph

    text = get_article_paragraph(50, 3)

    assert "\n165\n" not in text
    assert "appropriate safeguards" in text


def test_article_50_obligation_provisions():
    from src.legal_text import get_obligation_provision

    expected = {
        "Transparency: Natural Persons": "Article 50(1)",
        "Transparency: Synthetic Content": "Article 50(2)",
        "Transparency: Emotion & Biometric": "Article 50(3)",
        "Transparency: Content Resemblance": "Article 50(4)",
    }

    for obligation, reference in expected.items():
        provision = get_obligation_provision(obligation)

        assert provision is not None
        assert provision["reference"] == reference
        assert provision["text"] is not None


def test_unknown_obligation_has_no_provision():
    from src.legal_text import get_obligation_provision

    assert get_obligation_provision("Unknown Obligation") is None
