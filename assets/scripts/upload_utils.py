from fastapi import File, UploadFile


def dataUpload(file: UploadFile = File(...)):
    try:
        file_data = file.file.read()
        with open(f"uploads/{file.filename}", "wb") as f:
            f.write(file_data)

        return "Archivo recibido correctamente.", file.filename
    except Exception as e:
        return str(e)