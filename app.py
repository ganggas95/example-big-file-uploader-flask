from uploader import app_instance

if __name__ == "__main__":
    app_instance.run("0.0.0.0", 8123, debug=True)
