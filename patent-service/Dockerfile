FROM python:3.9-bullseye

WORKDIR /app

# Install necessary system libraries
RUN apt-get update && apt-get install -y libheif-dev build-essential libjpeg-dev zlib1g-dev libpng-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .




# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD ["uvicorn", "src.controller.app:app", "--host", "0.0.0.0", "--port", "8000"]
