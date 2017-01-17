#!/usr/bin/python
import global_APIs
import preliminary_block_list_gen
import block_merger
import block_database_opt
import sys
import os

#this is analyzing blocks from input file

#
#is_block_start
#is_block_finish
#block_analyze
#remove_multi_block
#block_nest_eliminate
#{{{
def search_correspond_pattern_from_database (pattern, block_database, mode):
	highest_ratio = 0
	highest_pattern = []
	same_ratio_pattern_list = []
	for block_name in block_database:
		block_pattern = block_database[block_name]
		if mode == "start":
			candidate = block_pattern["start"]
		if mode == "finish":
			candidate = block_pattern["finish"]
		
		ratio = global_APIs.calculate_match_ratio(pattern, candidate)

		if ratio > preliminary_block_list_gen.line_pattern_match_threshold and ratio > highest_ratio:
			highest_ratio = ratio
			highest_pattern = []
			highest_pattern.append(block_name) 
			same_ratio_pattern_list = []
			same_ratio_pattern_list.append(block_name)
		elif ratio > preliminary_block_list_gen.line_pattern_match_threshold and  ratio == highest_ratio:
			same_ratio_pattern_list.append(block_name)
			
		if highest_ratio > 0.99:
			break

	if len(same_ratio_pattern_list) > 1:
		return same_ratio_pattern_list


	return highest_pattern

def is_block_start (pattern, block_database):
	return search_correspond_pattern_from_database(pattern, block_database, "start")

def is_block_finish (pattern, block_database):
	return search_correspond_pattern_from_database(pattern, block_database, "finish")


def block_analyze (input_file, block_database, global_multi_list, dump_error_file = 0):
	block_list = database_analyze_block(input_file, block_database, dump_error_file)
	block_list = block_nest_eliminate (block_list)	

	if not global_multi_list == {}:
		block_list = remove_multi_block (block_list , global_multi_list )
	
	return block_list


def database_analyze_block(input_file, block_database, dump_error_file):
	block_list = []
	stock = []
	start_line_num = 0
	finish_line_num = 0
	line_counter = 1
	fl = open (input_file, "r")
	error_list = {}
	while True:
		line = fl.readline()
		if not line:	
			break
		line_message = global_APIs.get_line_message(line)
		pattern = global_APIs.gen_line_pattern(line_message)
		start_block_name_list = is_block_start (pattern,block_database)	
		finish_block_name_list = is_block_finish (pattern,block_database)
		
		if len(start_block_name_list) > 0:
			start_line_num = line_counter
			block_record = []
			block_record.append(start_block_name_list)
			block_record.append(line_counter)
		 	stock.append(block_record)
		
		if len(finish_block_name_list) > 0:
			finish_block_name = ""
			same_as_previous = 0
			if not len(block_list) == 0:
				previous_block = block_list[len(block_list) - 1]
				previous_block_name = previous_block[0]
				for i in range(0, len(finish_block_name_list)):
					finish_block_name_tmp = finish_block_name_list[i]
					if previous_block_name == finish_block_name_tmp:
						same_as_previous = 1
						finish_block_name = finish_block_name_tmp

			if not len(stock) == 0:
				start_block_record = stock.pop()
				start_block_name_list = start_block_record[0]
				start_line_num = start_block_record[1]
				match = 0
				for i in range (0, len(start_block_name_list)):
					start_block_name_tmp = start_block_name_list[i]
					for j in range (0, len(finish_block_name_list)):
						finish_block_name_tmp = finish_block_name_list[j]
						if finish_block_name_tmp == start_block_name_tmp:
							match = 1
							finish_block_name = finish_block_name_tmp
							break
				if match == 0:
#don't match
					if same_as_previous == 1:
						#ARES
						#nesting block have multiple line of finish
						#merge this block finish line with previous block
						previous_block[2] = str(line_counter)
						block_list[len(block_list) - 1] = previous_block
						#the poped record must be pushed back to stock  
						stock.append(start_block_record)
					else:
						for i in range (0, len(start_block_name_list)):
							error_list[start_block_name_list[i]] = ""
						for i in range (0, len(finish_block_name_list)):
							error_list[finish_block_name_list[i]] = ""
						print "ERROR report"
						print "=========================================================="
						print "line num"
						print line_counter
						print "start block_name"
						print start_block_name_list
						print "finish block_name"
						print finish_block_name_list
						print "start_line_num"
						print start_line_num
						print "=========================================================="
						print ""
				else:
#match
					finish_line_num = line_counter
					block_report = []

					# all element of block_report must by string type, for future merge	
					block_report.append(finish_block_name)
					block_report.append(str(start_line_num))
					block_report.append(str(finish_line_num))
					block_list.append(block_report)	
			else:
				#stock is empty
				if same_as_previous == 1:
					#merge this block finish line with previous block
					previous_block[2] = str(line_counter)
					block_list[len(block_list) - 1] = previous_block
				else:
					print "find finish line but no start line"
					print line_counter
					print finish_block_name_list
					for i in range (0, len(finish_block_name_list)):
						error_list[finish_block_name_list[i]] = ""





		line_counter = line_counter + 1
	if not len(stock) == 0:
		for i in range(0, len(stock)):
			left_list = stock[i][0]
			left_line_num = stock[i][1]
			print "left in stock"
			print left_list
			print left_line_num
			for left_block in left_list:
				error_list[left_block] = ""


	fl.close()
	if dump_error_file == 1:
		error_fl = open ("error_report.txt", "w")	
		for tmp in error_list:
			error_fl.write(tmp)
			error_fl.write("\n")
		
		error_fl.close()
	return block_list

def remove_multi_block (block_list , global_multi_list ):
	new_block_list = []
	recording = 0
	finish = ""
	global_multi_name = ""
	global_multi_start_line = ""
	if len(block_list) == 0:
		return []


	for i in range (0, len(block_list) - 1):
		block = block_list[i]
		block_name = block[0]
		block_start_line = block[1]
		block_finish_line = block[2]
		if recording == 0:
			for multi_block_name in global_multi_list:
				multi_block = global_multi_list[multi_block_name]
				multi_start = multi_block[0]
				multi_finish = multi_block[1]
				if block_name == multi_start:
					recording = 1
					finish = multi_finish
					global_multi_name = multi_block_name
					global_multi_start_line = block_start_line
					break
			if finish == "":
				new_block_list.append(block)
					
		else:
			if block_name == finish:
				next_block = block_list[i+1]
				next_block_name = next_block[0]
				if not next_block_name == finish:
					#multi block is {0, 8}
					#0 2 3 8 8 9
					#this block is 8, next block is 9 
					#so this block is the last one of multi block
					tmp = []
					tmp.append (global_multi_name)	
					tmp.append (global_multi_start_line)	
					tmp.append (block_finish_line)
					new_block_list.append(tmp)
					recording = 0
					finish = ""
					global_multi_name = ""
					global_multi_start_line = ""
			else:
				tmp = []
				tmp.append (global_multi_name)	
				tmp.append (global_multi_start_line)	
				tmp.append (block_finish_line)
				new_block_list.append(tmp)
				recording = 0
				finish = ""
				global_multi_name = ""
				global_multi_start_line = ""
					
	block = block_list[len(block_list) - 1]
	block_name = block[0]
	block_start_line = block[1]
	block_finish_line = block[2]
	if recording == 0:
		new_block_list.append(block)
		
	else:
		tmp = []
		tmp.append (global_multi_name)	
		tmp.append (global_multi_start_line)	
		tmp.append (block_finish_line)
		new_block_list.append(tmp)

		i = i + 1
	return new_block_list

def block_nest_eliminate (block_list):
#32 370 371
#22 369 372
#block_104 16 16
#block_102 15 19
	merge = 1
	while merge == 1:
		merge = 0
		i = 0
		while i < len(block_list) - 1:
			block = block_list[i]
			next_block = block_list[i+1]
			start_line = int(block[1])
			finish_line = int(block[2])
			next_start_line = int(next_block[1])
			next_finish_line = int(next_block[2])

			if start_line > next_start_line and finish_line < next_finish_line:
				#ARES
				merge = 1 
				del (block_list[i])
			else:
				i = i + 1

	return block_list
#}}}

#======================================================
#main function


def input_file_block_analyze (input_file, dump_error_file = 0):
	file_mode =  global_APIs.get_file_mode (input_file)
	have_database =  global_APIs.test_have_database(file_mode)
	block_database = block_database_opt.block_database_read(file_mode, str(have_database))
	global_multi_list = block_database_opt.multi_database_read(file_mode, str(have_database))

	block_list = block_analyze(input_file, block_database, global_multi_list, dump_error_file)
	return block_list

def create_exist_block_tmp_file (input_file, block_list):
	tmp_file = global_APIs.get_real_file_name(input_file)
	tmp_file += "_database_analyze_tmp_file.txt"
	fl = open (input_file, "r")
	tmp_fl = open (tmp_file, "w")
	line_counter = 0
	block_list_count = 0
	while True:
		line = fl.readline()
		line_counter = line_counter + 1
		if not line:	
			break
		in_block = 0
		correspond_block = ""
		block = block_list[block_list_count]
		start_line_num = block[1]
		finish_line_num = block[2]
		if line_counter >= int(start_line_num) and line_counter <= int(finish_line_num):
			in_block = 1
			correspond_block = block


		if in_block == 0:
			tmp_fl.write(line)
		else:
			finish_line_num = correspond_block[2]
			while line_counter < int(finish_line_num):
				line = fl.readline()
				line_counter = line_counter + 1
			tmp_fl.write(correspond_block[0])
			tmp_fl.write("\n")

			if not block_list_count == len(block_list) - 1: 
				block_list_count = block_list_count + 1
	fl.close()
	tmp_fl.close()
	return tmp_file



