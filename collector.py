import psutil
from datetime import datetime


def get_cpu_percent():
    cpu_usage=psutil.cpu_percent(interval=1)
    return cpu_usage

def get_memory_percent():
    ram=psutil.virtual_memory()
    ram_usage=ram.percent
    return ram_usage

def get_disk_percent():
    disk=psutil.disk_usage("/")
    disk_usage=disk.percent
    return disk_usage

def collect_metrics():
    return{
        "timestamp":str(datetime.now()),
        "cpu":get_cpu_percent(),
        "memory":get_memory_percent(),
        "disk":get_disk_percent()
    }
    

if __name__=="__main__":
    print(collect_metrics())