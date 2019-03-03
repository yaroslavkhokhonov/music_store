from flask import request
from flask_restful import Resource, reqparse, abort

from flaskr import db
from flaskr.models import Song
from flaskr.utils import with_pagination


def init_resources(api):
    api.add_resource(SongListResource, '/songs')
    api.add_resource(SongListSearchResource, '/songs/search')
    api.add_resource(SongPollResource, '/songs/rating')
    api.add_resource(SongDifficultyStatResource, '/songs/avg/difficulty')
    api.add_resource(SongRatingStatResource, '/songs/avg/rating/<song_id>')


class SongListResource(Resource):
    @with_pagination
    def get(self, page=None, page_size=None):
        query = Song.query

        if page is not None:
            query = query.paginate(page, page_size).items

        return [song.to_json() for song in query]


class SongListSearchResource(Resource):
    @with_pagination
    def get(self, page=None, page_size=None):
        parser = reqparse.RequestParser()
        parser.add_argument('message', type=str, required=True)
        message = parser.parse_args()['message']

        query = Song.query.filter({'$text': {'$search': message}})

        if page is not None:
            query = query.paginate(page, page_size).items

        return [song.to_json() for song in query]


class SongPollResource(Resource):
    def post(self):
        song_id = request.form.get('song_id')
        rating_str = request.form.get('rating')

        if not rating_str or not rating_str.isdigit():
            abort(400)
        rating = int(rating_str)

        if not (1 <= rating <= 5):
            abort(400)

        song = Song.query.get_or_404(song_id)
        song.ratings.append(rating)
        song.save()
        return song.to_json()


class SongDifficultyStatResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('level', type=int)
        level = parser.parse_args().get('level')

        pipeline = []
        if level is not None:
            pipeline.append({'$match': {'level': level}})

        pipeline.append({
            '$group': {
                '_id': None,
                'result': {'$avg': '$difficulty'}
            }
        })
        cursor = db.session.db.Song.aggregate(pipeline=pipeline, cursor={})

        for doc in cursor:
            return {'average_difficulty': doc['result']}
        else:
            return {'average_difficulty': None}


class SongRatingStatResource(Resource):
    def get(self, song_id):
        ratings = Song.query.get_or_404(song_id).ratings

        if not ratings:
            return {
                'average': None,
                'lowest': None,
                'highest': None,
            }

        return {
            'average': sum(ratings) / len(ratings),
            'lowest': min(ratings),
            'highest': max(ratings),
        }
