FROM python:3.11-slim

# Install system dependencies and Terraform
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    software-properties-common \
    && wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update && apt-get install -y terraform \
    && rm -rf /var/lib/apt/lists/*

# Set up work directory
WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app /app/app

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.address=0.0.0.0"]
