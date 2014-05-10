#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import re
import sqlite3
import time
import os,sys
import decomp
import ConfigParser
from hashlib import md5
from threading import Thread,Lock
from Queue import Queue

path = os.path.dirname(os.path.realpath(sys.argv[0]))
dbname='cydia.sqlite3.db'
conn = sqlite3.connect(path+'/'+dbname)
conn.text_factory = str
q = Queue()
repo='neo'
MAXC = 8
repo_list={
	'178':'http://apt.178.com/Packages.gz',
	'weiphone':'http://apt.weiphone.com/Packages.bz2'
}
user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53 Cydia/1.1.9 CyF/847.21'
i_headers={'User-Agent':user_agent}

def sync(lock):
	def syncWithLock(fn):
		def newFn(*args,**kwargs):
			lock.acquire()
			try:
				return fn(*args,**kwargs)
			finally:
				lock.release()
		newFn.func_name = fn.func_name
		newFn.__doc__ = fn.__doc__
		return newFn
	return syncWithLock
 
lock = Lock()
def thread_fetch():
	conn = sqlite3.connect(path+'/'+dbname)
	conn.text_factory = str
	while True:
		deb = q.get()
		getdeb(deb,conn)
		q.task_done()

def getFileName(url):
	splitPath = url.split('/')
	return splitPath.pop()
	
def package(realname,repo,unzip=True,conn=conn):
	if unzip:
		unfile=decomp.decomper()
		pack=unfile.decomp(realname,repo)   
	else:
		src=file('download/'+realname,'r+')
		des=file('pack/'+repo,'w+')
		des.writelines(src.read())
		src.close()
		des.close()
		pack='pack/'+repo
	file = open(pack)
	debline=''
	while True:
		line = file.readline()
		if line == '':
			break
		elif line == '\n':
			#getdeb(debline,conn)
			q.put(debline)
			debline=''
		else:
			debline+=line
	file.close()

@sync(lock)
def getdeb(lines,conn=conn):
	package = re.compile(r'Package: ([\S ]+)\n',re.S|re.I).findall(lines)
	version = re.compile(r'Version: ([\S ]+)\n',re.S|re.I).findall(lines)
	name = re.compile(r'Name: ([\S ]+)\n',re.S).findall(lines)
	section = re.compile(r'Section: ([\S ]+)\n',re.S|re.I).findall(lines)
	preDepends = re.compile(r'Pre-Depends: ([\S ]+)\n',re.S|re.I).findall(lines)
	depends = re.compile(r'Depends: ([\S ]+)\n',re.S|re.I).findall(lines)
	maintainer = re.compile(r'Maintainer: ([\S ]+)\n',re.S|re.I).findall(lines)
	conflicts = re.compile(r'Conflicts: ([\S ]+)\n',re.S|re.I).findall(lines)
	author = re.compile(r'Author: ([\S ]+)\n',re.S|re.I).findall(lines)
	filename = re.compile(r'Filename: ([\S ]+)\n',re.S|re.I).findall(lines)
	icon = re.compile(r'Icon: ([\S ]+)\n',re.S|re.I).findall(lines)
	description = re.compile(r'Description: ([\S ]+)\n',re.S|re.I).findall(lines)
	homepage = re.compile(r'Homepage: ([\S ]+)\n',re.S|re.I).findall(lines)
	depiction = re.compile(r'Depiction: ([\S ]+)\n',re.S|re.I).findall(lines)
	size = re.compile(r'^Size: ([\S ]+)\n',re.S|re.I|re.M).findall(lines)
	
	if package:
		package=package[0]
	else:
		package=''
	if version:
		version=version[0]
	else:
		version=''
	if name:
		name=name[0]
	else:
		name=package[0]
	if section:
		section=section[0]
	else:
		section=''
	if preDepends:
		preDepends=preDepends[0]
	else:
		preDepends=''
	if depends:
		depends=depends[0]
	else:
		depends=''
	if maintainer:
		maintainer=maintainer[0]
	else:
		maintainer=''
	if conflicts:
		conflicts=conflicts[0]
	else:
		conflicts=''
	if author:
		author=author[0]
	else:
		author=''
	if filename:
		filename=filename[0]
	else:
		filename=''
	if icon:
		icon=icon[0]
	else:
		icon=''
	if description:
		description=description[0]
	else:
		description=''
	if homepage:
		homepage=homepage[0]
	else:
		homepage=''
	if depiction:
		depiction=depiction[0]
	else:
		depiction=''
	if size:
		size=size[0]
	else:
		size=''
		
	findid=dbfind(package,repo,version,conn)
	if not findid:
		dbinsert(package,version,name,section,size,preDepends,depends,maintainer,conflicts,author,filename,icon,description,homepage,depiction,conn)
	else:
		dbupdate(findid,package,version,name,section,size,preDepends,depends,maintainer,conflicts,author,filename,icon,description,homepage,depiction,repo,conn)	

def mytime():
	return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def dbcreate():
	c = conn.cursor()
	c.execute('''create table cydia(
		id integer primary key autoincrement,
		package varchar(50) not null,
		version varchar(15) not null,
		name varchar(50) not null,
		section varchar(40) DEFAULT 'none',
		size varchar(30),
		maintainer varchar(50),
		description text,
		depiction text,
		homepage text,
		conflicts varchar(255),
		icon varchar(255),
		depends varchar(255),
		preDepends varchar(255),
		filename varchar(255),
		author varchar(50),
		download varchar(255),
		pubdatetime varchar(12),
		updatetime varchar(12),
		repo varchar(20)
	)''')
	conn.commit()
	c.close()

def dbinsert(package,version,name,section,size,preDepends,depends,maintainer,conflicts,author,filename,icon,description,homepage,depiction,conn):
	c = conn.cursor()
	c.execute('insert into cydia (package,version,name,section,size,preDepends,depends,maintainer,conflicts,author,filename,icon,description,homepage,depiction,pubdatetime,updatetime,repo) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',\
		(package,version,name,section,size,preDepends,depends,maintainer,conflicts,author,filename,icon,description,homepage,depiction,mytime(),mytime(),repo))
	conn.commit()
	c.close()

def dbupdate(id,package,version,name,section,size,preDepends,depends,maintainer,conflicts,author,filename,icon,description,homepage,depiction,repo,conn):
	c = conn.cursor()
	c.execute('update cydia set package=?,version=?,name=?,section=?,size=?,preDepends=?,depends=?,maintainer=?,conflicts=?,author=?,filename=?,\
		icon=?,description=?,homepage=?,depiction=?,repo=? where package=? and repo=? and id=?',\
		(package,version,name,section,size,preDepends,depends,maintainer,conflicts,author,filename,icon,description,homepage,depiction,repo,\
		package,repo,id))
	conn.commit()
	c.close()

def dbfind(package,repo,version,conn):
	c =conn.cursor() 
	flag=False
	c.execute('select id from cydia where package=? and version=? and repo=?',(package,version,repo))
	cresult=c.fetchall()
	for id in c:
		if id:
			flag=id
	c.close()
	return flag

def dblist():
	c = conn.cursor()
	c.execute('select * from cydia')
	for x in c:
		for y in x:
			print y

def usage():
	print '''Usage:
	python fetchvc.py createdb
	python fetchvc.py fetch 1-1611 #fetch archive list
	python fetchvc.py fetch 5633~5684 #fetch topics
	python fetchvc.py fetch 5633 #fetch a topic
	python fetchvc.py fetch q=keyword
	python fetchvc.py list #list the database
	python fetchvc.py feed #run every 30 min to keep up-to-date
	python fetchvc.py hot
	python fetchvc.py update #update first 20 pages, run on a daily basis'''

def check_file_date(savename):
	file="download/"+savename
	if not os.path.exists(file):
		return True
	today=time.strftime('%Y-%m-%d',time.localtime())	
	filedate=time.strftime('%Y-%m-%d',time.localtime(os.stat(file).st_ctime))
	if today>filedate:
		print 'need update'
		return True
	else:
		return False

def updatepack(reponame,realname,repourl):
	req=urllib2.Request(repourl,headers=i_headers)
	try:
		response=urllib2.urlopen(req)
	except HTTPError,e:
		print 'server error code:',e.code
	except URLError,e:
		print 'failed to reach a server.'
		print 'Reason: ',e.reason
	else:	
		data=response.read()
		with open('download/'+realname,'wb') as p:
			p.write(data)
		print 'download complete'
		return True

def checkFile(reponame,repourl):
	global repo
	unzip=True
	repo=reponame
	extname=getFileName(repourl)
	if extname=='Packages':
		unzip=False
	savename=reponame+extname
	if check_file_date(savename):
		if updatepack(reponame,savename,repourl):
			package(savename,reponame,unzip)

if __name__=='__main__':
	#initialize thread pool
	for i in range(MAXC):
		t = Thread(target=thread_fetch)
		t.setDaemon(True)
		t.start()

	conn = sqlite3.connect(path+'/'+dbname)
	conn.text_factory = str

for k,v in repo_list.items():
	checkFile(k,v)
	
	q.join()
