# Automated Cover Letter Generator

[![CI](https://github.com/dleather/JobGlider/actions/workflows/ci.yml/badge.svg)](https://github.com/dleather/JobGlider/actions)
[![codecov](https://codecov.io/gh/dleather/JobGlider/branch/main/graph/badge.svg)](https://codecov.io/gh/dleather/JobGlider)

Automated pipeline for creating personalized cover letters:

- Data Collection: Clipping job postings from Notion (or another source).
- Processing & Generation: Using an LLM (via Outlines) to produce a structured cover letter.
- PDF Output: Generating final PDF cover letters using LaTeX templates.
- Orchestration: Optional Zapier integration for automation, or direct polling/webhook triggers.

## Table of Contents

- [Automated Cover Letter Generator](#automated-cover-letter-generator)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Requirements](#requirements)
    - [Python Dependencies](#python-dependencies)
  - [Installation](#installation)
    - [Windows Setup](#windows-setup)
    - [Unix Setup (Linux/Mac)](#unix-setup-linuxmac)
    - [Docker Setup (Cross-Platform)](#docker-setup-cross-platform)
  - [Usage](#usage)
  - [Environment Variables](#environment-variables)
  - [Development](#development)
  - [Roadmap](#roadmap)
  - [License](#license)
  - [Questions or Contributions?](#questions-or-contributions)

## Features

- **Notion Integration**: Seamlessly clip job postings into your Notion database.
- **LLM-driven Generation**: Uses open-source LLMs (LLaMA, Mistral) or fallback to GPT-4/Claude.
- **Structured Output**: Enforced JSON schema via Outlines, ensuring reliable cover letter segments.
- **Latex PDF Generation**: Fills a TeX template, automatically produces professional PDFs.
- **Dockerized**: Simple deployment with docker-compose.

## Project Structure

```
.
├─.venv/               # Local virtual environment (Windows or Unix)
├─.venv-3.13/          # Another local virtual environment for Python 3.13
├─assets/              # Images or static assets
├─config/              # Configuration files (YAML, TOML, etc.)
├─cover_letters/       # Generated PDFs or letter drafts
├─data/                # If you store CSV/JSON data or intermediate results
├─docs/                # Documentation (api, dev, user)
├─examples/            # Example scripts or usage demos
├─logs/                # Log files
├─requirements.lock    # Locked dependencies
├─requirements.txt     # Main Python dependencies
├─scripts/             # Setup or utility scripts
│  ├─setup/
│  └─tools/
├─src/
│  ├─api/
│  ├─core/
│  ├─server/
│  │  └─webhook_server.py  # A Flask or FastAPI server for receiving triggers
│  └─utils/
├─templates/
│  ├─awesome-cv.cls                   # CV style (from Awesome-CV)
│  ├─awesome_cv_cover_letter_template.tex
│  └─coverletter.tex                  # A simpler cover letter template
├─tests/
│  ├─fixtures/
│  ├─integration/
│  └─unit/
├─Dockerfile
├─docker-compose.yml
├─README.md                           # You're reading it now
└─...
```

## Requirements

Below is the core list of dependencies you'll need outside of Python:

- **Python 3.9+**
  - Recommended to use Python 3.11 or 3.12, or you can try 3.13 if you're prepared to compile Rust code for certain packages.
- **Rust toolchain** (if needed for outlines-core compilation)
  - On Windows, Install Rust via rustup.
  - On Unix, install via your package manager or rustup.
- **TeX distribution**
  - On Windows: MiKTeX or TeX Live.
  - On Unix: sudo apt-get install texlive-latex-extra texlive-xetex (or distro equivalent).
- **Docker** (optional)
  - If you prefer containerized deployment.

### Python Dependencies

All Python libraries are listed in requirements.txt. Key libraries include:

- Outlines for structured generation.
- PyTorch or Transformers (depending on your open-source LLM usage).
- Flask or FastAPI if you run a server.
- requests or any HTTP library for triggers/integrations.

## Installation

### Windows Setup

1. **Install Python**
   - Get the latest Python 3.x from python.org.
   - During install, check "Add Python to PATH."

2. **(Optional) Install Rust**
   - If outlines-core needs to compile from source (no pre-built wheel for your Python version).
   - Download from rustup.rs → run the .exe.

3. **Install a TeX Distribution**
   - MiKTeX or TeX Live for Windows.

4. **Create & Activate Virtual Environment**

```
# In your project folder:
python -m venv .venv
.\.venv\Scripts\activate
```

5. **Install Python Dependencies**

```
pip install --upgrade pip
pip install -r requirements.txt
```

6. **Verify**

```
# Example check
python -m outlines --version
```

### Unix Setup (Linux/Mac)

1. **Install Python**
   - Use your package manager or python.org.
   - e.g., on Ubuntu:

```
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

2. **(Optional) Install Rust**
   - If needed for building outlines-core.
   - e.g. `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

3. **Install a TeX Distribution**
   - e.g. `sudo apt-get install texlive-latex-extra texlive-xetex`.

4. **Create & Activate Virtual Environment**

```
python3 -m venv .venv
source .venv/bin/activate
```

5. **Install Python Dependencies**

```
pip install --upgrade pip
pip install -r requirements.txt
```

6. **Verify**

```
python -m outlines --version
```

### Docker Setup (Cross-Platform)

1. **Install Docker**
   - Windows: Docker Desktop
   - macOS: Docker Desktop or `brew cask install docker`
   - Linux: Check your distro's repo or Docker Docs

2. **Build Image**

```
docker build -t cover-letter-app .
```

3. **Run Container**

```
docker run -p 8080:8080 cover-letter-app
```

4. **(Optional) docker-compose**
   - Use the provided docker-compose.yml if you have multiple services or want a simpler spin-up:

```
docker-compose up --build
```

   - This approach ensures a consistent environment across all platforms.

## Usage

1. **Start Your Backend (Locally or via Docker)**
   - If local (without Docker):

```
# Still in your .venv
python src/server/webhook_server.py
```

   - If Docker:

```
docker-compose up
```

2. **Add a Job Posting**
   - For example, in Notion, create a new entry in your "Job Postings" database.
   - If using Zapier or a custom script, it triggers the endpoint (e.g. POST /generate-letter).

3. **Cover Letter Generated**
   - The LLM processes it via Outlines, ensures JSON format.
   - A LaTeX template is filled, compiled to PDF, and saved in ./cover_letters.

4. **Review the PDF**
   - Check in cover_letters/YourCoverLetter.pdf.

## Environment Variables

You can use a .env file or system environment variables to store:

| Variable Name | Description | Example |
|---------------|-------------|---------|
| OPENAI_API_KEY | API key if using GPT-4 fallback. | sk-ABC123 |
| NOTION_API_TOKEN | If using direct Notion API polling. | secret_... |
| FLASK_ENV | Set to development or production. | development |

(Ensure .env is in your .gitignore to avoid committing secrets.)

## Development

- **Code Linting**
  - Use a linter (flake8, black, ruff) for consistent style:

```
pip install black
black src/
```

- **Unit Tests**
  - Place unit tests under tests/unit/.
  - Example:

```
pytest tests/unit
```

- **Integration Tests**
  - Check pipeline flow from Notion input to PDF output.
  - Place them in tests/integration/.

## Roadmap

- Add Kubernetes Deployment: Helm chart for scaling multiple LLM containers.
- Switch/Upgrade Models: Try LLaMA-2-13B, Mistral, or a fine-tuned version for better cover letters.
- Retrieval-Augmented Generation: Store resume or user data in a vector DB for highly contextual letters.
- User Interface: A small React/Flask front end for easier manual triggers.
- CI/CD: GitHub Actions to run tests, build Docker images automatically.

## License

MIT License – Feel free to use or adapt this project for your own purposes.
(Replace with your actual chosen license.)

## Questions or Contributions?

- Open an issue on GitHub or create a Pull Request.
- Feel free to reach out with suggestions, feature requests, or bug reports!

Happy Generating!
