FROM python:3.10-slim

# Set working directory
WORKDIR /app
#Env
ENV  MYSQL_HOST=mysql
ENV  MYSQL_USER=root
ENV  MYSQL_PASSWORD=rootpass
ENV  MYSQL_DATABASE=devops_exam

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and templates folder
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
