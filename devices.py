from config import MAC_ADDRESSES, NEXT_HOP_INTERFACE, is_router
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
            if is_router(device):
                for interface in device.interfaces.keys():
                    if device.interfaces[interface]["mac"] == mac_address:
                        return (device, interface)
            else:
                if MAC_ADDRESSES[device.name] == mac_address:
                    return (device, None)
        
        return (None, None)


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

    def receive(self, frame: bytes):
        self.data_link_layer.receive(frame)


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

        # Layers
        self.data_link_layer = DataLinkLayer(self)
        self.network_layer = NetworkLayer(self)

    def recieve(self, frame: bytes, interface: int):
        self.current_interface = interface
        self.data_link_layer.receive(frame, interface)

    def send(self, frame: bytes, interface: int):
        self.current_interface = interface
        self.data_link_layer.send(frame)

    def get_interface(self, interface: int):
        return self.interfaces[interface]

    def select_out_interface(self, next_hop: str):
        return NEXT_HOP_INTERFACE[next_hop]

    def get_ip(self, interface: int):
        return self.interfaces[interface]["ip"]

    def get_mac(self, interface: int):
        return self.interfaces[interface]["mac"]