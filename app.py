from flask import Flask, render_template, request,redirect,url_for
from werkzeug import secure_filename
import sys
from utils.utils import *
from utils.variables import *


#stting for Flask
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLD = 'static/media/upload'
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_FOLD)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/layout')
def layout():
	return render_template('layout.html')


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
			feat = net.blobs['fc7'].data[0]
			hashcode = dplm128(feat)
			result_path = hashrank(hashcode, 'Query', source=source)
			return render_template('result.html', result_path = result_path, query_path = '/static/media/upload/' + filename)
	result = request.args
	hashcode= result.get('hashcode')
	path= result.get('path')
	hashcode = hashcode.split(',')
	hashcode = [int(hashcode[0][1:]), int(hashcode[1]),int(hashcode[2]),int(hashcode[3][:-1])]
	result_path = hashrank(hashcode, 'Random',source)
	return render_template('result.html', result_path = result_path, query_path = '/static/media/dataset/' + path)


@app.route('/random')
def random():
	result_path = getPathAndCodeInRandom(random_number)
	return render_template('random.html', result_path = result_path)


if __name__ == '__main__':
	if flag:
		# setting for caffe
		sys.path.insert(0, caffe_root + 'python')
		import caffe
		caffe.set_mode_cpu()
		net = caffe.Net(net_file, caffe_model, caffe.TEST)
		transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
		transformer.set_transpose('data', (2, 0, 1))
		transformer.set_mean('data', np.array([103.939, 116.779, 123.68]))
		transformer.set_raw_scale('data', 255)
		transformer.set_channel_swap('data', (2, 1, 0))
		net.blobs['data'].reshape(1, 3, 224, 224)

		app.run()