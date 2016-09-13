import urllib2
import json
import mwparserfromhell
import threading
from functools import partial

URL = "https://ru.wikipedia.org/w/api.php?action=query&pageids=122980" \
      "&prop=revisions&rvprop=content&rvsection=1&format=json"

_subway_list = []
_subway_lock = threading.RLock()

def get_nearest_subway(coord):
    global _subway_list

    with _subway_lock:
        if not _subway_list:
            _subway_list = _get_subway_list()

    return min(_subway_list, key=partial(_distance, coord))


def _distance(s, d):
    return (s[0] - d[0]) ** 2 + (s[1] - d[1]) ** 2


def _get_subway_list():
    response = urllib2.urlopen(URL)
    json_response = json.load(response)
    wiki_table = json_response["query"]["pages"]["122980"]["revisions"][0]["*"]

    wiki_table = mwparserfromhell.parse(wiki_table).filter_templates()

    table = []
    for template in wiki_table:
        if template.name == "coord":
            table.append((
                float(template.get(1).value.get(0).value),
                float(template.get(2).value.get(0).value),
                template.get("name").value.get(0).value,
            ))

    return table


if "__main__" == __name__:
    import sys

    if 3 != len(sys.argv):
        print("Usage: %s latitude longitude" % sys.argv[0])
        sys.exit()

    nearest = get_nearest_subway((float(sys.argv[1]), float(sys.argv[2])))
    print(nearest[2])
