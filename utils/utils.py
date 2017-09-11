import h5py
import numpy as np
import pymysql

def filter_num(tree):
	for i in tree:
		if isinstance(i, list):
			return i

def bit2byte(blist, nbit):
	j = 0
	s = 0
	byte_result = []
	for i in blist:
		i = int(i)
		if j != (nbit-1):
			s += (i*2)**((nbit-1)-j)
		else:
			s += i
		j += 1
		if j == nbit:
			j = 0
			byte_result.append(s)
			s = 0
	return byte_result

def distmat(p1, p2):
	x1 = np.tile(np.sum(np.multiply(p1, p1), 1), (1, p2.shape[0]))
	x2 = np.tile(np.sum(np.multiply(p2, p2), 1), (1, p1.shape[0]))
	r = p1*p2.T
	dist = np.sqrt(x1+x2.T - 2*r)
	return dist

def sgh64_deep(feat):
	# load sgh model and transform to mat or value
	h5f = h5py.File('./caffe_model/SGH64_deep.h5', 'r')
	Wx = np.mat(h5f['Wx'][:])
	bias = np.mat(h5f['bias'][:])
	bases = np.mat(h5f['bases'][:])
	mean = np.mat(h5f['mean'][:])
	delta = h5f['delta'][:]
	delta = filter_num(delta.tolist())[0]
	h5f.close()

	byteresult = []
	feat = feat -mean
	kx = distmat(feat, bases)
	kx = np.multiply(kx, kx)
	kx = np.exp(-kx/(2*delta))
	kxx = kx - np.tile(bias, (feat.shape[0], 1))
	b = kxx * Wx
	b = np.where(b > 0, 1, 0)
	c = np.ndarray.tolist(b)
	blist = filter_num(c)
	byteresult = bit2byte(blist, 16)
	return byteresult

def hashrank(hashcode,model):
	con = pymysql.connect(host="127.0.0.1", user="root", passwd="hss123456", db="IRS")
	cur = con.cursor()
	img_path = {}
	if model=='Query':
		sql = " select img_path from ImageRetrievalSystem_img WHERE hammingdistance(%s,%s,%s,%s,sgh64_deep_1,sgh64_deep_2,sgh64_deep_3,sgh64_deep_4)<=2 ORDER BY hammingdistance(%s,%s,%s,%s,sgh64_deep_1,sgh64_deep_2,sgh64_deep_3,sgh64_deep_4) ASC, id DESC LIMIT 20" % (hashcode[0], hashcode[1], hashcode[2], hashcode[3], hashcode[0], hashcode[1], hashcode[2], hashcode[3])
		aa = cur.execute(sql)
		info = cur.fetchmany(aa)
		for i,item in enumerate(info):
			img_path[i] = item[0]
	elif model=='Random':
		sql = " select img_path,sgh64_deep_1, sgh64_deep_2,sgh64_deep_3,sgh64_deep_4 from ImageRetrievalSystem_img WHERE hammingdistance(%s,%s,%s,%s,sgh64_deep_1,sgh64_deep_2,sgh64_deep_3,sgh64_deep_4)<=2 ORDER BY hammingdistance(%s,%s,%s,%s,sgh64_deep_1,sgh64_deep_2,sgh64_deep_3,sgh64_deep_4) ASC, id DESC LIMIT 20" % (hashcode[0], hashcode[1], hashcode[2], hashcode[3], hashcode[0], hashcode[1], hashcode[2], hashcode[3])
		aa = cur.execute(sql)
		info = cur.fetchmany(aa)
		for item in info:
			img_path[item[0]] = [item[1], item[2],item[3],item[4]]
	cur.close()
	con.commit()
	con.close()
	return img_path


def getPathAndCodeInRandom(number):
	con = pymysql.connect(host="127.0.0.1", user="root", passwd="hss123456", db="IRS")
	cur = con.cursor()
	sql = "select img_path,sgh64_deep_1, sgh64_deep_2,sgh64_deep_3,sgh64_deep_4 from ImageRetrievalSystem_img order by rand() LIMIT %s" % number
	aa = cur.execute(sql)
	info = cur.fetchmany(aa)
	img_path = {}
	for item in info:
		img_path[item[0]] = [item[1], item[2],item[3],item[4]]
	cur.close()
	con.commit()
	con.close()
	return img_path