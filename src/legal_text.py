import re
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader


DEFAULT_REGULATION_PATH = Path(
    "data/raw/ai act regulation eu 20241689-QT0125001ENN.pdf"
)


@lru_cache(maxsize=1)
def load_reader(pdf_path=DEFAULT_REGULATION_PATH):
    """Load and cache the EU AI Act PDF reader."""
    return PdfReader(pdf_path)


@lru_cache(maxsize=1)
def load_page_texts(pdf_path=DEFAULT_REGULATION_PATH):
    """Extract and cache the text of every page in the EU AI Act."""
    reader = load_reader(pdf_path)

    return tuple(
        page.extract_text() or ""
        for page in reader.pages
    )


def find_article_page(article_number, pdf_path=DEFAULT_REGULATION_PATH):
    """Return the zero-based PDF page index containing an Article heading."""
    page_texts = load_page_texts(pdf_path)

    pattern = re.compile(
        rf"(?m)^Article {article_number}\s*$"
    )

    for page_index, text in enumerate(page_texts):
        if pattern.search(text):
            return page_index

    return None


def clean_extracted_text(text):
    """Remove PDF page-number artifacts from extracted legal text."""
    text = re.sub(r"(?m)^\s*\d{1,3}\s*$", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text


def get_article_text(article_number, pdf_path=DEFAULT_REGULATION_PATH):
    """Extract the complete text of an Article from the EU AI Act."""
    page_texts = load_page_texts(pdf_path)

    start_page = find_article_page(article_number, pdf_path)

    if start_page is None:
        return None

    article_pattern = re.compile(
        rf"(?m)^Article {article_number}\s*$"
    )
    next_article_pattern = re.compile(
        rf"(?m)^Article {article_number + 1}\s*$"
    )

    parts = []

    for page_index in range(start_page, len(page_texts)):
        text = page_texts[page_index]

        # On the first page, discard everything before the Article heading.
        if page_index == start_page:
            match = article_pattern.search(text)

            if match is None:
                return None

            text = text[match.start():]

        # Stop at the next Article heading.
        next_match = next_article_pattern.search(text)

        if next_match:
            text = text[:next_match.start()]
            parts.append(text)
            break

        parts.append(text)

    text = "\n".join(parts).strip()
    return clean_extracted_text(text)


def get_article_paragraph(
    article_number,
    paragraph_number,
    pdf_path=DEFAULT_REGULATION_PATH,
):
    """Extract a numbered paragraph from an Article."""
    article_text = get_article_text(article_number, pdf_path)

    if article_text is None:
        return None

    pattern = re.compile(
        rf"(?ms)^{paragraph_number}\.\s+"
        rf"(.*?)(?=^\d+\.\s+|\Z)"
    )

    match = pattern.search(article_text)

    if match is None:
        return None

    return match.group(0).strip()
