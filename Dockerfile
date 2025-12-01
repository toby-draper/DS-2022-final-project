# ---------------------------
# 1. Use official lightweight Python image
# ---------------------------
FROM python:3.10-slim

# ---------------------------
# 2. Set work directory inside the container
# ---------------------------
WORKDIR /app

# ---------------------------
# 3. Copy dependency file(s)
# ---------------------------
COPY requirements.txt .

# ---------------------------
# 4. Install dependencies
# ---------------------------
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------
# 5. Copy the rest of your app code
# ---------------------------
COPY . .

# ---------------------------
# 6. Expose the port your app uses
# ---------------------------
EXPOSE 8000

# ---------------------------
# 7. Run using Gunicorn (production WSGI server)
# ---------------------------
# "app" = app.py file
# "app" = Flask app variable inside app.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
