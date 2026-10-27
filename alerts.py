from collector import collect_metrics

THRESHOLDS = {"cpu": 80, "memory": 80, "disk": 90}


def check_thresholds(metrics, thresholds):
    alerts = []

    for name, limits in thresholds.items():
        value = metrics[name]
        if value > limits:
            alerts.append(f"{name} is at {value}% (limit is {limits})")
    return alerts


if __name__ == "__main__":
    metrics = collect_metrics()
    print(check_thresholds(metrics, THRESHOLDS))
