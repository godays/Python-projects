@patch("time.sleep")
@patch("sleepy.sleep")
def test_can_mock_all_sleep(mock_sleep_add, mock_sleep_multiply):
    outcome = deepest_sleep_function(1, 2)
    assert 5 == outcome

    mock_sleep_add.assert_called_once_with(3)
    mock_sleep_multiply.assert_called_once_with(5)
