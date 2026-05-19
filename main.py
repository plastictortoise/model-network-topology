from sys import argv
from devices import Host, Router, Topology
from config import IP_ADDRESSES, MAC_ADDRESSES, ROUTING_TABLE

if __name__ == "__main__":
    # Ensure that the program only runs with one argument
    if len(argv) != 2:
        print("Usage: python main.py <size>")
        exit(1)

    size = int(argv[1])

    topology = Topology()

    host_a = Host(
        name="Host A",
        ip=IP_ADDRESSES["Host A"],
        mac=MAC_ADDRESSES["Host A"],
        routing_table=ROUTING_TABLE["Host A"],
        port=80
    ) 

    host_b = Host(
        name="Host B",
        ip=IP_ADDRESSES["Host B"],
        mac=MAC_ADDRESSES["Host B"],
        routing_table=ROUTING_TABLE["Host B"],
        port=80
    )

    router = Router(
        name="Router R1",
        interfaces=[1, 2],
        routing_table=ROUTING_TABLE["Router R1"]
    )

    topology.add_device(host_a)
    topology.add_device(host_b)
    topology.add_device(router)

    for device in topology.devices:
        device.topology = topology

    message = "A" * size
    host_a.transport_layer.send(message, 80, IP_ADDRESSES["Host B"])