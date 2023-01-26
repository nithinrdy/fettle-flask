FROM python:3.8.15

# Set the working directory to /app

WORKDIR /working

# Install dependencies

COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy source code

COPY . .

# Run flask application

CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0"]
