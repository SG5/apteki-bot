# coding=utf-8

import database
import urllib2
import urllib
import lxml.html as html
from telegram import ReplyKeyboardMarkup as KeyboardMarkup

DRUG_GET_URL = "http://www.medlux.ru/" + urllib.quote("лекарства/")


def message_handler(message):
    """Handle message from user

    Args:
        message (:class:`telegram.Message`):
    """
    location = database.get_location(message.from_user.id)
    if not location:
        return {"text": "Для поиска лекарств отправь своё местоположение"}

    return get_drugs_message(message.text.encode('utf-8'))


def find_drugs(text):
    drugs_list = get_drug_list(text)

    if not drugs_list:
        return []

    result = []
    for drug in drugs_list:
        drug_text = drug.find("span").text.encode('utf-8')

        if text == drug_text:
            return [drug_text]

        result.append(drug_text)

    return result


def get_drugs_message(text):
    drugs_list = find_drugs(text)

    if not drugs_list:
        return {"text": "Такого препарата не найдено"}

    if 1 == len(drugs_list):
        return {"text": "Выбран препарат {}".format(drugs_list[0])}

    if 6 < len(drugs_list):
        return {"text": "Слишком много препаратов с таким названием, "
                        "попробуйте уточнить название",
                }

    reply_markup = KeyboardMarkup([drugs_list])
    return {"text": "Какой препарат вам подходит?", "reply_markup": reply_markup}


def get_drug_list(text):
    response = urllib2.urlopen(DRUG_GET_URL + urllib.quote(text))
    parser = html.parse(response).getroot()
    return parse_drug_list(parser)


def parse_drug_list(parser):
    try:
        return parser \
            .get_element_by_id("result-list") \
            .find_class("main-list").pop().getchildren()
    except KeyError:
        return []


if "__main__" == __name__:
    import sys

    if 2 != len(sys.argv):
        print("Usage: %s drug" % sys.argv[0])
        sys.exit()

    drugs = find_drugs(sys.argv[1])
    print(drugs)
