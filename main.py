from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from docx import Document
import shutil
import json
import os
import subprocess
from fastapi import HTTPException


libreoffice_check = subprocess.run(["libreoffice", "--version"], capture_output=True, text=True)
print("LibreOffice Version:", libreoffice_check.stdout)

app = FastAPI()

TEMP_DOCX = "temp.docx"
OUTPUT_PDF = "documento_editado.pdf"

def convert_docx_to_pdf(docx_path, pdf_path):
    try:
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", docx_path],
            check=True
        )
        print("✅ DOCX convertido a PDF correctamente.")
    except subprocess.CalledProcessError as e:
        print("❌ Error al convertir DOCX a PDF:", e)
        raise HTTPException(status_code=500, detail="Error al convertir DOCX a PDF")

@app.post("/edit-docx-to-pdf/")
async def edit_docx_to_pdf(
    file: UploadFile = File(...),
    replacements: str = Form(...)
):
    try:
        replacements = json.loads(replacements)  # Convertir JSON a diccionario
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in replacements")

    # Guardar el archivo DOCX temporalmente
    with open(TEMP_DOCX, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Cargar el documento Word
    doc = Document(TEMP_DOCX)

    # Aplicar reemplazos en párrafos
    for para in doc.paragraphs:
        texto_completo = "".join(run.text for run in para.runs)
        for clave, valor in replacements.items():
            if clave in texto_completo:
                texto_completo = texto_completo.replace(clave, valor)
                para.clear()
                para.add_run(texto_completo)

    # Aplicar reemplazos en tablas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    texto_completo = "".join(run.text for run in para.runs)
                    for clave, valor in replacements.items():
                        if clave in texto_completo:
                            texto_completo = texto_completo.replace(clave, valor)
                            para.clear()
                            para.add_run(texto_completo)

    # Guardar el documento editado
    doc.save(TEMP_DOCX)

    # Convertir DOCX a PDF usando docx2pdf
    convert_docx_to_pdf(TEMP_DOCX, OUTPUT_PDF)

    # Devolver el archivo PDF generado
    return FileResponse(OUTPUT_PDF, media_type="application/pdf", filename="temp.pdf")
