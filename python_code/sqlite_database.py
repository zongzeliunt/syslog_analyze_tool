#!/usr/bin/python

import sqlite3

conn=sqlite3.connect('example.db')
c= conn.cursor()

c.execute ("CREATE TABLE IF NOT EXISTS SINGLE_BLOCK (ID integer PRIMARY KEY, PATTERN_ID text, START text, FINISH text)")
pattern_id = "block_234"
start = "startares"
finish = "finishares"

c.execute ("INSERT INTO SINGLE_BLOCK(PATTERN_ID, START, FINISH) VALUES ('block_0', 'start', 'finish'   )")

tmp_command = "INSERT INTO SINGLE_BLOCK(PATTERN_ID, START, FINISH) VALUES ("
tmp_command += "'"
tmp_command += pattern_id
tmp_command += "'"
tmp_command += ", "
tmp_command += "'"
tmp_command += start 
tmp_command += "'"
tmp_command += ", "
tmp_command += "'"
tmp_command += finish
tmp_command += "'"
tmp_command += ")"

c.execute (tmp_command)

cursor = c.execute ("SELECT * FROM SINGLE_BLOCK")
for result in cursor:
	print result [0]
	print result [1]
	print result [2]



conn.commit()

conn.close()
