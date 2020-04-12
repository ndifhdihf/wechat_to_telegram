import os

class Contact():
	def __init__(self):
		self.contact = {}
		os.system('touch db/contact')
		with open('db/contact') as f:
			for line in f.readlines():
				if not line.strip():
					continue
				x, y = line.split(':')
				self.contact[x] = y

	def add(self, name, wid):
		if self.contact.get(name) == wid:
			continue
		with open('db/contact', 'a') as f:
			f.write('\n%s:%s' % (name, wid))

