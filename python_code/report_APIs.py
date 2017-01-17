#!/usr/bin/python
import global_APIs
import block_database_opt
import input_file_block_analyzer as input_file_block_analyzer
import block_merger 

def dump_block_example (block_database, input_file, block_list):
	print "dump example"
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
			pattern = global_APIs.gen_line_pattern (line_message)
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


def output_block_list_report (block_list, input_file, mode = 0):
	file_name = global_APIs.get_real_file_name (input_file)
	report_file = "block_report/"
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
		

def block_database_summary (file_name):
	#file_name is only a trigger
	file_mode = global_APIs.get_file_mode (file_name)
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
def count_block_happen_time (block_list):
	block_happen_count_list = {}
	for block in block_list:
		block_name = block[0]
		if block_name in block_happen_count_list:
			block_happen_count_list[block_name] += 1
		else:
			block_happen_count_list[block_name] = 1
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
		pattern = global_APIs.gen_line_pattern (line_message)
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


