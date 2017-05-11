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


def baler_type_file_block_DB_initializer (input_file):
#{{{
	result = global_APIs.global_folder_initializer(input_file)
	file_mode = "baler_mutrino"
	have_database = global_APIs.test_have_database(file_mode)
	largest_block_number = 0
	baler_pattern_correspond_dict = {}
	block_database = {}
	block_multi_database = {}
	if not have_database == -1:
		block_database = block_database_opt.block_database_read(file_mode, str(have_database))
		for block_name in block_database:
			pattern = r'block_([0-9]+)$'	
			matchobj = re.match (pattern, block_name)
			if matchobj:
				block_number = matchobj.group(1)
			if int(block_number) > largest_block_number:
				largest_block_number = int(block_number)
			baler_pattern_number = block_database[block_name]["start"][0][1]
			baler_pattern_correspond_dict[baler_pattern_number] = baler_pattern_number
			
	fl = open (input_file, "r")
	
	for line in fl.readlines():
		baler_pattern_number = global_APIs.get_baler_mutrino_message_pattern_number(line)
		if not baler_pattern_number in baler_pattern_correspond_dict:
			block_name = "block_"
			block_name += str(largest_block_number)
			largest_block_number += 1
			baler_pattern_correspond_dict[baler_pattern_number] = block_name
			tmp = {}
			baler_single_line_pattern = []
			baler_pattern_number_name = str(baler_pattern_number)
			pattern_element = []
			pattern_element.append(0)
			pattern_element.append(baler_pattern_number_name)
			baler_single_line_pattern.append(pattern_element)
			tmp["start"] =  baler_single_line_pattern
			tmp["finish"] = baler_single_line_pattern
			block_database[block_name] = tmp
	
	block_database_opt.block_database_store(block_database, file_mode)
	block_database_opt.block_multi_store(block_multi_database, file_mode)
	fl.close ()
#}}}

def baler_single_line_block_DB_initializer (folder_name):
	file_list = global_APIs.get_folder_file_list(folder_name)
	for file_name in file_list:
		baler_type_file_block_DB_initializer (file_name)

def baler_single_line_SLEBD_type_pattern_gen (folder_name):
#{{{
	single_line_SLEBD_pattern_list = baler_single_line_SLEBD_pattern_DB_read()
	file_list = global_APIs.get_folder_file_list(folder_name)
	empty_pattern_list = []
	for file_name in file_list:
		print file_name
		fl = open (file_name, "r")
		for line in fl.readlines():
			if global_APIs.is_baler_mutrino_format(line) == 0:
				break
			baler_pattern_number = global_APIs.get_baler_mutrino_message_pattern_number(line)
			baler_pattern_number = str(baler_pattern_number)	
			line_message = global_APIs.get_baler_mutrino_message_line_message(line)	
			SLEBD_line_pattern = global_APIs.gen_line_pattern(line_message)
			if len(SLEBD_line_pattern) == 0:
				if not baler_pattern_number in empty_pattern_list:
					empty_pattern_list.append(baler_pattern_number)
				continue
			tmp = []
			if baler_pattern_number in single_line_SLEBD_pattern_list:
				tmp = single_line_SLEBD_pattern_list[baler_pattern_number]
				exist = 0
				for pattern in tmp:
					if global_APIs.calculate_match_ratio(pattern, SLEBD_line_pattern) > preliminary_block_list_gen.line_pattern_match_threshold :
						exist = 1
						break
				if exist == 0:
					tmp.append(SLEBD_line_pattern)
			else:
				tmp = []
				tmp.append(SLEBD_line_pattern)
			single_line_SLEBD_pattern_list[baler_pattern_number] = tmp
	baler_single_line_SLEBD_pattern_DB_store (single_line_SLEBD_pattern_list)
	baler_single_line_empty_pattern_DB_store (empty_pattern_list)
#}}}

def baler_single_line_SLEBD_pattern_DB_store (single_line_SLEBD_pattern_list):
#{{{
	file_name = "sql_database/baler_mutrino/baler_single_line_SLEBD_pattern.txt"
	fl = open(file_name, "w")
	for baler_pattern_number in single_line_SLEBD_pattern_list:
		fl.write("baler_name " + str(baler_pattern_number) + "\n")
		for pattern in single_line_SLEBD_pattern_list[baler_pattern_number]:
			tmp = ""
			for i in range (0, len(pattern)):
				element = pattern[i]
				pos = element[0]
				word = element[1]
				tmp += str(pos)
				tmp += " "
				tmp += str(word)
				tmp += " "
			
			fl.write(tmp)
			fl.write("\n")
	fl.write ("baler_single_line_SLEBD_pattern_finished")
	fl.close()
#}}}

def baler_single_line_empty_pattern_DB_store (empty_pattern_list):
#{{{
	file_name = "sql_database/baler_mutrino/baler_single_line_empty_pattern.txt"
	fl = open(file_name, "w")
	for baler_pattern_number in empty_pattern_list:
		fl.write("baler_name " + str(baler_pattern_number) + "\n")
	fl.write ("baler_single_line_empty_pattern_finished")
	fl.close()
#}}}

def baler_single_line_SLEBD_pattern_DB_read ():
#{{{
	file_name = "sql_database/baler_mutrino/baler_single_line_SLEBD_pattern.txt"
	single_line_SLEBD_pattern_list = {}
	if not os.path.isfile (file_name):
		return {}
	fl = open(file_name, "r")
	current_baler_name = ""
	current_baler_list = []
	while True:
		line = fl.readline()
		if line == "baler_single_line_SLEBD_pattern_finished" or line == "":
			if not current_baler_name == "" and not current_baler_list == []:
				single_line_SLEBD_pattern_list[current_baler_name] = current_baler_list
			break
		baler_single_name_pattern = r'baler_name ([0-9]+)$'
		matchobj = re.match (baler_single_name_pattern, line)
		if matchobj:
			if current_baler_name == "":
				current_baler_name = str(matchobj.group(1))
				 
			else:
				single_line_SLEBD_pattern_list[current_baler_name] = current_baler_list
				current_baler_name = str(matchobj.group(1))
				current_baler_list = []
		else:
			pattern = block_database_opt.convert_string_into_pattern (line)
			current_baler_list.append(pattern)
	return single_line_SLEBD_pattern_list
#}}}

def baler_single_line_empty_pattern_DB_read ():
#{{{
	file_name = "sql_database/baler_mutrino/baler_single_line_empty_pattern.txt"
	single_line_empty_pattern_list = []
	if not os.path.isfile (file_name):
		return [] 
	fl = open(file_name, "r")
	current_baler_name = ""
	current_baler_list = []
	while True:
		line = fl.readline()
		if line == "baler_single_line_empty_pattern_finished" or line == "":
			break
		baler_single_name_pattern = r'baler_name ([0-9]+)$'
		matchobj = re.match (baler_single_name_pattern, line)
		if matchobj:
			single_line_empty_pattern_list.append(str(matchobj.group(1)))
	return single_line_empty_pattern_list
#}}}

def two_db_compare (SLEBD_sql_folder, baler_sql_folder):
#{{{
	SLEBD_DB = block_database_opt.block_database_read ("mutrino" , "0")
	baler_DB = block_database_opt.block_database_read ("baler_mutrino" , "0")
	baler_single_line_SLEBD_DB = baler_single_line_SLEBD_pattern_DB_read()
	shared_baler_block_list = {}
	shared_SLEBD_block_list = {}
	private_baler_block_list = []
	private_SLEBD_block_list = []

	for baler_block_name in baler_DB:
		is_single_line_pattern = 0 
		
		baler_correspond_SLEBD_list = []
		baler_start_line = baler_DB[baler_block_name]["start"]
		baler_finish_line = baler_DB[baler_block_name]["finish"]
		if baler_start_line == baler_finish_line:
			is_single_line_pattern = 1

		start_line_baler_line_num = str(baler_start_line[0][1])
		finish_line_baler_line_num = str(baler_finish_line[0][1])
		if not  start_line_baler_line_num in baler_single_line_SLEBD_DB or not finish_line_baler_line_num in baler_single_line_SLEBD_DB:
			#empty pattern, can be searched in baler empty list
			continue
		start_line_SLEBD_pattern_list = baler_single_line_SLEBD_DB[start_line_baler_line_num]
		finish_line_SLEBD_pattern_list = baler_single_line_SLEBD_DB[finish_line_baler_line_num]
		
		for start_line_SLEBD_pattern in start_line_SLEBD_pattern_list:
			found = 0
			for SLEBD_block_name in SLEBD_DB:
				SLEBD_start_line = SLEBD_DB[SLEBD_block_name]["start"]
				SLEBD_finish_line = SLEBD_DB[SLEBD_block_name]["finish"]
				if global_APIs.calculate_match_ratio(start_line_SLEBD_pattern, SLEBD_start_line) > preliminary_block_list_gen.line_pattern_match_threshold :
					if is_single_line_pattern == 1:
						found = 1 
					else:
						for finish_line_SLEBD_pattern in finish_line_SLEBD_pattern_list:
							if global_APIs.calculate_match_ratio(finish_line_SLEBD_pattern, SLEBD_finish_line) > preliminary_block_list_gen.line_pattern_match_threshold :
								found = 1
								break
					if found == 1:
						baler_correspond_SLEBD_list.append(SLEBD_block_name)
						if SLEBD_block_name in shared_SLEBD_block_list:
							tmp = shared_SLEBD_block_list[SLEBD_block_name]
							if not baler_block_name in tmp:
								tmp.append(baler_block_name)
								shared_SLEBD_block_list[SLEBD_block_name] = tmp
						else:
							tmp = []
							tmp.append(baler_block_name)
							shared_SLEBD_block_list[SLEBD_block_name] = tmp
				else:
					continue
				if found == 1:
					break
		if not baler_correspond_SLEBD_list == []:
			shared_baler_block_list[baler_block_name] = baler_correspond_SLEBD_list

	for baler_block_name in baler_DB:
		if not baler_block_name in shared_baler_block_list:
			private_baler_block_list.append(baler_block_name)
	for SLEBD_block_name in SLEBD_DB:
		if not SLEBD_block_name in shared_SLEBD_block_list:
			private_SLEBD_block_list.append(SLEBD_block_name)
	tmp_list = []
	tmp_list.append(shared_baler_block_list)		
	tmp_list.append(shared_SLEBD_block_list)		
	tmp_list.append(private_baler_block_list)		
	tmp_list.append(private_SLEBD_block_list)		
	return tmp_list
#}}}

def two_db_compare_result_analyze (result):
#{{{
	shared_baler_block_list = result[0]
	shared_SLEBD_block_list = result[1]
	private_baler_block_list = result[2]
	private_SLEBD_block_list = result[3]
	SLEBD_DB = block_database_opt.block_database_read ("mutrino" , "0")
	baler_DB = block_database_opt.block_database_read ("baler_mutrino" , "0")
	baler_single_line_SLEBD_DB = baler_single_line_SLEBD_pattern_DB_read()
	
	#print len(  shared_baler_block_list)
	#print len (shared_SLEBD_block_list)
	#print len (private_baler_block_list)
	#print len (private_SLEBD_block_list)

	"""
	for baler_block in shared_baler_block_list:	
		SLEBD_block_list = shared_baler_block_list[baler_block]
		if len(SLEBD_block_list) == 1: 
			continue
		baler_pattern = baler_DB[baler_block]
		baler_start = baler_pattern["start"][0][1]
		baler_finish = baler_pattern["finish"][0][1]
		print "baler"
		print baler_start
		print baler_finish
		print baler_single_line_SLEBD_DB[str(baler_start)]
		print baler_single_line_SLEBD_DB[str(baler_finish)]
		print "SLEBD"
		for SLEBD_block in SLEBD_block_list:
			print SLEBD_block
			print 	SLEBD_DB[SLEBD_block]
		print "\n"
	"""
	for SLEBD_block in shared_SLEBD_block_list:	
		baler_block_list = shared_SLEBD_block_list[SLEBD_block]
		if len(baler_block_list) == 1: 
			continue
		SLEBD_pattern = SLEBD_DB[SLEBD_block]
		SLEBD_start = SLEBD_pattern["start"]
		SLEBD_finish = SLEBD_pattern["finish"]
		print "SLEBD"
		print SLEBD_start
		print SLEBD_finish
		print "SLEBD"
		for baler_block in baler_block_list:
			baler_pattern = baler_DB[baler_block]
			baler_start = baler_pattern["start"][0][1]
			baler_finish = baler_pattern["finish"][0][1]
			print baler_block
			print baler_start
			print baler_single_line_SLEBD_DB[baler_start]
			print baler_finish
			print baler_single_line_SLEBD_DB[baler_finish]
		print "\n"
#}}}

def share_block_multi_analyze (result):
	shared_baler_block_list = result[0]
	shared_SLEBD_block_list = result[1]
	private_baler_block_list = result[2]
	private_SLEBD_block_list = result[3]
	SLEBD_DB = block_database_opt.block_database_read ("mutrino" , "0")
	baler_DB = block_database_opt.block_database_read ("baler_mutrino" , "0")
	baler_single_line_SLEBD_DB = baler_single_line_SLEBD_pattern_DB_read()
	
	print len(  shared_baler_block_list)
	print len (shared_SLEBD_block_list)
	print len (private_baler_block_list)
	print len (private_SLEBD_block_list)
	SLEBD_share_multi = []
	SLEBD_private_multi = []
	baler_share_multi = []
	baler_private_multi = []

	for block_name in SLEBD_DB:
		block = SLEBD_DB[block_name]
		start = block["start"]
		finish = block["finish"]
		single = 0
		if not start == finish:
			if block_name in shared_SLEBD_block_list:
				SLEBD_share_multi.append(block_name)
			if block_name in private_SLEBD_block_list:
				SLEBD_private_multi.append(block_name)
	for block_name in baler_DB:
		block = baler_DB[block_name]
		start = block["start"]
		finish = block["finish"]
		single = 0
		if not start == finish:
			if block_name in shared_baler_block_list:
				baler_share_multi.append(block_name)
			if block_name in private_baler_block_list:
				baler_private_multi.append(block_name)
	"""	
	for baler_block in baler_share_multi:	
		SLEBD_block_list = shared_baler_block_list[baler_block]
		baler_pattern = baler_DB[baler_block]
		baler_start = baler_pattern["start"][0][1]
		baler_finish = baler_pattern["finish"][0][1]
		print "baler"
		print baler_single_line_SLEBD_DB[str(baler_start)]
		print baler_single_line_SLEBD_DB[str(baler_finish)]
		print "SLEBD"
		for SLEBD_block in SLEBD_block_list:
			print SLEBD_block
			print 	SLEBD_DB[SLEBD_block]
		print "\n"
	"""	
	print len (SLEBD_share_multi)	
	print len (SLEBD_private_multi)	
	print len (baler_share_multi)	
	print len (baler_private_multi)	
	
	
def main(cmd_1, cmd_2 = ""):
	#result = global_APIs.global_folder_initializer(cmd_1)
#this one is only for single line test	
	#baler_single_line_block_DB_initializer(cmd_1)



###################################
#baler learning
	# this one is very necessary !!!!!
	#baler_single_line_SLEBD_type_pattern_gen(cmd_1)

	#multi_file_folder.folder_database_self_growing(cmd_1)
	#multi_file_folder.folder_analyzing (cmd_1)	

#SLEBD and baler compare
	result = two_db_compare (cmd_1, cmd_2)
	two_db_compare_result_analyze (result)
	#share_block_multi_analyze (result)


cmd_1 = sys.argv[1]
cmd_2 = sys.argv[2]
main(cmd_1, cmd_2)
