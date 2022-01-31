from unittest.mock import patch

import pytest

from task_kamaev_kirill_web_spy import *

PATH_GITLAB_FEATURES = "gitlab_features.html"
URL_GITLAB = "https://about.gitlab.com/features/"
EXPECTED_GITLAB = "gitlab_features_expected.html"


@pytest.mark.slow
@patch("task_kamaev_kirill_web_spy.SpyWeb.get_html_url")
def test_can_mock_web(mock_task_kamaev_kirill_web_spy_SpyWeb_get_html_url):
    sw = SpyWeb()
    content = sw.get_html_from_file(PATH_GITLAB_FEATURES)
    mock_task_kamaev_kirill_web_spy_SpyWeb_get_html_url.return_value = content

    content = sw.get_html_url(URL_GITLAB)
    av_cnt, n_av_cnt = sw.calculate_free_and_non_free_products(content)

    assert 351 == av_cnt
    assert 218 == n_av_cnt


@pytest.mark.slow
def test_can_calc_correctly_from_file():
    sw_local = SpyWeb()
    sw_local.calculate_free_and_non_free_products(sw_local.get_html_from_file(PATH_GITLAB_FEATURES))
    assert 351 == sw_local.av_cnt
    assert 218 == sw_local.n_av_cnt


@pytest.mark.slow
def test_main_works_correctly():
    command_line = ["task_kamaev_kirill_web_spy.py",
                    "offline"]
    with patch.object(sys, "argv", command_line):
        main()


@pytest.mark.integration_test
def test_gitlab_have_expected_vals():
    sw_local = SpyWeb()
    sw_internet = SpyWeb()

    sw_local.calculate_free_and_non_free_products(sw_local.get_html_from_file(EXPECTED_GITLAB))
    sw_internet.calculate_free_and_non_free_products(sw_internet.get_html_url(URL_GITLAB))

    assert sw_local.av_cnt == sw_internet.av_cnt and sw_local.n_av_cnt == sw_internet.n_av_cnt, f"expected free product count is {sw_local.av_cnt}, while you calculated {sw_internet.av_cnt}; expected enterprise product count is {sw_local.n_av_cnt}, while you calculated {sw_internet.n_av_cnt}"
