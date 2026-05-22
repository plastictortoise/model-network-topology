"""
Config: a helper function that checks if a device is a router or a host
"""
def is_router(device):
    return hasattr(device, "interfaces")

# IP addresses for the hosts
IP_ADDRESSES = {
    "Host A": "10.0.1.10",
    "Host B": "10.0.2.20"
}

# MAC addresses for the hosts
MAC_ADDRESSES = {
    "Host A": "AA:AA:AA:AA:AA:AA",
    "Host B": "DD:DD:DD:DD:DD:DD"
}

# Interfaces for the router
ROUTER_INTERFACES = {
    1: {"ip": "10.0.1.1", "mac": "BB:BB:BB:BB:BB:BB"},
    2: {"ip": "10.0.2.1", "mac": "CC:CC:CC:CC:CC:CC"},
}

# Mapping of IP addresses to MAC addresses
ARP_TABLE = {
    "10.0.1.10": "AA:AA:AA:AA:AA:AA",
    "10.0.1.1": "BB:BB:BB:BB:BB:BB",
    "10.0.2.1": "CC:CC:CC:CC:CC:CC",
    "10.0.2.20": "DD:DD:DD:DD:DD:DD"
}

# Ports for the transport layer
# Note: these ports are arbritary as there are no applications running on the application layer
SEND_PORT = 80
RECIEVE_PORT = 40

# Aliases for segment types
DATA_SEGMENT = 0
ACK_SEGMENT = 1

# Routing table to determine next-hop IP depending on destination
ROUTING_TABLE = {
    "Host A": {
        "10.0.1.10": "10.0.1.10",
        "10.0.2.20": "10.0.1.1"
    },
    "Host B": {
        "10.0.2.20": "10.0.2.20",
        "10.0.1.10": "10.0.2.1"
    },
    "Router R1": {
        "10.0.1.10": "10.0.1.10",
        "10.0.1.1": "10.0.1.1",
        "10.0.2.1": "10.0.2.1",
        "10.0.2.20": "10.0.2.20"
    }
}

# Mapping of IP addresses to interfaces
NEXT_HOP_INTERFACE = {
    "10.0.1.10": 1,
    "10.0.2.20": 2,
    "10.0.1.1": 1,
    "10.0.2.1": 2
}

# Maximum payload size for a segment
MAX_SEGMENT_PAYLOAD = 500