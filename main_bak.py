
#!/usr/bin/python
#coding:utf-8
import sys
import os
import re 
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



def main_1 (input_file):
#{{{

	print "begin"
	running_mode_list = [6]
	#running_mode is a list for what you want to run in this program
	#you can do multi operations in this program
	#1): file split
	#	your input argument should be a file name, this file is a multi node message mixed file.
	#2): learn pattern database and analyze block list on one file.
	#	be advised: to learn more block patterns, you'd better make a testing file which is mixed be multi node files one by one. this will increase the detect possibility of some one time showing blocks.
	#3): only block analyze, no pattern learning, if there is no pattern db program will rise alarm.
	#4): do timeframe predict test.	
	#5): ten fold cross validation.
	#	your input argument must be a folder path, the folder must have more than 2 files. program will select one file as testing file one by one. It will run learning on the rest files and test the block list on the testing file. 
	
	if 1 in running_mode_list:
		folder_name = global_APIs.log_file_split(input_file)
	if 2 in running_mode_list:
		#this will learn block list no matter there is block pattern db or not
		file_mode = global_APIs.get_file_mode (input_file)
		result = global_APIs.global_folder_initializer(input_file)
		learn_database_and_learn_block_on_one_file (input_file)
	if 3 in running_mode_list:
		file_mode = global_APIs.get_file_mode (input_file)
		result = global_APIs.global_folder_initializer(input_file)
		have_database = global_APIs.test_have_database(file_mode)
		if have_database == -1:
			print "Can't find this file format's pattern database, suggest do pattern learning first."
		else:
			general_run_process (input_file )
	if 4 in running_mode_list:
		file_mode = global_APIs.get_file_mode (input_file)
		result = global_APIs.global_folder_initializer(input_file)
		have_database = global_APIs.test_have_database(file_mode)
		if have_database == -1:
			print "Can't find this file format's pattern database, suggest do pattern learning first."
		else:
			block_list = input_file_block_analyzer.input_file_block_analyze(input_file)
			block_list = timeframe_analyze.add_time_index_into_block_list (block_list, input_file)
			timeframe_analyze.timeframe_analyze_main(block_list)
	if 5 in running_mode_list:
		ten_cross_validation(input_file)
	if 6 in running_mode_list:
		file_mode = global_APIs.get_file_mode (input_file)
		result = global_APIs.global_folder_initializer(input_file)
		block_database_learning (input_file)
		
	print "finish"
#}}}







#don't want to change
def ten_cross_validation (folder_name):
#{{{
	result = multi_file_folder.multi_cv_list_create(folder_name)
	test_file_list = result[0]
	train_file_list = result[1]
	#train
	file_mode = global_APIs.get_file_mode (test_file_list[0])

		
	database_path = "sql_database"
	database_path += file_mode


	for i in range (0, len(test_file_list)):
	    	#learning

		if os.path.isdir (database_path):
			shutil.rmtree(database_path)
		
		block_database_learning (train_file_list[i])
		general_run_process (test_file_list[i] )

#}}}		


#old code, just keeping
def block_database_learning_1 (input_file):
#{{{
	file_mode = global_APIs.get_file_mode (input_file)
	mode = 0
	#mode = 1 is only single line (no merging)
	#mode = 2 is ignore single line block
	#mode = 0 is single line included in block database
	if mode == 0:
	#{{{
		#STEP 2): initial block database learn
		block_database = preliminary_block_list_gen.preliminary_block_list_learner (input_file, mode)
		print "initial_block_database done"
		#STEP 3): first block_list analyze
		global_multi_list = {}
		block_list = input_file_block_analyzer.block_analyze(input_file, block_database, global_multi_list)
		print "initial block list done"
		#STEP 4) merge block_database based on block_list and block_database	
		result = block_merger.update_block_list_and_database (block_list, block_database)
		block_list = result[0]
		block_database = result[1]
		global_multi_list = result[2]
	
		#STEP 5) store to database
		block_database_opt.block_database_store(block_database, file_mode)
		block_database_opt.block_multi_store(global_multi_list, file_mode)
		#report_APIs.dump_block_example (block_database, input_file)
		
		
	#}}}
	if mode == 1:
	#{{{	
		#STEP 2): initial block database learn
		block_database = preliminary_block_list_gen.preliminary_block_list_learner (input_file, mode)
		#STEP 3): first block_list analyze
		global_multi_list = {}
		block_list = input_file_block_analyzer.block_analyze(input_file, block_database, global_multi_list)
		#STEP 4) merge block_database based on block_list and block_database
	
		result = block_merger.update_block_list_and_database (block_list, block_database)
		block_list = result[0]
		block_database = result[1]
		global_multi_list = result[2]
	
		#STEP 5) store to database
		block_database_opt.block_database_store(block_database, file_mode)
		block_database_opt.block_multi_store(global_multi_list, file_mode)
	
		
		#report_APIs.dump_block_example (block_database, input_file)
		
	#}}}
	if mode == 2:
	#{{{	
		#STEP 2): initial block database learn
		block_database = preliminary_block_list_gen.preliminary_block_list_learner (input_file, mode)
	
		#STEP 5) store to database
		global_multi_list = {}
		block_database_opt.block_database_store(block_database, file_mode)
		block_database_opt.block_multi_store(global_multi_list, file_mode)
	#}}}

#}}}

def block_database_update_base_on_exist (input_file):
	file_mode = global_APIs.get_file_mode (input_file)
	mode = 0
	#mode = 1 is only single line (no merging)
	#mode = 2 is ignore single line block
	#mode = 0 is single line included in block database
	if mode == 0:
	#{{{

		block_list = global_APIs.input_file_block_analyze(input_file)
		have_database = global_APIs.test_have_database(file_mode)
		block_database = block_database_opt.block_database_read(file_mode, str(have_database))
		global_multi_list = block_database_opt.multi_database_read(file_mode, str(have_database))

		result = block_merger.update_block_list_and_database (block_list, block_database, global_multi_list)
		block_list = result[0]
		block_database = result[1]
		global_multi_list = result[2]
		nickname = "1"	
		block_database_opt.block_database_store(block_database, file_mode, nickname)
		block_database_opt.block_multi_store(global_multi_list, file_mode, nickname)
		#report_APIs.dump_block_example (block_database, input_file)
		
	#}}}
	

def block_database_learning_debug (input_file):
#{{{
	file_mode = global_APIs.get_file_mode (input_file)
	#mode = 0
	#block_database = preliminary_block_list_gen.preliminary_block_list_learner (input_file, mode)
	
	block_list = input_file_block_analyzer.input_file_block_analyze(input_file)
	have_database = global_APIs.test_have_database(file_mode)
	block_database = block_database_opt.block_database_read(file_mode, str(have_database))
	global_multi_list = block_database_opt.multi_database_read(file_mode, str(have_database))

	block_list = input_file_block_analyzer.block_analyze(input_file, block_database, global_multi_list)

	block_merger.merge_debug(block_list)	
		

#}}}
