import pytest

from flaskr.models import Song


class TestSongListResource(object):
    def test_get_empty(self, client):
        result = client.get('/songs')
        assert result.status_code == 200
        assert result.json == []

    def test_get_list(self, client, random_song_generator):
        song = random_song_generator()
        result = client.get('/songs')
        assert result.status_code == 200
        assert result.json == [song.to_json()]

    def test_with_pagination(self, client, random_song_generator):
        # generate pool of 3 songs
        [random_song_generator() for _ in range(3)]

        # test first page
        result = client.get('/songs?page_size=2&page=1')
        assert result.status_code == 200
        assert len(result.json) == 2

        # test second page
        result = client.get('/songs?page_size=2&page=2')
        assert result.status_code == 200
        assert len(result.json) == 1

        # test non-existing page
        result = client.get('/songs?page_size=2&page=3')
        assert result.status_code == 404


class TestSongListSearchResource(object):
    def test_with_wrong_message(self, client, random_song_generator):
        song = random_song_generator()
        song.title = 'Beautiful song'
        song.artist = 'Slipknot'
        song.save()

        result = client.get('/songs/search?message=Bob')
        assert result.json == []

    def test_search_by_title(self, client, random_song_generator):
        song = random_song_generator()
        song.title = 'Beautiful song'
        song.artist = 'Slipknot'
        song.save()

        result = client.get('/songs/search?message=song')
        assert result.json == [song.to_json()]

    def test_search_by_artist(self, client, random_song_generator):
        song = random_song_generator()
        song.title = 'Beautiful song'
        song.artist = 'Avenged sevenfold'
        song.save()

        result = client.get('/songs/search?message=sevenfold')
        assert result.json == [song.to_json()]


class TestSongPollResource(object):
    def test_with_valid_params(self, client, random_song_generator):
        song = random_song_generator()
        data = {'song_id': song.mongo_id, 'rating': 1}
        result = client.post('/songs/rating', data=data)

        assert result.status_code == 200
        assert Song.query.get(song.mongo_id).ratings == [1]

    @pytest.mark.parametrize('song_id', [-1, 1, 'abc', None])
    def test_with_invalid_song_id(self, client, song_id):
        data = {'song_id': song_id, 'rating': 0}
        result = client.post('/songs/rating', data=data)
        assert result.status_code == 400

    @pytest.mark.parametrize('rating', [-1, 'abc', 10, None])
    def test_with_invalid_ratings(self, client, random_song_generator, rating):
        song = random_song_generator()
        data = {'song_id': song.mongo_id, 'rating': rating}
        result = client.post('/songs/rating', data=data)

        assert result.status_code == 400
        assert Song.query.get(song.mongo_id).ratings == []


class TestSongDifficultyStatResource(object):
    @pytest.mark.parametrize(
        'difficulties, levels, expected_value_for_all, expected_for_level1',
        [
            (
                [0, 0, 0],
                [1, 1, 1],
                0,
                0,
            ),
            (
                [1, 2, 3],
                [1, 1, 1],
                2,
                2,
            ),
            (
                [2, 4, 100500],
                [1, 1, 0],
                33502,
                3,
            ),
            (
                [1, 1, 1],
                [0, 0, 0],
                1,
                None,
            )
        ]
    )
    def test_with_valid_params(
        self, client, random_song_generator, difficulties, levels,
        expected_value_for_all, expected_for_level1
    ):
        songs = [random_song_generator() for _ in difficulties]
        for i, song in enumerate(songs):
            song.difficulty = difficulties[i]
            song.level = levels[i]
            song.save()

        # query for all levels
        result = client.get('/songs/avg/difficulty')
        assert result.status_code == 200
        assert result.json['average_difficulty'] == expected_value_for_all

        # query for only first level
        result = client.get('/songs/avg/difficulty?level=1')
        assert result.status_code == 200
        assert result.json['average_difficulty'] == expected_for_level1


class TestSongRatingStatResource(object):
    @pytest.mark.parametrize('ratings, results', [
        (
            [], [None, None, None],
        ),
        (
            [1, 1, 2, 3, 3],
            [2, 1, 3],
        ),
        (
            [1, 100, 10000],
            [3367, 1, 10000],
        )
    ])
    def test_with_valid_params(
        self, client, random_song_generator, ratings, results,
    ):
        song = random_song_generator()
        song.ratings = ratings
        song.save()

        result = client.get('/songs/avg/rating/{}'.format(song.mongo_id))
        expected = {
            'average': results[0],
            'lowest': results[1],
            'highest': results[2],
        }
        assert result.status_code == 200
        assert result.json == expected
