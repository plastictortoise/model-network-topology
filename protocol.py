import struct
from config import ARP_TABLE, MAX_SEGMENT_PAYLOAD, DATA_SEGMENT, ACK_SEGMENT, is_router


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

    """
    log: Helper function to log layer messages
    """
    def log(self, message: str):
        self.device.log(f"Layer {self.layer}: {message}")


"""
DataLinkLayer: defines the data link layer. Based on the Layer class.
"""
class DataLinkLayer(Layer):
    """
    init: General structure of the data link layer
    """
    def __init__(self, device: object):
        super().__init__(2) # Layer 2 for logging
        self.device = device # Device that the layer is attached to
        self.arp_table = ARP_TABLE # Local ARP table for the device

    """
    encapsulate: Encapsulates a packet into a frame
    """
    def encapsulate(self, packet: bytes, destination_mac: str):
        # Get the MAC address of the device
        if is_router(self.device):
            device_mac = self.device.get_mac(self.device.current_interface)
        else:
            device_mac = self.device.mac
        
        # Create the frame
        destination_mac = bytes.fromhex(destination_mac.replace(":", ""))
        mac = bytes.fromhex(device_mac.replace(":", ""))
        frame = struct.pack("!6s6sH", destination_mac, mac, 0x0800) + packet
        return frame

    """
    decapsulate: Fetches the payload from a frame
    """
    def decapsulate(self, frame: Frame):
        return frame.payload

    """
    send: Receives a packet from the network layer and sends it to the data link layer
    """
    def send(self, packet: bytes, destination_ip: str, interface: (int|None) = None):
        # Get device MAC address
        if is_router(self.device):
            device_mac = self.device.get_mac(self.device.current_interface)
        else:
            device_mac = self.device.mac

        self.log("Packet received from Network Layer")

        # Find the destination MAC address
        destination_mac = self.arp_table[destination_ip]
        self.log(f"Destination MAC lookup for next-hop IP ({destination_ip}) -> {destination_mac}")

        # Encapsulate the packet into a frame
        frame = self.encapsulate(packet, destination_mac)
        self.log(f"Frame created: SRC_MAC={device_mac}, DST_MAC={destination_mac}")
        
        # Get the device and interface for the destination MAC address
        device, interface = self.device.topology.get_device(destination_mac)
        
        if is_router(self.device):
            self.log(f"Frame forwarded on Interface {self.device.current_interface}")
        else:
            self.log(f"Frame sent")

        # Send the frame to the data link layer
        device.data_link_layer.receive(frame, interface)

    """
    receive: Receives a frame from the data link layer and sends it to the network layer
    """
    def receive(self, frame_bytes: bytes, interface: (int|None) = None):
        # Parse and decapsulate the frame
        frame = Frame(frame_bytes)
        packet_bytes = self.decapsulate(frame)

        # For logging purposes
        source_mac = str(frame.source_mac.hex()).upper()
        source_mac = ":".join(source_mac[i:i+2] for i in range(0, len(source_mac), 2))

        # Update the current interface
        if interface is not None:
            self.log(f"Frame received on Interface {interface}")
            self.log(f"Source MAC learned: {source_mac} on Interface {interface}")
            self.device.current_interface = interface
        else:
            self.log(f"Frame received")
            self.log(f"Source MAC learned: {source_mac}")
        
        # Send the packet to the network layer
        self.log(f"Packet delivered to Network Layer")
        self.device.network_layer.receive(packet_bytes)


"""
NetworkLayer: defines the network layer. Based on the Layer class.
"""
class NetworkLayer(Layer):
    """
    init: General structure of the network layer
    """
    def __init__(self, device: object):
        super().__init__(3) # Layer 3 for logging
        self.device = device

    """
    encapsulate: Encapsulates a segment into a packet
    """
    def encapsulate(self, segment: bytes, ttl: int, source_ip: str, destination_ip: str):
        # Pack the segment into a packet with the appropriate header information
        source_ip = bytes(int(i) for i in source_ip.split("."))
        destination_ip = bytes(int(i) for i in destination_ip.split("."))
        packet = struct.pack('!4s4sBBH', source_ip, destination_ip, ttl, 17, 12 + len(segment)) + segment
        return packet

    """
    decapsulate: Fetches the payload from a packet
    """
    def decapsulate(self, packet: Packet):
        return packet.payload

    """
    send: Receives a segment from the transport layer and sends it to the data link layer
    """
    def send(self, segment: bytes, destination_ip: str):
        ttl = 100
        # Receive the segment from the transport layer
        self.log(f"Segment received from Transport Layer: SRC_IP={self.device.ip}, DST_IP={destination_ip}, TTL={ttl}")
        self.log(f"Destination IP read: {destination_ip}")

        # Determine the next-hop IP from the routing table
        next_hop = self.device.routing_table[destination_ip]
        self.log("Routing table lookup performed")
        self.log(f"Next-hop IP determined: {next_hop}")

        # Select the outgoing interface
        out_interface = None
        if is_router(self.device):
            out_interface = self.device.select_out_interface(next_hop)
            self.log(f"Outgoing interface selected (Interface {out_interface})")
            self.device.current_interface = out_interface
        else:
            self.log("Outgoing interface selected")

        # Encapsulate the segment into a packet
        packet = self.encapsulate(segment, ttl, self.device.ip, destination_ip)
        self.log(f"Packet forwarded to Data Link Layer")

        # Send the packet to the data link layer
        self.device.data_link_layer.send(packet, next_hop)


    """
    receive: Receives a packet from the data link layer and sends it to the transport layer
    """
    def receive(self, packet_bytes: bytes):
        # Parse the packet
        packet = Packet(packet_bytes)
        # Recieve the packet from the data link layer
        destination_ip = ".".join(str(b) for b in packet.destination_ip)
        source_ip = ".".join(str(b) for b in packet.source_ip)
        destination_ip = ".".join(str(b) for b in packet.destination_ip)
        self.log(f"Packet received from Data Link Layer: SRC_IP={source_ip}, DST_IP={destination_ip}, TTL={packet.ttl}")
        self.log(f"Destination IP read: {destination_ip}")

        if is_router(self.device):
            ttl = packet.ttl

            # Discard the packet if TTL = 0
            if ttl <= 0:
                self.log("TTL expired")
                return

            # Decrement the TTL
            ttl -= 1
            self.log(f"TTL decremented: {ttl + 1} -> {ttl}")
            
            # Determine the next-hop IP from the routing table
            next_hop = self.device.routing_table[destination_ip]
            self.log("Routing table lookup performed")
            self.log(f"Next-hop IP determined: {next_hop}")

            # Select the outgoing interface
            out_interface = self.device.select_out_interface(next_hop)
            self.log(f"Outgoing interface selected (Interface {out_interface})")
            self.device.current_interface = out_interface

            # Encapsulate the packet into a new packet and send to the data link layer
            packet = self.encapsulate(packet.payload, ttl, source_ip, destination_ip)
            self.log("Packet forwarded to Data Link Layer")
            self.device.data_link_layer.send(packet, next_hop)
        else:
            self.log("Packet identified as local delivery")

            # Decapsulate the packet into a segment and send to the transport layer
            segment_bytes = self.decapsulate(packet)
            self.log("Segment delivered to Transport Layer")
            self.device.transport_layer.receive(segment_bytes, source_ip)


"""
TransportLayer: defines the transport layer. Based on the Layer class.
"""
class TransportLayer(Layer):
    """
    init: General structure of the transport layer
    """
    def __init__(self, device: object):
        super().__init__(4) # Layer 4 for logging
        self.device = device
        self.sequence_number = 0
        self.chunks = [] # Used for resending
        self.current_chunk = 0 # Used for resending
        self.awaiting_ack = False

    """
    send: Receives data from the application layer and sends it to the network layer
    """
    def send(self, data: str, source_port: int, destination_port: int, destination_ip: str):
        # Segment the data into chunks
        self.log(f"Data received from Application Layer. Data size={len(data)}")
        self.chunks = [data[i:i+MAX_SEGMENT_PAYLOAD] for i in range(0, len(data), MAX_SEGMENT_PAYLOAD)]

        # Encapsulate each chunk and send it to the network layer
        for chunk in self.chunks:
            segment = self.encapsulate(chunk, source_port, destination_port)
            self.log(f"Segment sent to Network Layer")
            self.device.network_layer.send(segment, destination_ip)

            self.awaiting_ack = True # Block until an ACK is recieved

    """
    receive: Receives a data segment from the network layer and sends it to the application layer.
    """
    def receive(self, segment_bytes: bytes, source_ip: str):
        # Parse the segment
        segment = Segment(segment_bytes)
        source_port = int(segment.source_port.hex(), 16)
        self.log("Segment received from Network Layer")

        # Verify the checksum
        if self.verify_checksum(segment.payload, int(segment.checksum.hex(), 16)):
            self.log("Checksum verified")
        else:
            self.log("Checksum verification failed. Discarding segment.")
            return # Discard the segment
        
        if segment.type == DATA_SEGMENT:
            # Verify the sequence number and request resend if incorrect
            if self.sequence_number != segment.sequence_number:
                self.log(f"Sequence number mismatch. Expected {self.sequence_number}, received {segment.sequence_number}. Resending last ACK.")
                ack_segment = self.encapsulate("", source_port, int(segment.source_port.hex(), 16))
                self.device.network_layer.send(ack_segment, source_ip)

            # Send an ACK to the network layer
            self.log(f"DATA segment delivered to Application Layer. Data size={len(segment.payload.decode())}")
            ack_segment = self.encapsulate("", source_port, int(segment.source_port.hex(), 16))
            self.log(f"Segment sent to Network Layer")
            self.device.network_layer.send(ack_segment, source_ip)

            # Update the sequence number
            self.sequence_number = 0 if segment.sequence_number == 1 else 1
        else:
            # Verify the sequence number and resend last chunk if incorrect
            if self.sequence_number != segment.sequence_number:
                self.log(f"Sequence number mismatch. Expected {self.sequence_number}, received {segment.sequence_number}. Resending last chunk.")
                self.device.transport_layer.send(self.chunks[self.current_chunk], source_port, int(segment.source_port.hex(), 16), source_ip)

            # Send an ACK to the network layer
            self.log(f"ACK recieved. seq={segment.sequence_number}")
            self.awaiting_ack = False # Unblock the sender
            self.sequence_number = 0 if segment.sequence_number == 1 else 1 # Update the sequence number
            self.current_chunk += 1 # Update the current chunk


    """
    checksum: Calculates the checksum of a message
    """
    def checksum(self, data: bytes):
        checksum = sum(data) % 256
        self.log("Checksum computed")
        return checksum
    
    """
    verify_checksum: Verifies the checksum of a message
    """
    def verify_checksum(self, data: bytes, checksum: int):
        return sum(data) % 256 == checksum

    """
    encapsulate: Encapsulates a message into a segment
    """
    def encapsulate(self, message: str, source_port: int, destination_port: int):
        # Determine the type of segment
        segment_type = DATA_SEGMENT if message != "" else ACK_SEGMENT

        if segment_type == DATA_SEGMENT:
            # Create a data segment with the appropriate header
            segment = struct.pack('!HHHHBB', source_port, destination_port, 10 + len(message.encode()), self.checksum(message.encode()), segment_type, self.sequence_number) + message.encode()
            self.log(f"Segment created by adding transport layer header (DATA, seq={self.sequence_number}) (encapsulation)")
        else:
            # Create an ACK segment
            segment = struct.pack('!HHHHBB', source_port, destination_port, 10, 0, segment_type, self.sequence_number)
            self.log(f"Segment created by adding transport layer header (ACK, seq={self.sequence_number})")

        return segment
    
    """
    decapsulate: Fetches the payload from a segment
    """
    def decapsulate(self, segment: object):
        return segment.payload.decode()
