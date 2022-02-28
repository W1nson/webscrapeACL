from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData
# import pandas as pd
months = {"January": '01', "February": '02', "March": '03', "April": '04', "May": '05', "June": '06', "July": '07', "August": '08', "September": '09',"October": '10', "November": '11',"December": '12'}
years = {"2021": 2021, "2022": 2022}
class dbConnect(): 
	def __init__(self): 
		self.db_string = "postgresql://winson:1229@localhost:5432/postgres"
		self.db = create_engine(self.db_string)

	def create(self): 
		# self.deleteAll()
		self.db.execute("CREATE SCHEMA IF NOT EXISTS ACL")
		self.db.execute("ALTER ROLE winson SET SEARCH_PATH TO ACL")
		self.db.execute("CREATE TABLE IF NOT EXISTS Papers(" +
		"id TEXT PRIMARY KEY," + 
		"title TEXT, " + 
		# "authors TEXT, " +
		"abstract TEXT, " 
		"forum TEXT, " + 
		"pdf TEXT, " + 
		# "software TEXT, " +
		# "data TEXT, " + 
		# "previous_URL TEXT, " + 
		# "previous_PDF TEXT, " + 
		# "response_PDF TEXT, " +
		# "month TEXT, " +
		"date DATE)")
		print("Papers TABLE CREATED")
	

	def df_to_sql(self, df, table):
		df.to_sql('Papers', self.db, if_exists='replace')


	def deleteAll(self): 
		self.db.execute("DROP SCHEMA IF EXISTS ACL CASCADE")
		print("DROP SCHEMA")

	def checkExists(self, year, month): 
		check = self.db.execute("SELECT EXISTS(SELECT 1 FROM papers WHERE EXTRACT(MONTH FROM date)='{}' AND EXTRACT(YEAR FROM date)='{}')".format(months[month], years[year]))
		for c in check: 
			return c[0]

	def insert(self, data):
		date =", \'{}-{}-01\'".format(data['year'], months[data['month']])
		del data['year'] 
		del data['month']
		columns = ', '.join(data.keys())
		columns += ', date'
		temp = [ v.replace('\'', '\'\'') if '\'' in v else v for v in data.values() ]
		temp = [ v.replace('%', '%%') if '%' in v else v for v in temp ]
		d = '\''+ '\', \''.join(temp) + '\' '
		d += date
		stmt = "INSERT INTO Papers ({}) VALUES ({})".format(columns, d)
		print(stmt) 
		self.db.execute(stmt)
		print('SUCCESS')

	def query(self, view, keyword=None, month=None, year=None):	
		stmt = "SELECT " + ', '.join(view) + " FROM Papers WHERE "
		stmt = stmt.replace('Month','EXTRACT(MONTH FROM date) AS month') 
		stmt = stmt.replace('Year', 'EXTRACT(YEAR FROM date) AS year')	

		if keyword == None and month == None and year == None:
			stmt = "SELECT " + ', '.join(view) + " FROM Papers "	
			stmt = stmt.replace('Month','EXTRACT(MONTH FROM date) AS month') 
			stmt = stmt.replace('Year', 'EXTRACT(YEAR FROM date) AS year')
			stmt += "ORDER BY year, month "	
			return self.db.execute(stmt) 

		if not keyword is None: 
			stmt += "LOWER(title) LIKE \'%%"+ keyword + "%%\' " 

		if not year is None: 
			stmt += "AND EXTRACT(YEAR FROM date) = {}".format(years[year])
		if not month is None: 
			stmt += "AND EXTRACT(MONTH FROM date) = {}".format(months[month])	

		stmt += "ORDER BY year, month "
		# print(stmt)
		out = self.db.execute(stmt) 
		
		return out

	def queryRange(self, view, keyword=None, startMonth=None, startYear=None, endMonth=None, endYear=None):		
		months = ["Select", "All", "January", "February", "March", "April", "May", "June", "July", "August", "September","October", "November","December"]
		stmt = "SELECT " + ', '.join(view) + " FROM Papers WHERE "
			
		if keyword == None and (startMonth == None or startYear == None or endMonth == None or endYear == None):
			return self.db.execute("SELECT " + ', '.join(view) + " FROM Papers") 

		if not keyword is None: 
			stmt += "LOWER(title) LIKE \'%%"+ keyword + "%%\' " 
		
		if not month is None:
			stmt += "AND month LIKE \'" + month + "\' "
		if not year is None: 
			stmt += "AND year LIKE \'" + year + "\' "

		stmt += "ORDER BY year, month "
		# print(stmt)
		out = self.db.execute(stmt) 
		 

	def update(self, data): 
		pass
	def delete(self, data): 
		pass

