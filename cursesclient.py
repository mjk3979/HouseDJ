import curses
from curses import panel
from curses import textpad
from groovesharkplugin import GroovesharkPlugin

class Menu(object):

	def __init__(self, items, stdscreen):
		self.window = stdscreen.subwin(0,0)
		self.window.keypad(1)
		self.panel = panel.new_panel(self.window)
		self.panel.hide()
		panel.update_panels()

		self.position = 0
		self.items = items
		self.items.append(('exit','exit'))

	def navigate(self, n):
		self.position += n
		if self.position < 0:
				self.position = 0
		elif self.position >= len(self.items):
				self.position = len(self.items)-1

	def display(self):
		self.panel.top()
		self.panel.show()
		self.window.clear()

		retval = None
		while True:
				self.window.refresh()
				curses.doupdate()
				for index, item in enumerate(self.items):
					if index == self.position:
						mode = curses.A_REVERSE
					else:
						mode = curses.A_NORMAL

					msg = '%d. %s' % (index, item[0])
					self.window.addstr(1+index, 1, msg, mode)

				key = self.window.getch()

				if key in [curses.KEY_ENTER, ord('\n')]:
					if self.position == len(self.items)-1:
						break
					else:
						if len(self.items[self.position]) > 1:
							val = self.items[self.position][1]()
						else:
							val = None
						retval = (self.position, val)
						break

				elif key == curses.KEY_UP:
					self.navigate(-1)

				elif key == curses.KEY_DOWN:
					self.navigate(1)

		self.window.clear()
		self.panel.hide()
		panel.update_panels()
		curses.doupdate()

		return retval

class Textbox():
	__slots__ = ('prompt', 'window', 'panel')

	def __init__(self, prompt, stdscreen):
		self.window = stdscreen.subwin(0,0)
		self.window.keypad(1)
		self.panel = panel.new_panel(self.window)
		self.panel.hide()
		panel.update_panels()
		self.prompt = prompt

	def display(self):
		self.panel.top()
		self.panel.show()
		self.window.clear()

		self.window.border(0)
		self.window.addstr(2, 2, self.prompt)
		self.window.refresh()
		curses.echo()
		retval = self.window.getstr(2, 23, 60)
		curses.noecho()
		retval = retval.decode('UTF-8')

		self.window.clear()
		self.panel.hide()
		panel.update_panels()
		curses.doupdate()

		return retval

class MyApp(object):

	def __init__(self, stdscreen):
		self.screen = stdscreen
		curses.curs_set(0)

		main_menu_items = [
					('Add', self.add)
					]
		main_menu = Menu(main_menu_items, self.screen)
		main_menu.display()
	
	def add(self):
		addMenu = [
			('Grooveshark', self.addFromGrooveshark)
		]
		addMenu = Menu(addMenu, self.screen)
		addMenu.display()
	
	def addFromGrooveshark(self):
		plugin = GroovesharkPlugin(lambda lst: Menu(lst, self.screen).display(), lambda p: Textbox(p, self.screen).display()).pickSong()

if __name__ == '__main__':
	curses.wrapper(MyApp)
