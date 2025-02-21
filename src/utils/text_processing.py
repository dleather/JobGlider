import re
from typing import List

def expand_job_title_acronyms(title):
    """
    Expand acronyms in a job title to their full forms.

    This function takes a job title string and replaces any recognized acronyms
    with their corresponding full forms based on a predefined dictionary of common
    job title acronyms.

    Args:
        title (str): The job title potentially containing acronyms.

    Returns:
        str: The job title with acronyms expanded to their full forms.
    """
    acronyms = {
        "VP": "Vice President",
        "CEO": "Chief Executive Officer",
        "CFO": "Chief Financial Officer",
        "CTO": "Chief Technology Officer",
        "COO": "Chief Operating Officer",
        "CIO": "Chief Information Officer",
        "CMO": "Chief Marketing Officer",
        "HR": "Human Resources",
        "PM": "Project Manager",
        "BA": "Business Analyst",
        "QA": "Quality Assurance",
        "UI": "User Interface",
        "UX": "User Experience",
        "PR": "Public Relations",
        "IT": "Information Technology",
        "SVP": "Senior Vice President",
        "EVP": "Executive Vice President",
        "AVP": "Assistant Vice President",
        "MD": "Managing Director",
        "GM": "General Manager",
    }
    
    words = title.split()
    expanded_words = [acronyms.get(word.upper(), word) for word in words]
    expanded_title = " ".join(expanded_words)
    
    return expanded_title

def split_text(text: str, max_length: int = 384, stride: int = 128) -> List[str]:
    """
    Split a text into overlapping chunks of a specified maximum length.

    This function divides a given text into chunks, each with a maximum length
    specified by the `max_length` parameter. The chunks overlap by a number of
    words specified by the `stride` parameter to ensure continuity between chunks.

    Args:
        text (str): The text to be split into chunks.
        max_length (int): The maximum number of words in each chunk.
        stride (int): The number of words to overlap between consecutive chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    words = text.split()
    
    if len(words) <= max_length:
        return [text]
    
    chunks = []
    step = max_length - stride
    start = 0
    
    # Generate chunks using sliding window approach
    while start + max_length <= len(words):
        chunks.append(" ".join(words[start:start + max_length]))
        start += step
    
    # Handle remaining words that don't fit perfectly
    if start < len(words):
        final_chunk = " ".join(words[start:])
        # Only add if different from last chunk and contains new content
        if not chunks or final_chunk != chunks[-1]:
            chunks.append(final_chunk)
    
    return chunks

def escape_latex(text):
    """
    Escape special LaTeX characters in a string.

    This function replaces special characters in a string with their LaTeX-safe
    equivalents to prevent errors when the string is processed in a LaTeX document.
    It avoids double escaping by checking if characters are already escaped.

    Args:
        text (str): The string containing potential LaTeX special characters.

    Returns:
        str: The string with LaTeX special characters escaped.
    """
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
    }
    
    pattern = '|'.join(re.escape(key) for key in latex_special_chars.keys())
    
    def replace(match):
        char = match.group(0)
        # Check if the character is already escaped
        start = match.start()
        if start > 0 and text[start-1] == '\\':
            return char  # Return the character as-is if it's already escaped
        return latex_special_chars[char]
    
    return re.sub(pattern, replace, text)

def clean_job_title(title):
    """
    Clean a job title by removing unwanted content and extra whitespace.

    This function removes any content within parentheses or square brackets
    from a job title and trims any extra whitespace, resulting in a cleaner
    and more readable job title.

    Args:
        title (str): The raw job title string.

    Returns:
        str: The cleaned job title.
    """
    title = re.sub(r'\([^)]*\)', '', title)
    title = re.sub(r'\[[^]]*\]', '', title)
    title = ' '.join(title.split())
    
    return title.strip()

def clean_text(text):
    """
    Clean text by removing specific boilerplate content and extra whitespace.

    This function removes common LinkedIn boilerplate text and trims extra
    whitespace from the input text, resulting in a cleaner and more concise
    version of the original text.

    Args:
        text (str): The raw text potentially containing boilerplate content.

    Returns:
        str: The cleaned text.
    """
    text = re.sub(r'LinkedIn.*?Skip to main content', '', text, flags=re.DOTALL)
    text = re.sub(r'Agree & Join LinkedIn.*?Cookie Policy\.', '', text, flags=re.DOTALL)
    text = ' '.join(text.split())
    return text
