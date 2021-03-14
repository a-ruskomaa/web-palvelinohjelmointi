import os
import tupa

app = tupa.create_app()

if __name__ == '__main__':
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    app.run(host, port)
