# coding=utf-8
import h5py
import numpy as np
import string
import random
import pymysql
import scipy.io as sio
import pickle

dplm_model_path = './hashing_model/DPLM128.h5'
dplm_code_path = './hashing_model/DPLM128Code.pkl'
dplm_path_path = './hashing_model/DPLM128Path.pkl'


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
	h5f = h5py.File(dplm_model_path, 'r')
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


def hashrank(hashcode,model,radus=2,source='memory'):
	img_path = {}
	img_path_cache = {}
	img_path_rank = []
	query_limit = 20
	random_limit = 30

# data from database
	if source=='database':
		con = pymysql.connect(host="127.0.0.1", user="root", passwd="hss123456", db="irs_dplm")
		cur = con.cursor()
		if model=='Query':
			sql = " select path from img WHERE hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4)<=36 ORDER BY hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4) ASC, id DESC LIMIT %s" 
			data = (hashcode[0], hashcode[1], hashcode[2], hashcode[3], hashcode[0], hashcode[1], hashcode[2], hashcode[3], query_limit)
			aa = cur.execute(sql, data)
			info = cur.fetchmany(aa)
			for i,item in enumerate(info):
				img_path[i] = item[0] # { id:path }
		elif model=='Random':
			sql = " select path,code_1,code_2,code_3,code_4 from img WHERE hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4)<=4 ORDER BY hammingdistance(%s,%s,%s,%s,code_1,code_2,code_3,code_4) ASC, id DESC LIMIT %s "
			data = (hashcode[0], hashcode[1], hashcode[2], hashcode[3], hashcode[0], hashcode[1], hashcode[2], hashcode[3], random_limit)
			aa = cur.execute(sql, data)
			info = cur.fetchmany(aa)
			for i, item in enumerate(info):
				img_path[i] = {item[0].rstrip():[item[1], item[2],item[3],item[4]]}  # { id: { path:[code1, code2, code3, code4] } }
		cur.close()
		con.commit()
		con.close()

# data from memory
	elif source=='memory':
		f1 = open(dplm_code_path, 'rb')
		f2 = open(dplm_path_path, 'rb')
		codebase = pickle.load(f1)
		pathbase = pickle.load(f2)
		f1.close()
		f2.close()

		if model=='Random':
			for i in codebase:
				dist = hammingdistance(hashcode,codebase[i])
				#img_path_cache { hammingdistance:{path:[code1, code2, code3, code4]} }
				if dist <= 4:
					if dist in img_path_cache.keys():
						img_path_cache[dist].append({ pathbase[i] : [ codebase[i][0],codebase[i][1],codebase[i][2],codebase[i][3] ] })
					else:
						img_path_cache[dist] = []
						img_path_cache[dist].append({ pathbase[i] : [ codebase[i][0],codebase[i][1],codebase[i][2],codebase[i][3] ] })
			# img_path {id:{path:[code1, code2, code3, code4]}}
			for value in iter(img_path_cache.values()):
				img_path_rank.extend(value)
				if len(img_path_rank)>random_limit:
					for i,item in enumerate(img_path_rank[:query_limit]):
						img_path[i] = item
				else:
					for i,item in enumerate(img_path_rank):
						img_path[i] = item

		elif model=="Query":
			for i in codebase:
				dist = hammingdistance(hashcode,codebase[i])
				#img_path_cache {hammingdistance:[path]}
				if dist <= 36:
					if dist in img_path_cache.keys():
						img_path_cache[dist].append(pathbase[i])
					else:
						img_path_cache[dist] = []
						img_path_cache[dist].append(pathbase[i])
			# img_path {id:path}
			for value in iter(img_path_cache.values()):
				img_path_rank.extend(value)
				if len(img_path_rank)>query_limit:
					for i,item in enumerate(img_path_rank[:query_limit]):
						img_path[i] = item
				else:
					for i,item in enumerate(img_path_rank):
						img_path[i] = item
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
		for i, item in enumerate(info):
			img_path[i] = {item[0].rstrip():[item[1], item[2],item[3],item[4]]}  # { id: { path:[code1, code2, code3, code4] } }
		cur.close()
		con.commit()
		con.close()
	elif source=='memory':
		f1 = open(dplm_code_path, 'rb')
		f2 = open(dplm_path_path, 'rb')
		codebase = pickle.load(f1)
		pathbase = pickle.load(f2)
		f1.close()
		f2.close()

		seed = range(len(codebase))
		randlist = random.sample(seed,number)
		for i,randindex in enumerate(randlist):
			img_path[i] = {pathbase[randindex]:[ codebase[randindex][0],codebase[randindex][1],codebase[randindex][2],codebase[randindex][3] ]}
	return img_path

# import time
# # hashcode = [2927750817, 1195056709, 404853706, 2309990425]

# time1 = time.time()
# print(getPathAndCodeInRandom(3, source='memory'))
# time2 = time.time()
# print(getPathAndCodeInRandom(3, source='database'))
# time3 = time.time()
# # hashrank(hashcode,'Random', source='memory')
# # time4 = time.time()
# # hashrank(hashcode,'Random', source='database')
# # time5 = time.time()

# print('memory:',time2-time1, 'database:',time3-time2)
# # print('memory:',time4-time3, 'database:',time5-time4)
