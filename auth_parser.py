import re


def parse_failed_login(line):
    pattern = r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\S+)"
    match = re.search(pattern, line)
    if match is None:
        return None
    return {"user": match.group("user"), "ip": match.group("ip")}


def parse_auth_file(path):
    results = []

    with open(path) as f:
        for line in f:
            res = parse_failed_login(line)
            if res is not None:
                results.append(res)
        return results


def count_failed_by_ip(failed_logins):
    counts = {}
    for record in failed_logins:
        ip = record["ip"]
        counts[ip] = counts.get(ip, 0) + 1
    return counts


if __name__ == "__main__":
    print(
        parse_failed_login(
            "Oct 27 14:02:11 server sshd[1234]: Failed password for root from 203.0.113.5 port 52114 ssh2"
        )
    )
    print(
        parse_failed_login(
            "Oct 27 14:02:15 server sshd[1234]: Failed password for invalid user admin from 203.0.113.5 port 52120 ssh2"
        )
    )
    print(
        parse_failed_login(
            "Oct 27 14:05:01 server sshd[1240]: Accepted password for muhammed from 192.168.1.20 port 50022 ssh2"
        )
    )
    print(len(parse_auth_file("logs/sample_auth.log")))
    print(count_failed_by_ip(parse_auth_file("logs/sample_auth.log")))
