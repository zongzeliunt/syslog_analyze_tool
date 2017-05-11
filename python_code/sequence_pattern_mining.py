#!/usr/bin/python
import os
import operator
import re
import shutil
import time 
import timeframe_analyze
import report_APIs
import input_file_block_analyzer
import python_code.global_APIs as global_APIs
ignore_repeat_block = 1

#block report file preprocessing
#file_block_list_read
#multi_node_find_common_block_list
#multi_node_block_report_split
#generate_private_list_file
#generate_common_list_file
#find_folder_node_id_and_block_report
#multi_file_folder_sequence_learning_list_read
#################################################################
#{{{
def file_block_list_read(file_name):
#this can be moved to global_APIs
#{{{
	node_block_list	= []
	node_block_list_fl = open(file_name, "r")
	total_block_list = {}
	candidate_analyze_list = []
	previous_block = ""
	while True:
		line = node_block_list_fl.readline()
		if line == "":
			break
		line = line.split(" ")
		block_name = line[0]
		pattern = r'.*(block_[0-9]+).*$'	
		matchobj = re.match (pattern, block_name)
		if matchobj:
			block_name = matchobj.group(0)
		if ignore_repeat_block == 1 and block_name == previous_block:
			continue
	
		node_block_list.append(block_name)
		if not block_name in total_block_list:
			total_block_list[block_name] = 1
		else:
			total_block_list[block_name] = total_block_list[block_name] + 1
		previous_block = block_name
	for block in total_block_list:
		if total_block_list[block] > 1:
			candidate_analyze_list.append(block)
 
	node_block_list_fl.close()
	result = []
	result.append(candidate_analyze_list)
	result.append(node_block_list)
	return result
#}}}

def multi_node_find_common_block_list (folder_name):
#find common block from multiple nodes
#{{{
	block_occupy_list = {}
	block_file_list = find_folder_node_id_and_block_report(folder_name)

	node_num = len(block_file_list)
	for node_id in block_file_list:
		block_report_file = block_file_list[node_id]
		node_block_list	= file_block_list_read(block_report_file)[1]
		for block_name in node_block_list:
			if block_name in block_occupy_list:
				tmp = block_occupy_list[block_name]
				if not node_id in tmp:
					tmp.append (node_id)
					block_occupy_list[block_name] = tmp
			else:
				tmp = []
				tmp.append(node_id)
				block_occupy_list[block_name] = tmp


	common_block_list = []
	private_block_list = {}
	for block_name in block_occupy_list:
		if len(block_occupy_list[block_name]) == node_num:
			common_block_list.append(block_name)
		if len(block_occupy_list[block_name]) == 1:
			node_id = block_occupy_list[block_name][0]
			if not node_id in private_block_list:
				tmp = []
				tmp.append(block_name)
				private_block_list[node_id] = tmp
			else:
				tmp = private_block_list[node_id]
				tmp.append(block_name)
				private_block_list[node_id] = tmp
	tmp = []
	tmp.append(common_block_list)
	tmp.append(private_block_list)
	return tmp
#}}}

def multi_node_block_report_split (common_block_list, private_block_list, folder_name):
#find common block list from multiple nodes based on common_block_list
#I can also use it to extract block list which I am interested
#{{{
	block_file_list = find_folder_node_id_and_block_report(folder_name)
	common_block_list_report = {}
	private_block_list_report = {}
	for node_id in block_file_list:
		if not node_id in private_block_list:
			private_block_node_list = []
		else:
			private_block_node_list = private_block_list[node_id]
		block_report_file = block_file_list[node_id]
		node_block_list	= file_block_list_read(block_report_file)[1]	
		tmp_common = []
		tmp_private = []
		for block_name in node_block_list:
			if block_name in common_block_list:
				tmp_common.append(block_name)
			if block_name in private_block_node_list:
				tmp_private.append(block_name)
				
		common_block_list_report[node_id] = tmp_common
		private_block_list_report[node_id] = tmp_private

	generate_common_list_file(common_block_list_report, folder_name)
	generate_private_list_file(private_block_list_report, folder_name)

#}}}

def generate_private_list_file (private_block_list_report, folder_name):
#{{{
	file_folder_path = folder_name + "/private_block_report/"
	if not os.path.isdir(file_folder_path):
		os.mkdir(file_folder_path)	
	
	for node_id in private_block_list_report:
		fl_name = file_folder_path + node_id + ".txt"
		fl = open (fl_name, "w")
		for block in private_block_list_report[node_id]:	
			fl.write(block)
			fl.write("\n")
		fl.close()
#}}}

def generate_common_list_file (common_block_list_report, folder_name):
#{{{
	file_folder_path = folder_name + "/common_block_report/"
	if not os.path.isdir(file_folder_path):
		os.mkdir(file_folder_path)	
	
	for node_id in common_block_list_report:
		fl_name = file_folder_path + node_id + ".txt"
		fl = open (fl_name, "w")
		for block in common_block_list_report[node_id]:	
			fl.write(block)
			fl.write("\n")
		fl.close()
#}}}

def find_folder_node_id_and_block_report (folder_name):
#{{{
	file_list = global_APIs.get_folder_file_list(folder_name)
	#c0-0c0s0n2_single_file.txt_block_report.txt
	pattern = r'^([a-z0-9\-]+)_(.*)_block_report.txt$'
	block_file_list = {} 
	for file_name in file_list:
		real_file_name = global_APIs.get_real_file_name(file_name)
		matchobj = re.match(pattern, real_file_name)
		if matchobj:
			node_id = matchobj.group(1)
			block_file_list[node_id] = file_name
	return block_file_list	
#}}}

def multi_file_folder_sequence_learning_list_read(folder_name):
#{{{
	file_list = global_APIs.get_folder_file_list(folder_name)
	sequences = []
	for file_name in file_list:
		tmp = []
		fl = open (file_name, "r")
		for line in fl.readlines():
			line = line.replace ("\n", "") 
			tmp.append ([line])
		#here is very important!
		#the sequence list is [[Block_1], [Block_2]], not [Block_1, Block_2]
		#this is for future we need to analyze 	[[Block_1], [Block_2, Block_3]]. Block_2 and Block_3 happen in the same time.
		#this is really useless for our block analyze, but we need to support it for prefixspan	
		sequences.append(tmp)	
		fl.close()
	return sequences	
#}}}


#}}}


#matrix operations
#multi_file_sequence_prior_matrix_gen
#gen_prior_matrix_from_candidate_list
#gen_status_matrix_based_on_prior_matrix
#search_prior_matrix_for_conflict
#{{{
def multi_file_sequence_prior_matrix_gen (sequences):
#{{{
	#we don't have a candidate_analyze_list any more. if in the future any block happen time is less than threshold, we need to erase it from the matrix
	#done block name list contains all block names we need to ananlyze
	#can add block name threshold filter here
	prior_matrix = {}
	done_block_name_list = []
	for node_block_list in sequences:
		result = gen_prior_matrix_from_one_sequence(prior_matrix, done_block_name_list, node_block_list)
		prior_matrix = result[0]
		done_block_name_list = result[1]
	count = 0
	file_name = "tmp_report/prior_matrix_"
	file_name += str(count)
	count += 1	
	file_name += ".txt"
	fl = open (file_name, "w")	
	for block in prior_matrix:
		fl.write( block)
		fl.write("\n")
		fl.write (str(prior_matrix[block]))
		fl.write("\n")
	fl.close()
	
	tmp = []
	tmp.append(prior_matrix)
	tmp.append(done_block_name_list)
	return tmp
#}}}

def gen_prior_matrix_from_one_sequence (prior_matrix, done_block_name_list, node_block_list):
#already done, including happen_count and last block index
#very useful!
#{{{
	#reopen every block record
	for main_block in prior_matrix:
		main_block_sub_list = prior_matrix[main_block]
		for sub_block in done_block_name_list:
			if sub_block in main_block_sub_list:
				sub_block_record = main_block_sub_list[sub_block]
				sub_block_record["open"] = "no"
				main_block_sub_list[sub_block] = sub_block_record
			else:
				sub_block_record = {}
				sub_block_record["open"] = "no"
				sub_block_record["count"] = 0 
			
				main_block_sub_list[sub_block] = sub_block_record
		prior_matrix[main_block] = main_block_sub_list


	previous_block = ""
	for report_list_block in node_block_list:
		if len(report_list_block) == 1:
			report_list_block = report_list_block[0]
			#here we need special treatment for length != 1:
			#this is for my algorithm have same feature as prefixspan
			#not useful for block analyze
			#here should have an else!
		if not report_list_block in done_block_name_list:
			done_block_name_list.append(report_list_block)

		if not report_list_block in prior_matrix:
			tmp = {}
			tmp["happen_count"] = 1
			prior_matrix[report_list_block] = tmp
			#important! 
			#when initilize block as matrix main block, it will still be treated as sub block.
			#example: list 0,1,2,0,2,1,0,1,2
			#prior count [0, 0] will be 3, not 2
			#others will be correct.
			#prior count [0, 0] is useless this time, if want to use it, must sub 1. 
		else:
			#re open all sub blocks
			main_block_sub_list = prior_matrix[report_list_block]
			for sub_block in main_block_sub_list:
				if sub_block == "happen_count" or sub_block == "last_block":
					#special index
					continue
				sub_block_record = main_block_sub_list[sub_block]
				sub_block_record["open"] = "yes"
				main_block_sub_list[sub_block] = sub_block_record
			if ignore_repeat_block == 0 or not report_list_block == previous_block:
				tmp = prior_matrix[report_list_block]["happen_count"] + 1	
				prior_matrix[report_list_block]["happen_count"]	= tmp
					

		for main_block in prior_matrix:
			main_block_sub_list = prior_matrix[main_block]
			if not report_list_block in main_block_sub_list:
				tmp =  {}
				tmp["count"] = 1
				tmp["open"] = "no"
				main_block_sub_list[report_list_block] = tmp
			else:
				sub_block_record = main_block_sub_list[report_list_block]
				if sub_block_record["open"] == "yes":
					sub_block_record["count"] = sub_block_record["count"] + 1
					sub_block_record["open"] = "no"
					main_block_sub_list[report_list_block] = sub_block_record
		previous_block = report_list_block


	#now, previous_block is the last block, we can record it
	if previous_block in prior_matrix:	
		last_block_sub_list = prior_matrix[previous_block]
		last_block_sub_list["last_block"] = "yes"
		prior_matrix[previous_block] = last_block_sub_list
	tmp = []
	tmp.append(prior_matrix)
	tmp.append(done_block_name_list)
	return tmp
#}}}

def gen_status_matrix_based_on_prior_matrix (candidate_analyze_list, prior_matrix):
#{{{
	#one block can only have 4 status with others:
	#1) prior: B_1, B_2
	#2) after: B_2, B_1
	#3) equal: B_2, B_1, B_2 (B_2 -> B_1 = 1, B_1 -> B_2 = 1)
	#4) tangle: B_2, B_1, B_1, B_2
	total_status_matrix = {}
	for main_block in candidate_analyze_list:
		status_list = {}
		prior_list = []
		after_list = []
		equal_wrap_list = []
		equal_wrapped_list = []
		tangle_list = []
		for sub_block in candidate_analyze_list:
			if main_block == sub_block:
				continue
			forward_conflict = search_prior_matrix_for_conflict(main_block, sub_block, prior_matrix)
			backward_conflict = search_prior_matrix_for_conflict(sub_block, main_block, prior_matrix)
			if forward_conflict == 0 and backward_conflict == 1:
				#prior
				prior_list.append(sub_block)
			elif forward_conflict == 1 and backward_conflict == 0:
				#after
				after_list.append(sub_block)
			elif forward_conflict == 0 and backward_conflict == 0:
				#equal
				if prior_matrix[main_block]["happen_count"] >= prior_matrix[sub_block]["happen_count"]:
					#main_block is wrapping sub_block
					equal_wrap_list.append(sub_block)		
				else:
					#main_block been wrapped by sub_block
					equal_wrapped_list.append(sub_block)		
			elif forward_conflict == 1 and backward_conflict == 1:
				#tangle, or should we say it's real conflict
				tangle_list.append(sub_block)
		status_list["prior"] = prior_list	
		status_list["after"] = after_list	
		status_list["equal_wrap"] = equal_wrap_list	
		status_list["equal_wrapped"] = equal_wrapped_list	
		status_list["tangle"] = tangle_list
		total_status_matrix[main_block] = status_list	

	file_name = "status_matrix.txt"
	fl = open (file_name, "w")	
	for block in total_status_matrix:
		fl.write( block)
		fl.write("\n")
		fl.write (str(total_status_matrix[block]))
		fl.write("\n")
	fl.close()

	return total_status_matrix	
#}}}

def search_prior_matrix_for_conflict(main_block, candidate_block, prior_matrix):
#{{{
	threshold_tolerance = 1.0
	#threshold is here
	#we can use this threshold to tolerate slight fault in training set

	#only a patch, but it can still self control. this is the last defence line
	if main_block not in prior_matrix or candidate_block not in prior_matrix:
		return 1


	main_block_sub_list = prior_matrix[main_block]
	candidate_block_sub_list = prior_matrix[candidate_block]
	candidate_block_happen_time = candidate_block_sub_list["happen_count"]
	main_block_happen_time = main_block_sub_list["happen_count"]
	if candidate_block in main_block_sub_list:
		main_block_prior_candidate_block_count = main_block_sub_list[candidate_block]["count"]
	else: 
		return 1
	if main_block in candidate_block_sub_list:
		candidate_block_prior_main_block_count = candidate_block_sub_list[main_block]["count"]
	else: 
		return 1
	
	if main_block_happen_time <= candidate_block_happen_time:
		valid_happen_time = main_block_happen_time
	else:
		valid_happen_time = candidate_block_happen_time
	if valid_happen_time == 1:
		valid_happen_time = main_block_happen_time
 
	if main_block_prior_candidate_block_count >= valid_happen_time * threshold_tolerance:
		#main and candidate is following a sequence
		#we don't need to care about candidate 
		return 0

	#candidate_block_prior_main_block_count >= (valid_happen_time - 1) * threshold_tolerance:
	return 1
#}}}

#only preserver
def gen_prior_matrix_from_candidate_list_1 (candidate_analyze_list, node_block_list):
#already done, including happen_count and last block index
#very useful!
#{{{
	prior_matrix = {}
	previous_block = ""
	for report_list_block in node_block_list:
		if not report_list_block in candidate_analyze_list:
			previous_block = report_list_block
			#if this block not in analyze list, ignore it 
			continue
		if not report_list_block in prior_matrix:
			tmp = {}
			tmp["happen_count"] = 1
			prior_matrix[report_list_block] = tmp
			#important! 
			#when initilize block as matrix main block, it will still be treated as sub block.
			#example: list 0,1,2,0,2,1,0,1,2
			#prior count [0, 0] will be 3, not 2
			#others will be correct.
			#prior count [0, 0] is useless this time, if want to use it, must sub 1. 
		else:
			#re open all sub blocks
			main_block_sub_list = prior_matrix[report_list_block]
			for sub_block in main_block_sub_list:
				if sub_block == "happen_count" or sub_block == "last_block":
					#special index
					continue
				sub_block_record = main_block_sub_list[sub_block]
				sub_block_record["open"] = "yes"
				main_block_sub_list[sub_block] = sub_block_record
			if ignore_repeat_block == 0 or not report_list_block == previous_block:
				tmp = prior_matrix[report_list_block]["happen_count"] + 1	
				prior_matrix[report_list_block]["happen_count"]	= tmp
					

		for main_block in prior_matrix:
			main_block_sub_list = prior_matrix[main_block]
			if not report_list_block in main_block_sub_list:
				tmp =  {}
				tmp["count"] = 1
				tmp["open"] = "no"
				main_block_sub_list[report_list_block] = tmp
			else:
				sub_block_record = main_block_sub_list[report_list_block]
				if sub_block_record["open"] == "yes":
					sub_block_record["count"] = sub_block_record["count"] + 1
					sub_block_record["open"] = "no"
					main_block_sub_list[report_list_block] = sub_block_record
		previous_block = report_list_block

	#frequent block is supervised in candidate_analyze_list, don't need to do any special treatment here

	#now, previous_block is the last block, we can record it
	if previous_block in prior_matrix:	
		last_block_sub_list = prior_matrix[previous_block]
		last_block_sub_list["last_block"] = "yes"
		prior_matrix[previous_block] = last_block_sub_list


	file_name = "tmp_report/prior_matrix.txt"
	fl = open (file_name, "w")	
	for block in prior_matrix:
		fl.write( block)
		fl.write("\n")
		fl.write (str(prior_matrix[block]))
		fl.write("\n")
	fl.close()
	

	return prior_matrix
#}}}
#}}}

#path find
#generate_critical_path
#topology_path_find
#find_critical_path_candidate_list_from_status_matrix
#find_sequential_pattern_from_candidate_list
#find_sub_path

#{{{
def generate_critical_path (done_block_name_list, prior_matrix):
#{{{
	status_matrix = gen_status_matrix_based_on_prior_matrix(done_block_name_list, prior_matrix)
	
	#critical_path
	#could be nothing, don't be surprised
	critical_path_candidate_list = find_critical_path_candidate_list_from_status_matrix(done_block_name_list, status_matrix)
	critical_path = find_sequential_pattern_from_candidate_list(critical_path_candidate_list, prior_matrix)
	print "critical_path!"
	print critical_path
	left_candidate_list = find_left_candidate_list_from_candidate_list_with_critical_path(critical_path, done_block_name_list)
	return left_candidate_list
#}}}

def find_left_candidate_list_from_candidate_list_with_critical_path(critical_path, candidate_analyze_list):
	left_list = []
	for block in candidate_analyze_list:
		if not block in critical_path:
			left_list.append(block)
	return left_list

def find_critical_path_candidate_list_from_status_matrix (candidate_analyze_list, status_matrix):
#{{{
	critical_path_candidate_block_list = []
	for main_block in status_matrix:
		if len(status_matrix[main_block]["tangle"]) == 0:
			#only no tangle can be added into critical path
			critical_path_candidate_block_list.append(main_block)
	return critical_path_candidate_block_list
#}}}


def topology_path_find (done_block_name_list, prior_matrix):
	status_matrix = gen_status_matrix_based_on_prior_matrix(done_block_name_list, prior_matrix)
	
	sub_path_list = find_sub_path (done_block_name_list, status_matrix, prior_matrix)
	
	print len(sub_path_list)
	return sub_path_list	

	"""
	total_found_sub_path_list = []
	previous_sub_path_list = []
	for i in range (0, 5):
		print "round " + str(i)
		tmp_list = []
		for tangle_index in range( i * 10, len(done_block_name_list) ):
			tmp_list.append(done_block_name_list[tangle_index])
		for tangle_index in range(0, i * 10):
			tmp_list.append(done_block_name_list[tangle_index])
		


		sub_path_list = find_sub_path (tmp_list, status_matrix, prior_matrix)
		#print tmp_list
		#print len (sub_path_list)
		#sub_path_list = block_path_list_name_reorder(sub_path_list)
		#sequence_pattern_store(sub_path_list, str(i))
		#print len(sub_path_list)
		if not previous_sub_path_list == []:
			two_sub_list_compare (sub_path_list , previous_sub_path_list)

		print len(sub_path_list)
		previous_sub_path_list = sub_path_list
		total_found_sub_path_list.append(sub_path_list)
	return total_found_sub_path_list
	"""

def sequence_pattern_store (sequence_list, prefix = "" ):
	file_name = "tmp_report/sub_pattern"
	if not prefix == "":
		file_name += "_" + prefix
	file_name += ".txt"
	fl = open (file_name, "w")
	for pattern in sequence_list:
		tmp = ""
		for block in pattern:
			tmp += str(block)
			tmp += " "
		fl.write(tmp)
		fl.write("\n")
	fl.close()

def find_sequential_pattern_from_candidate_list (candidate_list, prior_matrix):
#{{{
	#don't know if sorting is necessary
	growing_pattern = []
	for main_block in candidate_list:
		if growing_pattern == []:
			growing_pattern.append(main_block)
		else:
			insert_position = search_sub_block_insert_into_growing_pattern_position(growing_pattern, main_block, prior_matrix)
			if not insert_position == -1:
				growing_pattern.insert(insert_position, main_block)
	return growing_pattern	
#}}}

def find_sub_path (sorted_left_list, status_matrix, prior_matrix):
#{{
	growing_list = []
	done_block_list = []
	for main_list_index in range (0, len(sorted_left_list)):
		main_block = sorted_left_list[main_list_index]
		done_block_list.append(main_block)
		#print "detecting ============================================"
		#print main_block
		#print main_list_index
		main_block_tangle_list = status_matrix[main_block]["tangle"]
		if main_list_index == 0:
			tmp = []
			tmp.append(main_block)
			growing_list.append(tmp)
			for tangle_block in main_block_tangle_list:
				if not tangle_block in sorted_left_list:
					continue
				tmp = []
				tmp.append(tangle_block)
				growing_list.append(tmp)
		else:
			inserted = 0
			delete_list = []
			for growing_list_index in range(0, len(growing_list)):
				growing_pattern = growing_list[growing_list_index]
				if main_block in growing_pattern:
					inserted = 1
					continue
				#insert_pos = search_sub_block_insert_into_growing_pattern_position (growing_pattern, main_block, prior_matrix)
				insert_pos = search_sub_block_insert_into_growing_pattern_position_1 (growing_pattern, main_block, status_matrix)
				if not insert_pos == -1:
					inserted = 1
					delete_list.append(growing_list_index)
					new_list = list(growing_pattern)
					new_list.insert(insert_pos, main_block)
					if not new_list in growing_list:
						growing_list.append(new_list)
					for tangle_block in main_block_tangle_list:
						#branch
						if tangle_block in done_block_list:
							continue
						if not tangle_block in sorted_left_list:
							continue
						#insert_pos = search_sub_block_insert_into_growing_pattern_position (growing_pattern, tangle_block, prior_matrix)
						insert_pos = search_sub_block_insert_into_growing_pattern_position_1 (growing_pattern, tangle_block, status_matrix)
						if not insert_pos == -1:
							new_list = list(growing_pattern)
							new_list.insert(insert_pos, tangle_block)
							if not new_list in growing_list:
								growing_list.append(new_list)
			if inserted == 0:
				tmp = []
				tmp.append(main_block)
				growing_list.append(tmp)
			#delete
			new_growing_list = []
			for growing_pattern_index in range (0, len(growing_list)):
				if growing_pattern_index not in delete_list:
					new_growing_list.append(growing_list[growing_pattern_index])

			growing_list = list(new_growing_list)	
		#print growing_list
	return growing_list
#}}}

def search_sub_block_insert_into_growing_pattern_position_1 (growing_pattern, insert_block, status_matrix):
	insert_position = 0 
	possible_position = 0
	forward_switch = 0
	for i in range (0, len(growing_pattern)):
		list_block = growing_pattern[i]
		if insert_block in status_matrix[list_block]["tangle"] or list_block in status_matrix[insert_block]["tangle"]:
			return -1
		if forward_switch == 0:	
			if insert_block in status_matrix[list_block]["prior"]:
				insert_position = i + 1
				#insert_block is after list_block, do nothing and push position forward
			elif insert_block in status_matrix[list_block]["after"]:
				insert_position = i
				forward_switch = 1
				
			elif insert_block in status_matrix[list_block]["equal_wrap"]: 
				#insert_block is wrapped by list_block
				insert_position = i + 1
			
			elif insert_block in status_matrix[list_block]["equal_wrapped"]:
				#list_block is wrapped by insert_block	
				insert_position = i
				forward_switch = 1

		if forward_switch == 1:
			if list_block in status_matrix[insert_block]["after"]:
				if insert_position == -1:
					insert_position = i
			elif list_block in status_matrix[insert_block]["equal_wrap"]: 
				#insert_block is wrapped by list_block
				if insert_position == -1:
					insert_position = i
			
			elif list_block in status_matrix[insert_block]["equal_wrapped"]:
				#list_block is wrapped by insert_block	
				if insert_position == -1:
					insert_position = i + 1
	
	return insert_position




def search_sub_block_insert_into_growing_pattern_position(growing_pattern, sub_block, prior_matrix):
#could be done
#This one is useless, just keep and do verification
#I need to rewrite a new one, not searching prior_matrix but status_matrix
#{{{
	insert_position = -1
	possible_position = 0
	forward_switch = 0
	fail = 0
	#forward_switch == 0 means compare (block_in_growing_pattern, sub_block)
	#forward_switch == 1 means compare (sub_block, block_in_growing_pattern)
	for i in range (0, len(growing_pattern)):
		block = growing_pattern[i]
		if forward_switch == 0:	
			conflict = search_prior_matrix_for_conflict(block, sub_block, prior_matrix)
			if conflict == 1:
				#here must have a threshold tolerence feature! not every conflict can't be tolerated, maybe I must change search matrix for conflict
				forward_switch = 1 
				possible_position = i
		if forward_switch == 1:
			#switch = 1
			#if forward_switch just switched, this will judge immeditaly, 
			conflict = search_prior_matrix_for_conflict(sub_block, block, prior_matrix)
			if conflict == 1:
				fail = 1
				break
	if forward_switch == 0:
		#search continues to the end of growing_pattern
		#insert_position is the end of growing_pattern
		insert_position = len(growing_pattern)
	elif forward_switch == 1 and fail == 0:
		#insert_position is inside the growing_pattern
		insert_position = possible_position
	#else:
		#insert_position is -1
	return insert_position
#}}}

#}}}

#testing and verify
def block_report_folder_remove_done_critical_path (folder_name, left_candidate_list):
	file_list = global_APIs.get_folder_file_list(folder_name)
	sequences = []
	for file_name in file_list:
		tmp = []
		fl = open (file_name, "r")
		real_file_name = global_APIs.get_real_file_name(file_name)
		output_file_name = "left_block_file_folder/" + real_file_name
		output_fl = open (output_file_name, "w")
		for line in fl.readlines():
			line = line.replace ("\n", "") 
			if line in left_candidate_list:
				output_fl.write(line + "\n")
				
		sequences.append(tmp)	
		fl.close()
		output_fl.close()
	return sequences	
	


#{{{
def block_path_list_name_reorder (path_list):
	pattern = r'block_([0-9]+)$'
	total_path_list = []
	total_path_icon_list = {}
	for path in path_list:
		tmp_1_list = []
		for block in path:
			matchobj = re.match (pattern, block)
			if matchobj:
				block_num = matchobj.group(1)
			tmp = [block, block_num]
			tmp_1_list.append(tmp)
			
		sorted_tmp_1_list = sorted( tmp_1_list, key=operator.itemgetter(1), reverse=False)
		tmp_2_list = []
		tmp_2_icon = ""
		for block in sorted_tmp_1_list:
			tmp_2_list.append(block[0])
			tmp_2_icon += block[0]
		if tmp_2_list not in total_path_list:
			total_path_list.append(tmp_2_list)
		if not tmp_2_icon in total_path_icon_list:
			tmp = []
			tmp.append(path)
			total_path_icon_list[tmp_2_icon] = tmp
		else:
			tmp = total_path_icon_list[tmp_2_icon]
			tmp.append(path)
			total_path_icon_list[tmp_2_icon] = tmp
	#for icon in total_path_icon_list:
	#	if len(total_path_icon_list[icon]) > 1:
	#		print icon
	#		print 	total_path_icon_list[icon]
	
	return total_path_list


def two_sub_list_compare (sub_path_list_0, sub_path_list_1):
	common_sub_list = []
	list_0_private_list = []
	list_1_private_list = []
	for path in sub_path_list_0:
		if path in sub_path_list_1:
			common_sub_list.append(path)
		else: 
			list_0_private_list.append(path)
	for path in sub_path_list_1:
		if not path in common_sub_list:
			list_1_private_list.append(path)
	print "list 0 private"	
	for path in list_0_private_list:
		print path
	print "list 1 private"	
	for path in list_1_private_list:
		print path



def sub_path_list_verify_2(sub_path_list, node_block_list):
	#test path with existing record list
	for sub_path in sub_path_list:
		#print "testing"
		#print sub_path
		block_index = 0
		block_list_index = 0
		match_at_least_once = 0
		for block in node_block_list:
			path_block = sub_path[block_index]
			if block == [path_block]:
				#this is important, must be [path_block]
				match_at_least_once = 1 
				block_index += 1
			if block_index == len(sub_path):
				block_index = 0
			block_list_index += 1
		if not block_index == 0 or match_at_least_once == 0:
			# match at least once == 0: did not match
			#block_index == 0: match but not reach the last
			print "warning"
			print sub_path

def sub_path_list_verify_1(sub_path_list, sorted_left_list, prior_matrix):
	#try insert block into path 
	for sub_path in sub_path_list:
		warning_list = []
		warning = 0
		for main_list_index in range (0, len(sorted_left_list)):
			block = sorted_left_list[main_list_index][0]
			if block in sub_path:
 				continue
			insert_pos = search_sub_block_insert_into_growing_pattern_position (sub_path, block, prior_matrix)
			if not insert_pos == -1:
				warning = 1
				warning_list.append(block)
		if warning == 1:
			print "warning!!!!!!!!!"
			print sub_path
			print warning_list
#}}}


#################################################################
#above are useful


#2017 new block list analyze features:

#{{{
def single_node_block_happen_time_summary (node_block_list):
#this is a general function, not just for any sepcify node
#maybe I can move it to global_APIs
#{{{
	block_happen_time_list = {}
	happen_time_list = {}
	previous_block = ""
	for block in node_block_list:
		
		if block in block_happen_time_list:
			if ignore_repeat_block == 0 or not block == previous_block: 
				tmp = block_happen_time_list[block]
				tmp = tmp + 1
				block_happen_time_list[block] = tmp 
		else:
			block_happen_time_list[block] = 1
		previous_block = block
	
	for block in block_happen_time_list:
		happen_time = block_happen_time_list[block]
		if happen_time in happen_time_list:
			tmp = happen_time_list[happen_time]
			tmp.append(block)
			happen_time_list[happen_time] = tmp
		else:
			tmp = []
			tmp.append(block)
			happen_time_list[happen_time] = tmp
	return happen_time_list
#}}}

def common_block_happen_time_summary (common_block_list_report):
	node_block_list = common_block_list_report["c0-0c0s0n1"]
	happen_time_list = single_node_block_happen_time_summary(node_block_list)

	candidate_analyze_list = []
	candidate_happen_time = 0		
	longest_list_num = 0
	for time in happen_time_list:
		#here, the longest time is 4
		if len(happen_time_list[time]) > longest_list_num:
			longest_list_num = len(happen_time_list[time])
			candidate_analyze_list = happen_time_list[time]
			candidate_happen_time = time
	print candidate_happen_time
	print candidate_analyze_list	
	#ATTENTION! this is very important!!!!!!!
	#this candidate_analyze_list can be anything, not just same happen time list
	#don't need to worry candidate_happen_time, it's inside the prior matrix
	#in fact, this is not just finding critical_path, it's finding all sequential pattern
	#if want to find all sequential pattern, I need to make it looping
	#this critical path mining's entrance should ONLY be a node_block_list, candidate_analyze_list can be block which is interested, or all the blocks in node_block_list, so when looping, I should modify the node_block_list (remove already mined blocks from node_block_list)
	path = get_critical_path_from_candidate_analyze_list (candidate_analyze_list, node_block_list)
	print path

def get_critical_path_from_candidate_analyze_list (candidate_analyze_list, node_block_list):

	candidate_block_length = len(candidate_analyze_list)
	prior_matrix = gen_prior_matrix_from_candidate_list(candidate_analyze_list, node_block_list)



	critical_path = new_discover_sequential_pattern_from_prior_matrix(candidate_analyze_list, prior_matrix, node_block_list)
	


	#conflict block B_75/B_76, B_107/B_109
	#tangled sequence: 1) 109, 107, 110; 2) 107, 110, 109; 3) 107, 109, 110

	#valid_prior_count_list = find_valid_prior_count_list_from_prior_matrix (prior_matrix)
	#summary_critial_path (prior_matrix, valid_prior_count_list)	
	return critical_path





def new_discover_sequential_pattern_from_prior_matrix(candidate_analyze_list, prior_matrix, node_block_list):
#fourth version
	#here node_block_list is just for verification, nothing more useful
	candidate_analyze_list_bak = []
	#just copy a backup, don't know when we can use it
	for block in candidate_analyze_list:
		candidate_analyze_list_bak.append(block)
	status_matrix = gen_status_matrix_based_on_prior_matrix(candidate_analyze_list, prior_matrix)
	
	#critical_path
	#could be nothing, don't be surprised
	critical_path_candidate_list = find_critical_path_candidate_list_from_status_matrix(candidate_analyze_list, status_matrix)
	critical_path = find_sequential_pattern_from_candidate_list(critical_path_candidate_list, prior_matrix)
	#print "critical_path"
	#print critical_path

	left_candidate_list = find_left_candidate_list_from_candidate_list_with_critical_path(critical_path, candidate_analyze_list)
	#print "left_candidate"
	#print left_candidate_list
	
	tangle_block_count_list = []
	for block in status_matrix:
		if block in left_candidate_list:
			tmp = [block, len(status_matrix[block]["tangle"])]
			tangle_block_count_list.append(tmp)
	
	sorted_left_list = sorted( tangle_block_count_list, key=operator.itemgetter(1), reverse=True)
	#sorted_left_list = sorted( tangle_block_count_list, key=operator.itemgetter(1), reverse=False)
	sub_path_list = find_sub_path (sorted_left_list, status_matrix, prior_matrix)

	for i in range (0, 5):
		tmp_list = []
		for tangle_index in range( i, len(tangle_block_count_list) ):
			tmp_list.append(tangle_block_count_list[tangle_index])
		for tangle_index in range(0, i):
			tmp_list.append(tangle_block_count_list[tangle_index])
		sub_path_list = find_sub_path (tmp_list, status_matrix, prior_matrix)
		print "round " + str(i)
		print tmp_list
		print len(sub_path_list)
		#print sub_path_list
		sub_path_list = block_path_list_name_reorder(sub_path_list)
		print len(sub_path_list)
	

	#sub_path_list_0 = []
	#fl = open ("sub_pattern.txt", "r")
	#while True:
	#	line = fl.readline()
	#	if line == "":
	#		break
	#	tmp = []
	#	line = line.split(" ")
	#	for i in range (0, len(line) - 1):
	#		block = line[i]
	#		tmp.append(block)
	#	sub_path_list_0.append(tmp)
	#fl.close()
	#sub_path_list_1 = []
	#fl = open ("sub_pattern_1.txt", "r")
	#while True:
	#	line = fl.readline()
	#	if line == "":
	#		break
	#	tmp = []
	#	line = line.split(" ")
	#	for i in range (0, len(line) - 1):
	#		block = line[i]
	#		tmp.append(block)
	#	sub_path_list_1.append(tmp)
	#fl.close()
	#sub_path_list_0 = block_path_list_name_reorder(sub_path_list_0)
	#sub_path_list_1 = block_path_list_name_reorder(sub_path_list_1)

	
	#print "verify 1"
	#sub_path_list_verify_1(sub_path_list, sorted_left_list, prior_matrix)
	#print "verify 2"
	#sub_path_list_verify_2(sub_path_list, sorted_left_list, prior_matrix, node_block_list)
	#two_sub_list_compare (sub_path_list_0, sub_path_list_1)
	
	return critical_path

	



#}}}








