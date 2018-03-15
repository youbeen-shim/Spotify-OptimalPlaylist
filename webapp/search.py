import spotipy
from multiprocessing import Pool
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id='64deb14a2c08404aac50e1b947268ed8',
                                                      client_secret='f7687d71f94e4f01a652f23d41c6be12')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# TODO: tweak
MAX_TRACKS_PER_PLAYLIST = 20
RESULTS_PER_PAGE = 25
MAX_SEARCH_PAGES = 8


class Searcher:
    def __init__(self, query, query_filter='playlist'):
        self.data = {
            'playlists': 0,
            'ntracks': 0,
            'offset': -1,
            'tracks': {}
        }
        self.query = query
        self.filter = query_filter or 'playlist'

    @staticmethod
    def is_good_playlist(items):
        artists = set()
        albums = set()
        for item in items:
            track = item['track']
            if track:
                artists.add(track['artists'][0]['id'])
                albums.add(track['album']['id'])
        return len(artists) > 1 and len(albums) > 1

    @staticmethod
    def process_playlist(playlist):
        max_per_playlist = MAX_TRACKS_PER_PLAYLIST

        tracks = {}
        ntracks = 0
        pid = playlist['id']
        uid = playlist['owner']['id']

        try:
            results = sp.user_playlist_tracks(uid, playlist['id'])
            # fields="items.track(!album)")

            if results and 'items' in results and Searcher.is_good_playlist(results['items']):
                if len(results['items']) > max_per_playlist:
                    results['items'] = results['items'][:max_per_playlist]
                for item in results['items']:
                    track = item['track']
                    if track:
                        tid = track['id']
                        if tid not in tracks:
                            title = track['name']
                            artist = track['artists'][0]['name']
                            tracks[tid] = {
                                'title': title,
                                'artist': artist,
                                'playlists': [playlist['name']],
                                'count': 0,
                            }
                        tracks[tid]['count'] += 1
                        ntracks += 1
            else:
                # print 'mono playlist skipped'
                pass
        except spotipy.SpotifyException:
            # print 'trouble, skipping'
            pass
        return tracks, ntracks

    def crawl_playlists(self):
        limit = RESULTS_PER_PAGE
        max_pages = MAX_SEARCH_PAGES

        offset = 0 if self.data['offset'] < 0 else self.data['offset'] + limit
        results = sp.search(self.query, limit=limit, offset=offset, type=self.filter)
        playlist = results['playlists']
        total = playlist['total']
        for i in range(max_pages):
            print('Processing page', i + 1)
            with Pool(limit) as p:
                processed = p.map(self.process_playlist, playlist['items'])
                for tracks, ntracks in processed:
                    for k, v in tracks.items():
                        if k not in self.data['tracks']:
                            self.data['tracks'][k] = v
                        else:
                            self.data['tracks'][k]['count'] += v['count']
                            self.data['tracks'][k]['playlists'].append(v['playlists'][0])
                    self.data['ntracks'] += ntracks
                    self.data['playlists'] += 1
            if playlist['next']:
                results = sp.next(playlist)
                playlist = results['playlists']
            else:
                break

        self.data['offset'] = playlist['offset'] + playlist['limit']
        print('processed', self.data['playlists'], 'playlists out of', total)
        return self.data
