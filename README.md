
How to run
----------

1. Install and start mongodb database.
1. Add index for text search:

       db.reviews.createIndex({artist: "text", title: "text"})
1. Change database name in settings.py
1. Make virtual environment for python and install requirements:

        python -m venv *env_path*
        source *env_path*/bin/activate
        pip install -r requirements.txt
1.
    Set flask variables:

        export FLASK_APP=flaskr
        export FLASK_ENV=*develop* or *production*
1. Start flask server:

        flask run
