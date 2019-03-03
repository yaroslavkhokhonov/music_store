from datetime import datetime
import random

import pymongo
import pytest

from flaskr import create_app
from flaskr.models import Song, db

POOL_ARTIST = [
    'Bob', 'Pool', 'Alice', 'Joy'
]
TITLES = [
    'Storytime',
    'Adrenalize',
    'Afterlife',
    'Goodbye Moonmen'
]


@pytest.fixture
def random_song_generator():
    def generator():
        song = Song(
            artist=random.choice(POOL_ARTIST),
            title=random.choice(POOL_ARTIST),
            difficulty=random.uniform(0, 15),
            level=random.randint(0, 15),
            released=datetime.now().replace(microsecond=0),
        )
        song.save()
        return song

    return generator


@pytest.fixture
def client():
    app = create_app(test_config={
        'MONGOALCHEMY_DATABASE': 'test_db',
        'TESTING': True,
    })
    client = app.test_client()

    db.session.db.Song.remove()
    db.session.db.Song.create_index(
        [('artist', pymongo.TEXT), ('title', pymongo.TEXT)]
    )
    yield client
