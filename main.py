import json
import sys
from collector import collect_metrics
from alerts import check_thresholds, THRESHOLDS


metrics=collect_metrics()
alerts=check_thresholds(metrics,THRESHOLDS)

report={
    "metrics":metrics,
    "alerts":alerts
}

with open("report.json","w") as f:
    json.dump(report,f,indent=4)

print("CPU:", metrics["cpu"], "%")
print("RAM:", metrics["memory"], "%")
print("DISK:", metrics["disk"], "%")


if alerts:
    for alert in alerts:
        print(f"WARNING: {alert}")
    sys.exit(2)

else:
    print("All metrics are normal")
    
    
