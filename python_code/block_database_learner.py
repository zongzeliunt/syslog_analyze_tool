#!/usr/bin/python

import global_APIs
import preliminary_block_list_gen
import block_merger
import block_database_opt
import input_file_block_analyzer as input_file_block_analyzer
import sys
import os
import re 
#this is block database learner

def new_block_learn_based_on_exist_database (input_file, block_database, global_multi_list):
	block_list = input_file_block_analyzer.block_analyze(input_file, block_database, global_multi_list)
#tmp file creating
	tmp_file = input_file_block_analyzer.create_exist_block_tmp_file(input_file, block_list)
	return new_pattern_learning_on_tmp_learning_file (tmp_file, block_database, global_multi_list)


def new_pattern_learning_on_tmp_learning_file(tmp_file, block_database, global_multi_list):
#learn unseen block patterns from tmp file
	mode = 0 
	pattern_list = preliminary_block_list_gen.preliminary_block_list_learner(tmp_file, mode)
	if pattern_list == {}:
#find no new pattern
		os.remove(tmp_file)
		tmp = []
		tmp.append(block_database)
		tmp.append(global_multi_list)
		return tmp 

	new_block_list = input_file_block_analyzer.block_analyze(tmp_file, pattern_list, global_multi_list)

#replace exist blocks as barricade 
	new_block_list = block_list_add_barricade(tmp_file, new_block_list)

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
	file_mode = global_APIs.get_file_mode (input_file)
	have_database = global_APIs.test_have_database(file_mode)
	block_database = []
	block_list = []
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
	
	else:
		print "exist"
		block_database = block_database_opt.block_database_read(file_mode, str(have_database))
		global_multi_list = block_database_opt.multi_database_read(file_mode, str(have_database))
		result = new_block_learn_based_on_exist_database(input_file, block_database, global_multi_list)
		block_database = result[0]
		global_multi_list = result[1]

	print "block database merge done"
	block_database_opt.block_database_store(block_database, file_mode)
	block_database_opt.block_multi_store(global_multi_list, file_mode)
	
	#global_APIs.output_block_list_report(block_list, input_file)
	#report_APIs.dump_block_example (block_database, input_file)
		
#}}}
