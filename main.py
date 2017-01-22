#!/usr/bin/python
#coding:utf-8
import sys
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


def learn_database_and_learn_block_on_one_file (input_file):
	file_mode = global_APIs.get_file_mode (input_file)
	database_path = "sql_database"
	database_path += file_mode

	if os.path.isdir (database_path):
		shutil.rmtree(database_path)
	block_database_learner.block_database_learning (input_file)
	print "database done"

	report_APIs.general_run_process (input_file )

def main (input_file):
	print "begin"
	result = global_APIs.global_folder_initializer(input_file)

################################################################################
#feature 1: file split and remix	
	#result = multi_file_folder.log_file_split(input_file)
	#multi_file_folder.splited_folder_merge(result)

	#multi_file_folder.splited_folder_merge(input_file)
	#multi_file_folder.multi_file_learning_folder_gen(input_file)


################################################################################	
#feature 2: block database learning
	#block_database_learner.block_database_learning (input_file)
	
	#multi_file_folder.folder_learning (input_file)	
	
	#multi_file_folder.folder_single_line_pattern_learning (input_file)	


################################################################################	
#feature 3: block report analyzing
	#report_APIs.general_run_process (input_file, 1 )
	#multi_file_folder.folder_analyzing (input_file)	






################################################################################	
#just keep these functions, dont't use
	#learn_database_and_learn_block_on_one_file (input_file)
	
	#report_APIs.block_database_summary(input_file)

	#block_list = input_file_block_analyzer.input_file_block_analyze(input_file)
	#block_list = timeframe_analyze.add_time_index_into_block_list (block_list, input_file)

	#timeframe_analyze.timeframe_analyze_main(block_list)

	#pattern_list = preliminary_block_list_gen.preliminary_block_list_learner(input_file, 0)
	#print pattern_list
	
	



	print "finish"
	


input_file = sys.argv[1]
if not os.path.isfile(input_file):
	print "no file"
main(input_file)
