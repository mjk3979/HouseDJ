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
		if len(lst) == 0:
			print("Sorry Charlie.  No Results.")
			return None
		i, _ = inputChoice(list(res.name + " by " + res.artist.name if type(res) == grooveshark.classes.Song else res.name for res in lst))
		c = lst[i]
		if type(c) is grooveshark.classes.Song:
			return c
		return self.getSongRec(c.songs)

	def pickSong(self):
		responseTuple = inputChoice(["Song", "Artist", "Album"])
		if responseTuple == None:
			return None
		else:
			typ,_ = responseTuple
		typ = [Client.SONGS, Client.ARTISTS, Client.ALBUMS][typ]
		search = input('Grooveshark search: ')
		song = self.getSongRec(self.client.search(search, typ))
		if song == None:
			return None
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
