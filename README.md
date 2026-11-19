# System Monitor Agent

![Tests](https://github.com/muhammedakay1/system-monitor-agent/actions/workflows/tests.yml/badge.svg)

A small Python agent that checks CPU, memory and disk usage, raises alerts when a threshold is exceeded, and analyzes an SSH `auth.log` file for repeated failed logins. Results are printed, logged and saved as a JSON report. It runs as a command-line tool or in a Docker container, and was deployed and tested on an AWS EC2 instance.

## Features

- Reads CPU, memory and disk usage with `psutil`
- Compares each value with a threshold and raises an alert when it is exceeded
- Parses SSH `auth.log` files and alerts when one IP address has too many failed logins
- Writes a JSON report and a log file (`monitor.log`)
- Runs once or repeats every N seconds
- Returns exit codes that scripts and containers can use
- Runs in Docker as a non-root user
- Automated tests with pytest, run on every push by GitHub Actions

## Requirements

- Python 3
- The packages in `requirements.txt` (`psutil`, `pytest`)
- Docker (optional)

## Installation

```bash
git clone https://github.com/muhammedakay1/system-monitor-agent.git
cd system-monitor-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Check the system once:

```bash
python main.py
```

Check the system and analyze an SSH log:

```bash
python main.py --auth-log logs/sample_auth.log
```

Check every 10 seconds until stopped with Ctrl + C:

```bash
python main.py --interval 10
```

| Option | Description | Default |
|---|---|---|
| `--output` | Path of the JSON report | `report.json` |
| `--auth-log` | Path of an `auth.log` file to analyze | not used |
| `--interval` | Seconds between checks (`0` runs once) | `0` |

Exit codes (single run):

- `0`: everything is normal
- `1`: error (the `--auth-log` file was not found)
- `2`: at least one alert was raised

With `--interval`, the program keeps running and stops only with Ctrl + C.

## Example output

```
CPU: 6.5 %
RAM: 82.7 %
DISK: 19.0 %
WARNING: memory is at 82.7% (limit is 80)
WARNING: ssh: 4 failed logins from 203.0.113.5
```
## Report format

Each run writes (and overwrites) a JSON report:

```json
{
    "metrics": {
        "timestamp": "2026-10-29 20:02:10.123456",
        "cpu": 6.5,
        "memory": 82.7,
        "disk": 19.0
    },
    "alerts": [
        "memory is at 82.7% (limit is 80)",
        "ssh: 4 failed logins from 203.0.113.5"
    ]
}
```


## How detection works

- **System metrics:** an alert is raised when a value is greater than its limit. The default limits are CPU 80%, memory 80% and disk 90%.
- **SSH logins:** the tool counts `Failed password` lines per IP address in the whole file. An alert is raised when an IP reaches 3 failed logins. Lines with `invalid user` are included. Successful logins (`Accepted password`) and unrelated lines are ignored.

The limits are defined in `alerts.py` (`THRESHOLDS` and `SSH_FAIL_LIMIT`).

## SSH log format

```
Oct 27 14:02:11 server sshd[1234]: Failed password for root from 203.0.113.5 port 52114 ssh2
Oct 27 14:02:15 server sshd[1234]: Failed password for invalid user admin from 203.0.113.5 port 52120 ssh2
Oct 27 14:05:01 server sshd[1240]: Accepted password for muhammed from 192.168.1.20 port 50022 ssh2
```

A sample file is included in `logs/sample_auth.log`. On Linux the real file is usually `/var/log/auth.log`.

## Running tests

```bash
python -m pytest
```

## Docker

Build the image:

```bash
docker build -t system-monitor-agent .
```

Run it in the background on a Linux host, with the JSON reports saved to a local folder and the real SSH log mounted read-only:

```bash
mkdir -p data
sudo docker run -d \
  --name system-monitor-agent \
  --restart unless-stopped \
  --group-add 4 \
  -v "$PWD/data:/data" \
  -v "$PWD:/host:ro" \
  -v /var/log/auth.log:/var/log/auth.log:ro \
  system-monitor-agent:latest
```

What the options do:

- `-v "$PWD/data:/data"` keeps the JSON reports on the host.
- `-v "$PWD:/host:ro"` gives the agent read-only access to the host file system, so it measures the host disk and not the container's own disk.
- `-v /var/log/auth.log:/var/log/auth.log:ro` lets the agent read the real SSH log.
- `--group-add 4` adds the `adm` group (Ubuntu) so the non-root user can read `auth.log`.
- `--restart unless-stopped` starts the container again after a reboot or a crash.

Watch the output and stop the container:

```bash
sudo docker logs system-monitor-agent
sudo docker stop system-monitor-agent
sudo docker rm system-monitor-agent
```

Notes:

- The container runs as a non-root user (`appuser`) and checks the system every 60 seconds.
- `PYTHONUNBUFFERED=1` is set so the output shows up in `docker logs` immediately.
- Timestamps inside the container use UTC.

## Deployment on AWS EC2

The agent was deployed and tested on an AWS EC2 instance (`t3.micro`, Ubuntu, region `eu-central-1`) and run in Docker as shown above.

- SSH access was limited to a single IP address in the security group.
- Docker was installed on the instance and the image was built there.
- The host's RAM and disk values were checked against the values the container reported.
- The container read the real `/var/log/auth.log` through the read-only mount.
- The container restarts automatically (`--restart unless-stopped`).

Example log output from the instance:

```
CPU: 1.0 %
RAM: 47.2 %
DISK: 40.8 %
All metrics are normal
```

The instance was terminated after the tests to avoid costs.

## Project structure

- `main.py`: command-line entry point, runs the checks, writes the report and the log
- `collector.py`: reads CPU, memory and disk usage
- `alerts.py`: thresholds and alert logic
- `auth_parser.py`: parses SSH failed logins and counts them per IP
- `logs/sample_auth.log`: sample SSH log
- `tests/`: automated tests (pytest)
- `.github/workflows/tests.yml`: runs the tests on every push
- `Dockerfile`: container image definition

## Limitations

- Thresholds are fixed in the code and cannot be changed from the command line
- Disk usage is read from `/host`, the host folder mounted into the container. Outside Docker, this path must exist
- Only password-based SSH log lines in the format shown above are recognized (no `Invalid user ... from ...` lines yet)
- SSH failures are counted over the whole file, not within a time window
- The log timestamp has no year, so it is not parsed
- The report file is overwritten on every run

## Roadmap

- Recognize `Invalid user` lines in `auth.log`
- Count failed logins within a time window
- Make the thresholds configurable from the command line

## Disclaimer

Use this tool only on systems and logs you own or are authorized to analyze.
