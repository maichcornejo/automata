# Dockerfile

FROM python:3.11-slim

# Instalar las dependencias del sistema, incluyendo Graphviz
RUN apt-get update && apt-get install -y graphviz

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exponer el puerto 5000
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
