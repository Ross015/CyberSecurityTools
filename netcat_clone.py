import argparse
import asyncio
import ipaddress
import socket
import subprocess
import sys


class Factory():
    def build_client(self, settings):
        if(settings["udp"]):
            print("[+] Building UDP Client")
            # if the ip fails to detect version 6 then use 4.
            try:
                ipaddress.IPv6Address(settings["remote_host"])
                family=settings["family"]
            except:
                family = socket.AF_INET
                settings["host"] = "0.0.0.0"
            
            coroutine = settings["loop"].create_datagram_endpoint(
                lambda: UDP(settings),
                local_addr=(settings["host"], settings["port"]),
                remote_addr=(settings["remote_host"], settings["remote_port"]),
                family=family
            )
            return coroutine
        
        else:
            print("[+] Building TCP Client")
            # if the ip fails to detect version 6 then use 4.
            try:
                ipaddress.IPv6Address(settings["remote_host"])
                family=settings["family"]
            except:
                family = socket.AF_INET
                settings["host"] = "0.0.0.0"
                
            coroutine = settings["loop"].create_connection(
                lambda: TCP(settings),
                host=settings["remote_host"],
                port=settings["remote_port"],
                family=family
            )
            return coroutine
    
    def build_server(self, settings):   
        if(settings["udp"]):
            print("[+] Building UDP Server...")
            coroutine = settings["loop"].create_datagram_endpoint(
                lambda: UDP(settings),
                local_addr=(settings["host"], settings["port"]),
                family=settings["family"]
            )
            return coroutine
        
        else:
            print("[+] Building TCP Server...")
            # For some reason using sock instead of host, port in create_server()
            # allows me to dual stack
            sock = socket.socket(settings["family"], socket.SOCK_STREAM)
            sock.bind((settings["host"], settings["port"]))
            coroutine = settings["loop"].create_server(
                lambda: TCP(settings),
                sock=sock,
                family=settings["family"]
            )
            return coroutine
        
    
class TCP():
    def __init__(self, settings):
        self.loop = settings["loop"]
        self.loop.add_reader(sys.stdin, self.data_write)
        
    def connection_made(self, transport):
        self.transport = transport
    
    def data_received(self, data):
        print(data.decode().strip("\n"))
        
    def data_write(self):
        data = sys.stdin.readline()
        self.transport.write(data.encode())
        
        
class UDP():
    def __init__(self, settings):
        self.listen = settings["listen"]
        self.loop = settings["loop"]
        self.loop.add_reader(sys.stdin, self.datagram_write)
        
    def connection_made(self, transport):
        self.transport = transport
        
    def datagram_received(self, data, addr):
        self.addr = addr
        print(data.decode().strip("\n"))
        
    def datagram_write(self):
        data = sys.stdin.readline()
        try:
            if(self.listen):
                # if server, you wait for data received.
                self.transport.sendto(data.encode(), self.addr)
            else:
                self.transport.sendto(data.encode())
        except AttributeError:
            pass

           
class ValidPorts(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            if(not 0 < values <= 65536):
                raise argparse.ArgumentError(self, "Choose any port 1 through 65536") 
            setattr(namespace, self.dest, values)
        except TypeError:
            pass
        
        
def main():
    parser = argparse.ArgumentParser()
    # Server options
    parser.add_argument("-l", "--listen", action="store_true")
    parser.add_argument("-s", "--host", default="::0")
    parser.add_argument("-p", "--port", type=int, action=ValidPorts, default="45000")
    # Dual Options
    parser.add_argument("-u", "--udp", action="store_true")
    # Client options
    parser.add_argument("remote_host", nargs="?")
    parser.add_argument("remote_port", nargs="?", type=int, action=ValidPorts)
    args = parser.parse_args()
    
    # Server/Client Settings
    factory = Factory()
    loop = asyncio.get_event_loop()
        
    settings = {
        "port":args.port, 
        "host":args.host, 
        "udp":args.udp,
        "loop":loop,
        "family":socket.AF_INET6,
        "remote_host":args.remote_host,
        "remote_port":args.remote_port,
        "listen":args.listen
    }
    
    if(args.listen and not args.remote_host and not args.remote_port):
        coroutine = factory.build_server(settings)
    elif(not args.listen):
        coroutine = factory.build_client(settings)
    else:
        print("Invalid arguments")
        sys.exit()
    
    loop.run_until_complete(coroutine)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\n")
    finally:
        loop.close()
            
    
if(__name__ == "__main__"):
    main()
