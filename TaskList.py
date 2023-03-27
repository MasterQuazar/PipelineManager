"""
==============================================================

████████╗ █████╗ ███████╗██╗  ██╗██╗     ██╗███████╗████████╗
╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██║     ██║██╔════╝╚══██╔══╝
   ██║   ███████║███████╗█████╔╝ ██║     ██║███████╗   ██║   
   ██║   ██╔══██║╚════██║██╔═██╗ ██║     ██║╚════██║   ██║   
   ██║   ██║  ██║███████║██║  ██╗███████╗██║███████║   ██║   
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝   
==============================================================




DONE :
	- files browser system
	- settings system
	- export publish files system
	- logs premice
	- rough interface
	- export edit files work in progress
	- rough thumnails system








WORK IN PROGRESS :
	- GUI version 2
	- finish the thumbnails system
	- optimize the files searching system
		- by name
		- by extension
		- by keyword
			- in the project
			- in the whole pipeline
			- ON THE COMPUTER??

		"""	

		#USE PREFIX SOLUTION TO SAVE MEMORY
		import os

		for root, dirs, files in os.walk('.'):
		    matching_files = (filename for filename in files if filename.startswith('prefix'))
		    for filename in matching_files:
		        print(os.path.join(root, filename))


		#USE MULTIPROCESSING AND
		#CREATE ONE POOLS FOR EACH FOLDER
		#FIND A SOLUTION TO MAKE IT RECURSIVE
		#	-> ONE LOOP SEARCH FOR FOLDER NAMES
		#	-> FOR EACH FOLDER LAUNCH A FUNCTION TO SEARCH FILES IN USING MULTIPROCESSING

		import os
		from multiprocessing import Pool

		def find_matching_files(root):
		    matching_files = []
		    for dirpath, _, filenames in os.walk(root):
		        for filename in filenames:
		            if filename.startswith('prefix'):
		                matching_files.append(os.path.join(dirpath, filename))
		    return matching_files

		if __name__ == '__main__':
		    roots = ['/path/to/directory1', '/path/to/directory2', '/path/to/directory3']

		    with Pool(processes=len(roots)) as pool:
		        results = pool.map(find_matching_files, roots)

		    # Flatten the list of lists into a single list
		    matching_files = [filename for sublist in results for filename in sublist]

		    for filename in matching_files:
		        print(filename)
		"""


	- archive system
	- logs system (pushed)
	- export edit files automation?
		same location folder first
		same project folder first
	- save project template?
	- create new item project


	- search for textures system
	- connect textures system

	- archive in pipeline
	- archive in project
	- search for archive
	- search in archive
		- move item
		- put item in
		- remove item
		- delete archive
		- rename archive
"""