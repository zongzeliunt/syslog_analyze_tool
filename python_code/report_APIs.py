#!/usr/bin/python
import global_APIs
import block_database_opt
import input_file_block_analyzer as input_file_block_analyzer
import block_merger 
import operator
import re 

def dump_block_example (block_database, input_file, block_list):
	report_file = "block_report/"
	report_file += global_APIs.get_real_file_name(input_file)
	report_file += "_block_examples.txt"
	fl = open (input_file, "r")
	report_fl = open (report_file, "w")
	report_fl.write("Block example file\n")
	report_fl.write("Block learned from file: ")
	report_fl.write(input_file)
	report_fl.write("\n")
	line_counter = 0
	total_block_name_list = {}
	for block in block_database:
		total_block_name_list[block] = ""
	total_line_count = 1
	while total_block_name_list != {}:
		for block in block_list:
			block_name = block[0]
			block_start_line = int(block[1])
			block_finish_line = int(block[2]) 
			if block_name in total_block_name_list:
				report_fl.write (block_name + ":\n")
				while total_line_count < block_start_line:
				    	line = fl.readline()
					total_line_count = total_line_count + 1	
				while total_line_count <= block_finish_line:
				    	line = fl.readline()
					report_fl.write (line)
					total_line_count = total_line_count + 1	

				report_fl.write ("\n")
				del(total_block_name_list[block_name]) 
			else:
				continue
		break
	report_fl.close()
	fl.close()


def general_run_process (input_file, dump_error_file = 0 ):
#{{{
	#detect block database
	#learn block list
	#output report
	print "general run " + input_file
	file_mode = global_APIs.get_file_mode (input_file)
	block_list = input_file_block_analyzer.input_file_block_analyze(input_file, dump_error_file)
	block_happen_count_list = count_block_happen_time (block_list)

	
	#if want to do timeframe analyze, we need to add time index first.
	#block_list = timeframe_analyze.add_time_index_into_block_list (block_list, input_file)
	#timeframe_analyze_main(block_list)


	############################################################################
	#below this line output everything
		
	#print "block list"
	#for block in block_list:
	#	print block
	#print " "

	dump_uncovered_valid_line (block_list, input_file)



	output_block_list_report(block_list, input_file)
	
	report_tmp = []
	report_tmp.append("total block number:")
	report_tmp.append(len(block_list))
	report_tmp.append("total covered lines:")
	total_covered_line = calculate_coverage(block_list)
	report_tmp.append(total_covered_line)
	
	result = calculate_valid_line(input_file)
	total_line_num = result[0]
	total_valid_num = result[1]
	report_tmp.append("total lines:")
	report_tmp.append(total_line_num)
	report_tmp.append("total valid lines:")
	report_tmp.append(total_valid_num)

	report_tmp.append("total number of block patterns:")
	have_database = global_APIs.test_have_database(file_mode)
	block_database = block_database_opt.block_database_read(file_mode, str(have_database))
	report_tmp.append(len(block_database))
	output_block_list_report(report_tmp, input_file, 1)
	dump_block_example(block_database ,input_file, block_list)
	
	tmp = []
	tmp.append(len(block_list))
	tmp.append(total_covered_line)
	tmp.append(total_line_num)
	tmp.append(total_valid_num)
	tmp.append(block_list)

	return tmp
#}}}


def dump_uncovered_valid_line (block_list, input_file):
	if len(block_list) == 0:
		return
	report_file = "block_report/uncovered_valid_line.txt"
	fl = open (input_file, "r")
	report_fl = open (report_file, "w")
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
			#uncovered
			line_message = global_APIs.get_line_message (line)
			pattern = "" 
			if not global_APIs.is_baler_mutrino_format(line):
				pattern = global_APIs.gen_line_pattern(line_message)
			else:
				pattern = global_APIs.gen_baler_line_pattern (line)
			if not len(pattern) == 0:
			#valid line
				report_fl.write(line)
		else:
			finish_line_num = correspond_block[2]
			while line_counter < int(finish_line_num):
				line = fl.readline()
				line_counter = line_counter + 1

			if not block_list_count == len(block_list) - 1: 
				block_list_count = block_list_count + 1
		
	

	fl.close()
	report_fl.close()

def block_list_file_read (input_file):
	fl = open(input_file, "r")
	block_list = []
	for line in fl.readlines():
		line = line.split(" ")
		line [2] = line[2].replace("\n", "")	
		block_list.append(line)
	return block_list	

def output_block_list_report (block_list, input_file, mode = 0, report_file_path = "block_report/"):
	file_name = global_APIs.get_real_file_name (input_file)
	report_file = report_file_path
	report_file += file_name


	if mode == 0:
		report_file += "_block_report.txt"
		fl = open (report_file, "w")
		for block in block_list:
			tmp = ""
			for i in range (0, len(block)):
				tmp = tmp + str(block[i]) + " "
			
			fl.write(tmp)
			fl.write("\n")	
		fl.close() 
	elif mode == 1:
		report_file += "_summary.txt"
		fl = open (report_file, "w")
		for block in block_list:
			block = str(block)
			fl.write(block)
			fl.write("\n")	
		fl.close() 
	elif mode == 2:
		report_file += "_other_report.txt"
		fl = open (report_file, "w")
		for block in block_list:
			tmp = ""
			for i in range (0, len(block)):
				tmp = tmp + str(block[i]) + " "
			
			fl.write(tmp)
			fl.write("\n")	
		fl.close() 
		

def block_database_summary (file_mode):
	have_database = global_APIs.test_have_database(file_mode)
	block_database = block_database_opt.block_database_read(file_mode, str(have_database))
	single_block = 0
	multi_block = 0
	for block_name in block_database:
		block = block_database[block_name]
		start = block["start"]
		finish = block["finish"]
		if start == finish:
			single_block = single_block + 1
		else:
			multi_block = multi_block + 1
	print len(block_database)
	print single_block
	print multi_block
 

#summary
#count_block_happen_time
#calculate_coverage
#calculate_valid_line
#{{{
def block_list_happen_count(block_list):
	block_happen_count_list = {}
	for block in block_list:
		block_name = block[0]
		if block_name in block_happen_count_list:
			block_happen_count_list[block_name] += 1
		else:
			block_happen_count_list[block_name] = 1
	return 	block_happen_count_list

def count_block_happen_time (block_list):
	block_happen_count_list = block_list_happen_count(block_list)
	count_list = {}
	for block in block_happen_count_list:
		if block_happen_count_list[block] in count_list:
			count_list[block_happen_count_list[block]].append(block)
		else:
			count_list[block_happen_count_list[block]] = []
			count_list[block_happen_count_list[block]].append(block)
	return count_list

def calculate_coverage (block_list):
	total_line = 0
	for block in block_list:
		block_name = block[0]
		block_start = block[1]
		block_finish = block[2]
		total_line += int(block_finish) - int(block_start) + 1
	return total_line

def calculate_valid_line(input_file):
	fl = open (input_file, "r")
	total_line_num = 0
	total_valid_num = 0
	while True:
		line = fl.readline()
		if not line:	
			break
		line_message = global_APIs.get_line_message (line)
		total_line_num += 1
		pattern = "" 
		if not global_APIs.is_baler_mutrino_format(line):
			pattern = global_APIs.gen_line_pattern(line_message)
		else:
			pattern = global_APIs.gen_baler_line_pattern (line)
		
		if not len(pattern) == 0:
			total_valid_num += 1
		#else:
			#print "no valid pattern"
			#print line

	fl.close()	
	result = []
	result.append(total_line_num)
	result.append(total_valid_num)
	return result	
#}}}

def block_rength_other_report_analyze (input_file):
	fl = open(input_file, "r")
	count_list = {}
	for line in fl.readlines():
		line = line.split(" ")
		block_name = line[0]
		block_count = line[1]
		if block_count in count_list:
			count_list[block_count] += 1
		else:	
			count_list[block_count] = 1
	for count in count_list:
		print str(count) + " " + str(count_list[count])

	fl.close() 


def folder_analyze_result_log_conflict_detect (input_file):
	fl = open (input_file, "r")
	conflict_list = []
	for line in fl.readlines():
		#single error block_378
		pattern = r'(.*)single error block_([0-9]+)$'	
		matchobj = re.match (pattern, line)
		if matchobj:
			conflict_name = matchobj.group(2)
			if not conflict_name in conflict_list:
				conflict_list.append(conflict_name)	
	print conflict_list
	print len(conflict_list) 
	fl.close() 

def multi_line_block_happen_count (folder_name):
	file_list = global_APIs.get_folder_file_list(folder_name)
	pattern = r'(.*)_block_report.txt$'
	single_count = 0
	multi_count = 0
	total_block_count_1 = 0
	total_block_count_2 = 0
	for file_name in file_list:
		matchobj = re.match (pattern, file_name)
		if not matchobj:
			continue
		if global_APIs.get_real_file_name(file_name) == "total_tmp_learning_file_block_report.txt":
			continue
		block_list = block_list_file_read (file_name)
		print file_name
		print len(block_list)
		total_block_count_2 += len(block_list)
		for block in block_list:
			total_block_count_1 += 1
			start_line = block[1]	
			finish_line = block[2]
			if not finish_line == start_line:	
				multi_count += 1
			else:
				single_count += 1
	print total_block_count_1
	print total_block_count_2
	print single_count
	print multi_count

def block_report_folder_block_count_analyze (folder_name):
	file_list = global_APIs.get_folder_file_list(folder_name)
	pattern = r'(.*)_block_report.txt$'
	total_count = 0
	block_count_list = {}
	for file_name in file_list:
		matchobj = re.match (pattern, file_name)
		if not matchobj:
			continue
		block_list = block_list_file_read (file_name)
		total_count += len(block_list)
		block_happen_count_list = block_list_happen_count (block_list)
		for block in block_happen_count_list:
			if not block in block_count_list:
				block_count_list[block] = block_happen_count_list[block]
			else:
				block_count_list[block] += block_happen_count_list[block]
	tmp = []
	tmp.append(total_count)
	tmp.append(block_count_list) 	
	return tmp

def block_distribute_ratio_count (folder_name):
#{{{
	SLEBD_DB = block_database_opt.block_database_read("mutrino", "0")
#load SLEBD_DB here is for finding all block patterns
#database sorting
	block_pattern_list = []
	pattern = r'block_([0-9]+)$'
	sorted_block_name_list = []
	for block_name in SLEBD_DB:	
		matchobj = re.match (pattern, block_name)
		block_name_num = matchobj.group(1)
		sorted_block_name_list.append(int(block_name_num))
	sorted_block_name_list = sorted(sorted_block_name_list, reverse=False)
	
#database range detect
	range_control_num = 19
	#this is split into 20 parts
	#this control num is very important
	range_count = 0
	every_range_block_num = len(sorted_block_name_list)/range_control_num
	#len(block_count_list) is total block number, 737
	start_num = 0
	finish_num = 0
	range_list = []
	for block_name_num in sorted_block_name_list:
		if range_count == 0:
			start_num = block_name_num			
		range_count += 1
		if range_count == every_range_block_num:
			finish_num = block_name_num
			tmp = [start_num, finish_num]
			range_list.append(tmp)
			range_count = 0
	if not range_count == 0:
		tmp = [start_num, block_name_num]
		range_list.append(tmp)
		
#block_list folder analyze
	analyze_result = block_report_folder_block_count_analyze(folder_name)
	total_count = analyze_result[0]
	block_count_list = analyze_result[1]
	
	
	range_count = 0
	tmp_range = range_list[range_count]
	range_start = tmp_range[0]
	range_finish = tmp_range[1]
	
	range_block_happen_count = 0
	range_ratio_list = []
	for block_name_num in sorted_block_name_list:
		if block_name_num > range_finish:
			range_count += 1
			range_ratio_list.append(round(float(range_block_happen_count)/float(total_count), 4))
			range_block_happen_count = 0

		tmp_range = range_list[range_count]
		range_start = tmp_range[0]
		range_finish = tmp_range[1]

		block_name = "block_" + str(block_name_num)
		if block_name in block_count_list:
			block_happen_count = block_count_list [block_name]
			range_block_happen_count += block_happen_count
		else :
			continue
	if not range_block_happen_count == 0:
		range_ratio_list.append(round(float(range_block_happen_count)/float(total_count), 4))
		

	
	total_ratio = 0
	for i in range(0, len(range_ratio_list)):
		print range_ratio_list[i]
		total_ratio += range_ratio_list[i]
#}}}
