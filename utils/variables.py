# coding=utf-8
import configparser
import os

def getConfig(section, key):
	config = configparser.ConfigParser()
	path = os.path.split(os.path.realpath(__file__))[0] + '/configuration.conf'
	config.read(path.replace('utils/',''))
	return config.get(section, key)


query_limit = int(getConfig('limit', 'query_limit'))
random_limit = int(getConfig('limit', 'random_limit'))
query_radus = int(getConfig('limit', 'query_radus'))
random_radus = int(getConfig('limit', 'random_radus'))

model = getConfig('hashingmodel','model')
model_path = './hashing_model/'+ model + '.h5'
code_path = './hashing_model/'+ model + 'Code.pkl'
imgpath_path = './hashing_model/'+ model + 'Path.pkl'

caffe_root = getConfig('Caffe', 'caffe_root')
net_file = getConfig('Caffe', 'net_file')
caffe_model = getConfig('Caffe', 'caffe_model')

source = getConfig('mode','source')
random_number = int(getConfig('mode','random_number'))

SUN397 = './static/media/dataset/SUN397'

flag = True
if not os.path.exists(model_path):
	print('[ERROR] ', model_path, 'is not exist!')
	flag = False

if not os.path.exists(code_path):
	print('[ERROR] ', code_path, 'is not exist!')
	flag = False

if not os.path.exists(imgpath_path):
	print('[ERROR] ', imgpath_path, 'is not exist!')
	flag = False

if not os.path.exists(net_file):
	print('[ERROR] ', net_file, 'is not exist!')
	flag = False

if not os.path.exists(caffe_model):
	print('[ERROR] ', caffe_model, 'is not exist!')
	flag = False

if not os.path.exists(SUN397):
	print('[ERROR] ', SUN397, 'is not exist!')
	flag = False

