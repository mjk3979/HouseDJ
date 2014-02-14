class Song:
    __slots__=('title', 'artist')

    def __init__(self, title, artist):
        self.title = title
        self.artist = artist

    def __str__(self):
        return self.title + " by " + self.artist

    def __hash__(self):
        return hash(self.title + self.artist)

    def __eq__(self, other):
        return self.title == other.title and self.artist == other.artist

class ClientData:
    __slots__=('nickname')

    def __init__(self, nickname):
        self.nickname = nickname

    def __str__(self):
        return self.nickname

    def __hash__(self):
        return hash(self.nickname)

    def __eq__(self, other):
        return self.nickname == other.nickname
