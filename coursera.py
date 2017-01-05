import requests
import random
import json
import argparse

from collections import OrderedDict
from openpyxl import Workbook
from bs4 import BeautifulSoup
from lxml import etree


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--courses", dest="courses_amount", action="store", type=int,
                        default=20, help="courses amount for getting information about")
    parser.add_argument("--output", dest="output_filepath", action="store", type="string",
                        default=None, help="filepath for outputting exel file")
    return parser.parse_args()


def get_random_courses_page_urls(amount):
    courses_xml_data_page = "https://www.coursera.org/sitemap~www~courses.xml"
    try:
        courses_xml_data = requests.get(courses_xml_data_page).content
    except requests.exceptions.RequestException as error:
        print(error)
        return []
    else:
        tree = etree.XML(courses_xml_data)
        courses_amount = (len(tree))
        random_numbers = random.sample(range(courses_amount), amount)
        return [tree[random_number][0].text for random_number in random_numbers]


def get_course_page_html_content(course_page_url):
    try:
        course_page = requests.get(course_page_url)
    except requests.exceptions.RequestException as error:
        print(error)
    else:
        return BeautifulSoup(course_page.content.decode('utf-8', 'ignore'), "lxml")


def get_course_title(soup):
    title_html = soup.find("div", "title display-3-text")
    return title_html.text if title_html is not None else None


def get_course_rating(soup):
    rating_html = soup.find("div", "ratings-text")
    return rating_html.text.split()[0] if rating_html is not None else None


def get_course_language(soup):
    language_html = soup.find("div", "language-info")
    return language_html.text.split(",")[0] if language_html is not None else None


def get_course_subtitles(soup):
    try:
        subtitles = soup.find("div", "language-info").text.split(":")[1]
    except (IndexError, AttributeError):
        return "No subtitles"
    else:
        return subtitles


def get_course_total_weeks(soup):
    return len(soup.find_all("div", "week"))


def get_course_start_date(soup):
    course_json_data = soup.find("script", attrs={"type": "application/ld+json"})
    if course_json_data is not None:
        return json.loads(course_json_data.text)['hasCourseInstance'][0]["startDate"]


def output_courses_info_to_xlsx(courses_info, output_filepath):
    wb = Workbook()
    ws = wb.active
    ws.append(["TITLE", "RATING", "LANGUAGE", "SUBTITLES", "TOTAL WEEKS", "START DATE"])
    for course_info in courses_info:
        ws.append(list(course_info.values()))
    if output_filepath is not None:
        wb.save("{}/coursera_courses.xlsx").format(output_filepath)
    else:
        wb.save("coursera_courses.xlsx")


if __name__ == "__main__":
    args = get_args()
    courses_info = []
    for page_url in get_random_courses_page_urls(args.courses_amount):
        course_info = OrderedDict()
        soup = get_course_page_html_content(page_url)
        if soup is None:
            break
        course_info["title"] = get_course_title(soup)
        course_info["rating"] = get_course_rating(soup)
        course_info["language"] = get_course_language(soup)
        course_info["subtitles"] = get_course_subtitles(soup)
        course_info["total weeks"] = get_course_total_weeks(soup)
        course_info["start_date"] = get_course_start_date(soup)
        courses_info.append(course_info)
    output_courses_info_to_xlsx(courses_info, args.output_filepath)
