from gcloud import datastore
from google.appengine.api import app_identity

__client = datastore.Client(app_identity.get_application_id())


def add_location(user_id, user_location):
    with __client.transaction():

        key = __client.key("Location", user_id)
        location = __client.get(key)

        if location:
            location["latitude"] = user_location["latitude"]
            location["longitude"] = user_location["longitude"]
        else:
            location = datastore.Entity(key)
            location.update({
                "user_id": user_id,
                "latitude": user_location["latitude"],
                "longitude": user_location["longitude"],
            })

        __client.put(location)
        return location.key


def get_location(user_id):
    query = __client.query(kind='Location')
    query.add_filter('user_id', '=', user_id)

    result = list(query.fetch())
    return result[0] if result else []


if "__main__" == __name__:

    print add_location(1, {"latitude": 55.733431, "longitude": 37.581254,})
    print add_location(3, {"latitude": 55.733431, "longitude": 37.581254,})
    print get_location(3)