# Usamos una imagen base con Python
FROM python:3.9-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos los archivos necesarios a la imagen
COPY . /app

# Instalamos las dependencias necesarias
RUN pip install -r requirements.txt

# Exponemos el puerto donde se ejecutará la app
EXPOSE 2540

# Comando para ejecutar la app cuando el contenedor inicie
CMD ["python", "app.py"]
