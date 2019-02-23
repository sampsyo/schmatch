import os
import flask
from flask import request, render_template
from flask_sqlalchemy import SQLAlchemy

# Our Flask application.
app = flask.Flask(__name__, instance_relative_config=True)

# Configuration. We include some defaults and allow overrides.
app.config.from_object('schmatch.config_default')
app.config.from_pyfile('schmatch.cfg', silent=True)

# Our database. By default, use a SQLite path in our instance directory.
if 'SQLALCHEMY_DATABASE_URI' not in app.config:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(app.instance_path, app.config['SQLITE_DATABASE_NAME'])
db = SQLAlchemy(app)


class Resource(db.Model):
    """A resource is a thing that can be scheduled, like a person or a
    room. Every resource is either on the "left" or "right," where
    schedules will match left resources with right resources.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    left = db.Column(db.Boolean())


class Slot(db.Model):
    """A *slot* is a context in which resources can be matched in a
    schedule---i.e., a time range.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))


class Match(db.Model):
    """A *match* describes the resource binding in a given slot. It can
    match left resources with right resources, or it can describe the
    binding for a single resource.

    Either (but not both) of `left_resource` or `right_resource` may be
    null. If one is null, then the other's binding is described by the
    `description` field.

    There can be only one match for a given (slot, left_resource) pair,
    and similarly for a given (slot, right_resource) pair.
    """
    id = db.Column(db.Integer, primary_key=True)

    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'))
    slot = db.relationship('Slot')

    left_resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    left_resource = db.relationship('Resource',
                                    foreign_keys=[left_resource_id])

    right_resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    right_resource = db.relationship('Resource',
                                     foreign_keys=[right_resource_id])

    description = db.Column(db.String(256))


@app.route('/slots', methods=['GET', 'POST'])
def show_slots():
    if request.method == 'POST':
        slot = Slot(name=request.form['name'])
        db.session.add(slot)
        db.session.commit()

    # Show all the slots.
    slots = Slot.query.all()
    return render_template('slots.html', slots=slots)
