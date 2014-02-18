from common import *
from cmdline import *
import grooveshark
from grooveshark import Client
import subprocess

class GroovesharkPlugin:
	__slots__ = ('client', 'songmap')

	def __init__(self):
		self.client = Client()
		self.client.init()
		self.songmap = {}

	def getSongRec(self, lst):
		lst = list(lst)
		i, _ = inputChoice(list(res.name + " by " + res.artist.name if type(res) == grooveshark.classes.Song else res.name for res in lst))
		c = lst[i]
		if type(c) is grooveshark.classes.Song:
			return c
		return self.getSongRec(self, c.songs)

	def pickSong(self):
		typ, _ = inputChoice(["Song", "Artist", "Album"])
		typ = [Client.SONGS, Client.ARTISTS, Client.ALBUMS][typ]
		search = input('Grooveshark search: ')
		song = self.getSongRec(self.client.search(search, typ))
		retval = Song(song.name, song.artist.name)
		self.songmap[retval] = song.safe_download()
		return retval
	
	def getSongData(self, song):
		return self.songmap[song]


def main():
	plugin = GroovesharkPlugin()
	song = plugin.pickSong()
	print(song)
	f = open('test.mp3', 'wb')
	f.write(plugin.getSongData(song))
	f.close()

if __name__ == '__main__':
	main()
