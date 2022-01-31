from unittest.mock import patch

from sleepy import (sleep_add, sleep_multiply)


@patch("sleepy.sleep")
def test_can_patching_sleeping_add(mock_time_sleep):
    sleep_add(1, 2)
    mock_time_sleep.assert_called_once_with(3)


@patch("time.sleep")
def test_can_patching_sleeping_mul(mock_time_sleep):
    sleep_multiply(1, 2)
    mock_time_sleep.assert_called_once_with(5)
