iter_cnt = 0
def progresing_usd_course():
    nonlocal iter_cnt
    calc_usd = 76.32 + 0.1 * iter_cnt
    iter_cnt += 1
    return calc_usd
mock_get_usd_course.side_effect = progresing_usd_course