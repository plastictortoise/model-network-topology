# CITS3002 Group Project


| Student ID | Name                 |
| ---------- | -------------------- |
| 24494921   | Benjamin Passaportis |
| 24527669   | Tinashe Nemacha      |


## Overview

This project implements a simplified network topolgy simulator in python to demonstrate how data is transmitted between two hosts through a router using the Data Link, Network, and Transport layers. Key features include encapsulation, MAC and IP addressing, routing, frame forwarding, checksum verification, and reliable data transferral using the rdt2.2 alternating bit protocol. Data is segmented into 500 byte segments, encapsulated into IP-like packets and Ethernet-like frames, then forwarded across the network while outputting detailed logs at every layer to get an idea of end-to-end netowrk communication.

## Usage

```sh
python main.py <message_size>
```

Where `<message_size>` is the size of the segment payload in bytes.