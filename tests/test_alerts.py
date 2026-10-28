from alerts import check_thresholds



def test_no_alert_when_all_below_limit():
    metrics = {"cpu": 10, "memory": 40, "disk": 30}
    thresholds = {"cpu": 80, "memory": 80, "disk": 90}

    result = check_thresholds(metrics, thresholds)
    assert result == []


def test_when_cpu_is_95():
    metrics = {"cpu": 95, "memory": 40, "disk": 30}
    thresholds = {"cpu": 80, "memory": 80, "disk": 90}

    result = check_thresholds(metrics, thresholds)
    assert len(result) == 1
    assert "cpu" in result[0]


def test_when_cpu_is_80():
    metrics = {"cpu": 80, "memory": 40, "disk": 30}
    thresholds = {"cpu": 80, "memory": 80, "disk": 90}

    result = check_thresholds(metrics, thresholds)
    assert result == []
