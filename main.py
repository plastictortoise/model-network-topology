from sys import argv
from devices import Host, Router, Topology
from config import IP_ADDRESSES, MAC_ADDRESSES, ROUTING_TABLE, ROUTER_INTERFACES, SEND_PORT, RECIEVE_PORT

if __name__ == "__main__":
    # Ensure that the program only runs with one argument
    if len(argv) != 2:
        print("Usage: python main.py <size>")
        exit(1)

    # Size of the message to send
    size = int(argv[1])

    # Create the topology
    topology = Topology()

    # Create the devices
    host_a = Host(
        name="Host A",
        ip=IP_ADDRESSES["Host A"],
        mac=MAC_ADDRESSES["Host A"],
        routing_table=ROUTING_TABLE["Host A"]
    ) 

    host_b = Host(
        name="Host B",
        ip=IP_ADDRESSES["Host B"],
        mac=MAC_ADDRESSES["Host B"],
        routing_table=ROUTING_TABLE["Host B"]
    )

    router = Router(
        name="Router R1",
        interfaces=ROUTER_INTERFACES,
        routing_table=ROUTING_TABLE["Router R1"]
    )

    # Add the devices to the topology
    topology.add_device(host_a)
    topology.add_device(host_b)
    topology.add_device(router)

    # Set the topology for each device
    for device in topology.devices:
        device.topology = topology

    # Send a message of correct size
    message = "A" * size
    host_a.transport_layer.send(message, SEND_PORT, RECIEVE_PORT, IP_ADDRESSES["Host B"])