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

    def matches(self):
        """Get a query for all the matches involving this resource.
        """
        if self.left:
            return Match.query.filter_by(left_resource=self)
        else:
            return Match.query.filter_by(right_resource=self)


class Slot(db.Model):
    """A *slot* is a context in which resources can be matched in a
    schedule---i.e., a time range.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    matches = db.relationship("Match", lazy=True)

    def __repr__(self):
        return '<Slot {!r}>'.format(self.name)


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
    slot = db.relationship('Slot', lazy=True)

    left_resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    left_resource = db.relationship('Resource', lazy=True,
                                    foreign_keys=[left_resource_id])

    right_resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
    right_resource = db.relationship('Resource', lazy=True,
                                     foreign_keys=[right_resource_id])

    description = db.Column(db.String(256))

    def __repr__(self):
        return '<Match slot={} left={} right={}>'.format(
            self.slot_id,
            self.left_resource_id,
            self.right_resource_id,
        )


def get_schedule(resource, slots):
    """Given a list of slots, get a mapping from slot IDs to matches
    involving a resource (or None if there is no match in the slot).
    """
    sched = {s.id: None for s in slots}
    for match in resource.matches().all():
        assert sched[match.slot.id] is None
        sched[match.slot.id] = match
    return sched


def get_availability(slot, left=False):
    """Get a list of the resources that are available in a given slot.
    """
    # Find all the resource IDs that are taken in this slot.
    if left:
        taken_resources = [m.left_resource_id for m in slot.matches]
    else:
        taken_resources = [m.right_resource_id for m in slot.matches]
    taken_resources = [i for i in taken_resources if i is not None]

    # Get all the resources not in this list.
    if left:
        rsrcs = Resource.query.filter_by(left=True)
    else:
        rsrcs = Resource.query.filter_by(left=False)
    return rsrcs.filter(~Resource.id.in_(taken_resources)).all()


@app.route('/slots', methods=['GET', 'POST'])
def slots():
    if request.method == 'POST':
        slot = Slot(name=request.form['name'])
        db.session.add(slot)
        db.session.commit()

    # Show all the slots.
    slots = Slot.query.all()
    return render_template('slots.html', slots=slots)


@app.route('/', methods=['GET', 'POST'])
def resources():
    if request.method == 'POST':
        resource = Resource(
            name=request.form['name'],
            left=request.form['side'] == 'left',
        )
        db.session.add(resource)
        db.session.commit()

    # List the resources.
    resources = Resource.query.all()
    return render_template('resources.html', resources=resources)


@app.route('/schedules/<int:id>', methods=['GET', 'POST'])
def resource(id):
    resource = Resource.query.get(id)
    slots = Slot.query.all()

    # Update the schedule.
    if request.method == 'POST':
        # Remove all the old matches.
        resource.matches().delete()

        for slot in slots:
            slot_key = 'slot_{}'.format(slot.id)
            if slot_key in request.form:
                slot_value = request.form[slot_key]

                # The slot value is either "none" or the ID of an entity
                # to schedule.
                if slot_value != 'none':
                    # Add a match in this slot.
                    rsrc_id = int(slot_value)
                    if resource.left:
                        match = Match(
                            slot_id=slot.id,
                            left_resource_id=resource.id,
                            right_resource_id=rsrc_id,
                        )
                    else:
                        match = Match(
                            slot_id=slot.id,
                            left_resource_id=rsrc_id,
                            right_resource_id=resource.id,
                        )
                    db.session.add(match)

        db.session.commit()

    # Show current schedule and availability.
    avail = {s.id: get_availability(s, not resource.left) for s in slots}
    return render_template(
        'schedule.html',
        slots=slots,
        resource=resource,
        schedule=get_schedule(resource, slots),
        availability=avail,
    )
