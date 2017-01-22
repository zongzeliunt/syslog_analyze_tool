HPC system log analyze tool.
This tool have 3 main features:
1) Original syslog split and remix
2) Block database learning
3) Block report analyze



All the functions are included in main.py. If want to run these features, you can uncommon these function combinations in main.py
Things to pay attention:
1. Source code are inside folder "python_code". This tool will generate a lot folders when running. You can delete them but please keep "python_code" and "main.py". If you pay a long time to run block DB learning, please keep folder "sql_database". 
2. This tool can right now support just 3 kinds of syslog formats. If your format can't be supported please contact me. I will add format recognition API for you.
3. All the main features have been developed, from now on our research should on the base of this tool. I will soon develop a more friendly GUI for it. This time please change the function combination to achieve these features. 



This tool provided 3 examples to show these 3 main features.
1) Original syslog split and remix
	This feature will split original syslog file into multiple files by node id. These seperate files will be stored in a folder "splited_files".
	This feature can have 3 ways to run:
	a. Split original file and remix all seperate files.
		Function combination needed in main.py:
			result = multi_file_folder.log_file_split(input_file)
			multi_file_folder.splited_folder_merge(result)
		Command:
			python main.py examples_folder/example_1_file_split_remix/console.txt
		The remixed file is in the splited files folder.
	
	b. Remix designated file which you want. The input value should be a folder name. You can split original files and pick up any node's log file to remix. 
		Function needed in main.py:
			multi_file_folder.splited_folder_merge(input_file)
		Command:
			python main.py splited_files/console
	
	c. Generate a multiple learning file folder. Because of one huge learning file could cost very long time to learn block database, we can generate multiple learning files and learn block DB on them one by one. 
		Function needed in main.py:
			multi_file_folder.multi_file_learning_folder_gen(input_file)
		Command:
			python main.py splited_files/console
		One "tmp" folder will be generated under "splited_files/console". You can find 
18 files in this folder. Each of them are mixed by 5 nodes' log files. 



2) Block database learning
	This feature will learn block database from one single file or from multiple files in a folder. After one learning file been learned, it will be copied into a "done_learned_files" folder.
	a. Learn DB from one single file:
		Function needed in main.py:
			block_database_learner.block_database_learning (input_file)
		Command:
			python main.py examples_folder/example_2_block_pattern_database_learn/learning_file_folder/single_file/console.txt_4.txt
	
	b. Learn DB from multiple files:
		Function needed in main.py:
			multi_file_folder.folder_learning (input_file)
		Command:
			python main.py examples_folder/example_2_block_pattern_database_learn/learning_file_folder/mutiple_file


3) Block report analyze
	After block DB is learned, we can analyze block report list from analyze file. The analyze file do not to be the same as DB learning file. For example you have generated 15 learning files, you can learn DB from 5 of them and analyze block report from the rest 10 files. There could be block recognation conflict if analyze file set is different to the learning file set. If conflict happens we can add the conflicated analyze file into the learning set.
	This tool can analyze block report from one single file or multiple files. The block report are generated into the folder "block_report". Each analyze file will have its individual block report file, summary file and block example file.
	a. Analyze single file:
		Function needed in main.py:
			report_APIs.general_run_process (input_file, 1 )
		Command: 
			python main.py examples_folder/example_3_block_report_analyze/block_analyze_file/console.txt_4.txt

	b. Analyze multiple file:
		Function needed in main.py:
			multi_file_folder.folder_analyzing (input_file)
		Command: 
			python main.py examples_folder/example_3_block_report_analyze/block_analyze_file
