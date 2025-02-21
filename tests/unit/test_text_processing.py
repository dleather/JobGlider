from src.utils.text_processing import (
    expand_job_title_acronyms,
    split_text,
    escape_latex,
    clean_job_title,
    clean_text
)

def test_expand_job_title_acronyms_single():
    # unit
    assert expand_job_title_acronyms("VP") == "Vice President"

def test_expand_job_title_acronyms_mixed_case():
    # unit
    assert expand_job_title_acronyms("vP of Sales") == "Vice President of Sales"

def test_expand_job_title_acronyms_no_match():
    # unit
    assert expand_job_title_acronyms("Manager") == "Manager"

def test_expand_job_title_acronyms_multiple():
    # unit
    title = "COO and CTO"
    expected = "Chief Operating Officer and Chief Technology Officer"
    assert expand_job_title_acronyms(title) == expected

def test_split_text_short_text():
    # unit
    text = "Short text sample"
    chunks = split_text(text, max_length=5, stride=2)
    # Should just return the text in a single chunk since it's shorter than max_length
    assert chunks == ["Short text sample"]

def test_split_text_exact_length():
    # unit
    text = "One two three four five six"
    # max_length = 6, stride = 3
    # There's exactly 6 words, so it should only produce one chunk
    chunks = split_text(text, max_length=6, stride=3)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_split_text_long_text():
    # unit
    text = " ".join(f"word{i}" for i in range(1, 21))
    # max_length = 10, stride = 3
    chunks = split_text(text, max_length=10, stride=3)
    # Expected chunk logic:
    #  chunk1: words 1-10
    #  chunk2: words 8-17
    #  chunk3: words 15-20 (less than 10, but final chunk)
    assert len(chunks) == 3
    assert chunks[0] == " ".join(f"word{i}" for i in range(1, 11))   # words1..10
    assert chunks[1] == " ".join(f"word{i}" for i in range(8, 18))   # words8..17
    assert chunks[2] == " ".join(f"word{i}" for i in range(15, 21))  # words15..20

def test_escape_latex_no_special_chars():
    # unit
    text = "Hello World"
    assert escape_latex(text) == text

def test_escape_latex_special_chars():
    # unit
    text = "&%$#_{}"
    expected = r"\&\%\$\#\_\{\}"
    assert escape_latex(text) == expected

def test_escape_latex_already_escaped():
    # unit
    text = r"\& something"
    # The leading backslash is a single literal backslash in the string
    # This isn't 'double escaped' by the function because we only replace
    # unescaped special chars. 
    # The function looks for literal '&', not '\&'.
    assert escape_latex(text) == r"\& something"

def test_clean_job_title_parentheses():
    # unit
    title = "Project Manager (Contract)"
    assert clean_job_title(title) == "Project Manager"

def test_clean_job_title_square_brackets():
    # unit
    title = "Senior Developer [Temporary Role]"
    assert clean_job_title(title) == "Senior Developer"

def test_clean_job_title_mixed():
    # unit
    title = "QA (Quality Assurance) [Temp] Engineer"
    assert clean_job_title(title) == "QA Engineer"

def test_clean_text_boilerplate():
    # unit
    text = (
        "LinkedIn Some text Skip to main content "
        "Agree & Join LinkedIn More text Cookie Policy. Done."
    )
    cleaned = clean_text(text)
    assert "LinkedIn" not in cleaned
    assert "Skip to main content" not in cleaned
    assert "Agree & Join LinkedIn" not in cleaned
    assert "Cookie Policy." not in cleaned

def test_clean_text_regular_text():
    # unit
    text = "Just normal text with spaces   and tabs\t"
    cleaned = clean_text(text)
    assert cleaned == "Just normal text with spaces and tabs"