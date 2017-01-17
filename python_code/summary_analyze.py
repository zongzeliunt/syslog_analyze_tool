#!/usr/bin/python
#coding:utf-8
import sys
import os
import re 
import global_APIs as global_APIs
import block_merger as block_merger
import preliminary_block_list_gen as preliminary_block_list_gen
import input_file_block_analyzer as input_file_block_analyzer
import block_database_opt as block_database_opt
import report_APIs as report_APIs
import timeframe_analyze as timeframe_analyze
import block_database_learner as block_database_learner
import multi_file_folder as multi_file_folder
import shutil

# read block_length_other_report to calculate average block length  
def main (input_file):
	fl = open (input_file, "r")
	total_list = {}
	while True:
		line = fl.readline()
		if line == "":
			break
		line = line.split()
		num = line[1]
		
		if num in total_list:
			total_list[num] = total_list[num] + 1
		else:
			total_list[num] = 1

	for num in total_list:
		tmp = "num "
		tmp += str(num)
		tmp += ": "
		tmp += "count "
		tmp += str(total_list[num])
		print tmp



input_file = sys.argv[1]
if not os.path.isfile(input_file):
	print "no file"
main(input_file)
