Schedule Matcher
================

This is a little proof-of-concept tool for managing *systems of schedules* where resources need to be matched with one another. The purpose is scheduling for PhD visit days: there is a range of time windows during the day, during which prospective students need to meet with faculty. Of course, each person (prospective and faculty) can only be doing one thing at a time.

This is a [Flask][] web app that shows you each person schedule and lets you select, from a pop-up list, from the people on the opposite "side" who are available in each time slot. The interface is the same on both "sides," i.e., you can view and edit the schedule mapping from either the prospective or the faculty point of view.

[flask]: http://flask.pocoo.org


Setting Up
----------

You will need [Pipenv][]:

    $ pip install --user pipenv

Use it to set up the environment:

    $ pipenv install

Create the initial database:

    $ pipenv run python -m schmatch.create_db

Run a development server:

    $ FLASK_APP=schmatch pipenv run flask run

[pipenv]: https://pipenv.readthedocs.io/en/latest/
