import argparse
import logging
import json
import sys
import time
from collector import collect_metrics
from alerts import check_thresholds, THRESHOLDS,SSH_FAIL_LIMIT
from auth_parser import parse_auth_file, count_failed_by_ip





parser = argparse.ArgumentParser(description="Monitor CPU, memory and disk usage.")
parser.add_argument("--output", default="report.json", help="Path of the JSON report")
parser.add_argument("--auth-log", default=None, help="Path of an auth.log file to analyze")
parser.add_argument("--interval", type=int ,default=0, help="Seconds between checks (0 = run once)")
args = parser.parse_args()

logging.basicConfig(
    filename="monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Monitor started")


def run_once(args):       
    metrics = collect_metrics()
    alerts = check_thresholds(metrics, THRESHOLDS)

    if args.auth_log:
        try:  
            failed_logs=parse_auth_file(args.auth_log)
        except FileNotFoundError:
            print(f"WARNING: {args.auth_log} is not found ")
            logging.warning(f"{args.auth_log} is not found ")
            sys.exit(1)
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
        return 2

    else:
        print("All metrics are normal")
        logging.info("All metrics are normal")
        return 0

if args.interval>0:
    while True:
        run_once(args)
        time.sleep(args.interval)
else:
    sys.exit(run_once(args))