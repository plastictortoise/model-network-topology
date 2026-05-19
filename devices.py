from config import MAC_ADDRESSES, TOPOLOGY_LINKS
from protocol import DataLinkLayer, NetworkLayer, TransportLayer

"""
Topology: defines the topology of the network and enables the transmission of frames between devices.
"""

class Topology:
    def __init__(self):
        self.devices = []

    def add_device(self, device: object):
        self.devices.append(device)

    def get_device(self, mac_address: str):
        for device in self.devices:
            if MAC_ADDRESSES[device.name] == mac_address:
                return device
        
        return None

    def transmit(self, frame: bytes, sender: str, interface: (int|None) = None):
        for link in TOPOLOGY_LINKS:
            if link[0] == sender:
                if link[1] == interface:
                    self.devices[link[2]].data_link_layer.receive(frame)
                    return

"""
Device: defines the base class for all devices
"""
class Device:
    def __init__(self, name: str):
        self.name = name
        self.topology = None

    def log(self, message: str):
        print(f"{self.name}: {message}")


"""
Host: defines the host device. Contains all the layers for the host. Based on the Device class.
"""
class Host(Device):
    def __init__(self, name: str, ip: str, mac: str, routing_table: dict, port: int):
        # Device information
        super().__init__(name)
        self.ip = ip
        self.mac = mac
        self.routing_table = routing_table
        self.port = port

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

        # Layers
        self.data_link_layer = DataLinkLayer(self)
        self.network_layer = NetworkLayer(self)
        self.transport_layer = TransportLayer(self)
