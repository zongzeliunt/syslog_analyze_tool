#!/usr/bin/python

import global_APIs
import report_APIs
import preliminary_block_list_gen
import block_merger
import block_database_opt
import input_file_block_analyzer as input_file_block_analyzer
import sys
import os
import re 
import shutil
#this is block database learner



def new_pattern_learning_on_tmp_learning_file(tmp_file):
	file_mode = global_APIs.get_file_mode (tmp_file)
	have_database = global_APIs.test_have_database(file_mode)
	block_database = block_database_opt.block_database_read(file_mode, str(have_database))
	global_multi_list = block_database_opt.multi_database_read(file_mode, str(have_database))

#learn unseen block patterns from tmp file
	mode = 0 
	pattern_list = preliminary_block_list_gen.preliminary_block_list_learner(tmp_file, mode)
	print "new pattern learning new pattern found done"
	print len(pattern_list)
	if pattern_list == {}:
#find no new pattern
		os.remove(tmp_file)
		tmp = []
		tmp.append(block_database)
		tmp.append(global_multi_list)
		tmp.append(0)
		return tmp 

	new_block_list = input_file_block_analyzer.block_analyze(tmp_file, pattern_list, global_multi_list)
	print "new pattern learning new block_list done"
#replace exist blocks as barricade 
	new_block_list = block_list_add_barricade(tmp_file, new_block_list)
	print "new pattern learning add barricade done"
#do merge on these blocks
	#{{{
	result = block_merger.update_block_list_and_database (new_block_list, pattern_list, global_multi_list )
	tmp_block_list = result[0]
	#this tmp_block_list is useless! it have barricade
	new_block_database = result[1]
	global_multi_list = result[2]
	#}}}

	for block in new_block_database:
#ARES here should add a report

		block_num = preliminary_block_list_gen.get_lowest_pattern_list_num(block_database)
		block_name = "block_"
		block_name += str(block_num)
		block_database[block_name] = new_block_database[block]
	os.remove(tmp_file)
	tmp = []
	tmp.append(block_database)
	tmp.append(global_multi_list)
	tmp.append(1)
	
	return tmp 


def block_list_add_barricade (tmp_file, block_list):
	#add barricade to avoid merging exist block
	tmp_block_list = []
	block_list_num = 0
	fl = open (tmp_file , "r")
	line_counter = 1 
	pattern_block = r'^block\_([0-9]+)$'
	barricade_start_line = 0
	barricade_finish_line = 0
	#these block_[0-9] is because they are all new learned blocks, only have temp block name
	while block_list_num < len (block_list) - 1:
		#only add barricades between new blocks, ignore exist blocks before first new block and after last new block.
		this_block = block_list[block_list_num]
		this_block_start_line = int(this_block[1])
		this_block_finish_line = int(this_block[2])
		next_block = block_list[block_list_num + 1]
		next_block_start_line = int(next_block[1])
		next_block_finish_line = int(next_block[2])
		tmp_block_list.append(this_block)
		
		while line_counter < this_block_finish_line:
			line = fl.readline()
			line_counter = line_counter + 1

		barricade_start_line = line_counter + 1
		barricade_finish_line = line_counter + 1
		barricade_growing = 0
		while line_counter <= next_block_start_line:
			line = fl.readline()
			matchblock = re.match (pattern_block, line)
			#maybe in the future we can add "barricade" directly into tmp file, at that time we must support pattern realize "barricade"
			if matchblock:
				if barricade_growing == 0:
					barricade_growing = 1
					barricade_start_line = line_counter
				barricade_finish_line = line_counter
			
			else:
				if barricade_growing == 1:
					barricade_growing = 0
					tmp = ["barricade", str(barricade_start_line), str(barricade_finish_line)]
					tmp_block_list.append(tmp)
					barricade_start_line = line_counter
					barricade_finish_line = line_counter
			line_counter = line_counter + 1
		
		block_list_num = block_list_num + 1
	return tmp_block_list

def block_database_learning (input_file):
#{{{
	
	done_learning_file_folder = "done_learning_file_folder"
	if not os.path.isdir(done_learning_file_folder):
		os.mkdir(done_learning_file_folder)
	done_learning_file_dataset_folder = done_learning_file_folder + "/dataset/"
	if not os.path.isdir(done_learning_file_dataset_folder):
		os.mkdir(done_learning_file_dataset_folder)
	done_learning_file_EB_folder = done_learning_file_folder + "/EB_list/"
	if not os.path.isdir(done_learning_file_EB_folder):
		os.mkdir(done_learning_file_EB_folder)

	file_mode = global_APIs.get_file_mode (input_file)
	have_database = global_APIs.test_have_database(file_mode)
	block_database = []
	block_list = []
	add_new_pattern = 0
	if have_database == -1:
		mode = 0 
		block_database = preliminary_block_list_gen.preliminary_block_list_learner (input_file, mode)
		global_multi_list = {}
		block_list = input_file_block_analyzer.block_analyze(input_file, block_database, global_multi_list)
		print "initial_block_database_done"
		result = block_merger.update_block_list_and_database (block_list, block_database)
		block_list = result[0]
		block_database = result[1]
		global_multi_list = result[2]

		shutil.copy(input_file, done_learning_file_dataset_folder)
		report_APIs.output_block_list_report(block_list, input_file, 0, done_learning_file_EB_folder)
		add_new_pattern = 1	
	else:
		print "exist"
		block_database = block_database_opt.block_database_read(file_mode, str(have_database))
		global_multi_list = block_database_opt.multi_database_read(file_mode, str(have_database))
		#this is just for add this file and done block list in done_folder 	
		#test is this file is already in done_file_list
		exist = 0
		done_file_folder_list = global_APIs.get_folder_file_list(done_learning_file_dataset_folder)
		file_name = global_APIs.get_real_file_name(input_file)
		for done_file_name in done_file_folder_list:
			done_file_name = global_APIs.get_real_file_name(done_file_name)
			if file_name == done_file_name:
				exist = 1
				break
		if exist == 1:	
			file_EB_list_name = done_learning_file_EB_folder
			file_EB_list_name += file_name
			file_EB_list_name += "_block_report.txt" 
			block_list = report_APIs.block_list_file_read(file_EB_list_name)
		else :
			#this input file is not analyzed, need to get a block list again
			block_list = input_file_block_analyzer.block_analyze(input_file, block_database, global_multi_list, 1)
			shutil.copy(input_file, done_learning_file_dataset_folder)
			report_APIs.output_block_list_report(block_list, input_file, 0, done_learning_file_EB_folder)
			global_APIs.erase_conflict_block_based_on_error_report(input_file)

		total_learning_file_name = generate_total_learning_file_on_done_folder()
		result = new_pattern_learning_on_tmp_learning_file (total_learning_file_name)
		block_database = result[0]
		global_multi_list = result[1]
		add_new_pattern = result[2]


	print "block database merge done"
	if add_new_pattern == 1:
		#there is new pattern detected, need to update database and update all done files' EB lists
	    	block_database_opt.block_database_store(block_database, file_mode)
	    	block_database_opt.block_multi_store(global_multi_list, file_mode)
		update_existing_done_file_EB_list(input_file)
			
		
#}}}



def update_existing_done_file_EB_list (input_file):
	print "update"
	#input_file is just a file_mode tragger
	file_mode = global_APIs.get_file_mode (input_file)
	have_database = global_APIs.test_have_database(file_mode)
	block_database = block_database_opt.block_database_read(file_mode, str(have_database))
	global_multi_list = block_database_opt.multi_database_read(file_mode, str(have_database))

	done_learning_file_folder = "done_learning_file_folder"
	done_learning_file_dataset_folder = done_learning_file_folder + "/dataset/"
	done_learning_file_EB_folder = done_learning_file_folder + "/EB_list/"
	done_file_list = global_APIs.get_folder_file_list(done_learning_file_dataset_folder)
	

	for file_name in done_file_list:
		real_file_name = global_APIs.get_real_file_name(file_name)
		file_EB_list_name = done_learning_file_EB_folder
		file_EB_list_name += real_file_name
		file_EB_list_name += "_block_report.txt" 
		
		#block_list = report_APIs.block_list_file_read(file_EB_list_name)
		#tmp_file = input_file_block_analyzer.create_exist_block_tmp_file (file_name, block_list, error_report )

		#ARES this is just a temporary solution
		block_list = input_file_block_analyzer.block_analyze(file_name, block_database, global_multi_list)
		
		report_APIs.output_block_list_report(block_list, file_name, 0, done_learning_file_EB_folder)


def generate_total_learning_file_on_done_folder ():
	done_learning_file_folder = "done_learning_file_folder"
	done_learning_file_dataset_folder = done_learning_file_folder + "/dataset/"
	done_learning_file_EB_folder = done_learning_file_folder + "/EB_list/"
	done_file_list = global_APIs.get_folder_file_list(done_learning_file_dataset_folder)
	total_learning_file_name = "total_tmp_learning_file.txt"
	total_fl = open (total_learning_file_name, "w")
	error_report = global_APIs.analyze_error_list_file("error_report.txt")
	for file_name in done_file_list:
		real_file_name = global_APIs.get_real_file_name(file_name)
		file_EB_list_name = done_learning_file_EB_folder
		file_EB_list_name += real_file_name
		file_EB_list_name += "_block_report.txt" 
		block_list = report_APIs.block_list_file_read(file_EB_list_name)
		tmp_file = input_file_block_analyzer.create_exist_block_tmp_file (file_name, block_list, error_report )
		tmp_file_fl = open (tmp_file, "r")
		for line in tmp_file_fl.readlines():
			total_fl.write(line)
		tmp_file_fl.close()
		os.remove(tmp_file)	
	total_fl.close()
	os.remove ("error_report.txt")	

	return total_learning_file_name

