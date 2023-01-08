from socket import *
import socket as SocketLib
import threading

# Initializing Cashed WebSites as Empty List and Reading BlackListedWebsites
CashedWebsites = []
with open("blacklist.txt") as file:
    BlackListedWebSites = file.readlines()

# Setting up Server Socket with Port 10000
ServerSocket = socket(AF_INET, SOCK_STREAM)
ServerAddress = ('localhost', 10000)
ServerSocket.bind(ServerAddress)
ServerSocket.listen(1)


# Simple Console Coloring Using Anssi Code
class Colors:
    """ ANSI color codes """
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    LIGHT_GREEN = "\033[1;32m"
    LIGHT_RED = "\033[1;31m"
    BOLD = "\033[1m"
    END = "\033[0m"


# Function to Handle Connections
def handleConnection(ServerConnection, ClientAddress):
    try:
        # Timeout of 7 seconds so no Blocking occurs
        ServerConnection.settimeout(7)

        # Receive Data from Server Connection into a Huge Buffer
        print(f'Connection Initiated With: {ClientAddress[0]} at Port {ClientAddress[1]}')
        data = ServerConnection.recv(20000)
        CashedFlag = False
        FilteredData = data.decode('utf-8').split()[1].partition("/")[2]
        print(Colors.BLUE+f'Received HTTP Request for Website {FilteredData} from {ClientAddress[0]} at Port {ClientAddress[1]}')

        # Check if FilteredData is a Blocked URL on The Proxy Server
        for Website in BlackListedWebSites:
            if Website == FilteredData:
                print(Colors.RED+f"{FilteredData} is a Blacklisted Url on The Proxy Server")
                print(Colors.LIGHT_RED+'Sending Err Page to client'+Colors.END)

                # Return Blocked Html Page to client
                with open("Blocked.html") as file:
                    ServerConnection.send(bytes("HTTP/1.0 200 OK\r\n", 'utf-8'))
                    ServerConnection.send(bytes("Content-Type:text/html\r\n", 'utf-8'))
                    ServerConnection.send(bytes('\n', 'utf-8'))
                    ServerConnection.send(bytes(file.read(), 'utf-8'))
                return

        # Check if FilteredData is a Cashed Website on The Proxy Server
        for Website in CashedWebsites:
            if Website[0] == FilteredData:
                print(Colors.GREEN+f"Found Cashed Copy of {FilteredData} on Proxy Server")
                print(Colors.GREEN+'Sending File Content to client')

                # Return Cashed Website
                ServerConnection.sendall(Website[1])
                CashedFlag = True

        # Redirects to Main Server if not Cashed in Proxy Server
        if not CashedFlag:
            DataSocket = socket(AF_INET, SOCK_STREAM)
            Host = ""
            FilePath = "/"
            if len(FilteredData.split("/", 1)) > 1:
                Host = FilteredData.split("/", 1)[0]
                FilePath = FilteredData.split("/", 1)[1]
            else:
                Host = FilteredData.split("/", 1)[0]
            DataAddress = (Host, 80)
            try:
                print(Colors.RED+f"No Cashed Copy of {FilteredData} on Proxy Server")
                print(Colors.GREEN + "Redirecting to Main Server")
                DataSocket.connect(DataAddress)
                DataSocket.send(bytes(f"GET {FilePath} HTTP/1.1\r\nHost:{Host}\r\n\r\n", 'utf-8'))
                SiteData = DataSocket.recv(20000)
                ServerConnection.send(SiteData)
                CashedWebsites.append((FilteredData, SiteData))
            except SocketLib.error:
                # Returns 404 Page if Page Doesn't Exist
                print(Colors.RED+"Site not found Sending 404 Page To Client")
                with open("404.html") as file:
                    ServerConnection.send(bytes("HTTP/1.0 200 OK\r\n", 'utf-8'))
                    ServerConnection.send(bytes("Content-Type:text/html\r\n", 'utf-8'))
                    ServerConnection.send(bytes('\n', 'utf-8'))
                    ServerConnection.send(bytes(file.read(), 'utf-8'))
    except SocketLib.error:
        print(Colors.RED+"Connection TimedOut")


# Always Await a Connection
while 1:
    print(Colors.END+Colors.BOLD+'\nAwaiting Connection...')

    # Accept an incoming Connection if any
    ServerConnection, ClientAddress = ServerSocket.accept()

    # Uncomment This if you want to Use MultiThreading (Note: Comment line  if you want to use)
    # threading.Thread(target=handleConnection, args=(ServerConnection, ClientAddress)).start()

    handleConnection(ServerConnection, ClientAddress)
