#!/usr/bin/python
#coding:utf-8

import os
import sys
import re 
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
	pattern_index_list = {}
	single_line_pattern_list = {}


	for input_file in file_list:
		fl = open (input_file, "r")
		while True:
			line = fl.readline()
			if not line:	
				break
			line_message = 	global_APIs.get_line_message(line)
			if line_message == "":
				continue
			line_pattern = "" 
			if not global_APIs.is_baler_mutrino_format(line):
				line_pattern = global_APIs.gen_line_pattern(line_message)
			else:
				line_pattern = global_APIs.gen_baler_line_pattern (line)
			correspond_pattern = preliminary_block_list_gen.search_correspond_pattern_from_single_line_pattern_list (line_pattern, single_line_pattern_list)
			if correspond_pattern == "":
				line_pattern_index = preliminary_block_list_gen.gen_pattern_index(line_pattern)
				tmp = {}
				tmp["pattern"] = line_pattern
				single_line_pattern_list[line_pattern_index] = tmp
					
		fl.close()	
	
	block_num = 0
	for line_pattern in single_line_pattern_list:
		single_line_pattern = single_line_pattern_list[line_pattern]
		pattern = single_line_pattern["pattern"]	
		tmp = {}
		tmp["start"] = pattern	
		tmp["finish"] =	pattern	
		block_name = "block_"
		block_name += str(block_num)
		block_pattern_list[block_name] = tmp
		block_num = block_num + 1

	block_database_opt.block_database_store(block_pattern_list, file_mode)
	block_database_opt.block_multi_store({}, file_mode)

def folder_database_self_growing(folder_name):
	folder_name = global_APIs.get_real_folder_name (folder_name)
	file_list = global_APIs.get_folder_file_list(folder_name)
	done_file_list = []

	done_learning_file_folder = "done_learning_file_folder"
	if not os.path.isdir(done_learning_file_folder):
		os.mkdir(done_learning_file_folder)
	done_learning_file_dataset_folder = done_learning_file_folder + "/dataset/"
	if not os.path.isdir(done_learning_file_dataset_folder):
		os.mkdir(done_learning_file_dataset_folder)
	done_learning_file_EB_folder = done_learning_file_folder + "/EB_list/"
	if not os.path.isdir(done_learning_file_EB_folder):
		os.mkdir(done_learning_file_EB_folder)
	
	done_file_folder_list = global_APIs.get_folder_file_list(done_learning_file_dataset_folder)
	
	for file_name in done_file_folder_list:
		file_name = global_APIs.get_real_file_name(file_name)
		done_file_list.append(file_name)

	total_line_count = 0
	total_covered_count = 0
	average_cover_precent = 0.90
	total_file = "total_tmp_learning_file"

	total_progress_fl = open("total_progress_report.txt", "w")
	total_progress_fl.write("test begin\n")
	total_progress_fl.close()
	
	total_num = 0	
	for input_file in file_list:
		total_num += 1
		if global_APIs.get_real_file_name(input_file) in done_file_list:
			continue
		else:
			done_file_list.append(global_APIs.get_real_file_name(input_file))
		total_progress_fl = open("total_progress_report.txt", "a")
		print "learning " + input_file
		total_progress_fl.write("Analyzing " + input_file + "\n")	
		total_progress_fl.write("================================\n")
		total_progress_fl.write("total_num = " + str(total_num) + "\n")
			
		
		file_mode = global_APIs.get_file_mode (input_file)
		have_database = global_APIs.test_have_database(file_mode)
		input_file_covered_line_count = 0
		input_file_line_count = 0
		input_file_cover_precent = 0.0

		need_relearn = 0
		have_conflict = 0
		if have_database == -1:
			total_progress_fl.write("	No database, initial learn.\n")	

			block_database_learner.block_database_learning (input_file)
			input_file_block_result = report_APIs.general_run_process (input_file, 1 )
			input_file_covered_line_count = input_file_block_result[1]
			input_file_line_count = input_file_block_result[2]
			input_file_cover_precent = float(input_file_covered_line_count)/float(input_file_line_count)
			input_file_cover_precent = round(input_file_cover_precent , 3)

		else: 
			input_file_block_result = report_APIs.general_run_process (input_file, 1 )
			input_file_covered_line_count = input_file_block_result[1]
			input_file_line_count = input_file_block_result[2]
			input_file_cover_precent = float(input_file_covered_line_count)/float(input_file_line_count)
			input_file_cover_precent = round(input_file_cover_precent , 3)
			have_conflict = global_APIs.detect_if_have_EB_extraction_conflict(total_progress_fl)
			


		if have_conflict == 1:	
			total_progress_fl.write("	Have conflict.\n")	
			#erase conflict block pattern
			global_APIs.erase_conflict_block_based_on_error_report(input_file)
			need_relearn = 1
		total_progress_fl.write("	Coverage = " + str(input_file_cover_precent) + ".\n")	
		total_progress_fl.write("	Total Coverage = " + str(average_cover_precent) + ".\n")	
		
		if input_file_cover_precent < average_cover_precent:
			total_progress_fl.write("	Coverage " + str(input_file_cover_precent) + " lower than average " + str(average_cover_precent) + ".\n")	
			need_relearn = 1	
		
		if need_relearn == 1:
			total_progress_fl.write("	Re-learn\n")	
			shutil.copy(input_file, done_learning_file_dataset_folder)
		
			#block list is already there	
			block_list = input_file_block_result[4]
			report_APIs.output_block_list_report(block_list, input_file, 0, done_learning_file_EB_folder)
			block_database_learner.block_database_learning (input_file)
		

		have_conflict = 0
		total_progress_fl.close()
		
		

		#have_database = global_APIs.test_have_database(file_mode)
		#SLEBD_DB = block_database_opt.block_database_read(file_mode, str(have_database))
		#repeat_list = block_database_opt.repeat_db_test(SLEBD_DB)	
		


	print "Test done learning file conflict"
	result = folder_analyzing(done_learning_file_dataset_folder)
	have_conflict = result["have_conflict"]
	if have_conflict == 1:
		total_progress_fl = open("total_progress_report.txt", "a")
		total_progress_fl.write("merge done but have conflict\n" )	
		#here the final round merge still have conflict, we still need one round merge
		#database learning is on all the learning files, but still have chance to have conflict blocks
		#after erase conflict blocks, coverage will be lower than it should be
		#so I need to relearn one more time
		total_progress_fl.write("final verify")	
		total_progress_fl.write("================================\n")	
		total_tmp_learning_file_gen (total_file, done_learning_file_dataset_folder)
		block_database_learner.block_database_learning (total_file)
		os.remove(total_file)	

		total_progress_fl.close()

	
def total_tmp_learning_file_gen(total_file_name, folder_name ):

	error_report = global_APIs.analyze_error_list_file("error_report.txt")
	single_error_report = error_report[0]
	multi_error_report = error_report[1]
	
	#{{{
	total_fl = open(total_file_name, "w")
	done_learning_list = global_APIs.get_folder_file_list(folder_name)
	
	for done_file in done_learning_list:
		tmp_fl = open (done_file, "r")
		while True:
			line = tmp_fl.readline()
			if not line:
				break
			total_fl.write(line)
		tmp_fl.close()
	total_fl.close()
	#}}}

				
def folder_analyzing (folder_name, erase_conflict = 0):
	folder_name = global_APIs.get_real_folder_name (folder_name)
	
	file_list = global_APIs.get_folder_file_list(folder_name)
	total_block_length = 0
	total_covered_line = 0
	total_line_num = 0
	total_valid_num = 0
	
	total_block_length_summary_list = {}
	total_block_length_result_list = []
	
	total_report_file_name = "folder_analyzing_total_report.txt"
	
	total_fl = open(total_report_file_name, "w")
	total_fl.write("test begin \n")
	total_fl.close()
        have_conflict = 0

	for input_file in file_list:
		file_mode = global_APIs.get_file_mode (input_file)
		if file_mode == "":
			continue
		#print "analyze"
		#print input_file
		result = report_APIs.general_run_process (input_file, 1 )
		
		total_block_length = total_block_length + result[0] 
		total_covered_line = total_covered_line + result[1]
		total_line_num = total_line_num + result[2]
		total_valid_num = total_valid_num + result[3]
		block_list = result[4]
	
		summary_block_length (block_list, total_block_length_summary_list)
		have_conflict = global_APIs.detect_if_have_EB_extraction_conflict ()          

		if erase_conflict == 1 and have_conflict == 1:
                        global_APIs.erase_conflict_block_based_on_error_report (input_file)   
		total_fl = open (total_report_file_name, "a")
		total_fl.write ("analyzing " + input_file + "\n")
		total_fl.write ("===========================\n")
		total_fl.write ("	coverage: " + str(float(result[1]) / float(result[2])) + "\n")
		
		error_report = global_APIs.analyze_error_list_file("error_report.txt")
		single_error_report = error_report[0]
		multi_error_report = error_report[1]
				
		for error in single_error_report:
			total_fl.write ("	single error " + error + "\n")
		for error in multi_error_report:
			total_fl.write ("	multi error " + error + "\n")
		
		total_fl.write ("\n")
		total_fl.close()


		

	for block in total_block_length_summary_list:
		tmp = total_block_length_summary_list[block]
		tmp[0] = tmp[0] / tmp[1]
		result_tmp = []
		result_tmp.append(block)
		result_tmp.append(tmp[0])
		total_block_length_result_list.append(result_tmp)
		
	if file_mode == "":
		file_mode = "mutrino"


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


	output_report = {}
	output_report["total_block_number"] = total_block_length
	output_report["total_covered_lines"] = total_covered_line 
	output_report["total_lines"] = total_line_num 
	output_report["total_valid_lines"] = total_valid_num
	output_report["have_conflict"] = total_valid_num
	return output_report 



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
#sub_path_list_detector
#find_sub_path_console_log
#{{{
def whole_dataset_folder_gen_daily_log_file(folder_name):
#{{{
	sub_path_list = sub_path_list_detector(folder_name)
	wanted_file_num = 600 
	log_list = find_sub_path_console_log (sub_path_list, wanted_file_num)

	path = "console_log_daily_file/"
	if os.path.isdir(path):
		shutil.rmtree (path)
	os.mkdir(path)
	file_count = 1 	
	folder_count = 0
	for file_name in log_list:
		tmp_path = path
		tmp_path += str(folder_count)
		tmp_path += "/"
		if not os.path.isdir(tmp_path):
			os.mkdir(tmp_path)
			
		result = log_file_split(file_name)
		mixed_file_name = tmp_path
		mixed_file_name += "/"
		mixed_file_name += str(file_count)
		mixed_file_name += ".txt"
		splited_folder_merge(result, mixed_file_name)
		file_count += 1
		shutil.rmtree (result)
		if (file_count - 1 ) % 50 == 0 and not file_count == 1:
			folder_count += 1
#}}}	
	
def whole_dataset_folder_gen_daily_node_log_file(folder_name):
	sub_path_list = sub_path_list_detector(folder_name)
	total_wanted_file_num = 600 
	file_step = 20
	folder_count = 0
	path = "console_log_single_node_file"
	if os.path.isdir(path):
		shutil.rmtree (path)
	os.mkdir(path)	
	while folder_count < total_wanted_file_num/file_step :
		ignore_file_num = file_step * folder_count
		wanted_file_num = file_step * (folder_count + 1) 
		log_list = find_sub_path_console_log (sub_path_list, wanted_file_num, ignore_file_num)
		if log_list == []:
			break
		tmp_path = path
		tmp_path += "/"
		tmp_path += str(folder_count)
		if os.path.isdir(tmp_path):
			shutil.rmtree (tmp_path)
		os.mkdir(tmp_path)	
		whole_dataset_folder_gen_single_node_log_file(folder_name, wanted_file_num, ignore_file_num, tmp_path, str(folder_count))
		folder_count += 1
	

def whole_dataset_folder_gen_single_node_log_file(folder_name, wanted_file_num = 600, ignore_file_num = 0, path = "console_log_single_node_file", file_prefix = ""):
	sub_path_list = sub_path_list_detector(folder_name)
	log_list = find_sub_path_console_log (sub_path_list, wanted_file_num, ignore_file_num)

	if os.path.isdir(path):
		shutil.rmtree (path)
	os.mkdir(path)	
	
	node_list = {} 

	for file_name in log_list:
		fl = open (file_name, "r")
		while True:
			line = fl.readline()
			if not line:	
				break
			node_id = global_APIs.get_line_id (line)
			node_output_name = path 
			node_output_name += "/"
			if not file_prefix == "":
				node_output_name += file_prefix
				node_output_name += "_"
			
			node_output_name += node_id
			node_output_name += ".txt" 
			if not node_id in node_list:
				node_fl = open(node_output_name, "w")
				node_list[node_id] = node_fl	
			node_fl = node_list[node_id]
			node_fl.write(line)
		fl.close
	
	for node_id in node_list:
		node_fl = node_list[node_id]
		node_fl.close()
		

def sub_path_list_detector (folder_name):
	folder_list = [] 
	folder_list_1 = [] 
	
	pattern = r'p0-([0-9]+)t([0-9]+)$'		
	for filename in os.listdir (folder_name):
		#p0-20150218t105253

		matchobj = re.match (pattern, filename)
		if matchobj:
			folder_list.append (filename)		
	
	while not len (folder_list) == 0: 
		min_pos = 0
		min_date = 20209999
		min_time = 999999
		min_folder_name = ""
		for i in range (0, len(folder_list)):
			sub_folder_name = folder_list[i]
			matchobj = re.match (pattern, sub_folder_name)
			date = matchobj.group(1)
			time = matchobj.group(2)
			if int(date) < min_date:
				min_pos = i
				min_date = int(date)
				min_time = int(time)
				min_folder_name = sub_folder_name
			if int(date) == min_date and int(time) < min_time :
				min_pos = i
				min_time = int(time)
				min_folder_name = sub_folder_name
		tmp = folder_name
		tmp += "/"
		tmp += min_folder_name
		folder_list_1.append (tmp)
		del(folder_list[min_pos])	

	return folder_list_1

def find_sub_path_console_log (sub_folder_list, max_file_count = 10, ignore_file_count = 0):
	pattern = r'console-([0-9]+).cleansed$'
	file_count = 0
	total_needed_file_list = []	
	for sub_folder_name in sub_folder_list:
		#console-20150211.cleansed
		console_file_list = []	
		for filename in os.listdir (sub_folder_name):
			matchobj = re.match (pattern, filename)
			if matchobj:
				console_file_list.append (filename)
		while not len (console_file_list) == 0: 
			min_pos = 0
			min_date = 99999999
			min_console_name = ""
			for i in range (0, len(console_file_list)):
				console_file_name = console_file_list[i]
				matchobj = re.match (pattern, console_file_name)
				date = matchobj.group(1)
				if int(date) < min_date:
					min_pos = i
					min_date = int(date)
					min_console_name = console_file_name
			tmp = sub_folder_name
			tmp += "/"
			tmp += min_console_name
			if file_count >= ignore_file_count:
				total_needed_file_list.append (tmp)
			del(console_file_list[min_pos])
			file_count += 1 
			if file_count >= max_file_count:
				break	
				
		if file_count >= max_file_count:
			break	
	return total_needed_file_list

def splited_folder_merge (folder_name, file_name = ""):
	folder_name = global_APIs.get_real_folder_name (folder_name)
	file_list = global_APIs.get_folder_file_list(folder_name)
	if file_name == "":
		total_file_name = folder_name
		total_file_name += "_mixed.txt"
	else:
		total_file_name = file_name
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
