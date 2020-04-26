import os
import json
from flask import Flask
from flask import request, render_template
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
app_instance.config.from_object(BasicConfig)

FILES = dict({})


@app_instance.route("/upload", methods=["POST", "PUT"])
def upload():
    if request.method == "PUT":
        # Di sini akan diprosess file file yang sudah di split di Front-End
        files = request.files.get("file")
        # Selain File, dikirim juga meta data.
        # Alternative bisa menggunakan id saja
        # Bisa di taruh di query param atau query search
        # Di kasus ini saya taruh di form request
        metadata = json.loads(request.form.get("metadata"))

        filename = secure_filename(files.filename)

        # Membuat full path untuk temporary file
        full_path_temp_file = os.path.join(
            app_instance.config.get("TEMP_FOLDER"), filename)
        # Simpan temporary file
        files.save(full_path_temp_file)
        # Baca size dari temporary file yang disimpan
        size = os.stat(full_path_temp_file).st_size
        # Menambahkan isi dari binary data dari temporary file
        FILES[metadata["Name"]]["Data"] += files
        # Update besar file yang sudah di prosess
        FILES[metadata["Name"]]["Downloaded"] += size
        # Menampung nama file dari temprary file
        FILES[metadata["Name"]]["FileTemp"].append(filename)
        # Jika File size sama dengan besar file yang sudah di prosess
        if FILES[metadata["Name"]]["Size"] == FILES[metadata["Name"]]["Downloaded"]:
            # Membuat Full path target file
            full_path_target_file = os.path.join(
                app_instance.config.get("UPLOAD_FOLDER"),
                metadata["Name"]
            )
            # Buka dan buat file target / file hasil
            with open(full_path_target_file, "+w") as file:
                # Gabungkan binary files yang di simpan
                # Di file target / file hasil dan simpan
                file.writelines(FILES[metadata["Name"]]["Data"])
            # Menghapus temporary file yang sudah dibuat
            for del_file in FILES[metadata["Name"]]["FileTemp"]:
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
        # Di post hanya kirim meta data doang
        data = request.get_json(force=True)
        # Di bawah ini bisa disimpan di database
        # Ini untuk nama file
        FILES[data["Name"]] = dict({"Name": data["Name"]})
        # Ini untuk besar file
        FILES[data["Name"]]["Size"] = data["Size"]
        # Ini untuk besar file yang sudah diprogress di BE
        FILES[data["Name"]]["Downloaded"] = 0
        # Ini untuk menyimpan sementara binary data dari temporary file
        FILES[data["Name"]]["Data"] = []
        # Ini untuk menuimpan sementara nama file-file temporary
        # Tujuannya ketika selesai di gabungkan, file-file temporary akan dihapus
        FILES[data["Name"]]["FileTemp"] = []
        # Kirim meta data yang telah tersimpan
        return FILES[data["Name"]]


@app_instance.route("/")
def index():
    return render_template("index.html")
