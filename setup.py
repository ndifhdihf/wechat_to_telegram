import os
import sys

def kill():
	os.system("ps aux | grep ython | grep forward | awk '{print $2}' | xargs kill -9")

def setup():
	kill()
	if 'kill' in str(sys.argv):
		return 
	addtional_arg = ' '.join(sys.argv[1:])
	command = 'python3 -u forward.py %s' % addtional_arg
	os.system('touch nohup.out')
	os.system('nohup %s & tail -F nohup.out' % command)

if __name__ == '__main__':
	setup()