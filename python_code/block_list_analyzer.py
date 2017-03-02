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
#2017 new block list analyze features:

#{{{
def find_folder_node_id_and_block_report (folder_name):
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

def multi_file_find_critical_path (folder_name):
#first version, just showing an example
#{{{
	total_critical_path_list = {}
	file_list = global_APIs.get_folder_file_list(folder_name)
	for file_name in file_list:
		real_file_name = global_APIs.get_real_file_name(file_name)
		if real_file_name == "c0-0c0s2n2.txt":
			continue
		result = file_block_list_read(file_name)
		candidate_analyze_list = result[0] 
		node_block_list = result[1] 

		critical_path = get_critical_path_from_candidate_analyze_list (candidate_analyze_list, node_block_list)
		total_critical_path_list[real_file_name] = critical_path
	
	block_happen_summary = {}
	for file_name in total_critical_path_list:
		sub_list = total_critical_path_list[file_name]
		for block in sub_list:
			if block not in block_happen_summary:
				tmp = []
				tmp.append(file_name)
				block_happen_summary[block]=tmp
			else:
				tmp = block_happen_summary[block]
				tmp.append(file_name)
				block_happen_summary[block]=tmp
	total_critical_block_list = []
	for block in block_happen_summary:
		if len(block_happen_summary[block]) == len(total_critical_path_list):	
			total_critical_block_list.append(block)			
	#re-orgnize
	reorgnized_critical_path = []	
	file_name = "c0-0c0s0n1.txt"
	sub_list = total_critical_path_list[file_name]
	for block in sub_list:
		if block in total_critical_block_list:
			reorgnized_critical_path.append(block)

	print reorgnized_critical_path

	#generate_example_file
	block_report_file = "block_report/c0-0c0s0n1_single_file.txt_block_report.txt"
	message_file = "single_file_test/single_file/c0-0c0s0n1_single_file.txt"
	example_file = "critical_path_example.txt"
	message_file_line_count = 1
	critical_path_count = 0
	report_fl = open(block_report_file, "r")
	message_fl = open(message_file, "r")
	example_fl = open(example_file, "w")
	while True:
		if critical_path_count == len(reorgnized_critical_path):
			break
		critical_block = reorgnized_critical_path[critical_path_count]
		example_fl.write(critical_block + "\n")
		block_name = ""
		while not block_name  == critical_block:
			line = report_fl.readline()
			line=line.split()
			block_name = line[0] 
			start_line = int(line[1]) 
			finish_line = int(line[2]) 
		
		while not message_file_line_count == start_line:
			line=message_fl.readline()
			message_file_line_count += 1
		while message_file_line_count <= finish_line:
			line=message_fl.readline()
			message_file_line_count += 1
			example_fl.write(line)
		example_fl.write("\n")	
		

		critical_path_count += 1
		
	report_fl.close() 
	message_fl.close() 
	example_fl.close() 

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

def multi_node_find_interested_block_report (interested_block_list, folder_name):
#find common block list from multiple nodes based on common_block_list
#I can also use it to extract block list which I am interested
#{{{
	block_file_list = find_folder_node_id_and_block_report(folder_name)
	common_block_list_report = {}	
	for node_id in block_file_list:
		block_report_file = block_file_list[node_id]
		node_block_list	= file_block_list_read(block_report_file)[1]	
		tmp = []
		for block_name in node_block_list:
			if block_name in interested_block_list:
				tmp.append(block_name)
		common_block_list_report[node_id] = tmp

	#generate_common_list_file(common_block_list_report, folder_name)

	return common_block_list_report
#}}}

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
	
	#ATTENTION! this is very important!!!!!!!
	#this candidate_analyze_list can be anything, not just same happen time list
	#don't need to worry candidate_happen_time, it's inside the prior matrix
	#in fact, this is not just finding critical_path, it's finding all sequential pattern
	#if want to find all sequential pattern, I need to make it looping
	#this critical path mining's entrance should ONLY be a node_block_list, candidate_analyze_list can be block which is interested, or all the blocks in node_block_list, so when looping, I should modify the node_block_list (remove already mined blocks from node_block_list)
	get_critical_path_from_candidate_analyze_list (candidate_analyze_list, node_block_list)


def get_critical_path_from_candidate_analyze_list (candidate_analyze_list, node_block_list):

	candidate_block_length = len(candidate_analyze_list)
	prior_matrix = gen_prior_matrix_from_candidate_list(candidate_analyze_list, node_block_list)



	critical_path = new_discover_sequential_pattern_from_prior_matrix(candidate_analyze_list, prior_matrix)
	print critical_path	


	#conflict block B_75/B_76, B_107/B_109
	#tangled sequence: 1) 109, 107, 110; 2) 107, 110, 109; 3) 107, 109, 110

	#valid_prior_count_list = find_valid_prior_count_list_from_prior_matrix (prior_matrix)
	#summary_critial_path (prior_matrix, valid_prior_count_list)	
	return critical_path




def gen_candidate_block_only_list (candidate_analyze_list, node_block_list):
#may useful, may not. I can use it to generate a reference list
#{{{
	candidate_block_only_list = []
	file_name = "candidate_block_only_file.txt"
	fl = open(file_name, "w")
	for report_list_block in node_block_list:
		if not report_list_block in candidate_analyze_list:
			#if this block not in analyze list, ignore it 
			continue
		fl.write(report_list_block)
		fl.write("\n")

		candidate_block_only_list.append(report_list_block)
	fl.close()
	return candidate_block_only_list
#}}}	

def new_discover_sequential_pattern_from_prior_matrix(candidate_analyze_list, prior_matrix):
#fourth version
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

#	left_candidate_list = find_left_candidate_list_from_candidate_list_with_critical_path(critical_path, candidate_analyze_list)
#	print "left_candidate"
#	print left_candidate_list

#	non_critical_path_list = learn_non_critical_sequencial_patterns (left_candidate_list, prior_matrix, status_matrix)
#	print "non_critical_path"
#	print non_critical_path_list
	return critical_path
	
def learn_non_critical_sequencial_patterns (candidate_list, prior_matrix, status_matrix):
#{{{
	done_pattern_list = []
	growing_pattern_list = []
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
		equal_list = []
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
				equal_list.append(sub_block)		
			elif forward_conflict == 1 and backward_conflict == 1:
				#tangle, or should we say it's real conflict
				tangle_list.append(sub_block)
		status_list["prior"] = prior_list	
		status_list["after"] = after_list	
		status_list["equal"] = equal_list	
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

#fourth version
#############################################################################################################








def new_discover_sequential_pattern_from_prior_matrix_3(candidate_analyze_list, prior_matrix):
#third version
#{{{
	done_pattern_list = []
	candidate_analyze_list_bak = []
	#just copy a backup, don't know when we can use it
	for block in candidate_analyze_list:
		candidate_analyze_list_bak.append(block)

	
	#looping
	detected_growing_pattern = []
	for main_block in candidate_analyze_list:
		growing_pattern=[]
		growing_pattern.append(main_block)
		new_candidate_analyze_list = []
		for block in candidate_analyze_list:
			if not block == main_block:
				new_candidate_analyze_list.append(block)
		
		result = pattern_list_nesting_free_growing(growing_pattern, new_candidate_analyze_list, prior_matrix)
		for pattern in result:
			if pattern not in detected_growing_pattern:
				if len(pattern) >= 2: 
					detected_growing_pattern.append(pattern) 
		print main_block + "done"	
	#conflict block B_75/B_76, B_107/B_109
	#tangled sequence: 1) 109, 107, 110; 2) 107, 110, 109; 3) 107, 109, 110
	#for tangled sequence, 107 and 110 can be merged, 109 should be an individual one
	for pattern in detected_growing_pattern:
		print pattern
#}}}
def pattern_list_nesting_free_growing(growing_pattern, candidate_analyze_list, prior_matrix):
#{{{
	total_detected_pattern_list = []
	have_real_conflict = 0
	for i in range (0, len(candidate_analyze_list)):
		candidate_block = candidate_analyze_list[i]
		insert_pos = search_sub_block_insert_into_growing_pattern_position (growing_pattern, candidate_block, prior_matrix)
		if not insert_pos == -1:
			growing_pattern.insert(insert_pos, candidate_block)
		else:
			#conflict
			#should judge if that's a real conflict, if so must erase the conflict growing_pattern_block and grow a new list
			for position in range(0, len (growing_pattern)):
				pattern_block = growing_pattern[position]
				forward_conflict = search_prior_matrix_for_conflict(pattern_block, candidate_block, prior_matrix)
				backward_conflict = search_prior_matrix_for_conflict(candidate_block, pattern_block, prior_matrix)
				if forward_conflict == 1 and backward_conflict == 1:
					#this is a real conflict, these two blocks can exist in the same pattern, should branch to two growing patterns.
					#only branch to two and stop, if there is another conflict block in the future it will be branck again. however it seems impossible. for example, B_1 and B_3 is conflict, the possibility that in the future B_2 and B_3 is conflict again is very low, because B_1 and B_2 have very high possible to conflict. 
					#{{{
					have_real_conflict = 1
					new_candidate_analyze_list_0 = []
					new_candidate_analyze_list_1 = []
					growing_pattern_0 = []
					growing_pattern_1 = [] 
					#0: analyze list with conflict block, growing_pattern without.
					#1: analyze list without conflict block, growing_pattern with.
					for new_analyze_list_i in range (i, len(candidate_analyze_list)):
						new_candidate_analyze_list_0.append(candidate_analyze_list[new_analyze_list_i])
					for new_analyze_list_i in range (i+1, len(candidate_analyze_list)):
						new_candidate_analyze_list_1.append(candidate_analyze_list[new_analyze_list_i])
					for growing_pattern_position in range(0, len(growing_pattern)):
						if growing_pattern_position == position:
							growing_pattern_1.append(growing_pattern[growing_pattern_position])
						else:
							growing_pattern_0.append(growing_pattern[growing_pattern_position])
							growing_pattern_1.append(growing_pattern[growing_pattern_position])
					result = pattern_list_nesting_free_growing (growing_pattern_0, new_candidate_analyze_list_0, prior_matrix)
					for pattern in result:
						if pattern not in total_detected_pattern_list:
							total_detected_pattern_list.append(pattern)
					result = pattern_list_nesting_free_growing (growing_pattern_1, new_candidate_analyze_list_1, prior_matrix)
					for pattern in result:
						if pattern not in total_detected_pattern_list:
							total_detected_pattern_list.append(pattern)


					break
					#only branch once and break
					#}}}
		if have_real_conflict == 1:
			break
	if have_real_conflict == 0:
		total_detected_pattern_list.append(growing_pattern)
	return total_detected_pattern_list
#}}}

def new_discover_sequential_pattern_from_prior_matrix_2(candidate_analyze_list, prior_matrix):
#second version, it can detect 3 lists, not 4 from the large common list (0, 201)
#still not perfect, I need third version, nesting
#{{{
	done_pattern_list = []
	candidate_analyze_list_bak = []
	#just copy a backup, don't know when we can use it
	for block in candidate_analyze_list:
		candidate_analyze_list_bak.append(block)

	
	#looping
	detected_growing_pattern = []
		
	result = candidate_analyze_list_free_growing(candidate_analyze_list, prior_matrix)
	detected_growing_pattern = result[0]
	candidate_analyze_list = result[1]
	#this growing_pattern is just a maximum common sequence, still need to add more block into growing_pattern
	for pattern in detected_growing_pattern:
		print pattern
#}}}

def candidate_analyze_list_free_growing(candidate_analyze_list, prior_matrix):
#{{{
	detected_pattern_list = []
	analyze_left_list = []
	length = len(candidate_analyze_list)
	
	for main_block in candidate_analyze_list:
		
		growing_pattern = []
		growing_pattern.append(main_block)
		for candidate_block in candidate_analyze_list:		
			if candidate_block == main_block:
				continue
			insert_pos = search_sub_block_insert_into_growing_pattern_position (growing_pattern, candidate_block, prior_matrix)
			if not insert_pos == -1:
				growing_pattern.insert(insert_pos, candidate_block)
		if growing_pattern not in detected_pattern_list:
			detected_pattern_list.append(growing_pattern)
	result = []
	result.append(detected_pattern_list)
	result.append(analyze_left_list)
	return result
#}}}

def new_discover_sequential_pattern_from_prior_matrix_1(candidate_analyze_list, prior_matrix):
#first version, can work on simple list, if have large list it will consume long time
#{{{
	done_pattern_list = []
	#growing_pattern_list initilizing
	growing_pattern_list = []
	for main_block in prior_matrix:
		tmp = []
		tmp.append(main_block)
		growing_pattern_list.append(tmp)
		
	#looping!!!!, until growing pattern list is empty!

	for i in range(0, 4):
		new_found_growing_pattern_list = []
		#every time this list must reset to empty!
		length = len(growing_pattern_list)
		for growing_pattern in growing_pattern_list:
			grown = 0
			for sub_block in candidate_analyze_list:
				if sub_block in growing_pattern:
					continue
				#sub_block is the block ready to insert into growing_pattern
				insert_position = search_sub_block_insert_into_growing_pattern_position(growing_pattern, sub_block, prior_matrix)
				if not insert_position == -1:
					new_growing_pattern = []
					for block in growing_pattern:
						new_growing_pattern.append(block)
					new_growing_pattern.insert(insert_position, sub_block)
					grown = 1
					if not new_growing_pattern in new_found_growing_pattern_list:
						#I can't allow repeating new pattern add in new_found_list
						new_found_growing_pattern_list.append(new_growing_pattern)
			if grown == 0 and not len(growing_pattern) == 1:
				#this growing_pattern is not growing, move it to done_pattern_list
				#growing pattern have only one block is useless
				done_pattern_list.append(growing_pattern)
			growing_pattern_list = new_found_growing_pattern_list
			#here, growing_pattern_list should be set to new_found_growing_pattern_list
			#in other words, growing_pattern have only two fates: 1) grown, then add new growing_pattern into growing_pattern_list; 2) not grown, remove to done_pattern_list.
		print growing_pattern_list
#}}}

def search_sub_block_insert_into_growing_pattern_position(growing_pattern, sub_block, prior_matrix):
#could be done
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

########################################################################################################
#useful

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
 
	if main_block_prior_candidate_block_count >= valid_happen_time * threshold_tolerance and candidate_block_prior_main_block_count >= (valid_happen_time - 1) * threshold_tolerance:
		#main and candidate is following a sequence
		return 0
	return 1
#}}}

def gen_prior_matrix_from_candidate_list (candidate_analyze_list, node_block_list):
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
	last_block_sub_list = prior_matrix[previous_block]
	last_block_sub_list["last_block"] = "yes"
	prior_matrix[previous_block] = last_block_sub_list


	file_name = "prior_matrix.txt"
	fl = open (file_name, "w")	
	for block in prior_matrix:
		fl.write( block)
		fl.write("\n")
		fl.write (str(prior_matrix[block]))
		fl.write("\n")
	fl.close()
	

	return prior_matrix
#}}}

########################################################################################################
#useless
def find_valid_prior_count_list_from_prior_matrix (prior_matrix):
#right now seems valid_prior_count_list is not a very good plan, just keep it.
#maybe this list can be a critical path mining reference, start from the block which hae most valid_prior_count	
#for example, candidate list length is 59, block_0 is the very start block, block_0 have valid_prior_count == 58, this is very very DIEAL
#{{{
	valid_prior_count_list = {}
	total_block_count = len(prior_matrix)
	for main_block in prior_matrix:
		valid_count = 0
		is_last_block = 0
		main_block_sub_list = prior_matrix[main_block]
		if "last_block" in main_block_sub_list:
			#this is last_block
			is_last_block = 1
		for sub_block in main_block_sub_list:
			candidate_happen_time = main_block_sub_list["happen_count"]
			if sub_block == main_block or sub_block == "happen_count" or sub_block == "last_block":
				continue
			else:
				sub_block_record = main_block_sub_list[sub_block]
				suffcient_happen_time = candidate_happen_time
				if sub_block_record["count"] == suffcient_happen_time:
					valid_count = valid_count + 1
				#if sub_block_record["count"] <= candidate_happen_time - 2:
				#	print "warning"
				#	print main_block
				#	print sub_block
		valid_prior_count_list[main_block] = valid_count
			
	print valid_prior_count_list
	sorted_valid_prior_count_list = valid_prior_list_sorting (valid_prior_count_list)
	return sorted_valid_prior_count_list
#}}}

def valid_prior_list_sorting (valid_prior_count_list):
#{{{
	valid_prior_list = []
	for block in valid_prior_count_list:
		count = valid_prior_count_list[block]
		tmp = [block, count]
		valid_prior_list.append(tmp)
	
	sorted_list = sorted( valid_prior_list, key=operator.itemgetter(1), reverse=True)
	return sorted_list
#}}}

def summary_critial_path (prior_matrix, sorted_valid_prior_count_list):
#useless, just keeping
#{{{
	#attention! candidate_happen_time is not necessary here, it should be in the prior_matrix
	#must change in the future
	print sorted_valid_prior_count_list
	critical_path_list = []
	non_critical_path_list = []
	length = len(sorted_valid_prior_count_list)
	while not length == 0:
		candidate_block = sorted_valid_prior_count_list[0][0]
		#sorted_valid_prior_count_list is just like {[block_0, 58], {block_203, 57}}
		if critical_path_list == []:
			#critical_path_list could be empty, just add a new candidate_block in
			critical_path_list.append(candidate_block)		
		else:
			#adding candidate_block into critial_path
			have_conflict = 0
			for i in range (0, len(critical_path_list)):
				main_block = critical_path_list[i]
				result = search_prior_matrix_for_conflict(main_block, candidate_block, prior_matrix)
				if result == 1:
					#any conflict happens, do not compare candidate_block with any other blocks in critical_path_list
					#remove main_block from critical_path_list, add main_block and candidate_block into non_critical_path
					del (critical_path_list[i])
					non_critical_path_list.append(main_block)
					non_critical_path_list.append(candidate_block)
					have_conflict = 1
					break
			if have_conflict == 0:
				critical_path_list.append(candidate_block)			


		#compare candidate_block done, remove it from sorted_valid_prior_count_list, it can be at critical or non critical.
		del (sorted_valid_prior_count_list[0])
		length = len(sorted_valid_prior_count_list)

	print critical_path_list
	print non_critical_path_list
#}}}

#}}}










#order summary and analyze:
#happen_order_analyze
#compare_happen_order
#get_each_block_happen_line_num_list
#merge_suggest_from_happen_order
#{{{
def merge_suggest_from_happen_order (input_file):
	print "merge suggest from happen order"
	block_list = input_file_block_analyzer.input_file_block_analyze(input_file)

	block_list = timeframe_analyze.add_time_index_into_block_list (block_list, input_file)
	timeframe_predict_list = timeframe_analyze.timeframe_happen_predict_list_gen(block_list)
	block_order_list = happen_order_analyze(block_list)
	
	total_suggest_list = []
	for count in block_order_list:
		for suggest_part in block_order_list[count]:
			start_block = suggest_part[0]
			second_block = suggest_part[1]
			start_block_predict_list = timeframe_predict_list[start_block]
			if second_block in  start_block_predict_list:
				second_block_possibility = start_block_predict_list[second_block]
				if second_block_possibility > timeframe_analyze.predict_pos_threshold:
					total_suggest_list.append(suggest_part)

	#optimize
	total_suggest_list = block_order_suggest_merge_list_optimize(total_suggest_list)

	return total_suggest_list


	#['block_97', 'block_100']
	#['block_98', 'block_100']
	#can be merged to be ['block_97', 'block_100']
	# this makes sense
	#1) B97, B98 and B100 have same happen count in block list
	#2) B98 and B100 always follow B97, B100 always follow B98
	#3) [B97, B98] meets [B98, B100], means B98 have high probility can be merged with B97 and B100 have high probility can be merged with B98. There must be another pair [B97, B100] in the list. Then if we can find another pair [B97, B100] in the list we can remove them. 
	#4) what if the list is [B97, B98], [B98, B100], [B97, B100], [B98, B101]
	#	this is not very possible, if we have [B97, B98] and [B98, B101], there must be another pair [B97, B101] or [B100, B101].
	#	if there are not such pairs, we will remove nothing
	length = len(total_suggest_list)
	i = 0
	while i < length:
		this_pair = total_suggest_list[i]
		j = 0
		while j < length:
			if i == j: 
				j = j + 1
				continue
			that_pair = total_suggest_list[j]
			if this_pair[1] == that_pair[0]:
				tmp = [this_pair[0], that_pair[1]]
				if tmp in total_suggest_list:
					if i > j:
						del total_suggest_list [i]
						del total_suggest_list [j]
					else :
						del total_suggest_list [j]
						del total_suggest_list [i]

					length = length - 2
					if i > length:
						break
			j = j + 1
		i = i + 1
		
	return total_suggest_list


def happen_order_analyze (block_list):
	block_happen_count_list = report_APIs.count_block_happen_time (block_list)
	each_block_happen_line_num_list = get_each_block_happen_line_num_list(block_list)
	block_order_list = {}
	for count in 	block_happen_count_list:
		happen_count_sub_list = block_happen_count_list[count]
		for i in range (0, len(happen_count_sub_list)):
			start_block = happen_count_sub_list[i]
			for j in range (0, len(happen_count_sub_list) ):
				if i == j:
					continue
				second_block = happen_count_sub_list[j]
				order = compare_happen_order(count, start_block, second_block, each_block_happen_line_num_list)
				if not order == -1:
					if order == 0:
						tmp = [start_block, second_block]
					else:
						tmp = [second_block, start_block]
					if count in block_order_list:
						if not tmp in block_order_list[count]:
							block_order_list[count].append(tmp)
					else:
						block_order_list[count] = []
						block_order_list[count].append(tmp)
	return block_order_list

def compare_happen_order (count, start_block, second_block, each_block_happen_line_num_list):
	start_list = each_block_happen_line_num_list[start_block]
	second_list = each_block_happen_line_num_list[second_block]
	forward = -1
	#0 = forward, 1 = backward
	for i in range (0, count):
		start_line_start = start_list[i][0]
		start_line_finish = start_list[i][1]
		second_line_start = second_list[i][0]
		second_line_finish = second_list[i][1]
		if i == 0:
			if start_line_start <= second_line_start and start_line_finish <= second_line_finish:
				forward = 0
			elif start_line_start > second_line_start and start_line_finish > second_line_finish :
				forward = 1
			else:
				return -1
		else:
			if forward == 0:
				#forward, second_block should between start_block_list [0,1]
				#start [0,1]
				#second [0,1]
				#start [0] < second[0] < start[1] < second[1]
				last_start_line_start = start_list[i-1][0]
				last_start_line_finish = start_list[i-1][1]
				last_second_line_start = second_list[i-1][0]
				last_second_line_finish = second_list[i-1][1]
				#start[0] < second[0]	
				if not last_start_line_start <= last_second_line_start:
					return -1
				if not last_start_line_finish <= last_second_line_finish:
					return -1
	 			#second[0] < start[1]
				if not last_second_line_start <= start_line_start:
					return -1
				if not last_second_line_finish <= start_line_finish:
					return -1
				#start[1] < second[1]
				if not start_line_start <= second_line_start:
					return -1
				if not start_line_finish <= second_line_finish:
					return -1

			else:
				#backward, start_block should between second_block_list [0,1]
				#start [0] > second[0] > start[1] > second[1]
				last_start_line_start = start_list[i-1][0]
				last_start_line_finish = start_list[i-1][1]
				last_second_line_start = second_list[i-1][0]
				last_second_line_finish = second_list[i-1][1]
				#start[0] > second[0]
				if not last_start_line_start > last_second_line_start:
					return -1
				if not last_start_line_finish > last_second_line_finish:
					return -1
	 			#second[0] > start[1]
				if not last_second_line_start > start_line_start:
					return -1
				if not last_second_line_finish > start_line_finish:
					return -1
				#start[1] > second[1]
				if not start_line_start > second_line_start:
					return -1
				if not start_line_finish > second_line_finish:
					return -1


	
	return forward

def get_each_block_happen_line_num_list (block_list):
	each_block_happen_line_num_list = {}
	for block in block_list:
		block_name = block[0]
		start_line = block[1]
		finish_line = block[2]
		tmp = [start_line, finish_line]
		if block_name in each_block_happen_line_num_list:
			each_block_happen_line_num_list[block_name].append(tmp)
		else: 
			each_block_happen_line_num_list[block_name]=[]
			each_block_happen_line_num_list[block_name].append(tmp)
	return each_block_happen_line_num_list
#}}}
