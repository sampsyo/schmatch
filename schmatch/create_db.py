import os
from .app import app, db


def create(drop_first=False):
    os.makedirs(app.instance_path, exist_ok=True)
    if drop_first:
        db.drop_all()
    db.create_all()


if __name__ == '__main__':
    create()
