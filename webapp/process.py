import math


def process(data):
    # TODO: remove file output when no longer needed
    with open('out.json', 'w') as f:
        from json import dump
        dump(data, f)

    tracks = data['tracks']
    total = int(data['playlists'])

    top = [(obj, id) for id, obj in tracks.items()]

    top.sort(key=lambda o: o[0]['count'])
    top.reverse()

    # for obj, id in top[:200]:
    #     frac = 100.0 * obj['count'] / total

    out = {}
    min_count = 5
    for obj, id in top:
        if id and obj['count'] >= min_count:
            idf = math.log10(total / obj['count'])
            # ppm = 1000.0 * obj['count'] / total
            # out[id] = ppm;
            out[id] = idf

    # out['backoff_probability'] = 1000.0 * 1. / total
    out['backoff_idf'] = math.log10(total * 2 / 1)
    return top
