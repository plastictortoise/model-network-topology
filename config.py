def is_router(device):
    return hasattr(device, "interfaces")

IP_ADDRESSES = {
    "Host A": "10.0.1.10",
    "Host B": "10.0.2.20"
}

ROUTER_INTERFACES = {
    1: {"ip": "10.0.1.1", "mac": "BB:BB:BB:BB:BB:BB"},
    2: {"ip": "10.0.2.1", "mac": "CC:CC:CC:CC:CC:CC"},
}

MAC_ADDRESSES = {
    "Host A": "AA:AA:AA:AA:AA:AA",
    "Host B": "DD:DD:DD:DD:DD:DD"
}

ARP_TABLE = {
    "10.0.1.10": "AA:AA:AA:AA:AA:AA",
    "10.0.1.1": "BB:BB:BB:BB:BB:BB",
    "10.0.2.1": "CC:CC:CC:CC:CC:CC",
    "10.0.2.20": "DD:DD:DD:DD:DD:DD"
}

PORTS = {
    "Host A": 80,
    "Host B": 80,
    "Router R1": 80,
    "Router R2": 80
}

ROUTING_TABLE = {
    "Host A": {
        "10.0.1.1": "10.0.1.1",
        "10.0.2.20": "10.0.1.1"
    },
    "Host B": {
        "10.0.2.20": "10.0.2.20",
        "10.0.1.10": "10.0.2.1"
    },
    "Router R1": {
        "10.0.1.1": "10.0.1.1",
        "10.0.2.20": "10.0.2.20"
    }
}

NEXT_HOP_INTERFACE = {
    "10.0.1.10": 1,
    "10.0.2.20": 2,
    "10.0.1.1": 1,
    "10.0.2.1": 2
}

MAX_SEGMENT_PAYLOAD = 500
DATA_SEGMENT = 0
ACK_SEGMENT = 1