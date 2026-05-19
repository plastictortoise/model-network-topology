IP_ADDRESSES = {
    "Host A": "10.0.1.10",
    "Host B": "10.0.2.20"
}

MAC_ADDRESSES = {
    "Host A": "AA:AA:AA:AA:AA:AA",
    "Host B": "BB:BB:BB:BB:BB:BB",
    "Router R1": "CC:CC:CC:CC:CC:CC",
    "Router R2": "DD:DD:DD:DD:DD:DD"
}

ARP_TABLE = {
    "10.0.1.10": "AA:AA:AA:AA:AA:AA",
    "10.0.2.20": "BB:BB:BB:BB:BB:BB",
    "10.0.1.1": "CC:CC:CC:CC:CC:CC",
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
        "10.0.1.10": "10.0.2.20"
    },
    "Router R1": {
        "10.0.1.1": "10.0.1.1",
        "10.0.2.20": "10.0.2.20"
    }
}

TOPOLOGY_LINKS = {
    ("Host A", None): ("Router R1", 1),
    ("Host B", None): ("Router R1", 2),
    ("Router R1", 1): ("Host A", None),
    ("Router R1", 2): ("Host B", None),
}