import server
from common import Song
from common import ClientData

def main():
    c1 = ClientData("test")
    c2 = ClientData("matt")
    server.clients[c1] = server.Client(c1)
    server.clients[c1].recieveMessage([Song('Beast and the Harlot', 'A7X'), Song('United States of Pop 2013', 'DJ Earworm')])
    server.clients[c2] = server.Client(c2)
    server.clients[c2].recieveMessage([Song('Thunderhorse', 'Dethklok'), Song('Trouble', 'T Swift'), Song('One', 'Metallica')])
    for song in server.masterQueue:
        print(song)

if __name__ == "__main__":
    main()
