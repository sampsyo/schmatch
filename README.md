Schedule Matcher
================

You will need [Pipenv][]:

    $ pip install --user pipenv

Use it to set up the environment:

    $ pipenv install

Create the initial database:

    $ pipenv run python -m schmatch.create_db

Run a development server:

    $ FLASK_APP=schmatch.server pipenv run flask run

[pipenv]: https://pipenv.readthedocs.io/en/latest/
