import requests
import random
import json
import argparse
import os.path
import logging

from collections import OrderedDict
from openpyxl import Workbook
from bs4 import BeautifulSoup
from lxml import etree


def get_logger():
    logging.basicConfig(level=logging.INFO)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--courses", dest="courses_amount", action="store", type=int,
                        default=20, help="courses amount for getting information about")
    parser.add_argument("--output", dest="output_filepath", action="store", type=str,
                        default="", help="absolute folder filepath for outputted file")
    return parser.parse_args()


def get_random_courses_page_urls(amount):
    courses_xml_data_page = "https://www.coursera.org/sitemap~www~courses.xml"
    try:
        courses_xml_data = requests.get(courses_xml_data_page, timeout=15).content
    except requests.exceptions.RequestException:
        raise requests.exceptions.RequestException(
            u"Can not connect to coursera-xml-feed page")
    else:
        tree = etree.XML(courses_xml_data)
        all_courses_page_urls = [tree[i][0].text for i in range(len(tree))]
        return random.sample(all_courses_page_urls, amount)


def get_course_page_html_content(course_page_url):
    try:
        course_page = requests.get(course_page_url, timeout=15)
    except requests.exceptions.RequestException as error:
        logging.info(
            u"Can not connect to course URL:\n{}\n{}\n".format(course_page_url, error))
    else:
        return BeautifulSoup(course_page.content.decode("utf-8", "ignore"), "lxml")


def get_course_title(soup):
    title_html = soup.find("div", "title display-3-text")
    return title_html.text if title_html is not None else None


def get_course_rating(soup):
    try:
        rating = float(soup.find("div", "ratings-text").text.split()[0])
    except (IndexError, AttributeError, ValueError):
        return None
    else:
        return rating


def get_course_language(soup):
    language_html = soup.find("div", "language-info")
    return language_html.text.split(",")[0] if language_html is not None else None


def get_course_subtitles(soup):
    try:
        subtitles = soup.find("div", "language-info").text.split(":")[1]
    except (IndexError, AttributeError):
        return None
    else:
        return subtitles


def get_course_total_weeks(soup):
    weeks_html_list = soup.find_all("div", "week")
    return len(weeks_html_list) if weeks_html_list else None


def get_course_start_date(soup):
    course_json_data = soup.find("script", attrs={"type": "application/ld+json"})
    try:
        start_date = json.loads(course_json_data.text)["hasCourseInstance"][0]["startDate"]
    except (KeyError, AttributeError):
        return None
    else:
        return start_date


def output_courses_info_to_xlsx_file(courses_info):
    work_book = Workbook()
    work_sheet = work_book.active
    work_sheet.append(["TITLE", "RATING", "LANGUAGE", "SUBTITLES", "TOTAL WEEKS", "START DATE"])
    for course_info in courses_info:
        course_info_cells = [course_info if course_info is not None else "no info"
                             for course_info in list(course_info.values())]
        work_sheet.append(course_info_cells)
    return work_book


def save_xlsx_file(work_book, output_filepath):
    if not output_filepath:
        work_book.save("coursera_courses.xlsx")
        logging.info(u"File was successfully saved to script dir")
        return
    if not os.path.exists(output_filepath):
        work_book.save("coursera_courses.xlsx")
        logging.warning(u"Path does not exist. File was saved to script dir")
    else:
        work_book.save(os.path.join(output_filepath, "coursera_courses.xlsx"))
        logging.info(u"File was successfully saved to dir")


if __name__ == "__main__":
    get_logger()
    args = get_args()
    courses_info = []
    for page_url in get_random_courses_page_urls(args.courses_amount):
        course_info = OrderedDict()
        course_page_html_content = get_course_page_html_content(page_url)
        if course_page_html_content is None:
            courses_info.append({"error": "could not connect to %s" % page_url})
            continue
        course_info["title"] = get_course_title(course_page_html_content)
        course_info["rating"] = get_course_rating(course_page_html_content)
        course_info["language"] = get_course_language(course_page_html_content)
        course_info["subtitles"] = get_course_subtitles(course_page_html_content)
        course_info["total_weeks"] = get_course_total_weeks(course_page_html_content)
        course_info["start_date"] = get_course_start_date(course_page_html_content)
        courses_info.append(OrderedDict(course_info))
    save_xlsx_file(output_courses_info_to_xlsx_file(courses_info), args.output_filepath)
