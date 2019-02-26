from flask_mongoalchemy import MongoAlchemy

db = MongoAlchemy()


class Song(db.Document):
    artist = db.StringField()
    title = db.StringField()
    difficulty = db.FloatField()
    level = db.IntField()
    released = db.DateTimeField()
    ratings = db.ListField(db.IntField(), default=[])

    def to_json(self):
        return {
            '_id': str(self.mongo_id),
            'artist': self.artist,
            'title': self.title,
            'difficulty': self.difficulty,
            'level': self.level,
            'released': str(self.released),
        }
