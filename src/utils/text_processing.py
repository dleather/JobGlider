import re
from typing import List

def expand_job_title_acronyms(title):
    # Dictionary of common job title acronyms and their expansions
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
    
    # Split the title into words
    words = title.split()
    
    # Replace acronyms with their full forms
    expanded_words = [acronyms.get(word.upper(), word) for word in words]
    
    # Join the words back into a title
    expanded_title = " ".join(expanded_words)
    
    return expanded_title

def split_text(text: str, max_length: int = 384, stride: int = 128) -> List[str]:
    """Split the text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_length - stride):
        chunk = " ".join(words[i:i + max_length])
        chunks.append(chunk)
    return chunks

def escape_latex(text):
    """
    Escape special LaTeX characters in a string, avoiding double escaping.
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
    
    # Use regex to find characters to replace
    pattern = '|'.join(re.escape(key) for key in latex_special_chars.keys())
    
    # Replace function
    def replace(match):
        char = match.group(0)
        # Check if the character is already escaped
        if char == '\\' and match.start() > 0 and text[match.start()-1] == '\\':
            return char
        return latex_special_chars[char]
    
    return re.sub(pattern, replace, text)

def clean_job_title(title):
    # Remove content within parentheses and the parentheses themselves
    title = re.sub(r'\([^)]*\)', '', title)
    
    # Remove content within square brackets and the brackets themselves
    title = re.sub(r'\[[^]]*\]', '', title)
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    return title.strip()

def clean_text(text):
    # Remove common LinkedIn boilerplate text
    text = re.sub(r'LinkedIn.*?Skip to main content', '', text, flags=re.DOTALL)
    text = re.sub(r'Agree & Join LinkedIn.*?Cookie Policy\.', '', text, flags=re.DOTALL)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text