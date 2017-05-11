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
