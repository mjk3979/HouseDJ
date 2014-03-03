from common import *
import grooveshark
from grooveshark import Client
import subprocess

class GroovesharkPlugin:
	__slots__ = ('client', 'songmap', 'menuFunc', 'inputFunc')

	def __init__(self, menuFunc, inputFunc):
		self.client = Client()
		self.client.init()
		self.songmap = {}
		self.menuFunc = menuFunc
		self.inputFunc = inputFunc

	def getSongRec(self, lst):
		while True:
			lst = list(lst)
			if len(lst) == 0:
				print("Sorry Charlie.  No Results.")
				return None
			tup = self.menuFunc(list((s,) for s in (res.name + " by " + res.artist.name if type(res) == grooveshark.classes.Song else res.name for res in lst)))
			if tup == None:
				return None
			i = tup[0]
			c = lst[i]
			if type(c) is grooveshark.classes.Song:
				return c
			nxt = self.getSongRec(c.songs)
			if nxt != None:
				return nxt

	def pickSong(self):
		while True:
			responseTuple = self.menuFunc(list((s,) for s in ["Song", "Artist", "Album"]))
			if responseTuple == None:
				return None
			else:
				typ,_ = responseTuple
			typ = [Client.SONGS, Client.ARTISTS, Client.ALBUMS][typ]
			search = self.inputFunc('Grooveshark search: ')
			song = self.getSongRec(self.client.search(search, typ))
			if song != None:
				break
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
