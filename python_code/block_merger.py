#!/usr/bin/python
#coding:utf-8

import os
import sys
import report_APIs as report_APIs

global_search_deep_level = 7 
global_forward_step_num = 4 
global_similar_threshold = 0.99

#global_API:
#block_list_read
#{{{
def block_list_read (input_file):
	block_list = [] 
	if not os.path.isfile(input_file):
		print "no file"
	fl = open (input_file, "r")
	while True:
		line = fl.readline()
		if not line:	
			break
		line_part = line.split()
		tmp = []
		tmp.append(line_part[0])
		tmp.append(line_part[1])
		tmp.append(line_part[2])
		block_list.append( tmp)
	fl.close()
	return block_list
#}}}

#list and matrix:
#gen_next_list
#prior_next_list
#gen_pos_matrix
#matrix_show (useless)
#{{{
def gen_next_list (block_list):
	next_list = {}
	length = len(block_list)
	if length == 0:
		return next_list
	for i in range(0 , length - 1):
		this_block = block_list[i]	
		next_block = block_list[i+1]
		this_name = this_block[0]
		next_name = next_block[0]
		if this_name in next_list:
			this_list = next_list[this_name]
			if next_name not in this_list:
				this_list.append(next_name)
			next_list[this_name] = this_list
		else:
			this_list = []
			this_list.append(next_name)
			next_list[this_name] = this_list
	
	#last block
	last_block = block_list[length - 1]
	last_name = last_block[0]
	if last_name not in next_list:
		this_list = []
		this_list.append("last")
		next_list[last_name] = this_list
	else:
		this_list = next_list[last_name]
		this_list.append("last")
		next_list[last_name] = this_list
			
	return next_list

def gen_prior_list (block_list):
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
			continue
		if this_name in prior_list:
			this_list = prior_list[this_name]
			if prior_name not in this_list:
				this_list.append(prior_name)
			prior_list[this_name] = this_list
		else:
			this_list = []
			this_list.append(prior_name)
			prior_list[this_name] = this_list
	
	#last block
	first_block = block_list[0]
	first_name = first_block[0]
	if first_name not in prior_list:
		this_list = []
		this_list.append("first")
		prior_list[first_name] = this_list
	else:
		this_list = prior_list[first_name]
		this_list.append("first")
		prior_list[first_name] = this_list
			
	return prior_list

def gen_pos_matrix (block_list):
	pos_matrix = {}
	matrix_size = len (block_list)
	element_list = []
	
	for start_block in block_list:
		element_list.append (start_block)
	
	for start_block in block_list:
		tmp = {}
		if start_block == "barricade":
			for finish in block_list: 
				tmp[finish] = 0
			pos_matrix[start_block]= tmp
			continue


		for finish in block_list: 
			tmp[finish] = "" 			
		start_block_list = block_list[start_block]
		length = len(start_block_list)
		if length == 0:
			possibility = 0
		else:
			possibility = float(1)/float(length)
		possibility = round (possibility, 2)
		for finish_block in start_block_list:
#ARES
			if finish_block == "barricade":
				tmp[finish_block] = 0 
			else:
				tmp[finish_block] = possibility
		pos_matrix[start_block]= tmp
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

#def update_matrix (next_list, next_pos_matrix):
#	element_list = []
#	for next_pos in next_pos_matrix:
#		element_list.append (next_pos)
#	for start_block in next_pos_matrix:
#		start_block_next_pos_list = next_pos_matrix[start_block]
#		for finish_block in element_list:
#			if start_block_next_pos_list[finish_block] == "":
#				possibility = calculate_possibility(start_block, finish_block, next_list, next_pos_matrix, 0, start_block, [])
#				start_block_next_pos_list[finish_block] = possibility	
#				next_pos_matrix[start_block] = start_block_next_pos_list
#
# 
#	return next_pos_matrix
#}}}


#block_list merge:
#calculate_possibility
#try_find_merge_candidate
#optimize_merge_suggest_list
#block_list_remove_merged_block
#careful! these are very core parts, do not change anything inside!
#{{{
def calculate_possibility(start_block, finish_block, next_list, next_pos_matrix, level, root_start_block, previous_step_stock, ignore_itself = 0):
#{0 0 1} must also be {0 0 1}
#but {0 1 1 2} must merged to {0 2} and give a unique name 0
	total_pos = 0.0
	if start_block == finish_block:
		return 1.0
	if start_block == root_start_block and not level == 0:
		if ignore_itself == 1:
		#this is for calculating prediction possibility, to predict what is going to happen in the future.
			return 1.0
		else:
		#this is for merging
		#to avoid {0 0 1} to be merged to {0 1}
			return 0.0
	if level == global_search_deep_level:
		return 0.0
			
	start_block_next_list = next_list[start_block]
	start_block_next_pos_list = next_pos_matrix[start_block]
	new_previous_step_stock = []
	for previous in previous_step_stock:
		new_previous_step_stock.append(previous)
	new_previous_step_stock.append(start_block)
	for start_block_next in start_block_next_list:
		if start_block_next == "last":
			continue
		if start_block_next == "first":
			continue
		if start_block_next == "total_num":
			continue
		if start_block_next == start_block:
			if level == 0:
			    continue
			#ARES 10/11/2016
			#if block_7's next list have block_7, don't try to calculate the pos any more
			#to avoid add block_7 into previous step stock
			#list = 7 7 8
			#if level == 0, p(7 , 8) will be 1, so 7&8 will be merged
			#that's why I continue it, I must avoid merge 7 7 8 to 7 8
			#but if level is not 0
			#list = 24 31 31 32 31 33 31 34
			#p(24, 34) = p(24, 31) * p(31, 34)
			#p(24, 34) = p(24, 31) * (p(31, 34) + p(32, 34) +  p(33, 34) + p (34, 34))
			#I must add 31 into previous step list
					

		#here is very suspect
		if start_block in previous_step_stock:
			return 1.0
		       #block list = 1 2 1 3
		       #p(1, 3) = p(1, 2) * p(2, 1) * p (1, 3) + p (1, 3)
		       #          0.5     * 1.0     * 1.0 (assigned here) + 0.5 = 1.0
		#suspect finish
		else:	
			pos = start_block_next_pos_list[start_block_next]
			pos = pos*calculate_possibility (start_block_next, finish_block, next_list, next_pos_matrix, level+1, root_start_block, new_previous_step_stock, ignore_itself )
			total_pos += pos

	return total_pos
				
def gen_forward_list (block_list):
	forward_list = {}
	length = len(block_list)
	if length == 0:
		return forward_list
	for i in range(0 , length - 1):
		this_block = block_list[i]
		this_name = this_block[0]
		if this_name in forward_list:
			this_list = forward_list[this_name]
		else:
			this_list = []
		
		forward_step = 1
		total_step = 1
		#forward step is for make sure this block's next forward number of different block to be added into forward list
		#total step is for block list count
		while i + total_step < length and forward_step <= global_forward_step_num: 
			forward_block = block_list[i + total_step]
			forward_block_name = forward_block[0]
			if this_name == forward_block_name:
				#don't want to merge with itself
				total_step = total_step + 1
				continue
			
			if forward_block_name in this_list:
				#to prevent dozens of repeating blocks to hold forward step 
				total_step = total_step  + 1	
				continue
			else:
				#only when add forward block into forward list, then add forward step
				this_list.append(forward_block_name)
				forward_step = forward_step + 1	
				total_step = total_step  + 1	
		forward_list[this_name] = this_list
	
	#last block
	#I don't want to calculate possibility of this block with last icon, so we can remove this
	last_block = block_list[length - 1]
	last_name = last_block[0]
	if last_name not in forward_list:
		this_list = []
		this_list.append("last")
		forward_list[last_name] = this_list
	else:
		this_list = forward_list[last_name]
		this_list.append("last")
		forward_list[last_name] = this_list
			
	return forward_list
	

def try_find_merge_candidate (block_list):
	next_list = gen_next_list (block_list)
	prior_list = gen_prior_list (block_list)
	next_pos_matrix = gen_pos_matrix (next_list)
	prior_pos_matrix = gen_pos_matrix (prior_list)
	forward_list = gen_forward_list (block_list)
	length = len(forward_list)
	merge_start_list = []
	merge_suggest_list = []
	for this_name in forward_list:
		if this_name in merge_start_list:
			continue
		this_forward_list = forward_list[this_name]
		for next_name in this_forward_list:
			if next_name == "last":
				continue
			next_pos = calculate_possibility (this_name, next_name, next_list, next_pos_matrix, 0, this_name, [])
			if next_pos >= global_similar_threshold:
				#this can save calculate resource
				prior_pos = calculate_possibility (next_name, this_name, prior_list, prior_pos_matrix, 0, next_name, [])
				if prior_pos >= global_similar_threshold :
					tmp = []
					tmp.append(this_name)
					tmp.append(next_name)
					merge_suggest_list.append(tmp)
					merge_start_list.append(this_name)
					break
				

	return merge_suggest_list

def optimize_merge_suggest_list (merge_suggest_list):
	length = len (merge_suggest_list)
	new_merge_list = []
	for i in range (0, length):
		if not merge_suggest_list[i] in new_merge_list:
			new_merge_list.append (merge_suggest_list[i])		
	merge_suggest_list = new_merge_list
	new_merge_list = []
	
	merge = 1
	while merge == 1:
		merge = 0
		i = 0
		length = len (merge_suggest_list)
		while i < length:
			j = 0
			merge_suggest = merge_suggest_list[i]
			this_start = merge_suggest[0]
			this_finish = merge_suggest[1]
			while j < length:
				other_merge_suggest = merge_suggest_list[j]
				if merge_suggest == other_merge_suggest:
					j = j + 1
					continue
				other_start = other_merge_suggest[0]
				other_finish = other_merge_suggest[1]

				if this_finish == other_start:
					merge = 1
					tmp = []
					tmp.append (this_start)
					tmp.append (other_finish)
					merge_suggest_list[i] = tmp
					del (merge_suggest_list[j])	
					length = len (merge_suggest_list)
				else:
					j = j + 1
			i = i + 1
	return merge_suggest_list

def block_list_remove_merged_block (block_list, global_multi_list, merge_suggest_list, erase_list):
	length = len (block_list)
	new_block_list = []
	multi_list = []
	recording = 0
	
	global_start = ""
	global_start_line = ""
	global_finish = ""
	global_finish_line = ""
	i = 0

	while i in range (0 , length) :
		block = block_list[i]
		block_name = block[0]
		block_start_line = block[1]
		block_finish_line = block[2]	
	
		if recording == 0:
			is_start = 0 
			for merge_suggest in merge_suggest_list:
				merge_start = merge_suggest[0]
				merge_finish = merge_suggest[1]
				if block_name == merge_start:
					is_start = 1
					recording = 1
					global_start = merge_start
					global_finish = merge_finish
					global_start_line = block_start_line
					global_finish_line = block_finish_line
			if is_start == 0:
				new_block_list.append(block)	
		else:
			global_finish_line = block_finish_line			
			if block_name == global_finish:
				#match finish
				if not i == length - 1: 
					next_block = block_list[i+1]
					next_block_name = next_block[0]
				else:
					next_block_name = ""
				if not next_block_name == block_name:
					#finish block name is not repeating
					recording = 0
					tmp = [] 
					tmp.append(global_start)
					tmp.append(global_start_line)
					tmp.append(global_finish_line)
					new_block_list.append(tmp)
					if block_name in global_multi_list:
						#if merging {0, 4} and {4, 8} is multi, must make {0, 8} to be multi
						tmp = global_multi_list[block_name]
						multi_finish = tmp[1]
						tmp = []
						tmp.append(global_start)
						tmp.append(multi_finish)
						global_multi_list[global_start] = tmp
						del(global_multi_list[block_name])

					if not block_name in erase_list and not block_name in multi_list:
						erase_list.append(block_name)
				else:
					#finish is repeating: 7 8 8 8 8
					if not block_name in multi_list:
						multi_list.append(block_name)
					if not global_start in global_multi_list:
						tmp = []
						tmp.append(global_start)
						tmp.append(block_name)
						global_multi_list[global_start] = tmp
			else:
				#no match finish but recording, add to erase list
				if block_name not in erase_list:
					if not global_start == block_name and block_name not in multi_list:
						erase_list.append(block_name)
							
							
		i = i + 1
	
	for erase in erase_list:
		if erase in global_multi_list:
			multi_finish = global_multi_list[erase][1]
			erase_list.append (multi_finish)

	for merge in merge_suggest_list:
		merge_name = merge[0]
		if merge_name in erase_list:
			for i in range (0, len(erase_list) - 1):
				if erase_list[i] == merge_name:
					del erase_list[i]
	
	if recording == 1:
		tmp = [] 
		tmp.append(global_start)
		tmp.append(global_start_line)
		tmp.append(global_finish_line)
		new_block_list.append(tmp)
	
	length = len (erase_list)
	erase_list_tmp = {}
	
	for i in range (0, length):
		erase = erase_list[i]
		erase_list_tmp [erase] = ""


	for block in new_block_list:
		block_name = block[0]
		if block_name in erase_list_tmp:
			del erase_list_tmp[block_name]
	erase_list = []
	for erase in erase_list_tmp:
		erase_list.append(erase)

	tmp = []
	tmp.append(new_block_list)
	tmp.append(erase_list)
	tmp.append(global_multi_list)
	return tmp
#}}}


#block_list merge entry:
#get_block_list_merge_suggest_list
#update_block_list_and_database
#do not change anything inside 
#{{{
def get_block_list_merge_suggest_list (block_list):
	merge_suggest_list = try_find_merge_candidate (block_list)
	print "init merge suggest"
	print merge_suggest_list
	merge_suggest_list = optimize_merge_suggest_list (merge_suggest_list)
	print "optimized merge suggest"
	print merge_suggest_list

	return merge_suggest_list	

def update_block_list_and_database (block_list, block_database, global_multi_list = {}):
	while True:
		merge_suggest_list = get_block_list_merge_suggest_list (block_list)
		erase_list = []
		for merge in merge_suggest_list:
			if merge[0] in global_multi_list:
				tmp = global_multi_list[merge[0]]
				if not tmp[1] in erase_list:
					erase_list.append(tmp[1])
				del (global_multi_list[merge[0]])
		#merging {17, 19}, remove {17, 18} from global_multi_list
		#if 19 is multi, then {17, 19} will be add to global_multi_list in function block_list_remove_merged_block
	
		length = len(merge_suggest_list)
		if length == 0:
			break
		else:	
			result = block_list_remove_merged_block(block_list, global_multi_list, merge_suggest_list, erase_list)
			block_list = result[0]
			erase_list = result[1]
			global_multi_list = result[2]

		#update:
		for merge in merge_suggest_list:
			start_block = merge[0]
			if start_block in global_multi_list:
				continue
			else:
				#need update
				finish_block = merge[1]
				tmp = {}
				start_block_database = block_database[start_block] 
				finish_block_database = block_database[finish_block]
				start_block_start =  start_block_database ["start"]
				finish_block_finish = finish_block_database ["finish"]
				tmp["start"] = start_block_start  
				tmp["finish"] = finish_block_finish 
				if "start_line" in start_block_database:
					start_block_start_line =  start_block_database ["start_line"]
					finish_block_finish_line = finish_block_database ["finish_line"]
					tmp["start_line"] = start_block_start_line  
					tmp["finish_line"] = finish_block_finish_line  
				block_database[start_block] = tmp
		#erase must done after database updated
		for erase in erase_list:
			if erase in block_database:
				del block_database[erase]
		print "erase list"
		print erase_list
		#attention:
		#multi block "block_0" is a unique name, but have different status in different lists.
		#in global multi list, block_0 is "block_0": {block_0, block_8}
		#in block_database, we will have two blocks, block_0 and block_8
		#when analyzing block from orig log file, we will get block_0 and block_8. and all other lines between block_0 and block_8 will be ignored. we may get block_0, block_8, block_8 (block_8 multi times)
		#after the first analyze, the blocks from block_0 to the last one of continuous block_8 will be replaced by "block_0"

	tmp = []
	tmp.append(block_list)	
	tmp.append(block_database)
	tmp.append(global_multi_list)	
	return tmp	

#}}}


def merge_debug (block_list, start_block, finish_block):
	
	#for block in block_list:
	#	print block


	next_list = gen_next_list (block_list)
	prior_list = gen_prior_list (block_list)
	next_pos_matrix = gen_pos_matrix (next_list)
	prior_pos_matrix = gen_pos_matrix (prior_list)
	print "next_list"
	print next_list
	print "prior_list"
	print prior_list
	print "next_pos_matrix"
	print next_pos_matrix
	print "prior_pos_matrix"
	print prior_pos_matrix
	


	print "begin debug"
	tmp = ""
	tmp += start_block
	tmp += " vs "
	tmp += finish_block
	print tmp
	print "start block next list"
	print next_list[start_block]
	print "finish block prior list"
	print prior_list[finish_block]
	print "start block next matrix"
	start_block_next_matrix = next_pos_matrix[start_block]
	for next_ele in next_list[start_block]:
		print next_ele
		print start_block_next_matrix[next_ele]


	print "finish block prior matrix"
	finish_block_prior_matrix = prior_pos_matrix[finish_block]
	for prior_ele in prior_list[finish_block]:
		print prior_ele
		print finish_block_prior_matrix[prior_ele]

	print "next poss"
	print calculate_possibility (start_block, finish_block, next_list, next_pos_matrix, 0, start_block, [], 0)
	print "prior poss"
	print calculate_possibility (finish_block, start_block, prior_list, prior_pos_matrix, 0, finish_block, [], 0)


def block_merge_debug (input_file):
	block_list = report_APIs.block_list_file_read(input_file)
	merge_suggest_list = get_block_list_merge_suggest_list(block_list)
	forward_list = gen_forward_list (block_list)
	print "forward_list"
	print forward_list
#	merge_debug(block_list, "block_35", "block_42")
#	merge_debug(block_list, "block_39", "block_42")
#	merge_debug(block_list, "block_35", "block_39")






	








