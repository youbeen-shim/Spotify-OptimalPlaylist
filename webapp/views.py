from django.shortcuts import render
from .search import Searcher
from .process import process


def index_view(request):
    '''
    Index view renders a search bar with a list of results
    from the spotify_wrapper. landing page and subsequent searches
    end up here.
    if no query_filter is provided in the request we query with the default track filter
    validations of the query are handled by the api_wrapper instead of the view.
    '''
    search_query = request.GET.get('q')

    if search_query:
        search = Searcher(search_query)  # get_track_list(search_query, query_filter)
        data = search.crawl_playlists()
        items = process(data)
        count = len(items)
    else:
        count = 0
        items = []
    context = {
        'count': count,
        'items': items,
        'q': search_query
    }
    return render(request, 'index.html', context)
