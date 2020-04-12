import yaml
from common import getFile

def getFile(name):
	with open(name) as f:
		return yaml.load(f, Loader=yaml.FullLoader)