#!/usr/bin/python
#coding:utf-8
import sys
sys.path.append("/home/ares/syslog_tool_work_folder/")
import os
import re 
import time 
import python_code.global_APIs as global_APIs
import python_code.block_merger as block_merger
import python_code.preliminary_block_list_gen as preliminary_block_list_gen
import python_code.input_file_block_analyzer as input_file_block_analyzer
import python_code.block_database_opt as block_database_opt
import python_code.report_APIs as report_APIs
import python_code.timeframe_analyze as timeframe_analyze
import python_code.block_database_learner as block_database_learner
import shutil
import python_code.multi_file_folder as multi_file_folder



def main (input_file):
	print "begin"
#repeat test	
	#SLEBD_DB = block_database_opt.block_database_read("mutrino", "0")
	#repeat_list = block_database_opt.repeat_db_test(SLEBD_DB)	
	#print repeat_list

#total learning file block conflict summary
	#total_file = "total_tmp_learning_file"
	#done_learning_file_folder = "done_learning_file_folder"
	#multi_file_folder.total_tmp_learning_file_gen (total_file, done_learning_file_folder)

#single multi block summary
	#report_APIs.block_database_summary (input_file)	

#block report folder block total happen count
	#report_APIs.block_distribute_ratio_count(input_file)
		
#analyze block_length_other_report 
	#report_APIs.block_rength_other_report_analyze (input_file)
	report_APIs.multi_line_block_happen_count(input_file)

	print "finish"
	


input_file = sys.argv[1]
if not os.path.isfile(input_file):
	print "no file"
main(input_file)
