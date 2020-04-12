class Contact():
	def __init__(self):
		self.contact = {}
		with open('db/contact') as f:
			for line in f.readlines():
				if not line.strip():
					continue
				x, y = line.split(':')
				self.contact[x] = y

	def add(self, name, id):
		with open('db/contact', 'a') as f:
			f.write('%s:%s' % (name, id))

