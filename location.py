# coding=utf-8

import urllib2
import json
import mwparserfromhell
import threading
from functools import partial
from telegram import ReplyKeyboardHide as KeyboardHide


URL_SUBWAYS = "https://ru.wikipedia.org/w/api.php?action=query&pageids=122980" \
              "&prop=revisions&rvprop=content&rvsection=1&format=json"

URL_DRUGSTORES = "http://aptekamos.ru/apteka/api/Services/OrgInRdd/GetOrgList?" \
                 "startRow=1&numRows=10000"

_subway_list = []
_drugstores_list = []
_location_lock = threading.RLock()


def location_handler(location):
    subways = get_nearest_subway((location.latitude, location.longitude))
    stores = get_nearest_store((location.latitude, location.longitude))

    text = "Ближайшее к вам метро: {}\r\n" \
           "Рядом есть аптека {} по адресу {}"\
        .format(subways[2], stores[3], stores[2])

    return {
        "text": text,
        "reply_markup": KeyboardHide(),
    }


def get_nearest_subway(coord):

    if not _subway_list:
        _fill_lists()

    return min(_subway_list, key=partial(_distance, coord))


def get_nearest_store(coord):

    if not _drugstores_list:
        _fill_lists()

    return min(_drugstores_list, key=partial(_distance, coord))


def _fill_lists():
    with _location_lock:
        threads = []
        if not _subway_list:
            t = threading.Thread(target=_fill_subway_list, args=(_subway_list,))
            threads.append(t)
        if not _drugstores_list:
            t = threading.Thread(target=_fill_drugstore_list, args=(_drugstores_list,))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()


def _distance(s, d):
    return (s[0] - d[0]) ** 2 + (s[1] - d[1]) ** 2


def _fill_subway_list(fill_list):
    response = urllib2.urlopen(URL_SUBWAYS)
    json_response = json.load(response)
    wiki_table = json_response["query"]["pages"]["122980"]["revisions"][0]["*"]

    wiki_table = mwparserfromhell.parse(wiki_table).filter_templates()

    for template in wiki_table:
        if template.name == "coord":
            fill_list.append((
                float(template.get(1).value.get(0).value),
                float(template.get(2).value.get(0).value),
                template.get("name").value.get(0).value.encode('utf-8'),
            ))


def _fill_drugstore_list(fill_list):
    response = urllib2.urlopen(URL_DRUGSTORES)
    json_response = json.load(response)

    fill_list.extend([
        (
          r["gposY"],
          r["gposX"],
          r["orgAddress"].encode('utf-8'),
          r["orgName"].encode('utf-8'),
        ) for r in json_response["resultSet"]
    ])


if "__main__" == __name__:
    import sys

    if 3 != len(sys.argv):
        print("Usage: %s latitude longitude" % sys.argv[0])
        sys.exit()

    nearest = get_nearest_subway((float(sys.argv[1]), float(sys.argv[2])))
    print(nearest[2])

    nearest = get_nearest_store((float(sys.argv[1]), float(sys.argv[2])))
    print(nearest[2])

    t = type('test', (), {})()
    t.latitude = float(sys.argv[1])
    t.longitude = float(sys.argv[2])
    print (location_handler(t))
