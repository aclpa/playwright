FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN python -c "import easyocr; easyocr.Reader(['ko', 'en'])"

COPY . .

CMD ["/bin/bash"]
