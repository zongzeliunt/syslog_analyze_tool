#!/usr/bin/python
#coding:utf-8
import sys
sys.path.append("/home/ares/syslog_tool_work_folder/")
import os
import re 
import time 
import python_code.global_APIs as global_APIs


def baler_preprocess_folder_file (folder_name):
#{{{
	file_list = global_APIs.get_folder_file_list(folder_name)
	
	output_folder = "preprocessed_file_folder"
	if not os.path.isdir(output_folder): 	
		os.mkdir (output_folder)
	file_count = 0 
	node_name_list = {}
	for file_name in file_list:
		node_name = global_APIs.get_file_node_name(file_name)
		command_line = "./syslog2baler.pl -port 10513 host = "
		command_line +=	node_name
		command_line +=	" < "
		command_line +=	file_name
		os.system(command_line)
		node_name_list[node_name] = file_count	
		
		file_count += 1

	for node_name in node_name_list:
		correspond_node_id = node_name_list[node_name]	
		output_file_name = output_folder
		output_file_name += "/"
		output_file_name += node_name 
		output_file_name += ".txt" 

		command_line = "bquery -s store -H "
		command_line += str(correspond_node_id) 
		command_line += " -v -t msg ptn > "
		command_line += output_file_name

		os.system(command_line)
	return output_folder

#}}}


def main(cmd_1, cmd_2 = ""):
	baler_preprocess_folder_file(cmd_1)


cmd_1 = sys.argv[1]
cmd_2 = sys.argv[2]
main(cmd_1, cmd_2)

