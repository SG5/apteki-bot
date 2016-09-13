# coding=utf-8

import urllib2
import urllib
import lxml.html as html
from telegram import ReplyKeyboardMarkup as KeyboardMarkup
from telegram import ReplyKeyboardHide as KeyboardHide

DRUG_GET_URL = "http://www.medlux.ru/" + urllib.quote("лекарства/")


def drug_handler(text):
    drugs_list = get_drug_list(text)

    if len(drugs_list):
        keyboard = []
        for drug in drugs_list:
            drug_text = drug.find("span").text.encode('utf8')

            if text == drug_text:
                return {
                    "text": "Выбран препарат {}".format(drug_text),
                    "reply_markup": KeyboardHide()
                }
            keyboard.append(drug_text)

        if 6 < len(drugs_list):
            return {"text": "Слишком много препаратов с таким названием, "
                            "попробуйте уточнить название",
                    "reply_markup": KeyboardHide()}

        reply_markup = KeyboardMarkup([keyboard])
        return {"text": "Какой препарат вам подходит?", "reply_markup": reply_markup}

    return {"text": "Такого препарата не найдено"}


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

    drugs = drug_handler(sys.argv[1])
    print(drugs)
