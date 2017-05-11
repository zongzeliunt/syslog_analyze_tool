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
import python_code.block_list_analyzer as block_list_analyzer
import python_code.sequence_pattern_mining as sequence_pattern_mining



def main (cmd):
#################################################################
#step 1: generate common block list report from block list folder
	"""
	#cmd here is the folder name
	result = sequence_pattern_mining.multi_node_find_common_block_list (cmd)
	common_block_list = result[0]
	private_block_list = result[1]
	sequence_pattern_mining.multi_node_block_report_split(common_block_list, private_block_list, cmd)
	#this is for generate files don't have critical path
	sequence_pattern_mining.block_report_folder_remove_done_critical_path (cmd, left_candidate_list)

	"""
#################################################################
#step 2: folder read learning list
	record_sequences = sequence_pattern_mining.multi_file_folder_sequence_learning_list_read(cmd)
	result = sequence_pattern_mining.multi_file_sequence_prior_matrix_gen (record_sequences)
	prior_matrix = result[0]
	done_block_name_list = result[1]
	print "block total number"
	print len (done_block_name_list)

	#done block name list contains all block names we need to ananlyze
	#left_candidate_list = sequence_pattern_mining.generate_critical_path(done_block_name_list, prior_matrix)
	total_result = sequence_pattern_mining.topology_path_find(done_block_name_list, prior_matrix)
	print record_sequences[3]
	sequence_pattern_mining.sub_path_list_verify_2 (total_result , record_sequences[3])
		

	"""
	for sub_list in total_result:
		sequence_pattern_mining.sub_path_list_verify_2 (sub_list , record_sequences[0])
		sequence_pattern_mining.sub_path_list_verify_2 (sub_list , record_sequences[1])
		sequence_pattern_mining.sub_path_list_verify_2 (sub_list , record_sequences[2])
		sequence_pattern_mining.sub_path_list_verify_2 (sub_list , record_sequences[3])
	"""

	
	"""
	status_matrix = sequence_pattern_mining.gen_status_matrix_based_on_prior_matrix(done_block_name_list, prior_matrix)
	
	done_block_name_list = ['block_106','block_75', 'block_22', 'block_72', 'block_73' ]
	sub_path_list = sequence_pattern_mining.find_sub_path (done_block_name_list, status_matrix, prior_matrix)
	print sub_path_list
	
	done_block_name_list = ['block_106','block_75', 'block_22', 'block_73', 'block_72' ]
	sub_path_list = sequence_pattern_mining.find_sub_path (done_block_name_list, status_matrix, prior_matrix)
	print sub_path_list
	
	growing_pattern = [ 'block_22', 'block_73', 'block_75','block_106']
	insert_pos =  sequence_pattern_mining.search_sub_block_insert_into_growing_pattern_position_1 (growing_pattern, "block_72", status_matrix)
	print insert_pos
	new_list = list(growing_pattern)
	new_list.insert(insert_pos, "block_72")
	print new_list
	
	growing_pattern = [ 'block_22', 'block_72', 'block_75','block_106']	
	insert_pos = sequence_pattern_mining.search_sub_block_insert_into_growing_pattern_position_1 (growing_pattern, "block_73", status_matrix)
	print insert_pos
	new_list = list(growing_pattern)
	new_list.insert(insert_pos, "block_73")
	print new_list
	"""

	
	


input_file = sys.argv[1]
if not os.path.isfile(input_file):
	print "no file"
main(input_file)
