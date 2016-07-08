import random
import json
import sqlite3
import string
import os
import re

class database(object):

	database = "./data/test.db"
	filepath = "./data/Bookmarks"

	def __init__(self,dbase,fpath):
		self.database = dbase
		self.filepath = fpath
		if not os.path.exists(self.database):
			self.con = sqlite3.connect(self.database)
			query = "create table bookmarks(id integer primary key autoincrement,folder varchar,name varchar,url varchar,date integer);"
			self.sql(query)
			SQL_FTS = "CREATE VIRTUAL TABLE search_index USING fts4(id INT, content);"
			self.sql(SQL_FTS)
			self.import_from_file()
			self.con.commit()
		else:
			self.con = sqlite3.connect(self.database)






	def _extract_data(self):
		#path = "/home/alphawing/.config/chromium/Default/Bookmarks"
		f = open(self.filepath,'rU')
		a = json.load(f)
		b = ''
		rt = 'roots'
		#f = open("./data/bookmark_data",'wb')
		def recfunc(children,parent,s):
			for item in children:
				if item['type'] == 'url':
					name = item['name']
					url = item['url']
					date = int(item['date_added'])
					parent = parent
					s.append((parent,name,url,date))
					#f.write(s.encode('utf-8'))
				elif item['type'] == 'folder':
					recfunc(item['children'],item['name'],s)
		bm = []
		recfunc(a[rt]['bookmark_bar']['children'],'bookmark_bar',bm)
		return bm






	def _process_data(self,inp):

		random.shuffle(inp)
		tag = []
		clas = []
		data = []
		punct = set(string.punctuation)
		for tup in inp:
			z = ''.join(x if x not in punct else " " for x in tup[0])
			z = re.sub(r'[ ]+',r' ',z)
			tag.append(z)
			clas.append(tup[1])
			pass
		f = open("./data/bookmark_features","w")
		f.write("\n".join(tag).encode("utf8"))
		f = open("./data/bookmark_classes","w")
		f.write("\n".join(clas).encode("utf8"))






	
	def import_from_file(self):
		data = self._extract_data()
		query = "insert into bookmarks(folder,name,url,date) values(?,?,?,?)"
		SQL_POPULATE = "insert into search_index (id,content) select id,folder || ' ' || name || ' ' || url from bookmarks"
		for tup in data:
			self.sql(query,tup)
			#self.con.execute("insert into bookmarks(folder,name,url,date) values(?,?,?,?)",tup)
		self.sql(SQL_POPULATE)
		a = self.sqlselect("select * from search_index")
		self.con.commit()






	def get_features(self):
		query = "select name ||' '|| url , folder from bookmarks"
		a = self.sqlselect(query)
		self._process_data(a)






	def sql(self,SQL,param = None):
		if param:
			self.con.execute(SQL,param)
		else:
			self.con.execute(SQL)





	def sqlselect(self,SQL,param = None):
		if param:
			a = self.con.execute(SQL,param).fetchall()
		else:
			a = self.con.execute(SQL).fetchall()
		return a





	def add(self,tup):
		query = "insert into bookmarks(folder,name,url,date) values(?,?,?,?)"
		SQL_POPULATE = "insert into search_index (id,content) select id,folder || ' ' || name || ' ' || url from bookmarks where date = ?"
		self.sql(query,tup)
		self.sql(SQL_POPULATE,(tup[3],))





	def delete(self,tup = None):
		query = "delete from bookmarks where name = ? and date = ?"
		self.sql(query,tup)





	def search(self,text):
		SEARCH_FTS = "SELECT * FROM bookmarks WHERE id IN (  SELECT id FROM search_index WHERE content MATCH :Content)ORDER BY name "
		return self.sqlselect(SEARCH_FTS,dict(Content = text))
