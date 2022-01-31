import pytest
from bs4 import BeautifulSoup
from task_kamaev_kirill_asset_web_service import (
    app,
    get_courses,
    CBR_CURRENCY_BASE_DAILY_FILEPATH,
    DEFAULT_ENCODING,
    DEFAULT_STATUS_CODE,
)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_service_cbr_page_not_found(client):
    response = client.get("/cbr1/daily1")
    assert 404 == response.status_code


def test_service_cbr_indicators(client):
    response = client.get("/cbr/key_indicators")
    assert DEFAULT_STATUS_CODE == response.status_code


def test_offline_cbr_course():
    with open(CBR_CURRENCY_BASE_DAILY_FILEPATH, encoding=DEFAULT_ENCODING, mode="r") as fin:
        logging_html = fin.read()
    logging_soup = BeautifulSoup(logging_html, features="html.parser")
    table = logging_soup.find(
        "table", attrs={"class": "data"})
    get_courses(table)


def test_can_get_listof_assets(client):
    app.bank = {}
    response1 = client.get("/api/asset/add/RUB/T1/100/0.1")
    response2 = client.get("/api/asset/add/USD/T2/1000/0.1")
    response3 = client.get("/api/asset/add/EUR/T3/1000/0.1")
    response = client.get("/api/asset/calculate_revenue?period=1&period=2")
    assert response.is_json
