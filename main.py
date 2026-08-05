from app.application import create_application

if __name__ == "__main__":
    app = create_application()
    raise SystemExit(app.exec())
