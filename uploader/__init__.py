import os
import json
from flask import Flask, abort
from flask import request, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename


class BasicConfig(object):
    TEMP_FOLDER = os.path.join(
        os.getcwd(),
        "temp"
    )
    UPLOAD_FOLDER = os.path.join(
        os.getcwd(),
        "upload"
    )


app_instance = Flask(
    __name__,
)

cors = CORS()
app_instance.config.from_object(BasicConfig)

cors.init_app(app_instance)
FILES = dict({})


@app_instance.route("/upload", methods=["POST", "PUT"])
def upload():
    if request.method == "PUT":
        # Di sini akan diprosess file file yang sudah di split di Front-End
        req_filename = request.args.get("filename", default=None, type=str)
        if req_filename is None:
            abort(400)
        files = request.files.get("file")
        # Selain File, dikirim juga meta data.
        # Alternative bisa menggunakan id saja
        # Bisa di taruh di query param atau query search
        # Di kasus ini saya taruh di form request

        filename = secure_filename(files.filename)

        # Membuat full path untuk temporary file
        full_path_temp_file = os.path.join(
            app_instance.config.get("TEMP_FOLDER"), filename)
        # Simpan temporary file
        files.save(full_path_temp_file)
        # Baca size dari temporary file yang disimpan
        size = os.stat(full_path_temp_file).st_size
        # Menambahkan isi dari binary data dari temporary file
        print(FILES[req_filename]["data"])
        with open(full_path_temp_file, 'rb') as file_temp:
            FILES[req_filename]["data"].append(file_temp.read())
            # file_temp.close()
        # Update besar file yang sudah di prosess
        FILES[req_filename]["downloaded"] += size
        # Menampung nama file dari temprary file
        FILES[req_filename]["file_temp"].append(filename)
        # Jika File size sama dengan besar file yang sudah di prosess
        if FILES[req_filename]["size"] == FILES[req_filename]["downloaded"]:
            # Membuat Full path target file
            full_path_target_file = os.path.join(
                app_instance.config.get("UPLOAD_FOLDER"),
                req_filename
            )
            # Buka dan buat file target / file hasil
            with open(full_path_target_file, "+wb") as file:
                # Gabungkan binary files yang di simpan
                # Di file target / file hasil dan simpan
                file.writelines(FILES[req_filename]["data"])
            # Menghapus temporary file yang sudah dibuat
            for del_file in FILES[req_filename]["file_temp"]:
                os.remove(os.path.join(
                    app_instance.config.get("TEMP_FOLDER"),
                    del_file
                ))
            return {
                "status": "Complete",
            }
        return {
            "status": "Uploading"
        }
    if request.method == 'POST':
        # Di post hanya kirim meta data saja
        data = request.get_json(force=True)
        # Di bawah ini bisa disimpan di database
        # Ini untuk nama file
        FILES[data["filename"]] = dict({"filename": data["filename"]})
        # Ini untuk besar file
        FILES[data["filename"]]["size"] = data["size"]
        # Ini untuk besar file yang sudah diprogress di BE
        FILES[data["filename"]]["downloaded"] = 0
        # Ini untuk menyimpan sementara binary data dari temporary file
        FILES[data["filename"]]["data"] = []
        # Ini untuk menyimpan sementara nama file-file temporary
        # Tujuannya ketika selesai di gabungkan, file-file temporary akan dihapus
        FILES[data["filename"]]["file_temp"] = []
        # Kirim meta data yang telah tersimpan
        return FILES[data["filename"]]


@app_instance.route("/")
def index():
    return render_template("index.html")
