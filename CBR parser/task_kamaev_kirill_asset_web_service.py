"""asset web service"""
from typing import Dict
from collections import defaultdict
from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.bank = {}

CBR_COURSE_DAILY_CUR_BASE_URL = "https://www.cbr.ru/eng/currency_base/daily/"
CBR_KEY_INDICATORS_BASE_URL = "https://www.cbr.ru/eng/key-indicators/"
CBR_CURRENCY_BASE_DAILY_FILEPATH = "cbr_currency_base_daily.html"
CBR_KEY_INDICATORS_BASE_FILEPATH = "cbr_key_indicators.html"

DEFAULT_ENCODING = "utf-8"
DEFAULT_STATUS_CODE = 200


def get_courses(table):
    """ get dict of courses"""
    rows = table.find_all('tr')
    res_dict = defaultdict()
    for row in rows:
        th_tags = row.find_all('th')
        if len(th_tags) == 0:
            columns = row.find_all('td')
            i = 0
            currency = str()
            rate = 0
            unit = 1
            for column in columns:
                if 1 == i:
                    currency = column.get_text()
                if 2 == i:
                    unit = int(column.get_text())
                if 4 == i:
                    rate = round(float(column.get_text()) / unit, 8)
                i += 1
            res_dict[currency] = rate
    return res_dict


def get_key_indicators(div_drop):
    """get dict key indicators"""
    course_flag = False
    metals_flag = False
    res_dict = defaultdict()

    for div_el in div_drop:
        if div_el.get_text().find("Main Indicators of Financial Market") != -1:
            cur_dropdown_content = div_el.findChildren(
                "div", recursive=False)[1]
            div = cur_dropdown_content.findChildren(
                "div", recursive=False)

            for div_cur_value in div:
                if metals_flag:
                    met_table = div_cur_value.find("table")
                    rows = met_table.find_all(
                        'tr', class_=lambda x: x != 'denotements')
                    for row in rows:
                        currency = row.find(
                            "div", attrs={"class": "col-md-3"}).get_text()
                        tmp = row.find_all('td')
                        tmp_len = len(row.find_all('td'))
                        cur_rate = tmp[tmp_len - 1].get_text().replace(",", "")

                        rate = round(float(cur_rate), 8)
                        res_dict[currency] = rate
                    metals_flag = False
                if course_flag:
                    course_table = div_cur_value.find("table")
                    rows = course_table.find_all(
                        'tr', class_=lambda x: x != 'denotements')
                    for row in rows:
                        currency = row.find(
                            "div", attrs={"class": "col-md-3"}).get_text()
                        cur_rate = row.find_all(
                            'td')[2].get_text().replace(",", "")

                        rate = round(float(cur_rate), 8)
                        res_dict[currency] = rate

                    course_flag = False

                if div_cur_value.get_text().find("Precious Metals") != -1:
                    metals_flag = True
                if div_cur_value.get_text().find("Foreign Currency Market") != -1:
                    course_flag = True
    return res_dict


def parse_cbr_currency_base_daily(html_data: str) -> Dict[str, float]:
    """parsing courses from html data docstr"""
    logging_soup = BeautifulSoup(html_data, features="html.parser")
    table = logging_soup.find(
        "table", attrs={"class": "data"})
    res_dict = get_courses(table)
    return res_dict


@app.errorhandler(404)
def page_do_not_exist(error):
    """page not found docstring"""
    return "This route is not found", 404


@app.route("/cbr/daily")
def get_cbr_daily_courses():
    """ get cbr courses route docstring"""
    try:
        course_response = requests.get(CBR_COURSE_DAILY_CUR_BASE_URL)
        res_dict = parse_cbr_currency_base_daily(course_response.text)
        return jsonify(res_dict)
    except requests.exceptions.ConnectionError:
        return "CBR service is unavailable", 503


def parse_cbr_key_indicators(html_data: str) -> Dict[str, float]:
    """parsing key indicators from html data doc string"""
    logging_soup = BeautifulSoup(html_data, features="html.parser")
    div_drop = logging_soup.find_all(
        "div", attrs={"class": "dropdown"})

    res_dict = get_key_indicators(div_drop)
    return res_dict


@app.route("/cbr/key_indicators")
def get_cbr_key_indicators():
    """ get cbr key indicators route docstring"""
    try:
        indicators_response = requests.get(CBR_KEY_INDICATORS_BASE_URL)
        res_dict = parse_cbr_key_indicators(indicators_response.text)
        return jsonify(res_dict)
    except requests.exceptions.ConnectionError:
        return "CBR service is unavailable", 503


class AssetItem:
    """ class AssetItem check"""

    def __init__(self, char_code: str, name: str, capital: float, interest: float):
        """initialization function asset"""
        self.char_code = char_code
        self.name = name
        self.capital = capital
        self.interest = interest

    def calculate_revenue(self, years: int) -> float:
        """calculate revenue docstring"""
        revenue = self.capital * ((1.0 + self.interest) ** years - 1.0)
        return revenue

    def return_list(self):
        """return list"""
        return [self.char_code, self.name, self.capital, self.interest]


@app.route('/api/asset/add/<char_code>/<name>/<int:capital>/<float:interest>')
@app.route('/api/asset/add/<char_code>/<name>/<float:capital>/<float:interest>')
@app.route('/api/asset/add/<char_code>/<name>/<int:capital>/<int:interest>')
@app.route('/api/asset/add/<char_code>/<name>/<float:capital>/<int:interest>')
def add_asset(char_code, name, capital, interest):
    """add_new_asset function docstring"""
    if name in app.bank:
        return f"Asset '{name}' is already exist", 403
    asset1 = AssetItem(char_code, name, float(capital), float(interest))
    app.bank[name] = asset1
    return f"Asset {name} was successfully added"


@app.route('/api/asset/get')
def api_asset_get_return():
    """get asset list function docstring"""

    name_query_list = request.args.getlist("name")
    if isinstance(name_query_list, str):
        name_query_list = [name_query_list]
    set_name = set(name_query_list)
    result = []
    for ass_values in app.bank.values():
        if ass_values.name in set_name:
            result.append(ass_values.return_list())

    sorted_result = sorted(result, key=lambda x: x[0])
    return jsonify(sorted_result)


@app.route('/api/asset/list')
def api_asset_list_return():
    """get asset list function docstring"""
    result = []
    for ass in app.bank.values():
        result.append(ass.return_list())
    sorted_result = sorted(result, key=lambda x: x[0])
    return jsonify(sorted_result), 200


@app.route('/api/asset/cleanup')
def asset_clean_bank():
    """cleanup func docstring"""
    app.bank = {}
    return "there are no more assets", 200


@app.route('/api/asset/calculate_revenue')
def get_total_revenue():
    """ calculate revenue docstring"""
    res_dict = {}

    all_periods_param = request.args.getlist("period")

    if isinstance(all_periods_param, str):
        all_periods_param = [all_periods_param]

    cur_cbr_courses = get_cbr_daily_courses()
    json_cbr_course = cur_cbr_courses.json

    json_cbr_key_ind = get_cbr_key_indicators().json
    json_cbr_key_ind['RUB'] = 1
    json_cbr_course.update(json_cbr_key_ind)

    for period in map(int, all_periods_param):
        revenue = 0
        for ass in app.bank.values():
            if ass.char_code in json_cbr_course:
                revenue += json_cbr_course[ass.char_code] * \
                           ass.calculate_revenue(period)

        res_dict[period] = round(revenue, 8)
    return jsonify(res_dict)


if __name__ == '__main__':
    app.run()
