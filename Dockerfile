# FROM python:3.13.2

# WORKDIR /fastapi-app


# COPY requirements.txt .

# RUN pip install -r requirements.txt


# COPY ./src ./src

# ENV PYTHONPATH=/fastapi-app


# CMD ["python","./src/main.py"]

FROM python:3.13.2

WORKDIR /fastapi-app

# Add PYTHONPATH so Python can resolve `src` as a top-level package
ENV PYTHONPATH=/fastapi-app

# Install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your source code
COPY ./src ./src
COPY .env .env
COPY ./static ./static



# Run your FastAPI app using uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

