#!/usr/bin/python
#coding:utf-8

import os
import sys
import shutil
import global_APIs
import report_APIs
import block_database_opt
import block_database_learner
import input_file_block_analyzer 
import preliminary_block_list_gen


file_mix_limit = 20
def multi_cv_list_create (folder_name):
	if not os.path.isdir("multi_cv_tmp_folder"):
		os.mkdir("multi_cv_tmp_folder")	
	
	print folder_name
	folder_name = global_APIs.get_real_folder_name (folder_name)
	
	file_list = global_APIs.get_folder_file_list(folder_name)

	train_file_list = []
	test_file_list = []
	for file_name in file_list:
		tmp_file_list = []
		for tmp_file in file_list:
			if not tmp_file == file_name:	
				tmp_file_list.append(tmp_file)
			
		total_file_name = "multi_cv_tmp_folder/mixed_file_without_"
		total_file_name += global_APIs.get_real_file_name(file_name)
		total_file_name += ".txt"
		total_fl = open(total_file_name, "w")
		for tmp_file in tmp_file_list:
			fl = open (tmp_file, "r")
			while True:
				line = fl.readline()
				if not line:	
					break
				total_fl.write(line)	
			fl.close()	
		total_fl.close()
		train_file_list.append(total_file_name)
		test_file_list.append(file_name)

	return [test_file_list, train_file_list]


def multi_file_learning_folder_gen (folder_name):
	if os.path.isdir(folder_name + "/tmp/"):
		shutil.rmtree (folder_name + "/tmp/")
	
	folder_name = global_APIs.get_real_folder_name (folder_name)
	file_list = global_APIs.get_folder_file_list(folder_name)

	os.mkdir(folder_name + "/tmp/")

	file_count = 0
	total_file_count = 0
	for file_name in file_list:
		print "file name"
		print file_name
		total_file_name = folder_name
		total_file_name += "/tmp/" 
		total_file_name += global_APIs.get_real_file_name(folder_name)
		total_file_name += "_" 
		total_file_name += str(total_file_count) 
		total_file_name += ".txt"
	
		if not os.path.isfile(total_file_name):
			total_fl = open(total_file_name, "w")
		else:
			total_fl = open(total_file_name, "a")
			
		fl = open (file_name, "r")
		while True:
			line = fl.readline()
			if not line:	
				break
			total_fl.write(line)	
		fl.close()	
		total_fl.close()


		file_count += 1
		if file_count == file_mix_limit:
			file_count = 0 
			total_file_count += 1

def folder_single_line_pattern_learning (folder_name):
	folder_name = global_APIs.get_real_folder_name (folder_name)
	
	file_list = global_APIs.get_folder_file_list(folder_name)
	file_mode = global_APIs.get_file_mode(file_list[0])	

	error_list = {}
	block_pattern_list = {}
	block_num = 0
	pattern_index_list = {}


	for input_file in file_list:
		fl = open (input_file, "r")
		single_line_pattern_list = {}
		while True:
			line = fl.readline()
			if not line:	
				break
			line_message = 	global_APIs.get_line_message(line)
			if line_message == "":
				continue
			line_pattern = global_APIs.gen_line_pattern(line_message)
			correspond_pattern_index = preliminary_block_list_gen.gen_pattern_index(line_pattern)
			if not correspond_pattern_index in pattern_index_list:
				pattern_index_list[correspond_pattern_index] = ""
				
				tmp = {}
				tmp["start"] = line_pattern	
				tmp["finish"] =	line_pattern	
				block_name = "block_"
				block_name += str(block_num)
				block_pattern_list[block_name] = tmp
				block_num = block_num + 1
		fl.close()	

	block_database_opt.block_database_store(block_pattern_list, file_mode)
	block_database_opt.block_multi_store({}, file_mode)


def folder_learning (folder_name):
#this must be in multi file folder
	folder_name = global_APIs.get_real_folder_name (folder_name)
	
	file_list = global_APIs.get_folder_file_list(folder_name)
	
	error_list = {}
	done_learning_file_folder = "done_learning_file_folder"
	if not os.path.isdir(done_learning_file_folder):
		os.mkdir(done_learning_file_folder)

	total_progress_fl = open("total_progress_report.txt", "w")

	for input_file in file_list:
		print "learn"
		print input_file
		

		shutil.copy(input_file, done_learning_file_folder)
		tmp = "Learning "
		tmp += input_file
		tmp += "\n" 
		total_progress_fl.write(tmp)



		file_mode = global_APIs.get_file_mode (input_file)
		have_database = global_APIs.test_have_database(file_mode)
		if have_database == -1:
			block_database_learner.block_database_learning (input_file)
		else:
			block_database = block_database_opt.block_database_read(file_mode, str(have_database))
			global_multi_list = block_database_opt.multi_database_read(file_mode, str(have_database))
			
			total_file = "total_tmp_learning_file"
			total_fl = open(total_file, "w")
			done_learning_list = global_APIs.get_folder_file_list(done_learning_file_folder)
			
			for done_file in done_learning_list:
				tmp_fl = open (done_file, "r")
				while True:
					line = tmp_fl.readline()
					if not line:
						break
					total_fl.write(line)
				tmp_fl.close()
			total_fl.close()
			
			block_list = input_file_block_analyzer.block_analyze(total_file, block_database, global_multi_list, 1)
			error_report = global_APIs.analyze_error_list_file("error_report.txt")

			#delete conflict DB
			for error in error_report:
				print "delete " + error
				if error in block_database:
					del (block_database[error])
				if error in global_multi_list:
					del (global_multi_list[error])
			block_database_opt.block_database_store(block_database, file_mode)
			block_database_opt.block_multi_store(global_multi_list, file_mode)
			
			block_database_learner.block_database_learning (total_file)
			os.remove(total_file)	
	
	total_progress_fl.close()
			


def folder_analyzing (folder_name):
	folder_name = global_APIs.get_real_folder_name (folder_name)
	
	file_list = global_APIs.get_folder_file_list(folder_name)
	total_block_length = 0
	total_covered_line = 0
	total_line_num = 0
	total_valid_num = 0
	
	total_block_length_summary_list = {}
	total_block_length_result_list = []

	for input_file in file_list:
		file_mode = global_APIs.get_file_mode (input_file)
		print "analyze"
		print input_file
		result = report_APIs.general_run_process (input_file, 1 )
		
		total_block_length = total_block_length + result[0] 
		total_covered_line = total_covered_line + result[1]
		total_line_num = total_line_num + result[2]
		total_valid_num = total_valid_num + result[3]
		block_list = result[4]
	
		summary_block_length (block_list, total_block_length_summary_list)

	for block in total_block_length_summary_list:
		tmp = total_block_length_summary_list[block]
		tmp[0] = tmp[0] / tmp[1]
		result_tmp = []
		result_tmp.append(block)
		result_tmp.append(tmp[0])
		total_block_length_result_list.append(result_tmp)
		



	report_tmp = []
	report_tmp.append("total block number:")
	report_tmp.append(total_block_length)
	report_tmp.append("total covered lines:")
	report_tmp.append(total_covered_line)
	report_tmp.append("total lines:")
	report_tmp.append(total_line_num)
	report_tmp.append("total valid lines:")
	report_tmp.append(total_valid_num)
	report_tmp.append("total number of block patterns:")
	have_database = global_APIs.test_have_database(file_mode)
	block_database = block_database_opt.block_database_read(file_mode, str(have_database))
	report_tmp.append(len(block_database))
	report_APIs.output_block_list_report(report_tmp, "total_result", 1)
	
	
	
	report_APIs.output_block_list_report(total_block_length_result_list, "block_length", 2)





def summary_block_length (block_list, total_block_length_summary_list ):
	for block in block_list:
		block_name = block[0]
		block_start = block[1]
		block_finish = block[2]
		if block_name in total_block_length_summary_list:
			tmp = total_block_length_summary_list[block_name]
			tmp[0] = tmp[0] + int(block_finish) - int(block_start) + 1
			tmp[1] = tmp[1] + 1
			total_block_length_summary_list[block_name] = tmp
		else: 
			tmp = []
			tmp.append(int(block_finish) - int(block_start) + 1)
			tmp.append(1)
			total_block_length_summary_list[block_name] = tmp

	return total_block_length_summary_list




#frontend APIs:
#log_file_split
#splited_folder_merge
#{{{
def splited_folder_merge (folder_name):
	folder_name = global_APIs.get_real_folder_name (folder_name)
	file_list = global_APIs.get_folder_file_list(folder_name)
	total_file_name = folder_name
	total_file_name += "_mixed.txt"
	total_fl = open(total_file_name, "w")

	for file_name in file_list:
		fl = open (file_name, "r")
		while True:
			line = fl.readline()
			if not line:	
				break
			total_fl.write(line)	
		fl.close()	
	
	total_fl.close()

def log_file_split (input_file):
	node_list = ""
	path = ""
	real_file_name = global_APIs.get_real_file_name(input_file)
	file_mode = global_APIs.get_file_mode (input_file)

	
	path = "splited_files/"
	if not os.path.isdir(path):
		os.mkdir(path)	
	
	path += file_mode
	path += "/"
	if not os.path.isdir(path):
		os.mkdir(path)	
	
	path += real_file_name

	if os.path.isdir(path):
		shutil.rmtree (path)
	os.mkdir(path)	
	
	fl = open (input_file, "r")
	while True:
		line = fl.readline()
		if not line:	
			break
		node_id = global_APIs.get_line_id (line)
		node_output_name = path 
		node_output_name += "/"
		node_output_name += real_file_name
		node_output_name += "_"
		node_output_name += node_id
		node_output_name += ".txt" 
		if os.path.isfile (node_output_name):
			node_fl = open (node_output_name, "a")
		else :
			node_fl = open (node_output_name, "w")
		
		node_fl.write(line)
		node_fl.close()
	
	fl.close()	
	return path

#}}}
