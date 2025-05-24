from app import create_app
from core.config import settings

app = create_app(settings)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
