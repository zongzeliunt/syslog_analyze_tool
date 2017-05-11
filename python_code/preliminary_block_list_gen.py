#!/usr/bin/python
import global_APIs

line_pattern_match_threshold = 0.60 
line_pattern_dismatch_threshold = 0.32 
ignore_single_line_single_word = 0 
#this database learner is for the first 2 steps:
#1) pattern dictionary generate
#2) adjecent lines combination
#finally it will generate a preliminary block list





def preliminary_block_list_learner (input_file, mode):
	single_line_pattern_list = pattern_dict_creater (input_file)
	file_mode = global_APIs.get_file_mode (input_file)
	if file_mode == "baler_mutrino":
		#baler pattern is always length == 1
		ignore_single_line_single_word = 0
	if mode == 0:
		#learn all
		pattern_gap_list = pattern_gap_calculate (single_line_pattern_list)
		block_line_num_list = block_grouper(pattern_gap_list, single_line_pattern_list)
		block_pattern_list = block_pattern_data_base_update (block_line_num_list, single_line_pattern_list, 0)
		
	if mode == 1:
		#ignore single lines
		pattern_gap_list = pattern_gap_calculate (single_line_pattern_list)
		block_line_num_list = block_grouper(pattern_gap_list, single_line_pattern_list)
		
		block_pattern_list = block_pattern_data_base_update (block_line_num_list, single_line_pattern_list, 1)
	if mode == 2:
		#only learn single lines
		block_line_num_list = single_line_block_gen(single_line_pattern_list)
		
		block_pattern_list = block_pattern_data_base_update (block_line_num_list, single_line_pattern_list, 0)
	
	return block_pattern_list

#done APIs:
#pattern_dict_creater
#search_correspond_pattern_from_single_line_pattern_list
#gen_pattern_index
#pattern_gap_calculate
#block_grouper
#get_lowest_pattern_list_num
#block_pattern_data_base_update
#search_line_pattern_by_line_number
#single_line_block_gen
#block_list_reorder

#{{{

def single_line_block_gen (single_line_pattern_list):
	first_step_block_list = []
	for single_line_pattern_index in single_line_pattern_list:
		single_line_pattern_data = single_line_pattern_list[single_line_pattern_index]
		pattern = single_line_pattern_data["pattern"]
		first = single_line_pattern_data["first"]
		tmp = []
		tmp.append(first)
		tmp.append(first)
		first_step_block_list.append(tmp)
	
	second_step_block_list = block_list_reorder (first_step_block_list)
	return second_step_block_list


def pattern_dict_creater (input_file):
	line_counter = 1
	fl = open (input_file, "r")
	single_line_pattern_list = {}
	while True:
		line = fl.readline()
		if not line:	
			break
		line_message = 	global_APIs.get_line_message(line)
		line_pattern = ""
		if line_message == "":
			line_counter = line_counter + 1
			continue
		
		if not global_APIs.is_baler_mutrino_format(line):
			line_pattern = global_APIs.gen_line_pattern(line_message)
		else:
			line_pattern = global_APIs.gen_baler_line_pattern (line)
		
		correspond_pattern = search_correspond_pattern_from_single_line_pattern_list (line_pattern, single_line_pattern_list)
		if not correspond_pattern == "":
			correspond_pattern_index = gen_pattern_index(correspond_pattern)
			tmp = single_line_pattern_list[correspond_pattern_index]

			if not "second" in tmp:
				tmp["second"] = line_counter
			tmp["count"] = tmp["count"] + 1
			list_tmp = tmp["list"]
			list_tmp.append(line_counter)
			tmp["list"] = list_tmp
			#single_line_pattern_list[correspond_pattern] = tmp
		else:
			line_pattern_index = gen_pattern_index(line_pattern)
			tmp = {}
			tmp["first"] = line_counter
			tmp["count"] = 1
			tmp["pattern"] = line_pattern
			list_tmp = []
			list_tmp.append(line_counter)
			tmp["list"] = list_tmp
			single_line_pattern_list[line_pattern_index] = tmp
		line_counter = line_counter + 1

	fl.close()
	return single_line_pattern_list


def search_correspond_pattern_from_single_line_pattern_list (pattern, single_line_pattern_list):
	for single_line_pattern_data in single_line_pattern_list:
		tmp = single_line_pattern_list[single_line_pattern_data]
		single_line_pattern = tmp["pattern"]
		match_ratio = global_APIs.calculate_match_ratio(pattern, single_line_pattern)
		if match_ratio > line_pattern_match_threshold:
#here, we may add a dismatch list in that pattern, for the future add "value_0". but now I dom't need that
			return single_line_pattern
	return ""
		
def gen_pattern_index (pattern):
	index = ""
	for word in pattern:
		index += word[0]
		index += " "
		index += word[1]
		index += " "
	return index

def pattern_gap_calculate (single_line_pattern_list):
	pattern_gap_list = {}
	for single_line_pattern_index in single_line_pattern_list:
		single_line_pattern_data = single_line_pattern_list[single_line_pattern_index]
		if "second" in single_line_pattern_data:
			pattern = single_line_pattern_data["pattern"]
			second = single_line_pattern_data["second"]
			first = single_line_pattern_data["first"]
			count = single_line_pattern_data["count"]
			gap = second - first
			if gap in pattern_gap_list:
				gap_line_number_list = pattern_gap_list[gap]
				tmp = []
				tmp.append(first)
				tmp.append(count)
				gap_line_number_list.append (tmp)
				pattern_gap_list[gap] = gap_line_number_list
			else:
				gap_line_number_list = [] 
				tmp = []
				tmp.append(first)
				tmp.append(count)
				gap_line_number_list.append (tmp)
				pattern_gap_list[gap] = gap_line_number_list
	#regroup by order
	for pattern_gap in pattern_gap_list:
		first_list = pattern_gap_list[pattern_gap]
		tmp = []
		line_num = 0
		while not len(first_list) == 0:
			min_num = 99999999
			lowest = 0
			for i in range(0, len(first_list)):
				first = first_list[i]
				if first[0] < min_num:
					min_num = first[0] 
					lowest = i
			tmp.append(first_list[lowest])	
			del (first_list[lowest])
		pattern_gap_list[pattern_gap] = tmp	
	return pattern_gap_list

def block_grouper (pattern_gap_list, single_line_pattern_list):
	first_step_block_list = []
	for key in pattern_gap_list:
		line_number_list = pattern_gap_list[key]
		begin_line = line_number_list[0]
		end_line = line_number_list[0]
	
		begin_line_number = begin_line[0]	
		begin_line_happen_count = begin_line[1]
		end_line_number = end_line[0]	
		end_line_happen_count = end_line[1]
		growing = 0
		for i in range(1, len(line_number_list)):
			next_line = line_number_list[i]
			next_line_number = next_line[0]
			next_line_happen_count = next_line[1]
			if next_line_number - end_line_number == 1 and end_line_happen_count == next_line_happen_count:
				if two_lines_can_merge (key, end_line_number, next_line_number, single_line_pattern_list):
					growing = 1
					end_line_number = next_line_number
					end_line_happen_count = next_line_happen_count
			else:
				if not begin_line_number == end_line_number:
					tmp = []
					tmp.append(begin_line_number)
					tmp.append(end_line_number)
					first_step_block_list.append(tmp)
#TODO, just in case in the future
				if begin_line_number == end_line_number:
					tmp = []
					tmp.append(begin_line_number)
					tmp.append(end_line_number)
					first_step_block_list.append(tmp)
				begin_line_number = next_line_number
				begin_line_happen_count = next_line_happen_count
				end_line_number = next_line_number
				end_line_happen_count = next_line_happen_count
				growing = 0	
			i = i + 1
		if growing == 1:
			tmp = []
			tmp.append(begin_line_number)
			tmp.append(end_line_number)
			first_step_block_list.append(tmp)
		if growing == 0: 
			tmp = []
			tmp.append(begin_line_number)
			tmp.append(end_line_number)
			first_step_block_list.append(tmp)
	second_step_block_list = block_list_reorder (first_step_block_list)
	
	return second_step_block_list


def block_list_reorder (first_step_block_list):
	second_step_block_list = []

	while not len(first_step_block_list) == 0:
		min_line_num = 99999999
		min_element_pos = 0			
		for i in range (0, len(first_step_block_list)):
			block_element = first_step_block_list[i]
			start_line_num = block_element[0]
			if start_line_num < min_line_num:
				min_line_num = start_line_num
				min_element_pos = i
			i = i + 1
		second_step_block_list.append(first_step_block_list[min_element_pos])
		del (first_step_block_list[min_element_pos])
	return second_step_block_list


def two_lines_can_merge (gap, first_line_number, next_line_number, single_line_pattern_list):
	first_pattern_list = search_line_pattern_by_line_number(first_line_number, single_line_pattern_list, 1)
	next_pattern_list = search_line_pattern_by_line_number(next_line_number, single_line_pattern_list, 1)
	first_line_happen_list = first_pattern_list["list"]
	next_line_happen_list = next_pattern_list["list"]
	can_merge = 1
	for i in range (0, len(first_line_happen_list)):
		#the length of the first list and next list are same
		if not next_line_happen_list[i] - first_line_happen_list[i] == 1:
			can_merge = 0

	return can_merge


def get_lowest_pattern_list_num (block_pattern_list):
	count = 0
	tmp = "block_"
	tmp += str(count)
	while tmp in block_pattern_list:
		count = count + 1
		tmp = "block_"
		tmp += str(count)
	return count 	


def block_pattern_data_base_update (block_line_num_list, single_line_pattern_list, ignore_single_line):
	block_pattern_list = {}
	for block in block_line_num_list:
		block_num = get_lowest_pattern_list_num(block_pattern_list)	
		block_start_line_num = block[0]
		block_finish_line_num = block[1]
		start_line_pattern = search_line_pattern_by_line_number(block_start_line_num, single_line_pattern_list)
		finish_line_pattern = search_line_pattern_by_line_number(block_finish_line_num, single_line_pattern_list)
		if start_line_pattern == " " or finish_line_pattern == " ":
			continue

		if ignore_single_line == 1:
			if block_start_line_num == block_finish_line_num:
				#ignore all single lines
				continue
			else:
				tmp = {}
				tmp["start"] = start_line_pattern	
				tmp["finish"] =	finish_line_pattern	
				tmp["start_line"] = block_start_line_num
				tmp["finish_line"] = block_finish_line_num
				block_name = "block_"
				block_name += str(block_num)
				block_pattern_list[block_name] = tmp	

		if ignore_single_line == 0:
			if block_start_line_num == block_finish_line_num and len(start_line_pattern) == 1 and ignore_single_line_single_word == 1:
				#single line pattern only have one word is meanless. do not add it in block pattern list
				continue
			else:
				tmp = {}
				tmp["start"] = start_line_pattern	
				tmp["finish"] =	finish_line_pattern	
				tmp["start_line"] = block_start_line_num
				tmp["finish_line"] = block_finish_line_num
				block_name = "block_"
				block_name += str(block_num)
				block_pattern_list[block_name] = tmp	
	return block_pattern_list

def search_line_pattern_by_line_number (line_number, single_line_pattern_list, need_info_list = 0):
	for single_line_pattern in single_line_pattern_list:
		key = single_line_pattern_list[single_line_pattern]
		first_line_num = key["first"]
		if first_line_num == line_number:
			pattern = key["pattern"]
			if need_info_list == 0:
				return pattern
			else:
				return key
	return ""
#}}}







