#coding=utf-8
import h5py
import numpy as np
import string
import random
import pymysql
import scipy.io as sio

def salt():
	seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	sa = []
	for i in range(8):
		sa.append(random.choice(seed))
		salt = ''.join(sa)
	return salt

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

def sqdist(p1, p2):
	x1 = np.tile(np.sum(np.multiply(p1, p1), 1), (1, p2.shape[0]))
	x2 = np.tile(np.sum(np.multiply(p2, p2), 1), (1, p1.shape[0]))
	r = p1*p2.T
	dist = x1+x2.T - 2*r
	return dist

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

def dplm128(feat):
	model = sio.loadmat('./caffe_model/DPLM128.mat')
	W = np.mat(model['W'])
	sigma = model['sigma'][0][0]
	anchor = np.mat(model['anchor'])
	mean = np.mat(model['mean'])
	mean0 = np.mat(sio.loadmat('./caffe_model/m0.mat')['m'])
	byteresult = []
	feat = np.mat(feat)
	feat = feat / np.linalg.norm(feat)
	x = np.exp(-sqdist(feat, anchor)/(2*sigma*sigma))
	x = x - mean0
	x = x - mean
	b = x * W
	b = np.where(b>0, 1, 0)
	c = np.ndarray.tolist(b)
	blist = filter_num(c)
	byteresult = bit2byte(blist, 32)
	return byteresult


def hashrank(hashcode,model):
	con = pymysql.connect(host="127.0.0.1", user="root", passwd="hss123456", db="irs_dplm")
	cur = con.cursor()
	img_path = {}
	if model=='Query':
		sql = " select path from img WHERE hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4)<=36 ORDER BY hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4) ASC, id DESC" % (hashcode[0], hashcode[1], hashcode[2], hashcode[3], hashcode[0], hashcode[1], hashcode[2], hashcode[3])
		aa = cur.execute(sql)
		info = cur.fetchmany(aa)
		for i,item in enumerate(info):
			img_path[i] = item[0]
	elif model=='Random':
		sql = " select path,code_1,code_2,code_3,code_4 from img WHERE hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4)<=4 ORDER BY hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4) ASC, id DESC " % (hashcode[0], hashcode[1], hashcode[2], hashcode[3], hashcode[0], hashcode[1], hashcode[2], hashcode[3])
		aa = cur.execute(sql)
		info = cur.fetchmany(aa)
		for item in info:
			img_path[item[0]] = [item[1], item[2],item[3],item[4]]
	cur.close()
	con.commit()
	con.close()
	return img_path


def getPathAndCodeInRandom(number):
	con = pymysql.connect(host="127.0.0.1", user="root", passwd="hss123456", db="irs_dplm")
	cur = con.cursor()
	sql = "select path,code_1,code_2,code_3,code_4 from img order by rand() LIMIT %s" % number
	aa = cur.execute(sql)
	info = cur.fetchmany(aa)
	img_path = {}
	for item in info:
		img_path[item[0]] = [item[1], item[2],item[3],item[4]]
	cur.close()
	con.commit()
	con.close()
	return img_path