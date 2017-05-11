#!/usr/bin/python
import global_APIs 

def block_database_store (block_database, file_mode, nickname = "0"):
	file_name = "sql_database/"
	file_name += file_mode
	file_name += "/" 
	file_name += "block_database_cfg_"
	file_name +=  nickname
	file_name += ".txt"
	fl = open (file_name, "w")

	for block_name in block_database:
		block = block_database[block_name]
		fl.write(str(block_name))
		fl.write(" \n")
		
		block_start = block["start"]
		tmp = ""
		for i in range (0, len(block_start)):
			element = block_start[i]
			pos = element[0]
			word = element[1]
			tmp += str(pos)
			tmp += " "
			tmp += str(word)
			tmp += " "
		fl.write(tmp)
		fl.write("\n")
		
		block_finish = block["finish"]	
		tmp = ""
		for i in range (0, len(block_finish)):
			element = block_finish[i]
			pos = element[0]
			word = element[1]
			tmp += str(pos)
			tmp += " "
			tmp += str(word)
			tmp += " "
		fl.write(tmp)
		fl.write("\n")

	fl.close()

def block_database_read (file_mode, nickname = "0"):
	block_database = {}
	file_name = "sql_database/"
	file_name += file_mode
	file_name += "/" 
	file_name += "block_database_cfg_"
	file_name +=  nickname
	file_name += ".txt"
	fl = open (file_name, "r")
	while True:
		line_1 = fl.readline()
		line_2 = fl.readline()
		line_3 = fl.readline()
		if not line_1 or not line_2 or not line_3:	
			break
		block_name = line_1.split()[0]
		start_pattern = convert_string_into_pattern(line_2)
		finish_pattern = convert_string_into_pattern(line_3)
		tmp = {}
		tmp["start"] = start_pattern
		tmp["finish"] = finish_pattern
		block_database[block_name] = tmp	
				


	fl.close()
	return block_database

def convert_string_into_pattern (string):
	pattern = []
	
	string_element_list = string.split()
	i = 0
	while i < len(string_element_list) :
		pos = 	string_element_list[i]
		word = string_element_list[i+1]
		i = i + 2
		tmp = []
		tmp.append(pos)
		tmp.append(word)
		pattern.append(tmp)
	return pattern 



def block_multi_store (multi_list, file_mode, nickname = "0"):
#{'block_68': ['block_68', 'block_69'], 'block_99': ['block_99', 'block_100'], 'block_39': ['block_39', 'block_42']}

	file_name = "sql_database/"
	file_name += file_mode
	file_name += "/" 
	file_name += "multi_block_database_cfg_"
	file_name +=  nickname
	file_name += ".txt"
	fl = open (file_name, "w")
	for multi_block_name in multi_list:
		fl.write(multi_block_name)
		fl.write(" \n")
		element = multi_list[multi_block_name]
		fl.write (element[0])
		fl.write (" ")
		fl.write (element[1])
		fl.write (" \n")

	fl.close()

def multi_database_read (file_mode, nickname = "0"):
#{'block_68': ['block_68', 'block_69'], 'block_99': ['block_99', 'block_100'], 'block_39': ['block_39', 'block_42']}
	multi_list = {}
	file_name = "sql_database/"
	file_name += file_mode
	file_name += "/" 
	file_name += "multi_block_database_cfg_"
	file_name +=  nickname
	file_name += ".txt"
	fl = open (file_name, "r")
	while True:
		line_1 = fl.readline()
		line_2 = fl.readline()
		if not line_1 or not line_2 :	
			break
		multi_name = line_1.split()[0]
		tmp = []
		tmp.append (line_2.split()[0])
		tmp.append (line_2.split()[1])
		multi_list[multi_name] = tmp	


	fl.close()
	return multi_list

def repeat_db_test(SLEBD_DB):
	share_DB = {}
	count = 0
	done_list = []
	for this_DB in SLEBD_DB :
		if this_DB in done_list:
			continue
		done_list.append(this_DB)
		tmp = []
		this_start_pattern = SLEBD_DB[this_DB]["start"]
		this_finish_pattern = SLEBD_DB[this_DB]["finish"]
		match = 0
		for that_DB in SLEBD_DB:
			if that_DB == this_DB:
				continue
			that_start_pattern = SLEBD_DB[that_DB]["start"]
			that_finish_pattern = SLEBD_DB[that_DB]["finish"]
			if this_start_pattern == that_start_pattern and this_finish_pattern == that_finish_pattern:
				match = 1
				tmp.append (that_DB)
				done_list.append(that_DB)
		if match == 1:
			tmp.append (this_DB)
			share_DB[str(count)] = tmp			
			count += 1
	return share_DB	
	
