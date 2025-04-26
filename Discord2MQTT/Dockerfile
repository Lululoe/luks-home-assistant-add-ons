ARG BUILD_FROM
FROM $BUILD_FROM

# Set environment variables
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy the application
COPY . .

# Install Python and necessary tools
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv

# Create and activate virtual environment, then install dependencies
RUN python3 -m venv $VIRTUAL_ENV && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Make run.sh executable
RUN chmod +x /app/run.sh

# Run the script using run.sh
CMD [ "/app/run.sh" ]