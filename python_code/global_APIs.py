#!/usr/bin/python
import os
import re
import shutil
import time 
import report_APIs
import input_file_block_analyzer
global_num_word_except_list = ["ipv4", "ipv6"]
global_num_word_forbid_list = ["", ""]


def global_folder_initializer (input_file):
	if os.path.isfile (input_file):
		file_mode = get_file_mode (input_file)
	if os.path.isdir(input_file):
		file_list = get_folder_file_list(input_file)
		
		file_mode = get_file_mode (file_list[0])

	if not os.path.isdir("block_report"):
		os.mkdir("block_report")	
	
	if not os.path.isdir("sql_database"):
		os.mkdir("sql_database")	

	sql_path = "sql_database/"
	sql_path += file_mode
	if not os.path.isdir(sql_path):
		os.mkdir(sql_path)	

	return True

#file mode 
#get_folder_file_list
#get_file_mode
#get_real_file_name
#get_real_folder_name
#test_have_database
#{{{
def get_folder_file_list (folder_name):
	file_list = []
	for filename in os.listdir (folder_name):
		file_path_name = folder_name
		file_path_name += "/"
		file_path_name += filename
		file_list.append(file_path_name)
	return file_list

def get_file_mode (input_file):
	fl = open (input_file, "r")
	find_suitable_pattern_line = 0
	while find_suitable_pattern_line == 0:
		line = fl.readline()
		if not line:
			#here must have an error out
			tmp = "Can't detect file mode from file "
			tmp += input_file
			print tmp
			return ""

		if not get_line_message (line) == "":
			find_suitable_pattern_line = 1 
			break
	fl.close()
	if is_console_format (line):
		return "console"
	
	if is_mutrino_format (line):
		return "mutrino"	
	if is_message_format (line):
		return "message"	
	if is_redhat_message_format (line):
		return "redhat_message"	
	return ""

def get_real_folder_name(folder_name):
	matchobj = re.match (r'(.*)/$', folder_name)
	if matchobj:
		folder_name = matchobj.group(1)
	return folder_name
	
def get_real_file_name (input_file):
	file_name = input_file
	pattern = r'.*\/(.*)$'	
	matchobj = re.match (pattern, input_file)
	if matchobj:
		file_name = matchobj.group(1)
	return file_name


def test_have_database (file_mode):
	#cfg_0 is the basic version
	database_version = -1
	for i in range(0, 9):
		database_file_name = "sql_database/"
		database_file_name += file_mode
		database_file_name += "/" 
		database_file_name += "block_database_cfg_"
		database_file_name += str(i) 
		database_file_name += ".txt"
		if os.path.isfile(database_file_name):
			database_version = i
	#ARES
	#return default version 0
	if not database_version == -1:
		return 0
	return database_version 
#}}}


#pattern:
#is_pattern_format
#gen_line_pattern
#calculate_match_ratio
#{{{


def is_pattern_format (word):
	num_pattern = r'([0-9]+)' 
	letter_pattern = r'([a-zA-Z]+)' 
	have_num = 0
	have_letter = 0
	matchnum = re.search (num_pattern, word)
	
	matchletter = re.search (letter_pattern, word)
	
	if matchnum:
		have_num = 1
	if matchletter:
		have_letter = 1

	if have_num == 1:
		match_except = 0 
#ARES TODO
#need to add an exception list, if some word in this exception list we can still treat them as pattern
#for exapmle: word = net.ipv4.tcp_wmem
#	here, ipv4 can be a exception word
		for except_word in global_num_word_except_list:
			matchobj = re.match(r'^(.*)' + except_word + '(.*)$', word)
			if matchobj != None:
				match_except = 1
				break
		if match_except == 0:
			return ""

	for forbid_word in global_num_word_forbid_list:
		matchobj = re.match(r'^(.*)' + forbid_word + '(.*)$', word)
		if matchobj != None:
			return ""
	
	
	#print re.search ("", word[i])


	is_all_f = 1
	for i in range (0, len(word)):
		if word[i] != "f":
			is_all_f = 0
			break
	if is_all_f == 1:
		return ""

	if have_letter:
		word = word_remove_symbol(word)
	
	for i in range (0, len(word)):
		if word[i] == " ":
			del(word[i])
	return word	

def word_remove_symbol (word):
#remove symbol
#if the word is only symbol then do nothing
#if the word have letter then must remove symbol
	tmp_word = ""
	letter_pattern = r'([a-zA-Z0-9])' 
	for i in range (0, len(word)):
		matchletter = re.search (letter_pattern, word[i])

		if matchletter:
			tmp_word += word[i]
	return tmp_word


def gen_line_pattern (line):
	count = 0
	pattern = []
#ARES change 10/5/16
#I want to convert "=" into space. left side of equal symbol is variable, right side is value. I don't want to ignore the variable	
#2015-02-11T17:34:35.336767-06:00 c0-0c0s2n2 EFI: mem132: type=1, attr=0xf, range=[0x000000000b7ba000-0x000000000b7cb000) (0MB)
	line = line.replace ("=", " ")
#ARES change done

	for word in line.split():
		word = is_pattern_format (word)
		if not word == "":
			tmp_pattern = []
			tmp_pattern.append(str(count))
			tmp_pattern.append(word)
			pattern.append(tmp_pattern)
		count += 1
		if count == 10:
			break
	return pattern

def calculate_match_ratio (pattern, key):
	match_count = 0.0
	dismatch_count = 0.0
	pattern_length = len(pattern)
	key_length = len(key)

	pattern_pos = 0
	key_pos = 0
	
	while True:
		if pattern_pos == pattern_length or key_pos == key_length:
			break
		key_pattern_index = key[key_pos]	
		pattern_index = pattern[pattern_pos]	
		
		key_pattern_index_pos = key_pattern_index[0]
		pattern_index_pos = pattern_index[0]
		key_pattern_word = key_pattern_index[1]
		pattern_word = pattern_index[1]

		if key_pattern_index_pos == pattern_index_pos:
			if key_pattern_word == pattern_word:
				match_count = match_count + 1
			else:
				dismatch_count = dismatch_count + 1
			key_pos = key_pos + 1
			pattern_pos = pattern_pos + 1
		else:
#ARES recent add
########################################
			if key_pattern_word == pattern_word:
				match_count = match_count + 0.5
				key_pos = key_pos + 1
				pattern_pos = pattern_pos + 1
			else:
				dismatch_count = dismatch_count + 1
########################################
				if key_pattern_index_pos < pattern_index_pos:
					key_pos = key_pos + 1
				else:
					pattern_pos = pattern_pos + 1
	while pattern_pos != pattern_length:
		pattern_pos = pattern_pos + 1
		dismatch_count = dismatch_count + 1
	while key_pos != key_length:
		key_pos = key_pos + 1
		dismatch_count = dismatch_count + 1
	if match_count == 0:
		return 0.0

	match_ratio = match_count/(match_count + dismatch_count)
	return match_ratio

#}}}

#message format global APIS:
#get_line_id
#get_line_message
#get_line_time
#{{{
def get_line_id (line):
	line_id = ""
	if is_console_format (line):
		line_id = get_console_message_line_node_id (line)
	if is_mutrino_format (line):
		line_id = get_mutrino_message_line_node_id (line)
	if is_message_format (line):
		line_id = get_message_line_node_id (line)
	if is_redhat_message_format (line):
		line_id = get_redhat_message_line_node_id (line)
	return line_id 

def get_line_message (line):
	line_mess = ""
	if is_console_format (line):
		line_mess = get_console_message_line_message (line)
	if is_mutrino_format (line):
		line_mess = get_mutrino_message_line_message (line)
	if is_message_format (line):
		line_mess = get_message_line_message (line)
	if is_redhat_message_format (line):
		line_mess = get_redhat_message_line_message (line)
	return line_mess 

def get_line_time (line):
	line_time = ""
	if is_console_format (line):
		line_time = get_console_message_line_time (line)
	if is_mutrino_format (line):
		line_time = get_mutrino_message_line_time (line)
	if is_message_format (line):
		line_time = get_message_line_time (line)
	if is_redhat_message_format (line):
		line_time = get_redhat_message_line_time (line)
	return line_time 
#}}}

#all about console format file:
#is_console_format
#get_console_message_line_time
#get_console_message_line_node_id
#get_console_message_line_message
#{{{
def is_console_format (line):
	pattern = r'^\[(.*)\]\[([a-zA-Z0-9\.\_\-]+)\](.*)$'	
	matchobj = re.match (pattern, line)
	if matchobj:
		return matchobj 
	else:
		return 0

def get_console_message_line_time (line):
	extract_result = is_console_format (line)
	return extract_result.group(1)

def get_console_message_line_node_id (line):
	extract_result = is_console_format (line)
	return extract_result.group(2)

def get_console_message_line_message (line):
	extract_result = is_console_format (line)
	return extract_result.group(3)
#}}}

#all about mutrino format file:
#is_mutrino_format
#get_mutrino_message_line_time
#get_mutrino_message_line_node_id
#get_mutrino_message_line_message
#get_mutrino_line_time_index
#{{{
def is_mutrino_format (line):
#2015-02-11T17:25:57.385723-06:00 c0-0c0s0n1 ERROR: Type:2; Severity:80; Class:3; Subclass:D; Operation: 2
	pattern = r'^([0-9T\-\:\.]+) ([a-z0-9\-]+) (.*)$'	
	matchobj = re.match (pattern, line)
	if matchobj:
		return matchobj 
	else:
		return 0

def get_mutrino_message_line_time (line):
	extract_result = is_mutrino_format (line)
	return extract_result.group(1)

def get_mutrino_message_line_node_id (line):
	extract_result = is_mutrino_format (line)
	return extract_result.group(2)

def get_mutrino_message_line_message (line):
	extract_result = is_mutrino_format (line)
	return extract_result.group(3)

def get_mutrino_line_time_index (line_time):
	#2015-02-11T17:25:57.385723-06:00
		
	pattern = r'^([0-9]+)\-([0-9]+)\-([0-9]+)T([0-9]+)\:([0-9]+)\:([0-9]+)\.(.*)$'	
	matchobj = re.match (pattern, line_time)
	year = ""
	month = "" 
	date = ""
	hour = ""
	minute = ""	
	second = ""
	if matchobj:
		year = matchobj.group(1)
		month = matchobj.group(2)
		date = matchobj.group(3)
		hour = matchobj.group(4)
		minute = matchobj.group(5)
		second = matchobj.group(6)
		time_index = calculate_time_index(month,date,hour,minute,second, year)
	else:
		time_index = ""

	return time_index


#}}}

#all about message format file:
#is_message_format
#get_message_line_unknown
#get_message_line_time
#get_message_line_node_id
#get_message_line_source
#get_message_line_index
#get_message_line_message
#{{{
def is_message_format (line):
#<6>1 2015-02-11T17:32:19.496117-06:00 c0-0c0s0n1 kernel - p0-20150211t172524 - Initializing cgroup subsys cpuset
	pattern = r'^(\<[0-9]+\>[0-9]+) ([0-9T\-\:\.]+) ([a-z0-9\-]+) ([ ]*.*) - (p[0-9\-]+t[0-9]+) - (.*)$'	
	matchobj = re.match (pattern, line)
	if matchobj:
		return matchobj 
	else:
		return 0

def get_message_unknown (line):
	extract_result = is_message_format (line)
	return extract_result.group(1)

def get_message_line_time (line):
	extract_result = is_message_format (line)
	return extract_result.group(2)

def get_message_line_node_id (line):
	extract_result = is_message_format (line)
	return extract_result.group(3)

def get_message_line_source (line):
	extract_result = is_message_format (line)
	return extract_result.group(4)

def get_message_line_index (line):
	extract_result = is_message_format (line)
	return extract_result.group(5)

def get_message_line_message (line):
	extract_result = is_message_format (line)
	return extract_result.group(6)
#}}}


#all about redhat message file:
#is_redhat_message_format
#get_redhat_message_line_time
#get_redhat_message_line_node_id
#get_redhat_message_line_source
#get_redhat_message_line_message
#get_redhat_message_line_time_index
#{{{
def is_redhat_message_format (line):
#Jul 31 11:20:18 centostest1 NetworkManager[1281]: <info> NetworkManager (version 0.8.1-75.el6) is starting...
#Jul 31 11:20:33 centostest1 rtkit-daemon[1950]: Sucessfully made thread 1955 of process 1948 (/usr/bin/pulseaudio) owned by '42' RT at priority 5.
	pattern = r'^([A-Za-z]+) ([ 0-9]+) ([0-9\:]+) ([a-zA-Z0-9\-]+) ([a-zA-Z0-9\[\]\-\:]+) (.*)$'	
	matchobj = re.match (pattern, line)
	if matchobj:
		return matchobj 
	else:
		return 0

def get_redhat_message_line_time (line):
	extract_result = is_redhat_message_format (line)
	tmp = ""
	tmp += extract_result.group(1)
	tmp += " "
	tmp += extract_result.group(2)
	tmp += " "
	tmp += extract_result.group(3)
	tmp += " "
	return tmp

def get_redhat_message_line_time_index (line_time):
	#Jul 31 11:20:32
	pattern = r'^([A-Za-z]+)[ ]+([0-9]+)[ ]+([0-9]+)\:([0-9]+)\:([0-9]+)(.*)$'	
	matchobj = re.match (pattern, line_time)
	month = "" 
	date = ""
	hour = ""
	minute = ""	
	second = ""
	if matchobj:
		month = matchobj.group(1)
		date = matchobj.group(2)
		hour = matchobj.group(3)
		minute = matchobj.group(4)
		second = matchobj.group(5)
		time_index = calculate_time_index(month,date,hour,minute,second)
	else:
		time_index = ""

	return time_index


def get_redhat_message_line_node_id (line):
	extract_result = is_redhat_message_format (line)
	return extract_result.group(4)

def get_redhat_message_line_source (line):
	extract_result = is_redhat_message_format (line)
	source = extract_result.group(5)
	pattern = r'^(.*):$'
	matchobj = re.match(pattern, source)
	if matchobj:
		source = matchobj.group(1)
	pattern = r'^(.*)\[(.*)\]$'
	matchobj = re.match(pattern, source)
	if matchobj:
		source = matchobj.group(1)
	

	return source

def get_redhat_message_line_message (line):
	extract_result = is_redhat_message_format (line)
	return extract_result.group(6)
#}}}

#all about time format:
#calculate_time_index
#calculate_month_index
#get_line_time_index
#get_index_time_format
#{{{
def get_line_time_index (line):
	line_time_index = ""
	if is_console_format (line):
		line_time_index = get_console_message_line_time (line)
	if is_mutrino_format (line):
		line_time = get_mutrino_message_line_time (line)
		line_time_index = get_mutrino_line_time_index (line_time)
	if is_message_format (line):
		line_time_index = get_message_line_time (line)
	if is_redhat_message_format (line):
		line_time = get_redhat_message_line_time (line)
		line_time_index = get_redhat_message_line_time_index (line_time)
	return line_time_index 

def get_index_time_format (time_index):
	x = time.localtime(float(time_index))
	time_format = time.strftime("%Y-%m-%d %H:%M:%S",x)
	return time_format

def calculate_time_index (month,date,hour,minute,second, year = "" ):
	month_index = calculate_month_index(month)
	if year == "":
		year = "2016"
	tmp = year
	tmp += "-"
	tmp += str(month_index)
	tmp += "-"
	tmp += date
	tmp += " "
	tmp += hour
	tmp += ":"
	tmp += minute
	tmp += ":"
	tmp += second

	time_result = time.strptime(tmp,'%Y-%m-%d %H:%M:%S')
	
	time_index = time.mktime(time_result)
	return int(time_index)

def calculate_month_index (month):
	if month.isdigit():
		return int(month)
	month = month.lower()
	total_day = 0
	if month == "jan":
		return 1
	if month == "feb":
		return 2
	if month == "mat":
		return 3
	if month == "apr":
		return 4
	if month == "may":
		return 5
	if month == "jun":
		return 6
	if month == "jul":
		return 7
	if month == "aug":
		return 8
	if month == "sep":
		return 9
	if month == "oct":
		return 10
	if month == "nov":
		return 11
	if month == "dec":
		return 12
	


	#if month == "jan":
	#	total_day = 0
	#if month == "feb":
	#	total_day = 31
	#if month == "mat":
	#	total_day = 59
	#if month == "apr":
	#	total_day = 90 
	#if month == "may":
	#	total_day = 120
	#if month == "jun":
	#	total_day = 151
	#if month == "jul":
	#	total_day = 181
	#if month == "aug":
	#	total_day = 212
	#if month == "sep":
	#	total_day = 243
	#if month == "oct":
	#	total_day = 273
	#if month == "nov":
	#	total_day = 304
	#if month == "dec":
	#	total_day = 334
	#return total_day
#}}}








def analyze_error_list_file (error_file):
	fl = open (error_file, "r")
	single_error_list = []
	multi_error_list = []
	single_multi_switch = 0
	while True:
		line = fl.readline()
		if line == "":
			break
		line = line.split()
		if len(line) < 1:
			continue
		name = line[0] 
		if name == "single_error:":
			single_multi_switch = 0
			continue
		elif name == "multi_error:":
			single_multi_switch = 1 
			continue
		else:
			if single_multi_switch == 0:
				single_error_list.append(name)
			if single_multi_switch == 1:
				multi_error_list.append(name)
	fl.close()
	#os.remove(error_file)
	tmp = []
	tmp.append(single_error_list)
	tmp.append(multi_error_list)
	return tmp 



