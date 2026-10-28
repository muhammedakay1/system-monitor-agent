import argparse
import logging
import json
import sys
from collector import collect_metrics
from alerts import check_thresholds, THRESHOLDS,SSH_FAIL_LIMIT
from auth_parser import parse_auth_file, count_failed_by_ip





parser = argparse.ArgumentParser(description="Monitor CPU, memory and disk usage.")
parser.add_argument("--output", default="report.json", help="Path of the JSON report")
parser.add_argument("--auth-log", default=None, help="Path of an auth.log file to analyze")
args = parser.parse_args()

logging.basicConfig(
    filename="monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Monitor started")

metrics = collect_metrics()
alerts = check_thresholds(metrics, THRESHOLDS)

if args.auth_log:
    failed_logs=parse_auth_file(args.auth_log)
    ip_counts=count_failed_by_ip(failed_logs)
    for ip, count in ip_counts.items():
        if count>=SSH_FAIL_LIMIT:
            alerts.append(f"ssh: {count} failed logins from {ip}")

report = {"metrics": metrics, "alerts": alerts}

with open(args.output, "w") as f:
    json.dump(report, f, indent=4)

print("CPU:", metrics["cpu"], "%")
print("RAM:", metrics["memory"], "%")
print("DISK:", metrics["disk"], "%")


if alerts:
    for alert in alerts:
        print(f"WARNING: {alert}")
        logging.warning(alert)
    sys.exit(2)

else:
    print("All metrics are normal")
    logging.info("All metrics are normal")
