#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# code.py: based on web.py
#
# author: observer
# email: jingchaohu@gmail.com
# blog: http://obmem.com
# last edit @ 2009.12.16
import web
import sqlite3
import re
import md5
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

web.config.debug = True

db = web.database(dbn='sqlite', db='cydia.sqlite3.db')

urls = (
	'/', 'index', 
)

repo={
	'weiphone':'http://apt.weiphone.com/',
	'178':'http://static.apt.178.com/debs/'}

render = web.template.render('templates/')

app = web.application(urls, globals())

class index:
	def GET(self):
		i = web.input(id=None,page='1',q=None)
		if i.id:
			myvar = dict(id=i.id)
			rec = db.select('cydia',vars=myvar,where="id=$id")
			for r in rec:
				fl = None
				fl=self.download(r)
				return render.id([r,fl])				
			return render.error(404)
		else:
			if not i.q:
				vc = db.select('cydia',order='updatetime DESC',limit=20,offset=20*(int(i.page)-1))
				num = db.select('cydia',what="count(*) as count")[0].count
				arg = '/?page'
			else:
				qs = i.q.split(' ')
				qslen=len(qs)
				if qslen==1:
					where="name ='"+qs[0]+"' or name like '%"+qs[0]+"' or name like '"+qs[0]+"%'"
				elif qslen>1:
					qs = [ 'name like \'%'+x+'%\'' for x in qs ]
					where = ' and '.join(qs)					

				vc = db.select('cydia',order='updatetime DESC',limit=20,\
					offset=20*(int(i.page)-1),where=where)
				num = db.select('cydia',what="count(*) as count",where=where)[0].count
				arg = '/?q='+i.q+'&page'
			prev = int(i.page)-1 == 0 and '1' or str(int(i.page)-1)
			next = int(i.page)+1 <= (num-1)/20+1 and str(int(i.page)+1) or i.page
			end = str((num-1)/20+1)
			pages = [prev,next,end]
			left = min(4,int(i.page)-1)
			right = min(4,int(end)-int(i.page))
			if left < 4:
				right = min(8-left,int(end)-int(i.page))
			if right < 4:
				left = min(8-right,int(i.page)-1)
			while left > 0:
				pages.append(str(int(i.page)-left))
				left -= 1
			j = 0
			while j <= right:
				pages.append(str(int(i.page)+j))
				j += 1
			return render.index([vc,pages,arg,i.q,num])
	
	def download(self,file):
		downloadStr=''
		if file['repo']=='weiphone':
			downloadStr=repo['weiphone']+file['filename']
			return downloadStr
		elif file['repo']=='178':
			match=re.match(r'download\/(\d+)\.deb',file['filename'])
			if match:
				debid=match.group(1)
				hash=md5.new()
				hash.update(debid)
				debMd5=hash.hexdigest()
				debMd5=debMd5[0:3]				
				downloadStr=repo['178']+debMd5+'/'+debid+'.deb'
			return downloadStr
		elif file['repo']=='bigboss':
			downloadStr=repo['bigboss']+file['filename']
			return downloadStr
		
	
	
#定义404错误显示内容
def notfound():
    return web.notfound("Sorry, the page you were looking for was not found.")
    
app.notfound = notfound

if __name__ == "__main__":
	web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
	app.run()
