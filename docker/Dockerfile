FROM vllm/vllm-openai:latest

# Install system utilities
RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
# Using --no-cache-dir to keep image size down
RUN pip install --no-cache-dir \
    langchain>=0.3.0 \
    langchain-core>=0.3.0 \
    langchain-openai>=0.2.0 \
    langchain-google-genai>=2.0.0 \
    langgraph>=0.2.0 \
    pydantic>=2.0.0 \
    pydantic-settings>=2.0.0 \
    python-dotenv>=1.0.0 \
    aiomysql>=0.2.0 \
    httpx>=0.27.0 \
    faiss-cpu>=1.7.0 \
    sentence-transformers>=2.2.0 \
    numpy>=1.24.0

# Copy project files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app/src

# Reset entrypoint to allow running specific commands (bash by default)
ENTRYPOINT []
CMD ["/bin/bash"]
