import os
from .app import app, db

if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    db.create_all()
