from config import MAC_ADDRESSES, NEXT_HOP_INTERFACE, is_router
from protocol import DataLinkLayer, NetworkLayer, TransportLayer

"""
Topology: defines the topology of the network and enables the transmission of frames between devices.
"""
class Topology:
    def __init__(self):
        self.devices = []

    """
    add_device: Adds a device to the topology
    """
    def add_device(self, device: object):
        self.devices.append(device)

    """
    get_device: Returns the device and interface for a given MAC address
    """
    def get_device(self, mac_address: str):
        for device in self.devices:
            if is_router(device):
                # Check all interfaces of the router to find the matching MAC address
                for interface in device.interfaces.keys():
                    if device.interfaces[interface]["mac"] == mac_address:
                        return (device, interface)
            else:
                # Find the device with the matching MAC address
                if MAC_ADDRESSES[device.name] == mac_address:
                    return (device, None)
        
        return (None, None)


"""
Device: defines the base class for all devices
"""
class Device:
    def __init__(self, name: str):
        self.name = name
        self.topology = None # Stores local topology for topolgy-independent usage

    """
    log: Helper function to log device messages
    """
    def log(self, message: str):
        print(f"{self.name}: {message}")


"""
Host: defines the host device. Contains all the layers for the host. Based on the Device class.
"""
class Host(Device):
    def __init__(self, name: str, ip: str, mac: str, routing_table: dict):
        # Device information
        super().__init__(name)
        self.ip = ip
        self.mac = mac
        self.routing_table = routing_table

        # Layers
        self.data_link_layer = DataLinkLayer(self)
        self.network_layer = NetworkLayer(self)
        self.transport_layer = TransportLayer(self)


"""
Router: defines the router device with two interfaces. Contains all the layers for the router. Based on the Device class.
"""
class Router(Device):
    def __init__(self, name: str, interfaces: list, routing_table: dict):
        # Device information
        super().__init__(name)
        self.interfaces = interfaces
        self.routing_table = routing_table
        self.current_interface = None
        self.next_hop_interface = NEXT_HOP_INTERFACE

        # Layers
        self.data_link_layer = DataLinkLayer(self)
        self.network_layer = NetworkLayer(self)

    """
    receive: Receives a frame from a specific interface using the data link layer
    """
    def recieve(self, frame: bytes, interface: int):
        self.current_interface = interface
        self.data_link_layer.receive(frame, interface)

    """
    send: Sends a frame on a given interface using the data link layer
    """
    def send(self, frame: bytes, interface: int):
        self.current_interface = interface
        self.data_link_layer.send(frame)

    """
    get_interface: Returns the interface information for a given interface
    """
    def get_interface(self, interface: int):
        return self.interfaces[interface]

    """
    select_out_interface: Selects the outgoing interface for a given next-hop IP
    """
    def select_out_interface(self, next_hop: str):
        return self.next_hop_interface[next_hop]

    """
    get_ip: Returns the IP address for a given interface
    """
    def get_ip(self, interface: int):
        return self.interfaces[interface]["ip"]

    """
    get_mac: Returns the MAC address for a given interface
    """
    def get_mac(self, interface: int):
        return self.interfaces[interface]["mac"]