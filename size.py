# returns the size of toponym
def get_toponym_size(toponym):
    lon_1, lat_1 = toponym['boundedBy']['Envelope']['lowerCorner'].split()
    lon_2, lat_2 = toponym['boundedBy']['Envelope']['upperCorner'].split()

    lon_delta = abs(float(lon_1) - float(lon_2))
    lat_delta = abs(float(lat_1) - float(lat_2))

    return ','.join(list(map(str, [lon_delta, lat_delta])))