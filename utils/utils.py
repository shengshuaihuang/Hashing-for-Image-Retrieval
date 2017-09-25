# coding=utf-8
import h5py
import numpy as np
import string
import random
import pymysql
import scipy.io as sio
import pickle

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


def dplm128(feat):
	h5f = h5py.File('./hashing_model/DPLM128.h5', 'r')
	W = np.mat(h5f['W'][:])
	sigma = h5f['sigma'][:][0][0]
	anchor = np.mat(h5f['anchor'][:])
	mean0 = np.mat(h5f['mean0'][:])
	mean = np.mat(h5f['mean'][:])
	h5f.close()
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

def hammingdistance(x,y):
	return bin(x[0]^y[0]).count('1')+bin(x[1]^y[1]).count('1')+bin(x[2]^y[2]).count('1')+bin(x[3]^y[3]).count('1')


def hashrank(hashcode,model, source='memory'):
	img_path = {}
	if source=='database':
		con = pymysql.connect(host="127.0.0.1", user="root", passwd="hss123456", db="irs_dplm")
		cur = con.cursor()
		if model=='Query':
			sql = " select path from img WHERE hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4)<=36 ORDER BY hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4) ASC, id DESC LIMIT 20" 
			data = (hashcode[0], hashcode[1], hashcode[2], hashcode[3], hashcode[0], hashcode[1], hashcode[2], hashcode[3])
			aa = cur.execute(sql, data)
			info = cur.fetchmany(aa)
			for i,item in enumerate(info):
				img_path[i] = item[0]
		elif model=='Random':
			sql = " select path,code_1,code_2,code_3,code_4 from img WHERE hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4)<=4 ORDER BY hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4) ASC, id DESC LIMIT 30 "
			data = (hashcode[0], hashcode[1], hashcode[2], hashcode[3], hashcode[0], hashcode[1], hashcode[2], hashcode[3])
			aa = cur.execute(sql, data)
			info = cur.fetchmany(aa)
			for item in info:
				img_path[item[0]] = [item[1], item[2],item[3],item[4]]
		cur.close()
		con.commit()
		con.close()
	elif source=='memory':
		f1 = open('./hashing_model/DPLM128Code.pkl', 'rb')
		f2 = open('./hashing_model/DPLM128Path.pkl', 'rb')
		codebase = pickle.load(f1)
		pathbase = pickle.load(f2)
		f1.close()
		f2.close()
		if model=='Query':
			for i in codebase:
				if hammingdistance(hashcode,codebase[i]) <= 36:
					img_path[i] = pathbase[i]
				if len(img_path)==20:
					break
		elif model=='Random':
			for i in codebase:
				if hammingdistance(hashcode,codebase[i]) <= 4:
					img_path[pathbase[i]] = [codebase[i][0],codebase[i][1],codebase[i][2],codebase[i][3]]
				if len(img_path)==30:
					break
	return img_path

def getPathAndCodeInRandom(number, source='memory'):
	img_path = {}
	if source=='database':
		con = pymysql.connect(host="127.0.0.1", user="root", passwd="hss123456", db="irs_dplm")
		cur = con.cursor()
		sql = "select path,code_1,code_2,code_3,code_4 from img order by rand() LIMIT %s" 
		data = (number)
		aa = cur.execute(sql, data)
		info = cur.fetchmany(aa)
		for item in info:
			img_path[item[0]] = [item[1], item[2],item[3],item[4]]
		cur.close()
		con.commit()
		con.close()
	elif source=='memory':
		pass
	return img_path