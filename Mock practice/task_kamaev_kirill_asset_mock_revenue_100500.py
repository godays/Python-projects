mock_asset_class.calculate_revenue.return_value = 100500.0
mock_asset_class.build_from_str.return_value = mock_asset_class
periods = [1, 2, 5, 10]

with open(asset_filepath) as asset_fin:
    print_asset_revenue(asset_fin, periods=periods)

    captured = capsys.readouterr()

    assert len(periods) == len(captured.out.splitlines())
    for line in captured.out.splitlines():
        assert "100500" in line
