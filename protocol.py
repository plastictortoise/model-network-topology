import struct
from config import ARP_TABLE, MAX_SEGMENT_PAYLOAD


def is_router(device):
    return hasattr(device, "interfaces")


"""
Frame: defines the structure of the frames for use in the data link layer
"""
class Frame:
    def __init__(self, header: bytes):
        self.destination_mac = header[0:6]
        self.source_mac = header[6:12]
        self.type = header[12:14]
        self.payload = header[14:]


"""
Packet: defines the structure of the packets for use in the network layer
"""
class Packet:
    def __init__(self, header: bytes):
        self.source_ip = header[0:4]
        self.destination_ip = header[4:8]
        self.ttl = header[8]
        self.protocol = header[9]
        self.total_length = header[10:12]
        self.payload = header[12:]


"""
Segment: defines the structure of the segments for use in the transport layer
"""
class Segment:
    def __init__(self, header: bytes):
        self.source_port = header[0:2]
        self.destination_port = header[2:4]
        self.length = header[4:6]
        self.checksum = header[6:8]
        self.type = header[8]
        self.sequence_number = header[9]
        self.payload = header[10:]


"""
Layer: defines the base class for all layers
"""
class Layer:
    def __init__(self, layer: int):
        self.layer = layer

    def log(self, message: str):
        self.device.log(f"Layer {self.layer}: {message}")


"""
DataLinkLayer: defines the data link layer. Based on the Layer class.
"""
class DataLinkLayer(Layer):
    def __init__(self, device: object):
        super().__init__(2) # Layer 2 for logging
        self.device = device

    def encapsulate(self, packet: bytes, destination_mac: str):
        destination_mac = bytes.fromhex(destination_mac.replace(":", ""))
        mac = bytes.fromhex(self.device.mac.replace(":", ""))
        frame = struct.pack("!6s6sH", destination_mac, mac, 0x0800) + packet
        return frame

    def decapsulate(self, frame: Frame):
        return frame.payload

    def send(self, segment: bytes, destination_mac: str, interface: (int|None) = None):
        self.log("Packet received from Network Layer")
        frame = self.encapsulate(segment, destination_mac)
        self.device.topology.get_device(destination_mac).data_link_layer.receive(frame, interface)

    def receive(self, frame_bytes: bytes, interface: (int|None) = None):
        frame = Frame(frame_bytes)
        packet_bytes = self.decapsulate(frame)

        if interface is not None:
            packet_bytes = self.device.get_interface(interface).network_layer.receive(packet_bytes)
        else:
            packet_bytes = self.device.network_layer.receive(packet_bytes)


"""
NetworkLayer: defines the network layer. Based on the Layer class.
"""
class NetworkLayer(Layer):
    def __init__(self, device: object):
        super().__init__(3) # Layer 3 for logging
        self.device = device

    def encapsulate(self, segment: bytes, ttl: int, destination_ip: str):
        ip = bytes(int(i) for i in self.device.ip.split("."))
        destination_ip = bytes(int(i) for i in destination_ip.split("."))
        packet = struct.pack('!4s4sBBH', ip, destination_ip, ttl, 17, 12 + len(segment)) + segment
        return packet

    def decapsulate(self, packet: Packet):
        return packet.payload

    def send(self, segment: bytes, destination_ip: str):
        ttl = 100
        self.log(f"Segment received from Transport Layer: SRC_IP={self.device.ip}, DST_IP={destination_ip}, TTL={ttl}")
        self.log(f"Destination IP read: {destination_ip}")

        next_hop = self.device.routing_table[destination_ip]
        self.log("Routing table lookup performed")
        self.log(f"Next-hop IP determined: {next_hop}")

        out_interface = None
        if is_router(self.device):
            out_interface = self.device.select_out_interface(next_hop)
            self.log(f"Outgoing interface selected (Interface {out_interface})")
        else:
            self.log("Outgoing interface selected")


        packet = self.encapsulate(segment, ttl, destination_ip)
        destination_mac = ARP_TABLE[destination_ip]
        self.log(f"Packet forwarded to Data Link Layer")
        self.device.data_link_layer.send(packet, destination_mac)

    def receive(self, packet_bytes: bytes):
        packet = Packet(packet_bytes)
        segment_bytes = self.decapsulate(packet)
        self.device.transport_layer.receive(segment_bytes)


"""
TransportLayer: defines the transport layer. Based on the Layer class.
"""
class TransportLayer(Layer):
    def __init__(self, device: object):
        super().__init__(4) # Layer 4 for logging
        self.device = device
        self.awaiting_ack = False

    def send(self, data: str, destination_port: int, destination_ip: str):
        self.log(f"Data received from Application Layer. Data size={len(data)}")
        chunks = [data[i:i+MAX_SEGMENT_PAYLOAD] for i in range(0, len(data), MAX_SEGMENT_PAYLOAD)]
        for chunk in chunks:
            segment = self.encapsulate(chunk, destination_port)
            self.device.network_layer.send(segment, destination_ip)

            self.awaiting_ack = True

    def receive(self, segment_bytes: bytes):
        segment = Segment(segment_bytes)
        self.log("Segment received from Network Layer")
        self.log(f"Payload: {self.decapsulate(segment)}")

        if self.verify_checksum(segment.payload, int(segment.checksum.hex(), 16)):
            self.log("Checksum verified")
        else:
            self.log("Checksum verification failed")
            return

    def checksum(self, data: bytes):
        checksum = sum(data) % 256
        self.log("Checksum computed")
        return checksum

    def verify_checksum(self, data: bytes, checksum: int):
        return sum(data) % 256 == checksum

    def encapsulate(self, message: str, destination_port: int, sequence_number: int = 0):
        segment = struct.pack('!HHHHBB', self.device.port, destination_port, 10 + len(message.encode()), self.checksum(message.encode()), 0, sequence_number) + message.encode()
        self.log(f"Segment created by adding transport layer header (DATA, seq={sequence_number}) (encapsulation)")
        return segment
    
    def decapsulate(self, segment: object):
        return segment.payload.decode()
