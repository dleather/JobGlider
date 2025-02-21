FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libffi-dev \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    wget \
    unzip \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Font installation
RUN set -ex \
    && FONT_VERSION="5.15.4" \
    && FONT_SHA256="4917ebb73c1c23d26aba25b0f7aff3b3f1330efb688f4591d5cda1811ba9dd7f" \
    && mkdir -p /usr/local/share/fonts/FontAwesome /usr/share/texmf/fonts/opentype/public/fontawesome \
    # Download and verify
    && wget -q "https://use.fontawesome.com/releases/v${FONT_VERSION}/fontawesome-free-${FONT_VERSION}-desktop.zip" \
    && echo "${FONT_SHA256} fontawesome-free-${FONT_VERSION}-desktop.zip" | sha256sum -c - \
    # Extract and install
    && unzip -q "fontawesome-free-${FONT_VERSION}-desktop.zip" \
    && mv "fontawesome-free-${FONT_VERSION}-desktop/otfs/"*.otf /usr/local/share/fonts/FontAwesome/ \
    # Rename for consistency
    && mv "/usr/local/share/fonts/FontAwesome/Font Awesome 5 Free-Solid-900.otf" \
        "/usr/local/share/fonts/FontAwesome/FontAwesome5Free-Solid-900.otf" \
    # Setup for LaTeX
    && cp "/usr/local/share/fonts/FontAwesome/FontAwesome5Free-Solid-900.otf" \
        "/usr/share/texmf/fonts/opentype/public/fontawesome/" \
    && mktexlsr \
    # Update font cache
    && fc-cache -f -v \
    # Cleanup
    && rm -rf "fontawesome-free-${FONT_VERSION}-desktop.zip" \
              "fontawesome-free-${FONT_VERSION}-desktop" \
    # Verify installation
    && fc-list | grep -i "FontAwesome" \
    && ls -l /usr/local/share/fonts/FontAwesome/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]