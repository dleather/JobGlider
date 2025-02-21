FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install necessary packages
RUN apt-get update && apt-get install -y \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    wget \
    unzip \
    fontconfig

# Create FontAwesome directory
RUN mkdir -p /usr/local/share/fonts/FontAwesome

# Download and install FontAwesome
RUN wget -q https://use.fontawesome.com/releases/v5.15.4/fontawesome-free-5.15.4-desktop.zip \
    && unzip fontawesome-free-5.15.4-desktop.zip \
    && mv fontawesome-free-5.15.4-desktop/otfs/*.otf /usr/local/share/fonts/FontAwesome/ \
    && rm -rf fontawesome-free-5.15.4-desktop.zip fontawesome-free-5.15.4-desktop

RUN mkdir -p /usr/share/texmf/fonts/opentype/public/fontawesome && \
    cp /usr/local/share/fonts/FontAwesome/Font\ Awesome\ 5\ Free-Solid-900.otf /usr/share/texmf/fonts/opentype/public/fontawesome/ && \
    mktexlsr

RUN mv "/usr/local/share/fonts/FontAwesome/Font Awesome 5 Free-Solid-900.otf" "/usr/local/share/fonts/FontAwesome/FontAwesome5Free-Solid-900.otf"

# Update font cache
RUN fc-cache -f -v

# Verify FontAwesome installation
RUN ls -l /usr/local/share/fonts/FontAwesome/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
