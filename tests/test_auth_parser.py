from auth_parser import parse_failed_login, count_failed_by_ip

def test_parse_normal_failed_login():
    line = "Oct 27 14:02:11 server sshd[1234]: Failed password for root from 203.0.113.5 port 52114 ssh2"

    result = parse_failed_login(line)

    assert result == {"user": "root", "ip": "203.0.113.5"}



def test_parse_invalid_failed_login():
    line = "Oct 27 14:02:15 server sshd[1234]: Failed password for invalid user admin from 203.0.113.5 port 52120 ssh2"

    result = parse_failed_login(line)

    assert result == {"user": "admin", "ip": "203.0.113.5"}
    
    
def test_parse_success_login():
    line="Oct 27 14:05:01 server sshd[1240]: Accepted password for muhammed from 192.168.1.20 port 50022 ssh2"
    
    result=parse_failed_login(line)
    
    assert result is None
    
    
def test_parse_count_failed_by_ip():
    line=[
        {"user":"muhammed", "ip":"192.168.1.10"},
        {"user":"admin", "ip":"192.168.1.10"},
        {"user":"man", "ip":"192.168.2.100"},
    ]
    result=count_failed_by_ip(line)
    
    assert result =={"192.168.1.10":2,"192.168.2.100":1}