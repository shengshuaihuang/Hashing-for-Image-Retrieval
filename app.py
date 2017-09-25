from flask import Flask, render_template, request,redirect,url_for
from werkzeug import secure_filename
import numpy as np
from numpy import linalg as LA
import sys
import os
import pymysql

from utils.utils import *

# setting for caffe
caffe_root = '/home/hsshuai/caffe/'
sys.path.insert(0, caffe_root + 'python')
import caffe

caffe.set_mode_cpu()
net_file = './caffe_model/VGG_ILSVRC_16_layers_deploy.prototxt'
caffe_model = './caffe_model/VGG_ILSVRC_16_layers.caffemodel'
net = caffe.Net(net_file, caffe_model, caffe.TEST)

transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2, 0, 1))
transformer.set_mean('data', np.array([103.939, 116.779, 123.68]))
transformer.set_raw_scale('data', 255)
transformer.set_channel_swap('data', (2, 1, 0))
net.blobs['data'].reshape(1, 3, 224, 224)


#stting for Flask
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = 'static/media/upload'
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/layout')
def layout():
	return render_template('layout.html')




def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/result', methods = ['POST', 'GET'])
def result():
	if request.method == 'POST':
		f = request.files['file']
		if f and allowed_file(f.filename):
			filename = secure_filename(f.filename)
			filename =  filename.split('.')[0] + '_' + salt() + '.' + filename.split('.')[1]
			save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			f.save(save_path)
			im = caffe.io.load_image(save_path)
			net.blobs['data'].data[...] = transformer.preprocess('data', im)
			output = net.forward()
			# feat = net.blobs['fc8'].data[0] # uncomment if use SGH method
			feat = net.blobs['fc7'].data[0]
			hashcode = dplm128(feat)
			# result_path = hashrank(hashcode, 'Query', source = 'database')
			result_path = hashrank(hashcode, 'Query')
			return render_template('result.html', result_path = result_path, query_path = filename)

@app.route('/random', methods = ['POST', 'GET'])
def random():
	if request.method == 'POST':
		result = request.form
		hashcode = result['hashcode']
		hashcode = hashcode.split(',')
		hashcode = [int(hashcode[0][1:]), int(hashcode[1]),int(hashcode[2]),int(hashcode[3][:-1])]
		# result_path = hashrank(hashcode, 'Random', source = 'database')
		result_path = hashrank(hashcode, 'Random')
		return render_template('random.html', result_path = result_path)
	else:
		result_path = getPathAndCodeInRandom(50, source='database')
		return render_template('random.html', result_path = result_path)

if __name__ == '__main__':
	app.run(debug=True)