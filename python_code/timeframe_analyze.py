#!/usr/bin/python
#coding:utf-8

import os
import sys
import global_APIs
import report_APIs
import block_merger
predict_time_gap = 5
predict_pos_threshold = 0.95


#main function
#timeframe_predict_main
def timeframe_analyze_main (block_list):
	timeframe_happen_predict_list = timeframe_happen_predict_list_gen(block_list)
	predict_fail_list = timeframe_block_sequence_test(block_list, timeframe_happen_predict_list)
	block_happen_count_list = report_APIs.count_block_happen_time (block_list)
	timeframe_predict_result_report (predict_fail_list, block_happen_count_list, timeframe_happen_predict_list)

#core APIs
#timeframe_happen_predict_list_gen
#timeframe_block_sequence_test
#{{{
def timeframe_happen_predict_list_gen (block_list):
	next_list = gen_next_happen_count_list (block_list)
	prior_list = gen_prior_happen_count_list (block_list)
	next_pos_matrix = gen_happen_count_pos_matrix (next_list)
	prior_pos_matrix = gen_happen_count_pos_matrix (prior_list)

	timeframe_happen_predict_list = {}
	effect_test_count_list = {}
	block_num = 0


	for block_num in range(0, len(block_list) - 1):
		this_block = block_list[block_num]
		this_block_name = this_block[0]
		this_block_start_time_index = this_block[3]
		this_block_finish_time_index = this_block[4]
		next_block_num = 1
	
		if this_block_name in timeframe_happen_predict_list:
			tmp = timeframe_happen_predict_list[this_block_name]
		else:
			tmp = {}
			tmp ["effect_count"] = 0

		while True:
			if block_num + next_block_num >= len(block_list):
				break
			next_block = block_list[block_num + next_block_num]
			next_block_name = next_block[0]
			next_block_start_time_index = next_block[3]
			next_block_finish_time_index = next_block[4]
			if next_block_name in tmp or next_block_name == this_block_name: 
				next_block_num += 1
#ARES questionable
#effect_count must be same as future predict count.
#for example, when learning, block_1 tested next 5 blocks
#when predicting, block_1 will predict next 5 blocks too.
#this example is the learning and predicting model are the same, or should I say is cheating
#but in the future, I must calculate the effect_count in this way.
				#tmp ["effect_count"] = tmp["effect_count"] + 1
				continue
			if int(next_block_start_time_index) - int(this_block_finish_time_index) > predict_time_gap:
				break		
			next_block_num += 1
			
			next_pos = block_merger.calculate_possibility (this_block_name, next_block_name, next_list, next_pos_matrix, 0, this_block_name, [], 1)
						
			prior_pos = block_merger.calculate_possibility (next_block_name, this_block_name, prior_list, prior_pos_matrix, 0, next_block_name, [], 1)

			total_pos = (next_pos + prior_pos) / 2
			tmp [next_block_name] = total_pos
			tmp ["effect_count"] = tmp["effect_count"] + 1
		timeframe_happen_predict_list[this_block_name] = tmp

	timeframe_report_file = "block_report/time_frame.txt"
	fl = open (timeframe_report_file, "w")
	for time_predict in timeframe_happen_predict_list:
		fl.write (time_predict)
		fl.write (str(timeframe_happen_predict_list[time_predict]))
		fl.write("\n")
	fl.close()


	return timeframe_happen_predict_list

def timeframe_block_sequence_test (block_list, timeframe_happen_predict_list):
	predict_list = []
	predict_fail_list = []

#just making mistakes

	for block_num in range(0, len(block_list) - 1):
		this_block = block_list[block_num]
		this_block_name = this_block[0]
		this_block_start_time_index = this_block[3]
		this_block_finish_time_index = this_block[4]
		event_pos_list = timeframe_happen_predict_list[this_block_name]
		i = 0
		length = len(predict_list)
		while i < length:
			predict_ele = predict_list[i]
			predict_time = predict_ele["predict_time"] 
			predict_event_list = predict_ele["predict_event"]
			source_event = predict_ele["source_event"]

			if this_block_start_time_index - predict_time > predict_time_gap:
				#check time out first
				if predict_ele["happened"] == 0:
					tmp = {}
					tmp ["source"] = source_event
					tmp ["predicted_time"] = global_APIs.get_index_time_format(predict_time - predict_time_gap)
					tmp ["predict_event_list"] = predict_event_list
					predict_fail_list.append(tmp)
				del (predict_list[i])
				length = len(predict_list)
				
			elif this_block_name in predict_event_list:
				predict_ele["happened"] = 1
				i = i + 1
			else:
				i = i + 1
		
		predict_ele = {}
		tmp = []
		for event in event_pos_list:
			if event == "effect_count":
				continue
			if event_pos_list[event] > predict_pos_threshold:
				tmp.append(event)
		if not len(tmp) == 0:
			predict_ele["predict_time"] = this_block_finish_time_index + predict_time_gap 
			predict_ele["predict_event"] = tmp
			predict_ele["source_event"] = this_block_name
			predict_ele["happened"] = 0
			#ARES
			#questionable
			length = len(predict_list)
			i = 0
			while i < length:
				predict_element = predict_list[i]
				source_event = predict_element["source_event"]
				if this_block_name == source_event:
					del predict_list [i]	
					length = len(predict_list)
				else:
					i = i + 1					
			######################
			
			predict_list.append(predict_ele)

	return predict_fail_list	
#}}}


#time_index:
#add_time_index_into_block_list
#{{{
def add_time_index_into_block_list (block_list, input_file):	
	fl = open (input_file, "r")
	block_num = 0
	line_num = 1


	while block_num < len(block_list):
		block = block_list[block_num]
		block_name = block[0]
		block_start = block[1]
		block_finish = block[2]
	
		line = fl.readline()
		while line_num < int(block_start):
			line = fl.readline()
			line_num = line_num + 1
		#reach start_line
		start_time = global_APIs.get_line_time(line)
		start_time_index = global_APIs.get_line_time_index(line)
		start_line = line_num
	
		while line_num < int(block_finish):
			line = fl.readline()
			line_num = line_num + 1
		#reach finish_line
		finish_time = global_APIs.get_line_time(line)	
		finish_time_index = global_APIs.get_line_time_index(line)	
		finish_line = line_num
		
		block.append(start_time_index)
		block.append(finish_time_index)
		block.append(start_time)
		block.append(finish_time)
		block_list[block_num] = block
		line_num = line_num + 1
		block_num = block_num + 1

	fl.close()
	return block_list
#}}}


#list and matrix:
#gen_next_happen_count_list
#gen_prior_happen_count_list
#gen_happen_count_pos_matrix
#matrix_show
#{{{
def gen_next_happen_count_list (block_list):
	next_list = {}
	length = len(block_list)
	if length == 0:
		return next_list
	for i in range(0 , length - 1):
		this_block = block_list[i]	
		next_block = block_list[i+1]
		this_name = this_block[0]
		next_name = next_block[0]
		if next_name == this_name:
			#ignore itself
			continue
		if this_name in next_list:
			this_list = next_list[this_name]
			if next_name not in this_list:
				this_list[next_name] = 1
			else:
				this_list[next_name] = this_list[next_name] + 1
				
			next_list[this_name] = this_list
			this_list["total_num"] = this_list["total_num"] + 1
		else:
			this_list = {}
			this_list[next_name] = 1
			this_list["total_num"] = 1
			next_list[this_name] = this_list
	
	#last block
	last_block = block_list[length - 1]
	last_name = last_block[0]
	if last_name not in next_list:
		this_list = {}
		this_list["last"] = 1
		next_list[last_name] = this_list
		next_list[last_name]["total_num"] = 0
	else:
		this_list = next_list[last_name]
		this_list["last"] = 1
		next_list[last_name] = this_list
	next_list[last_name]["total_num"] = next_list[last_name]["total_num"] + 1
			
	return next_list

def gen_prior_happen_count_list (block_list):
	prior_list = {}
	length = len(block_list)
	if length == 0:
		return prior_list
	for i in range(0 , length - 1):
		prior_block = block_list[i]
		prior_name = prior_block[0]
		this_block = block_list[i+1]	
		this_name = this_block[0]
		if this_name == prior_name:
			#ignore itself
			continue
		if this_name in prior_list:
			this_list = prior_list[this_name]
			if prior_name not in this_list:
				this_list[prior_name] = 1
			else:
				this_list[prior_name] = this_list[prior_name] + 1
			prior_list[this_name] = this_list
			this_list["total_num"] = this_list["total_num"] + 1
		else:
			this_list = {}
			this_list[prior_name] = 1
			this_list["total_num"] = 1
			prior_list[this_name] = this_list
	
	#last block
	first_block = block_list[0]
	first_name = first_block[0]
	if first_name not in prior_list:
		this_list = {}
		this_list["first"] = 1
		prior_list[first_name] = this_list
		prior_list[first_name]["total_num"] = 0
	else:
		this_list = prior_list[first_name]
		this_list["first"] = 1
		prior_list[first_name] = this_list
	prior_list[first_name]["total_num"] = prior_list[first_name]["total_num"] + 1
			
	return prior_list

def gen_happen_count_pos_matrix (block_list):
	pos_matrix = {}
	matrix_size = len (block_list)
	element_list = []
	
	for start_block in block_list:
		element_list.append (start_block)
	
	for start_block in block_list:
		tmp = {}
		for finish in block_list: 
			tmp[finish] = "" 			
		start_block_list = block_list[start_block]
		length = start_block_list["total_num"]
		for block_name in start_block_list:
			if block_name == "total_num":
				continue
			happen_count = start_block_list[block_name]
			if length == 0:
				possibility = 0
			else: 
				possibility = float(happen_count)/float(length)
			tmp[block_name] = possibility
		pos_matrix[start_block] = tmp

	return pos_matrix

def matrix_show (next_pos_matrix):
	element_list = []
	for next_pos in next_pos_matrix:
		element_list.append (next_pos)
	tmp = "        "
	for ele in element_list:
		tmp += ele
		tmp += " "
	print tmp
	for next_pos in next_pos_matrix:
		element_next_list = next_pos_matrix[next_pos]
		tmp = next_pos
		tmp += " "
		for ele in element_list:
			if str(element_next_list[ele]) == "":
				tmp += "   "
			else:
				tmp += str(element_next_list[ele])
			tmp += "|"
		print tmp
#}}}

#report
#timeframe_predict_result_report
#{{{
def timeframe_predict_result_report (predict_fail_list, block_happen_count_list, timeframe_happen_predict_list):
	fail_list = {}
	fail_list_1 = {}
	suggest_list = {}
	for predict_fail in predict_fail_list:
		source_block = predict_fail["source"]
		if source_block in fail_list:
			fail_list[source_block]["fail_count"] = fail_list[source_block]["fail_count"] + 1
			fail_list[source_block]["fail_time"].append(predict_fail["predicted_time"])	
		else:
			tmp = {}
			tmp["fail_count"] = 1
			for count in block_happen_count_list:
				if source_block in block_happen_count_list[count]:
					tmp["happen_count"] = count
					break
			tmp["effect_test_count"] = timeframe_happen_predict_list[source_block]["effect_count"]
			tmp["predict_event_list"] = predict_fail["predict_event_list"]
			tmp["fail_time"] = []
			tmp["fail_time"].append(predict_fail["predicted_time"])	
			fail_list[source_block] = tmp	
	
	for source_block in fail_list:
		fail_count = fail_list[source_block]["fail_count"]
		happen_count = fail_list[source_block]["happen_count"]
		if float(fail_count)/float(happen_count) < 0.5:
			suggest_list[source_block] = fail_list[source_block]
		else:
			fail_list_1[source_block] = fail_list[source_block]
			
	
	print "suggest_pay_attention"
	for source_block in suggest_list:
		print source_block
		print suggest_list[source_block]	

	print "predict_fail"
	for source_block in fail_list_1:
		print source_block
		print fail_list_1[source_block]	
#}}}

