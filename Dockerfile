# Usa una imagen base de Python
FROM python:3.10

# Instalar LibreOffice para la conversión de DOCX a PDF
RUN apt-get update && apt-get install -y libreoffice libreoffice-common


# Configurar el directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app/

# Asegurar que pip está actualizado antes de instalar dependencias
RUN python -m pip install --upgrade pip

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8000
EXPOSE 8000

# Ejecutar la API con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
