#coding: utf-8

#Copyright 2023, Robin Delaporte AKA Quazar, All rights reserved.


import maya.cmds as mc
import pymel.core as pm
import os
import ctypes
import sys
import pickle
import json 
import yaml

from tqdm import tqdm
from datetime import datetime
from functools import partial
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

"""
	[Origin]
	[key]
	[name]
	[mayaProjectName]
	[type]
	[editPublishFolder]
"""


"""
publish export tasklist
	removing the references (import them or break them)
	delete all the namespaces in namespace editor
	export the selection in the scene under a new scene (publish scene)

	rigging scene:
		delete unused nodes
		reset controllers position
		hide sks (check gesse document)
		delete renderman volume aggregate if present in the scene
"""






class PipelineApplication:




	def load_settings_function(self):
		if (self.project_path == None) or (self.project_path == "None"):
			mc.warning("Impossible to load settings!")
			return None, None, None
		else:
			
			if type(self.project_path)==list:
				self.project_path = self.project_path[0]
			
		
		
		
			try:	
				with open(os.path.join(self.project_path, "PipelineManagerData/PipelineSettings.yaml"), "r") as read_file:
					load_data = yaml.load(read_file,Loader=yaml.Loader)
				
				self.settings = load_data["dict1"]
				self.settings_dictionnary = load_data["dict2"]
				self.additionnal_settings = load_data["dict3"]

				
				print("Settings loaded successfully!")
			
			except:
				self.settings, self.settings_dictionnary, self.additionnal_settings = self.create_pipeline_settings_function()
				print("Settings file created in your project!")
				
		return self.settings, self.settings_dictionnary, self.additionnal_settings






	def letter_verification_function(self, content):
		letter = "abcdefghijklmnopqrstuvwxyz"
		figure = "0123456789"

		list_letter = list(letter)
		list_capital = list(letter.upper())
		list_figure = list(figure)

		list_content = list(content)
		if list_content == None:
			return False

		valid = False
		for i in range(0, len(list_content)):
			if (list_content[i] in list_letter)==True or (list_content[i] in list_capital)==True or (list_content[i] in list_figure)==True:
				valid=True
		return valid
		#OLD SYSTEM
		"""
		for i in range(0, len(list_content)):
			if (list_content[i] in list_letter)==True or (list_content[i] in list_capital)==True or (list_content[i] in list_figure)==True:
				return True
			else:
				if (i == len(list_content) - 1):
					return False
		"""




	def define_project_path_ui_function(self, type,event):
		
		if type == "project":
			mc.textField(self.project_label, edit=True, text=mc.workspace(query=True, active=True))
			folder = mc.workspace(query=True, active=True)
		else:
			#open a file explorer to define a folder
			folder = mc.fileDialog2(fm=3)
			if folder == None:
				mc.error("You have to define one folder!")
				return
			else:
				mc.textField(self.project_label, edit=True, text=folder[0])
				#folder = mc.workspace(query=True, active=True)


		with open(os.path.join(self.program_folder, "Data/PipelineData.dll"), "wb") as read_file:
			pickle.dump(folder, read_file)

		self.project_path = folder 
		self.reload_settings_function()

		#self.load_shading_settings_function()
		
		
		self.save_settings_file()
		





	def reload_settings_function(self):
		self.settings, self.settings_dictionnary, self.additionnal_settings = self.load_settings_function()



		self.type_list_value = []
		for key, value in self.settings_dictionnary.items():
			self.type_list_value.append(key)

		setting_key_list = []
		setting_value_list = []
		setting_default_folder_list = []
		setting_keyword_list = []

		for setting_key, setting_value in self.settings.items():

			#create the default folder buttons
			setting_key_list.append(setting_key)
			setting_value_list.append(setting_value[0])
			setting_keyword_list.append(setting_value[1])

			if setting_value[2] == None:
				setting_default_folder_list.append("None")
			else:
				setting_default_folder_list.append(setting_value[2])



		mc.textScrollList(self.type_list, edit=True, removeAll=True, append=self.type_list_value)
		#mc.textScrollList(self.settings_type_list, edit=True, removeAll=True, append=setting_key_list)
		#mc.textScrollList(self.setting_syntax_list, edit=True, removeAll=True, append=setting_value_list)
		#mc.textScrollList(self.setting_keyword_list, edit=True, removeAll=True, append=setting_keyword_list)
		#mc.textScrollList(self.settings_folder_list, edit=True, removeAll=True, append=setting_default_folder_list)

		




	def save_settings_file(self):

		if self.project_path == "None":
			mc.error("Impossible to save the settings file\nYou have to set the pipeline folder first!")
		else:
			#get content of the pipeline path
			try:
				path = mc.textField(self.project_label, query=True, text=True)
			except:
				path = self.project_path
			if os.path.isdir(path)==False:
				mc.error("You have to define a valid pipeline folder first!")
				return
			if type(self.project_path)==list:
				self.project_path = self.project_path[0]
			if os.path.isdir(os.path.join(path, "PipelineManagerData"))==False:
				os.mkdir(os.path.join(path, "PipelineManagerData"))
			
			try:
				print("SAVING!")
				saving_dictionnary = {
					"dict1":self.settings,
					"dict2":self.settings_dictionnary,
					"dict3":self.additionnal_settings,
				}
				with open(os.path.join(path, "PipelineManagerData/PipelineSettings.yaml"), "w") as save_file:
					yaml.dump(saving_dictionnary, save_file, indent=4)
			except AttributeError:
				print("Impossible to save!")
				self.create_pipeline_settings_function()
			self.add_log_content_function("Settings file saved successfully")




	def create_pipeline_settings_function(self):
		print("Settings file created!")
		basic_file_type_list = ["mod", "rig", "groom", "cloth", "lookdev", "layout", "camera", "anim", "render", "compositing"]

		#TYPE OF DATA
		#DETECTION OF FILES
		self.settings_dictionnary = {
			"character": basic_file_type_list,
			"prop": basic_file_type_list, 
			"set": basic_file_type_list,
			"fx": "unknown",
			"shots": ["layout", "camera", "anim", "render", "compositing"],
		}
		self.settings = {
			"character":["[project]_[key]_[name]_[type]", "char", None],
			"prop":["[project]_[key]_[name]_[type]", "prop", None],
			"set":["[project]_[key]_[name]_[type]", "set", None],
			"fx":["[project]_[key]_[name]_[type]","fx", None],
			"shots":["[project]_[key]_[sqversion]_[shversion]", "shots", None]
		}
		self.additionnal_settings = {
			"checkboxValues":[False, True, False, False, False],
			"3dSceneExtension":[".ma",".mb"],
			"3dItemExtension":[".obj", ".fbx"],
			"texturesExtension":[".png", ".tif",".tiff",".tex", ".exr", ".jpg"],
			"mayaProjectName":"maya",
			"editPublishFolder":["edit", "publish"]
		}

		self.save_settings_file()
		return self.settings, self.settings_dictionnary, self.additionnal_settings




	def add_log_content_function(self, log_new_content):
		now = datetime.now()
		new_content = "[%s/%s/%s:%s:%s] %s" % (now.year, now.month, now.day, now.hour, now.minute, log_new_content)
		self.log_list_content.append(new_content)

		try:
			mc.textScrollList(self.log_list, edit=True, removeAll=True, append=self.log_list_content)
		except:
			pass




	def add_team_log_content_function(self, log_new_content):
		#get project path
		folder_path = mc.textField(self.project_label, query=True, text=True)
		if os.path.isfile(os.path.join(folder_path, "PipelineManagerData/PipelineManagerTeamLog.dll"))==True:
			#get the content of this file
			try:
				with open(os.path.join(folder_path, "PipelineManagerData/PipelineManagerTeamLog.dll"), "rb") as read_file:
					team_content = pickle.load(read_file)
				#get the old content
			except:
				mc.error("Impossible to change the team log file!")
				return 
			else:
				if type(team_content)==list:
					
					
					team_content.append(log_new_content)
					with open(os.path.join(folder_path, "PIpelineManagerData/PipelineManagerTeamLog.dll"), "wb") as save_file:
						pickle.dump(team_content, save_file)





	def display_new_list_function(self):

		"""
		check the selection of all list to create the content of the next one
		if you change the previous one check if the content of the next list need to change
		if it does, change it (obvious bro)
		"""
		type_selection = mc.textScrollList(self.type_list, query=True, si=True)
		kind_selection = mc.textScrollList(self.kind_list, query=True, si=True)
		name_selection = mc.textScrollList(self.name_list, query=True, si=True)

		
		
		if type_selection != None:
			past_type_list = self.new_type_list 
			self.new_type_list = []

			for element in type_selection:
				for key, value in self.settings_dictionnary.items():
					if key == element:
						if type(value) != list:
							value = [value]
						for item in value:
							if (item in self.new_type_list)==False:
								self.new_type_list.append(item)
			if (past_type_list != self.new_type_list):
				mc.textScrollList(self.kind_list, edit=True, removeAll=True, append=self.new_type_list)


			
		if (type_selection != None) or (kind_selection != None) or (name_selection != None):
			self.search_files_function(type_selection, kind_selection, name_selection)






	def search_files_function(self, type_selection, kind_selection, name_selection):
		#get the content of all checkbox
		#to define the searching field
		project_limit = mc.checkBox(self.searchbar_checkbox, query=True, value=True)
		scenes_limit = mc.checkBox(self.scenes_checkbox, query=True, value=True)
		items_limit = mc.checkBox(self.items_checkbox, query=True, value=True)
		textures_limit = mc.checkBox(self.textures_checkbox, query=True, value=True)
		default_folder = mc.checkBox(self.folder_checkbox, query=True, value=True)

		project_name = os.path.basename(os.path.normpath(mc.textField(self.project_label, query=True, text=True)))

		starting_folder = []

		#define the starting folder of the research
		if type_selection != None:
			if default_folder == True:
				#search for the default folder name
				for t in type_selection:
					for key, value in self.settings.items():
						if key == t:
							starting_folder.append(t)
				if len(starting_folder)==0:
					mc.warning("No default folder defined!")
				else:
					mc.warning(starting_folder)
				'''
				for key, value in self.settings.items():
					if key == type_selection[0]:
						if value[2] != None:
							starting_folder = value[2]
				if starting_folder == None:
					mc.warning("No default folder for that type!")
				'''

		if project_limit == True:
			if mc.workspace(query=True, active=True) != None:
				starting_folder = [mc.workspace(query=True, active=True)]
			else:
				starting_folder = None
				mc.warning("No project defined!")


		if len(starting_folder) == 0:
			mc.warning("Pipeline folder set as starting folder!")
			starting_folder = [mc.textField(self.project_label, query=True, text=True)]

		
		for item in starting_folder:
			if os.path.isdir(item) == False:
				mc.error("Impossible to launch searching beacuse of the starting folder not existing!\n[%s]"%item)
				return
	

	
		#define the extension list according to checkbox
		extension_list = []
		if mc.checkBox(self.scenes_checkbox, query=True, value=True)== True:
			extension_list += self.additionnal_settings["3dSceneExtension"]
		if mc.checkBox(self.textures_checkbox, query=True, value=True)==True:
			extension_list += self.additionnal_settings["texturesExtension"]
		if mc.checkBox(self.items_checkbox, query=True, value=True)==True:
			extension_list += self.additionnal_settings["3dItemExtension"]
		#define the number of files from the starting folder
		total_files = 0
		for folder in starting_folder:
			total_files += int(sum([len(files) for root, dirs, files in os.walk(folder)]))
		i = 0



		#self.progress_bar = mc.progressWindow(title="Processing...", progress=0, status="Starting",min=0, max=total_files)
		#print(starting_folder)
		print("Searching...")




		
		final_file_list = []
		final_name_list = []

		
		
		
		for folder in starting_folder:
			print("searching in [%s]"%folder)
			p = 0 
			total_files = int(sum([len(files) for root, dirs, files in os.walk(folder)]))
			self.progress_bar = mc.progressWindow(title="Processing...", progress=0, status="Starting", min=0, max=total_files)
			for r, d, f in os.walk(folder):
				

				if ("PipelineManagerData" in d)==True:
					d.remove("PipelineManagerData")

				for file in f:
					p+=1
					print("[%s | %s]		checking - %s"%(p, total_files, file))
					mc.progressWindow(edit=True, progress=p, status="Processing...")
					#get files information
					file_path = os.path.dirname(file)
					file_name = os.path.splitext(os.path.basename(file))[0]
					file_extension = os.path.splitext(file)[1]
					#check if extension of the file is in the list
					if (len(extension_list)!= 0) and (file_extension in extension_list)==False:
						continue
					
					#split de filename to check the len of the syntax
					#get the syntax and the keyword of the current type
					for t in type_selection:
						error=False
						syntax = self.settings[t][0]
						keyword = self.settings[t][1]

						splited_filename = file_name.split("_")
						splited_syntax = syntax.split("_")

						

						if len(splited_filename) != len(splited_syntax):
							error=True
							continue

						#DISPLAY ONLY FILES WITH THE RIGHT SIZE
						#print("\nNEW FILE - %s"%file)
						#print("[key]" in splited_syntax)





						if "[type]" in splited_syntax:
							type_index = splited_syntax.index("[type]")
							"""
							if no type is selected then 
							skip the type error
							"""
							if kind_selection == None:
								pass
							#print(splited_filename[type_index], splited_filename[type_index] in kind_selection, kind_selection)
							elif (splited_filename[type_index] in kind_selection)==False:
								error=True 
								print("ERROR type %s" % file)
								continue


						if "[key]" in splited_syntax:
							key_index = splited_syntax.index("[key]")

							#print(splited_filename[key_index], keyword)
							if splited_filename[key_index] != keyword:
								print("ERROR key %s" % file)
								error=True 
								#print("keyword error")
								continue
							else:
								print(file)


						#check the whole syntax of the file
						if "[project]" in splited_syntax:
							project_index = splited_syntax.index("[project]")
							#print(splited_filename[keyword_index], project_name)
							if splited_filename[project_index] != project_name:
								print("ERROR project %s" % file)
								error=True 
								continue

						if "[version]" in splited_syntax:	
							version_index = splited_syntax.index("[version]")

							if (splited_filename[version_index]) != "publish":
								if (len(splited_filename[version_index].split("v")) == 2):
									if (splited_filename[version_index].split("v")[0] != "") or (splited_filename[version_index].split("v")[1].isdigit()==False):
										print("ERROR version %s" % file)
										error=True
	
										continue
								else:

									error=True
									continue

						if "[sqversion]" in splited_syntax:
							version_index = splited_syntax.index(["sqversion"])
							if (len(splited_filename[version_index].split("sq"))==2):
								if (splited_filename[version_index].split("sq")[0] != "") or (splited_filename[version_index].split("sq")[1].isdigit()==False):
									error=True 

									continue
						if "[shversion]" in splited_syntax:
							version_index = splited_syntax.index(["shversion"])
							if (len(splited_filename[version_index].split("sh"))==2):
								if (splited_filename[version_index].split("sh")[0] != "") or (splited_filename[version_index].split("sh")[1].isdigit()==False):
									error=True 

									continue
						#check that the file is contained in name list selection
						if (name_selection != None):
							#check the name keyword in the syntax
							if ( "[name]" in splited_syntax ) == False:
								print("ERROR name %s" % file)
								error=True
								continue
							else:
								
								
								if (splited_filename[splited_syntax.index("[name]")] in name_selection) == False:
									print("ERROR name %s" % file)
									error=True 
									continue

								


						if ("[name]" in splited_syntax) and (error == False):
							name = splited_filename[splited_syntax.index("[name]")]
							if (name in final_name_list)==False:
								final_name_list.append(name)


						if ("[artist]" in splited_syntax):
							artist_name = splited_filename[splited_syntax.index("[artist]")]
							print(artist_name)
						


					


					if error == False:
						#print("FILE CHECKED - %s" % file)
						final_file_list.append(file)

		print("\nSEARCHING DONE!!!\n")
		mc.progressWindow(endProgress=True)

		
		mc.textScrollList(self.result_list, edit=True,removeAll=True, append=final_file_list)
		mc.textScrollList(self.name_list, edit=True, removeAll=True, append=final_name_list)
		
				





		#create the starting folder
		"""
		for r, d, f in os.walk(folder_name):
			if ("PipelineManagerData" in d)==True:
				d.remove("PipelineManagerData")
			
			for file in f:
				files_in_folder.append(os.path.join(r, file))
		
		 	
		#splited_file = os.path.splitext(os.path.basename(file))[0].split("_")
	

					else:
						for i in range(0, len(splited_syntax)):
							#check each keyword
							#store the name after the control!!!
							if splited_syntax[i] == "[key]":
								if splited_file[i] != keyword:
									error=True
							elif splited_syntax[i] == "[project]":
								if splited_file[i] != project_name:
									error=True
							
							#elif splited_syntax[i] == "[state]":
							#	if (splited_file[i] in ["edit", "publish"])==False:
							#		error=True
							
							elif splited_syntax[i] == "[type]":
								if kind_selection != None:
									if (splited_file[i] in kind_selection)==False:
										error=True
							elif splited_syntax[i] == "[version]":
								if splited_file[i] != "publish":
									splited = splited_file[i].split("v")
									if len(splited) != 2:
										if (splited[0] != "") or (splited[1].isnumeric())==False:
											error=True
							elif splited_syntax[i] == "[name]":
								name = splited_file[i]
							elif splited_syntax[i] == "[shversion]":
								if splited_file[i] != "publish":
									splited = splited_file[i].split("sh")
									if len(splited)!=2:
										error=True
									else:
										if (splited[0]!="") or (splited[0].isdigit())==False:
											error=True
							elif splited_syntax[i] == "[sqversion]":
								if splited_file[i] != "publish":
									splited = splited_file[i].split("sq")
									if len(splited)!=2:
										error=True
									else:
										if (splited[0]!="") or (splited[0].isdigit())==False:
											error=True
							
							else:
								#check if the syntax item is the same item in the filename
								#it mean that no variable was use in the syntax field
								if splited_syntax[i] != splited_file[i]:
									error=True
		"""
							




	def save_syntax_function(self, event):
		#check selection of the textscrolllist
		selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		new_content = mc.textField(self.setting_syntax_textfield, query=True, text=True)

		if (self.letter_verification_function(new_content)==None) or (self.letter_verification_function(new_content)==False):
			mc.error("You have to write a new syntax to replace the old one!")
			return
		if selection == None:
			mc.error("You have at least one setting to change!")
			return 
		else:
			selection = selection[0]
			#get list of informations from settings dictionnary
			keys = list(self.settings.keys())
			values = list(self.settings.values())


			self.settings[selection][0] = new_content

			"""

			for rank in selection:
				for i in range(0, len(keys)):
					#check if at the specified rank
					if (int(rank)-1) == i:
						self.add_log_content_function("[%s] New syntax has been saved" % keys[i])
						values[i][0] = new_content
			for i in range(0, len(keys)):
				self.settings[keys[i]] = values[i]

			"""

			self.save_settings_file()
			self.deselect_all_lists()
			mc.warning("Nomenclature saved successfully for [%s]" % selection)



	def deselect_all_lists(self):
		mc.textScrollList(self.type_list, edit=True, deselectAll=True)
		mc.textScrollList(self.name_list, edit=True, deselectAll=True)
		mc.textScrollList(self.kind_list, edit=True, deselectAll=True)
		mc.textScrollList(self.result_list, edit=True, deselectAll=True)






	def reset_default_syntax_function(self,event):
		
		self.default_settings = {
			"character":["[project]_[key]_[name]_[type]", "char", None],
			"prop":["[project]_[key]_[name]_[type]", "prop", None],
			"set":["[project]_[key]_[name]_[type]", "set", None,],
			"fx":["[project]_[key]_[name]_[type]","fx", None,],
			"shots":["[project]_[key]_[sqversion]_[shversion]", "shots", None,]
		}
		basic_file_type_list = ["mod", "rig", "groom", "cloth", "lookdev", "layout", "camera", "anim", "render", "compositing"]

		#TYPE OF DATA
		#DETECTION OF FILES
		self.default_settings_dictionnary = {
			"character": basic_file_type_list,
			"prop": basic_file_type_list, 
			"set": basic_file_type_list,
			"fx": "unknown",
			"shots": ["layout", "camera", "anim", "render", "compositing"],
		}

		self.default_additional_settings = {
			"checkboxValues":[False, True, False, False],
			"3dSceneExtension":[".ma",".mb"],
			"3dItemExtension":[".obj", ".fbx"],
			"texturesExtension":[".png", ".tif",".tiff",".tex", ".exr", ".jpg"],
			"mayaProjectName":"maya",
			"editPublishFolder":["edit", "publish"]
		}

		
		
		self.settings = self.default_settings
		self.settings_dictionnary = self.default_settings_dictionnary
		self.additionnal_settings = self.default_additional_settings
		self.save_settings_file()




	def define_default_folder_function(self, event):
		#get pipeline folder
		project_name = mc.textField(self.project_label, query=True, text=True)
		#get selection in textscrolllist
		selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		if (selection == None):
			mc.error("You have to select a type to define a new default folder!")
			return
		else:
			#open a file dialogue interface
			if os.path.isdir(project_name)==False:
				new_default_folder = mc.fileDialog2(ds=1, fm=3)
			else:
				new_default_folder = mc.fileDialog2(ds=1, fm=3, dir=project_name)

			if new_default_folder == None:
				mc.warning("No default folder saved!")
				return
			else:
				for key, value in self.settings.items():
					if key == selection[0]:
						value[2] = new_default_folder[0]
						self.settings[key] = value
						self.save_settings_file()

						mc.button(self.setting_default_folder_button, edit=True, label=new_default_folder[0])
		

		



	def import_in_scene_function(self, command, event):
		#get the selection in the file list
		file_selection = mc.textScrollList(self.result_list, query=True, si=True)
		folder_name = (mc.textField(self.project_label, query=True, text=True))
		#project_name = os.path.basename(os.path.normpath(folder_name))

		if file_selection == None:
			mc.error("You have to select at least one file!")
			return 



		#try to find file in the folder
		for item in file_selection:
			for r, d, f in os.walk(folder_name):
				for file in f:
					if file == item:
						self.add_log_content_function("[%s] File found in project" % item)
						if os.path.isfile(os.path.join(r, item)):
							try:
								if command==False:
									mc.file(os.path.join(r, item), i=True)
								if command==True:
									mc.file(os.path.join(r, item), r=True)
								self.add_log_content_function("[%s] File imported successfully"%item)
							except:
								mc.error("Impossible to import file!")
								return
								


	def clean_function(self, event):
		nodes_list = mc.ls(st=True)
		node_name = []
		node_type = []

		for i in range(0, len(nodes_list)):
			if i%2 == 0:
				node_name.append(nodes_list[i])
			else:
				node_type.append(nodes_list[i])
		#for each node check its connection
		for item in node_name:
			print(mc.listConnections(item))




	def delete_type_function(self, event):
		#get the value in the type textscrolllist
		type_list = mc.textScrollList(self.settings_type_list, query=True, si=True)

		if type_list == None:
			mc.error("You have to select at least one type to delete!")
			return

		else:
			
			for item in type_list:
				#delete the corresponding key in the dictionnary
				self.settings.pop(item)
				self.settings_dictionnary.pop(item)

		
			
			self.save_settings_file()
			keys = list(self.settings.keys())
			mc.textScrollList(self.settings_type_list, edit=True, removeAll=True, append=keys)
			mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True)


	def save_project_name_function(self, event):
		#check the content of the textfield
		content = mc.textField(self.settings_project_folder_textfield, query=True, text=True)
		if self.letter_verification_function(content)==False:
			mc.error("You have to write a name to save!")
			return
		for key, value in self.settings.items():
			value[4] = content
			self.settings[key] = value
		mc.warning("Maya project name saved successfully!")
		return
			

	def create_type_function(self, event):
		"""
		take the content of the type name textfield / setting syntax textfield
		and create a new setting

		if there is no content in the syntax field put "" in the syntax
		#so the program will detect that it's impossible to search for file
		"""
		setting_name_content = mc.textField(self.setting_type_textfield, query=True, text=True)
		setting_syntax_content = mc.textField(self.setting_syntax_textfield, query=True, text=True)
		setting_keyword_content = mc.textField(self.setting_keyword_textfield, query=True, text=True)

		print(setting_name_content)
		if (self.letter_verification_function(setting_name_content)==False) or (self.letter_verification_function(setting_name_content)==None):
			mc.error("You have to define a name!")
			return

		if (self.letter_verification_function(setting_syntax_content)==False) or (self.letter_verification_function(setting_syntax_content)==None):
			mc.warning("No nomenclature saved with the new Kind!")
			setting_syntax_content = "NoSyntaxDefined"
		if (self.letter_verification_function(setting_keyword_content) == False) or (self.letter_verification_function(setting_keyword_content)==None):
			mc.warning("No keyword saved with the new Kind!")
			setting_keyword_content = "NoKeywordDefined"

		if (setting_name_content in self.settings)==True:
			mc.error("An existing type with the same name already exist!")
			return
		else:
			#delete all the buttons on the GUI
			#self.delete_button_function()
			#create the new key in the dictionnary
			
			self.settings[setting_name_content] = [setting_syntax_content, setting_keyword_content, None, [None, None], "maya"]
			self.settings_dictionnary[setting_name_content] = self.file_type
			self.save_settings_file()
			keys = list(self.settings.keys())
			mc.textScrollList(self.settings_type_list, edit=True, removeAll=True, append=keys)
			mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True)
			

		

	def save_keyword_function(self, event):
		try:
			selection = mc.textScrollList(self.settings_type_list, query=True, sii=True)[0]
		except TypeError:
			mc.error("You have to select one Kind to change in the list!")
			return
		content = mc.textField(self.setting_keyword_textfield, query=True, text=True)

		#check if the content contain something
		if (self.letter_verification_function(content)==False) or (self.letter_verification_function(content)==None):
			mc.error("You have to define a new keyword!")
			return
		keyword_exist = False
		for key, value in self.settings.items():
			if value[1] == content:
				keyword_exist = True
		if keyword_exist == True:
			mc.error("This keyword is already taken!")
			return
		else:
			
			#change the value in the dictionnary
			keys = list(self.settings.keys())
			values = list(self.settings.values())

			for i in range(0, len(keys)):
				if i == (int(selection) - 1):
					self.settings[keys[i]] = [values[i][0], content, values[i][2]]	
			#save the new dictionnary
			self.save_settings_file()
			self.refresh_export_type_list_function()
			mc.warning("Keyword saved successfully!")
			




	def create_file_kind_function(self, event):
		type_selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		if type_selection == None:
			mc.error("You have to select at least one Type Name!")
			return
		new_kind_name = mc.textField(self.create_file_kind_textfield, query=True, text=True)
		if (self.letter_verification_function(new_kind_name)==False) or (self.letter_verification_function(new_kind_name)==None):
			mc.error("You have to define a name for the new type!")
			return
		else:
			for item in type_selection:
				settings_list = list(self.settings_dictionnary[item])
				settings_list.append(new_kind_name)
				self.settings_dictionnary[item] = settings_list
			self.save_settings_file()
			mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True, append=self.settings_dictionnary[item])
			mc.warning("Item created successfully!")
			return

	def delete_file_kind_function(self, event):
		type_selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		kind_selection = mc.textScrollList(self.settings_type_textscrolllist, query=True, si=True)
		try:
			if len(type_selection)==None or len(kind_selection)==None:
				mc.error("You have to select a Type Name and a type to delete!")
				return
		except:
			mc.error("You have to select a Type Name and a type to delete!")
		else:
			settings_list = list(self.settings_dictionnary[type_selection[0]])
			for item in kind_selection:
				settings_list.remove(item)

			self.settings_dictionnary[type_selection[0]] = settings_list
			self.save_settings_file()
			mc.warning("Item removed successfully!")
			mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True, append=self.settings_dictionnary[type_selection[0]])
			return

	def rename_file_kind_function(self, event):
		#take the content in textfield
		textfield_content = mc.textField(self.create_file_kind_textfield, query=True, text=True)

		if (self.letter_verification_function(textfield_content))==False or (self.letter_verification_function(textfield_content))==None:
			mc.error("You have to define a new name!")
			return
		else:
			type_selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
			kind_selection = mc.textScrollList(self.settings_type_textscrolllist, query=True, si=True)

			if (type_selection==None) or (kind_selection==None):
				mc.error("You have to select a file type to rename!")
				return
			else:
				#rename in the dictionnary
				settings_list = list(self.settings_dictionnary[type_selection[0]])

				for i in range(0, len(settings_list)):
					if (settings_list[i] in kind_selection)==True:
						settings_list[i] = textfield_content
				self.settings_dictionnary[type_selection[0]] = settings_list
				self.save_settings_file()
				mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True, append=settings_list)
				mc.warning("Item renamed successfully!")
				return

	def export_edit_file_function(self, event):
		"""
		create the full filename from syntax settings
		"""
		final_syntax = []
		if mc.textScrollList(self.export_edit_kind_textscrolllist, query=True, si=True)==None:
			mc.error("You have to select a type!")
			return

		for kind, content in self.settings.items():
			if kind == mc.textScrollList(self.export_edit_kind_textscrolllist, query=True, si=True)[0]:
				syntax = content[0].split("_")

				for element in syntax:
					if element == "[project]":
						final_syntax.append(os.path.basename(os.path.normpath(mc.workspace(query=True, active=True))))
					if element == "[key]":
						final_syntax.append(content[1])
					if element == "[artist]":
						#get the content of artist textfield
						artist_name = mc.textField(self.export_artist_name_textfield, query=True, text=True)
						if (self.letter_verification_function(artist_name)) != True:
							mc.error("You have to enter a valid artist name!")
							return
						else:
							final_syntax.append(artist_name)
					if element == "[name]":
						name = mc.textField(self.export_edit_name_textfield, query=True, text=True)
						if (self.letter_verification_function(name)==False) or (self.letter_verification_function(name)==None):
							mc.error("You have to define a name for the new file!")
							return
						else:
							final_syntax.append(name)
					if element == "[type]":
						type_selection = mc.textScrollList(self.export_edit_type_textscrolllist, query=True,si=True)
						if type_selection == None:
							mc.error("You have to select a type!")
							return
						else:
							final_syntax.append(type_selection[0])
					if (element == "[version]") or (element == "[shversion]") or (element == "[sqversion]"):
						if element == "[version]":
							version = list(str(mc.intField(self.export_edit_fileversion, query=True, value=True)))
						if element == "[shversion]":
							version = list(str(mc.intField(self.export_edit_shotversion, query=True, value=True)))
						if element == "[sqversion]":
							version = list(str(mc.intField(self.export_edit_sqversion, query=True, value=True)))
						if len(version)<3:
							while len(version) < 3:
								version.insert(0,"0")
						final_syntax.append("v"+"".join(version))
					

		final_filename = "_".join(final_syntax)
		#check if we need to find the default folder
		if mc.checkBox(self.export_edit_defaultfolder_checkbox, query=True, value=True)==True:
			
			for kind, content in self.settings.items():
			
				if kind == mc.textScrollList(self.export_edit_kind_textscrolllist, query=True, si=True)[0]:
					default_folder = content[2]
	
					if (default_folder == None) or (default_folder == "None"):
						mc.error("Impossible to use default folder You need to define on in settings!")
						return
					else:
						final_filename = os.path.join(default_folder, final_filename+".ma")
		
			

		else:
			try:
				folder = mc.fileDialog2(fm=3)[0]
			except:
				mc.error("You have to select a destination folder!")
				return
			else:
				final_filename = os.path.join(folder, final_filename+".ma")


		
		#save the current file
		#rename the current file
		#save the renamed 
		if os.path.isfile(final_filename)==False:
			try:
				mc.file(save=True)
			except:
				mc.warning("Impossible to save the current file\nNo name defined for it!")
				pass
			mc.file(rename=final_filename)
			mc.file(save=True, f=True, type="mayaAscii")

			mc.warning("EDIT FILE SUCCESFULLY SAVED\n[%s]"%final_filename)
			self.take_picture_function("test")
			self.add_log_content_function("Export edit file succeed [%s]"%final_filename)
		else:
			self.add_log_content_function("Export edit file failed, the file already exist")
			mc.error("This file already exist!")
			return
		




		


	def export_publish_function(self, event):
		#get current project path
		project_path = mc.workspace(query=True, active=True)
		project_name = os.path.basename(project_path)
		current_scene_path = (mc.file(query=True, sn=True))
		"""
		save the current file as it is
		check all elements of the publish step list
		save the current file as the new publish file

		save the current file in the current project folder
		search for the pulbish folder
		"""
		try:
			mc.file(save=True)
		except:
			mc.error("Impossible to save the current file!")
			return
		selection = mc.textScrollList(self.export_publish_textscrolllist, query=True, si=True)

		if type(selection)==list:
			for item in selection:

				#DELETE UNUSED NODES
				if item == self.publish_step_list[0]:
					#delete unused nodes
					mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1, "deleteUnusedNodes");')
					mc.warning("Unused nodes deleted")


				#HIDE JOINTS
				if item == self.publish_step_list[1]:
					#hide all joints
					#display override in ref mode
					select_all = mc.select(all=True)
					selection = mc.ls(sl=True)
					final_selection = []

					for item in selection:
						final_selection.append(item)

						if mc.listRelatives(item, allDescendents=True) != None:
							final_selection += mc.listRelatives(item, allDescendents=True)
					
					joint_list = []
					for item in final_selection:
						if mc.objectType(item) == "joint":
							joint_list.append(item)
					
					for joint in joint_list:
						mc.setAttr("%s.overrideEnabled"%joint,1)
						mc.setAttr("%s.overrideDisplayType"%joint,2)
					mc.select(all=True, deselect=True)

					mc.warning("All controllers hidden")


				#REMOVE ALL ANIMATIONS KEYS
				if item == self.publish_step_list[2]:
					#select all nurbs curve and remove all keys on them
					print("hello world!")

		#check the nomenclature of the current file to define the right publish nomenclature
		#get checkbox values
		if mc.checkBox(self.export_publish_samelocation_checkbox, query=True, value=True)==True:
			#get current location of the file your working on
			publish_path = os.path.dirname(mc.file(query=True, sn=True))
			if os.path.dirname(publish_path)==False:
				mc.error("Impossible to export, no location existing!")
				return
			#change the nomenclature of the current file
			extension = os.path.splitext(current_scene_path)[1]
			splited_name = os.path.basename(os.path.splitext(current_scene_path)[0]).split("_")
			version_present=False
			for i in range(0, len(splited_name)):
				if list(splited_name[i])[0] == "v":
					#print(splited_name[i].split("v"))
					
					if len(splited_name[i].split("v"))==2:
						
						if (splited_name[i].split("v")[1].isnumeric())==True:
							splited_name[i] = "publish"
							version_present=True 
							break
			if version_present==False:
				splited_name.insert(0, "Publish")
			filename = "_".join(splited_name)+extension
			mc.file(save=True)
			#save the new file at the new destination
			mc.file(rename=os.path.join(publish_path, filename))
			if extension == ".ma":
				mc.file(save=True, type="mayaAscii")
			if extension == ".mb":
				mc.file(save=True, type="mayaBinary")
			mc.warning("Publish scene saved successfully")
			print(os.path.join(publish_path, filename))



		if mc.checkBox(self.export_publish_searchlocation_checkbox, query=True, value=True)==True:
			#get values from folder presets
			edit_folder_name = mc.textField(self.settings_editfolder_textfield, query=True, text=True)
			publish_folder_name = mc.textField(self.settings_publishfolder_textfield, query=True, text=True)

			if (self.letter_verification_function(edit_folder_name)==False) or (self.letter_verification_function(publish_folder_name)==False):
				mc.error("Impossible to get edit / publish folder names!")
				return
			
			if os.path.isdir(project_path)==False:
				mc.error("Impossible to export, project isn't defined!")
				return
			
			find = False 
			path = current_scene_path
			folder_to_recreate = []
			for i in range(0, len(current_scene_path.split("/"))):
			

				if os.path.basename(path) == edit_folder_name:
					if os.path.isdir(os.path.join(os.path.dirname(path), publish_folder_name))==True:
						folder_to_recreate.pop(-1)
						publish_path = os.path.join(os.path.dirname(path), publish_folder_name)
						find = True

						#recreate folders if they don't exist
						folder_to_recreate.reverse()
						for i in range(0, len(folder_to_recreate)):
							if os.path.isdir(os.path.join(publish_path,folder_to_recreate[i]))==False:
								os.mkdir(os.path.join(publish_path, folder_to_recreate[i]))
							publish_path = os.path.join(publish_path,folder_to_recreate[i])
							
						#detect the new nomenclature of the file
						extension = os.path.splitext(current_scene_path)[1]
						splited_name = os.path.basename(os.path.splitext(current_scene_path)[0]).split("_")
						version_present=False
						for i in range(0, len(splited_name)):
							if list(splited_name[i])[0] == "v":
								#print(splited_name[i].split("v"))
								
								if len(splited_name[i].split("v"))==2:
									
									if (splited_name[i].split("v")[1].isnumeric())==True:
										splited_name[i] = "publish"
										version_present=True 
										break
								
						if version_present==False:
							splited_name.insert(0, "Publish")
						filename = "_".join(splited_name)+extension
						
						#save the current file
						mc.file(save=True)
						#save the new file at the new destination
						mc.file(rename=os.path.join(publish_path, filename))
						if extension == ".ma":
							mc.file(save=True, type="mayaAscii")
						if extension == ".mb":
							mc.file(save=True, type="mayaBinary")

						mc.warning("Publish scene saved successfully")
						print(os.path.join(publish_path, filename))
						self.take_picture_function("test")
						break
				folder_to_recreate.append(os.path.basename(os.path.dirname(path)))	
				if os.path.basename(path) == project_name:
					mc.error("No edit folder found in the project!")
					return

				
				path = os.path.normpath(path+os.sep+os.pardir)



			
			



						










	def archive_in_project_function(self, event):
		#check the content of the selection
		selection = mc.textScrollList(self.result_list, query=True, si=True)
		if (len(selection) == 0) or (selection == None):
			mc.error("You have to select something to create put it in the project archive!")
			return
		folder = mc.textField(self.project_label, query=True, text=True)
		if os.path.isdir(os.path.join(folder, "PipelineManagerData"))==False:
			mc.error("You have to set the pipeline folder first!")
			return
		#find the path of the selection files
		for i in range(0, len(selection)):
			for r, d, f in os.walk(folder):
				for file in f:
					if file == selection[i]:
						selection[i] = os.path.join(r, file)
						

		if os.path.isfile(os.path.join(folder, "PipelineManagerData/PipelineArchive.zip"))==False:
			with ZipFile(os.path.join(folder, "PipelineManagerData/PipelineArchive.zip"), "w", ZIP_DEFLATED) as zip_archive:
				for i in range(0, len(selection)):
					zip_archive.write(selection[i], os.path.basename(selection[i]))
					print("[%s/%s]"%(i+1, len(selection)),os.path.basename(selection[i]), " - ARCHIVED")
			mc.warning("Project archive created")

		mc.warning("Files successfully added to the archive!")
		return







	def save_folder_preset_function(self, event):
		#check the content of textfields
		content1 = mc.textField(self.settings_editfolder_textfield, query=True, text=True)
		content2 = mc.textField(self.settings_publishfolder_textfield, query=True, text=True)
		
		value1 = self.letter_verification_function(content1)
		value2 = self.letter_verification_function(content2)

		print(content1, content2, value1, value2)
				
		if (value1 == False) or (value1 == None):
			content1 = None 
		if (value2 == False) or (value2 == None):
			content2 = None
		for key, value in self.settings.items():
			value[3] = [content1, content2]
			self.settings[key] = value 
			print(self.settings[key])
		self.save_settings_file()






	def searchbar_function(self, event):
		#or limit to the project?
		#search for files in the whole pipeline?
		final_extension_list = []

		project_limit = mc.checkBox(self.searchbar_checkbox, query=True, value=True)
		scenes_limit = mc.checkBox(self.scenes_checkbox, query=True, value=True)
		items_limit = mc.checkBox(self.items_checkbox, query=True, value=True)
		textures_limit = mc.checkBox(self.textures_checkbox, query=True, value=True)
		searchbar_content = mc.textField(self.main_assets_searchbar, query=True, text=True)

		if scenes_limit == True:
			final_extension_list = final_extension_list + self.additionnal_settings["3dSceneExtension"]
		if items_limit == True:
			final_extension_list = final_extension_list + self.additionnal_settings["3dItemExtension"]
		if textures_limit ==True:
			final_extension_list = final_extension_list + self.additionnal_settings["texturesExtension"]


		

		if (self.letter_verification_function(searchbar_content)==False) or (self.letter_verification_function(searchbar_content)==None):
			mc.error("Nothing to search!")
			return
		searchbar_content = searchbar_content.split(";")

		if project_limit == True:
			starting_folder = mc.workspace(query=True, active=True)
			if starting_folder == None:
				mc.error("Impossible to search in project!")
				return

		else:
			starting_folder = mc.textField(self.project_label, query=True, text=True)
			if os.path.isdir(starting_folder)==False:
				mc.error("Impossible to search!")
				return

		
        

		#list all the files in defined directory
		file_list = []
		total_files = int(sum([len(files) for root, dirs, files in os.walk(starting_folder)]))
		i=0
		self.progress_bar = mc.progressWindow(title="Processing...", progress=0, status="Starting", min=0, max=total_files)

		print("Searching...")
		for r,d,f in (os.walk(starting_folder)):

			print("Checking folder [%s]" % r)
			mc.progressWindow(edit=True, progress=i, status="Processing...")

			if ("PipelineManagerData" in d)==True:
				d.remove("PipelineManagerData")

			for file in f:
				i+=1
				print("[%s | %s]		checking - %s"%(i,total_files,file))
				valid=True

				if len(final_extension_list) != 0:
					if (os.path.splitext(file)[1] in final_extension_list) != True:
						continue

				for keyword in searchbar_content:
					if (keyword in file) == False:
						valid=False 

				if valid == True:
					file_list.append(file)
			
		mc.progressWindow(endProgress=True)
                
     	
        
		mc.textScrollList(self.result_list, edit=True, removeAll=True, append=file_list)




	def open_location_function(self, data, event):
		print(data, event)
		#check selection in result textscrolllist
		selection = mc.textScrollList(self.result_list, query=True, si=True)[0]
		#check the location of the file in the pipeline
		pipeline_path = mc.textField(self.project_label, query=True, text=True)
		#go through all the files
		for r, d, f in os.walk(pipeline_path):
			for file in f:
				if os.path.basename(file) == selection:
					#open a browser with the location of that file
					if data == "folder":
						mc.fileDialog2(ds=1, fm=0, dir=r)
					else:
						#open the file
						try:
							mc.file(save=True,type="mayaAscii")
						except:
							mc.warning("Impossible to save the current scene!")
							return

						try:
							print(os.path.join(r, file))
							print(os.path.isfile(os.path.join(r, file)))	
							mc.file(os.path.join(r, file), force=True,o=True)
						except:
							mc.error("Impossible to open the file!")
					break




	def set_project_function(self, event):
		#check the first item of the selection
		try:
			selection = mc.textScrollList(self.result_list, query=True, si=True)[0]
		except:
			mc.error("You have to select an item first!")
			return
		#get the path of the file
		pipeline_path = mc.textField(self.project_label, query=True, text=True)
		pipeline_name = os.path.basename(pipeline_path)
		#get project keyword
		project_name = self.additionnal_settings["mayaProjectName"]
		for r, d, f in os.walk(pipeline_path):
			for file in f:
				if os.path.basename(file) == selection:
					original_path = os.getcwd()

					"""
					go to path of the file
					"""
					os.chdir(r)
					path = os.getcwd()
					defined = False
					for i in range(0, len(r.split("/"))+1):
						#print(os.getcwd(), os.path.basename(path), project_name)
						if os.path.basename(path) == project_name:
							#set project here!!!
							mc.workspace(path, openWorkspace=True)
							mc.warning("Project path set to : %s"%path)
							defined=True
							

						
						path = os.path.normpath(path+os.sep+os.pardir)
						os.chdir(path)

					if defined==False:
						mc.error("Impossible to find a project folder for that file!")
						return


	def open_file_function(self, event):
		try:
			selection = mc.textScrollList(self.result_list, query=True, si=True)[0]
		except:
			mc.error("You have to select a file to open!")
			return

		#get path of the scene
		current_scene = mc.file()
		pipeline_path = mc.textField(self.project_label, query=True, text=True)
		for r, d, f in os.walk(pipeline_path):
			for file in f:
				if os.path.basename(file) == selection:
					#save current file
					try:
						mc.file(save=True)
					except RuntimeError:
						mc.warning("This file doesn't have any name!")
						
					mc.file(new=True, force=True)
					mc.file(os.path.join(r, file), o=True)
					mc.warning("File opened successfully")
					self.take_picture_function("test")


	def replace_filename_function(self,event):
		"""
		get fileselection
		"""
		selection = mc.textScrollList(self.result_list, query=True, si=True)
		pipeline_path = mc.textField(self.project_label, query=True, text=True)
		replace = mc.textField(self.rename_replace_content, query=True, text=True)
		replaceby = mc.textField(self.rename_replaceby_content, query=True, text=True)

		for r, d, f in os.walk(pipeline_path):
			for file in f:
				for element in selection:
					if os.path.basename(file) == element:
						old_scene = os.path.join(r, file)
						new_scene = os.path.join(r, file.replace(replace, replaceby))

						try:
							os.rename(old_scene, new_scene)
							mc.warning("Renamed successfully!")
							print(old_scene)
							print(new_scene)
							print("\n")
						except:
							mc.warning("Impossible to rename!")
							print(old_scene)

		mc.textScrollList(self.result_list, edit=True, removeAll=True)
		mc.textField(self.main_assets_searchbar, edit=True, text="")




	def take_picture_function(self, event):
		#get current frame 
		current_frame = int(pm.currentTime(query=True))
		#get the name of the current filename
		current_file = mc.file(query=True, sn=True)
		#check if the file exist in the pipeline
		if os.path.isfile(current_file) == False:
			mc.error("This file isn't saved in your pipeline yet!\nSave it first!")
			return
		current_filename = os.path.splitext(os.path.basename(mc.file(query=True, sn=True)))[0]

		#define the path of the image folder
		#query the value of the pipeline textfield
		pipeline_path = mc.textField(self.project_label, query=True, text=True)

		if os.path.isdir(os.path.join(pipeline_path, "PipelineManagerData/ThumbnailsData"))==False:
			try:
				os.mkdir(os.path.join(pipeline_path, "PipelineManagerData/ThumbnailsData"))
			except:
				mc.error("Impossible to create thumbnail folder in the current pipeline!")
				return
		else:
			path = os.path.join(pipeline_path, "PipelineManagerData/ThumbnailsData/Thumbnail_%s.jpg"%current_filename)
			mc.playblast(fr=current_frame, v=False, format="image", c="jpg", orn=False, wh=[300,300],cf=path)

			mc.warning("Picture saved!\n%s"%path)
			return





	def search_for_thumbnail_function(self):
		self.search_for_note_function()
		#get the name of the selected item
		selection = os.path.splitext(mc.textScrollList(self.result_list, query=True, si=True)[0])[0]
		#get the name of the current project
		current_project = mc.textField(self.project_label, query=True, text=True)
		if os.path.isdir(os.path.join(current_project, "PipelineManagerData/ThumbnailsData"))==False:
			mc.error("Thumbnails folder doesn't exist in that pipeline!")
			return 
		if os.path.isfile(os.path.join(current_project, "PipelineManagerData/ThumbnailsData/Thumbnail_%s.jpg"%selection))==False:
			print(os.path.join(current_project, "PipelineManagerData/ThumbnailsData/Thumbnail_%s"%selection))
			mc.warning("image not found!")
			return
		else:
			mc.image(self.image_box, edit=True,image=os.path.join(current_project,"PipelineManagerData/ThumbnailsData/Thumbnail_%s.jpg"%selection))
			mc.warning("image set!")
			return



	def save_current_scene_function(self, event):
		try:
			mc.file(save=True)
		except RuntimeError:
			return
		else:	
			#save new picture of that scene
			self.take_picture_function("test")	



	def save_additionnal_settings_function(self, event):
		#get value of each checkbox
		searchbar_limit = mc.checkBox(self.searchbar_checkbox, query=True, value=True)
		scenes = mc.checkBox(self.scenes_checkbox, query=True, value=True)
		items = mc.checkBox(self.items_checkbox, query=True, value=True)
		textures = mc.checkBox(self.textures_checkbox, query=True, value=True)
		folder = mc.checkBox(self.folder_checkbox, query=True, value=True)

		#get each extension list
		scenes_extension_list = mc.textField(self.assets_scene_extension_textfield, query=True, text=True).split(";")
		items_extension_list = mc.textField(self.assets_items_extension_textfield, query=True, text=True).split(";")
		textures_extension_list = mc.textField(self.assets_textures_extension_textfield, query=True, text=True).split(";")

		self.additionnal_settings["checkboxValues"] = [searchbar_limit, scenes, items, textures, folder]
		self.additionnal_settings["3dSceneExtension"] = scenes_extension_list
		self.additionnal_settings["3dItemExtension"] = items_extension_list
		self.additionnal_settings["texturesExtension"] = textures_extension_list

		"""
		self.default_additional_settings = {
			"checkboxValues":[False, True, False, False],
			"3dSceneExtension":["ma","mb"],
			"3dItemExtension":["obj", "fbx"],
			"texturesExtension":["png", "tif","tiff","tex", "exr", "jpg"],
			"mayaProjectName":"maya",
			"editPublishFolder":["edit", "publish"]
		}
		"""
		self.save_settings_file()
		mc.warning("Saved!")



		
	def define_export_nomenclature_function(self, status):
		type_selection = mc.textScrollList(self.export_type_textscrolllist, query=True, si=True)
		kind_selection = mc.textScrollList(self.export_kind_textscrolllist, query=True, si=True)

		if type_selection == None:
			mc.error("You have to select a type!")
			return
		nomenclature = self.settings[type_selection[0]]
		if ("[type]" in nomenclature) and (kind_selection == None):
			mc.error("You have also to select a kind!")
			return
		else:
			#get the nomenclature of the current type
			nomenclature = self.settings[type_selection[0]][0]
			keyword = self.settings[type_selection[0]][1]
			defaultfolder = self.settings[type_selection[0]][2]

			splited_nomenclature = nomenclature.split("_")
			splited_filename = os.path.splitext(os.path.basename(mc.file(query=True, sn=True)))[0].split("_")
			
			print(type_selection[0])
			print(splited_nomenclature)
			print(splited_filename)

			final_filename = []

			for i in range(0, len(splited_nomenclature)):
				#print(splited_nomenclature[i])
				if splited_nomenclature[i] == "[key]":
					#print("nique tes grands morts maya!")
					#print(type_selection[0])
					final_filename.append(keyword)
					#final_filename.append(type_selection[0])

				if splited_nomenclature[i] == "[artist]":
					artist_name = mc.textField(self.export_artist_name_textfield, query=True, text=True)
					if self.letter_verification_function(artist_name) != True:
						mc.error("Impossible to get the artist name!")
						return
					else:
						final_filename.append(artist_name)

				if splited_nomenclature[i] == "[name]":
					if mc.checkBox(self.export_edit_name_checkbox, query=True, value=True)==True:
						#go through the actual filename and try to get the keyword to get the nomenclature
						#print(list(self.settings.keys()))
						actual_keyword = None
						actual_name = None

						if len(splited_filename)==0:
							mc.error("Impossible to get the name in the current filename!")
							return
						for word in splited_filename:
							for setting_name, setting_content in self.settings.items():
								if word == setting_content[1]:
									actual_keyword = setting_content[1]
									if ("[name]" in setting_content[0].split("_")) == False:
										mc.error("Impossible to get the name from the actual filename!")
										return
									else:
										actual_name = splited_filename[setting_content[0].split("_").index("[name]")]
						if( actual_keyword == None) or (actual_name == None):
							mc.error("Impossible to get the actual name of the file to create the filename!")
							return
						else:
							print(actual_name)
							final_filename.append(actual_name)
					else:
						#try to get the content of the textfield
						content = mc.textField(self.export_edit_name_textfield, query=True, text=True)
						if (self.letter_verification_function(content)==True):
							print(content)
							final_filename.append(content)
						else:
							mc.error("Impossible to get the name in textfield!")
							return

				if splited_nomenclature[i] == "[version]":
					#if mc.checkBox(self.export_edit_version_checkbox, query=True, value=True) == False:
						#try to get the version in textfield
					content = mc.intField(self.export_edit_version_intfield, query=True, value=True)
					if len(list(str(content))) == 1:
						content = "v00%s"%content 
					else:
						content = "v0%s"%content 

					final_filename.append(content)

				if splited_nomenclature[i] == "[sqversion]":
					content = str(mc.intField(self.export_edit_sequence_intfield, query=True, value=True))
					if len(list(content))==1:
						value = "sq00%s"%content 
					else:
						value = "sq0%s"%content
					final_filename.append(value)

				if splited_nomenclature[i] == "[shversion]":
					content = str(mc.intField(self.export_edit_shot_intfield, query=True, value=True))
					if len(list(content))==1:
						value = "sh00%s"%content 
					else:
						value = "sh0%s"%content
					final_filename.append(value)

				if splited_nomenclature[i] == "[project]":
					if self.project_path == None:
						mc.error("Impossible to get project name because project isn't defined!")
						return
					else:
						final_filename.append(os.path.basename(self.project_path))

				if splited_nomenclature[i] == "[type]":
					final_filename.append(kind_selection[0])
			
			print(final_filename)
			return "_".join(final_filename)+".ma"





	def define_export_path_function(self, filename, statut):
		"""
		--> export in current folder
		--> export in same folder
		--> default folder assist
			DEFINE PATH FROM VARIABLES
		"""

		"""
		list of variables for path
		"""
		type_selection = mc.textScrollList(self.export_type_textscrolllist, query=True, si=True)
		kind_selection = mc.textScrollList(self.export_kind_textscrolllist, query=True, si=True)
		splited_filename = os.path.splitext(os.path.basename(mc.file(query=True, sn=True)))[0].split("_")

		if type_selection == None:
			mc.error("You have to select a type!")
			return

		nomenclature = self.settings[type_selection[0]]
		if (("[type]") in nomenclature) and (kind_selection == None):
			mc.error("You have to select a kind for that nomenclature!")
			return

		if mc.checkBox(self.export_current_folder_checkbox, query=True, value=True)==True:
			#get the path of the current file
			path = os.path.dirname(mc.file(query=True, sn=True))
			if (self.letter_verification_function(path)==True) and (path != None):
				return path
			else:
				mc.error("Impossible to get current filepath!")
				return
		if mc.checkBox(self.export_custom_folder_checkbox, query=True, value=True)==True:
			folder = mc.fileDialog2(fm=3)
			if folder == None:
				mc.error("You have to define one folder!")
				return
			else:
				return folder
				#folder = mc.workspace(query=True, active=True)
		if mc.checkBox(self.export_assist_folder_checkbox, query=True, value=True)==True:
			final_filepath = []
			#check the value of the default folder
			default_folder_path = self.settings[type_selection[0]][2]
			if default_folder_path == None:
				mc.error("Impossible to detect a default folder in settings!")
				return
			splited_default_folder = default_folder_path.split("/")

			for i in range(0, len(splited_default_folder)):
				#KEYWORD CONDITIONS


				if (splited_default_folder[i][0] == "[") and (splited_default_folder[i][-1] == "]"):
					if splited_default_folder[i] == "[Origin]":
						final_filepath.append(self.project_path)



					if splited_default_folder[i] =="[key]":
						final_filepath.append(type_selection[0])

					if splited_default_folder[i] == "[name]":
						if mc.checkBox(self.export_edit_name_checkbox, query=True, value=True)==True:
							#go through the actual filename and try to get the keyword to get the nomenclature
							#print(list(self.settings.keys()))
							actual_keyword = None
							actual_name = None
							for word in splited_filename:
								for setting_name, setting_content in self.settings.items():
									if word == setting_content[1]:
										actual_keyword = setting_content[1]
										if ("[name]" in setting_content[0].split("_")) == False:
											mc.error("Impossible to get the name from the actual filename to create the path!")
											return
										else:
											actual_name = splited_filename[setting_content[0].split("_").index("[name]")]
							if( actual_keyword == None) or (actual_name == None):
								mc.error("Impossible to get the actual name of the file!")
								return
							else:
								final_filepath.append(actual_name)
						else:
							#try to get the content of the textfield
							content = mc.textField(self.export_edit_name_textfield, query=True, text=True)
							if (self.letter_verification_function(content)==True):
								final_filepath.append(content)
							else:
								mc.error("Impossible to get the name in textfield!")
								return


					if splited_default_folder[i] == "[mayaProjectName]":
						final_filepath.append(self.additionnal_settings["mayaProjectName"])
					

					if splited_default_folder[i] == "[type]":
						final_filepath.append(kind_selection[0])


					if splited_default_folder[i] == "[editPublishFolder]":
						if statut=="publish":
							final_filepath.append(self.additionnal_settings["editPublishFolder"][1])
						else:
							final_filepath.append(self.additionnal_settings["editPublishFolder"][0])


					if splited_default_folder[i] == "[sqversion]":
						sequence = str(mc.intField(self.export_edit_sequence_intfield, query=True, value=True))
						if len(list(sequence)) == 1:
							sequence = "sq00%s"%sequence 
						else:
							sequence = "sq0%s"%sequence 
						final_filepath.append(sequence)
					if splited_default_folder[i] == "[shversion]":
						sequence = str(mc.intField(self.export_edit_shot_intfield, query=True, value=True))
						if len(list(sequence)) == 1:
							sequence = "sh00%s"%sequence 
						else:
							sequence = "sh0%s"%sequence 
						final_filepath.append(sequence)

						
				

				#PROPER VALUES
				else:
					final_filepath.append(splited_default_folder[i])

			return "/".join(final_filepath)



		


				



	def export_edit_function(self, info, event):
		filename = self.define_export_nomenclature_function("edit")
		filepath = self.define_export_path_function(filename, "edit")
		final_path = os.path.join(filepath, filename)
		print("Returned filename : [%s]"%filename)
		print("Returned filepath : [%s]"%filepath)
		
		#save the current scene with current filename
		
		
		

		
		if info == "standard":
			#save the new scene with the new name
			#try to create all folder and save the file
			
			try:
				mc.file(save=True, type="mayaAscii")
			except:
				mc.warning("Impossible to save the current file before creating edit!")
			try:
				os.makedirs(filepath, exist_ok=True)
				mc.file(rename=final_path)
				mc.file(save=True, type="mayaAscii")

				mc.warning("File saved successfully!")
				print(final_path)
				return
			except:
				mc.error("Impossible to save the file!")
				return
		else:
			#get maya selection
			selection = mc.ls(sl=True)
			if (len(selection))==0:
				mc.error("No item selected to export!")
				return
			try:
				os.makedirs(filepath, exist_ok=True)
				mc.file(final_path,force=True, shader=True, pr=True, es=True, type="mayaAscii")
				mc.warning("Selection exported successfully!")
				print(final_path)
				return
			except:
				mc.error("Impossible to export selection!")
				return
			

	def create_path_function(self, event):
		os.makedirs(path, exist_ok=True)

	def export_publish_function(self, event):
		#go through the current filename and try to find keyword to then define version position
		splited_filename = os.path.basename(os.path.splitext(mc.file(query=True, sn=True))[0]).split("_")
		
		for i in range(0, len(splited_filename)):
			for key, value in self.settings.items():
				if value[1] == splited_filename[i]:
					splited_nomenclature = value[0].split("_")

					if "[version]" in splited_nomenclature:
						index = splited_nomenclature.index("[version]")
						splited_filename[index] = self.additionnal_settings["editPublishFolder"][1]
					elif "[name]" in splited_nomenclature:
						index = splited_nomenclature.index("[name]")
						splited_filename[index] = splited_filename[index]+"Publish"
					else:
						mc.error("Impossible to create the publish keyword in the nomenclature!")
						return

		filename = "_".join(splited_filename) + ".ma"
		filepath = self.define_export_path_function(filename, "publish")
		final_path = os.path.join(filepath, filename)
		print("Returned filename : [%s]"%filename)
		print("Returned filepath : [%s]"%filepath)
		print(final_path)


		"""
		for each folder that does not exist, 
		create it if it's possible
		"""
		os.makedirs(filepath, exist_ok=True)
		#save the file inside the new path
		mc.file(save=True, type="mayaAscii")
		mc.file(rename=final_path)
		mc.file(save=True, type="mayaAscii")


	def save_note_function(self, event):
		#check the selection in file list
		selection = mc.textScrollList(self.result_list, query=True, si=True)
		if selection == None:
			return
		else:
			#save a note for each file selected!
			pipeline_path = mc.textField(self.project_label, query=True, text=True)
			if (pipeline_path==None) or (pipeline_path == "None"):
				mc.error("Impossible to save note!")
				return
			else:
				#take the content of the scrollfield
				note_content = mc.scrollField(self.note_textfield, query=True, text=True)
				try:
					with open(os.path.join(pipeline_path, "PipelineManagerData/NoteData.dll"), "rb") as read_file:
						content = pickle.load(read_file)
				except:
					mc.warning("Note file corrupted or doesn't exists!")
					content = {}

				for file in selection:
					content[file] = note_content

				try:
					with open(os.path.join(pipeline_path, "PipelineManagerData/NoteData.dll"), "wb") as save_file:
						pickle.dump(content, save_file)
				except:
					mc.error("Impossible to save note file!")
					return
				else:
					mc.warning("Note saved successfully!")
					return


	def search_for_note_function(self):
		#try to open the note data
		project_path = mc.textField(self.project_label, query=True, text=True)

		try:
			with open(os.path.join(project_path, "PipelineManagerData/NoteData.dll"), "rb") as read_file:
				note_content = pickle.load(read_file)
		except:
			mc.warning("Impossible to read note file!")
			return
		else:
			selection = mc.textScrollList(self.result_list, query=True, si=True)
			if (selection == None):
				return
			selection = selection[0]
			"""
			print(note_content)
			print(selection in note_content)
			"""
			if selection in note_content:
				note = note_content[selection]
				#replace the note in textfield
				mc.scrollField(self.note_textfield, edit=True, clear=True)
				mc.scrollField(self.note_textfield, edit=True, text=note)

			else:
				print("No note found!")



	def create_template_function(self, event):
		#get the name
		template_name = mc.textField(self.template_textfield, query=True, text=True)
		if (self.letter_verification_function(template_name) != True):
			mc.error("You have to define a name for the new template!")
			return

		#get a folder
		root_folder = mc.fileDialog2(fm=3, ds=1)	
		if root_folder == None:
			mc.error("You have to define a folder architecture to copy!")
			return

		#copy folders inside
		folder_list = []
		past_origin = os.getcwd()
		root_folder = root_folder[0]
		


		root_folder_name = os.path.basename(root_folder)
		for root, dirs, files in os.walk(root_folder):
			for dir_name in dirs:
				
				path =(os.path.join(root, dir_name))
				index = path.index(root_folder_name)

				folder_list.append(path[index:].replace(root_folder_name, ""))
		
		#try to get the dictionnary from the template file in the pipeline
		project_name = mc.textField(self.project_label, query=True, text=True)
		if (project_name == None) or (project_name == "NOne"):
			mc.error("Impossible to get project name!")
			return
		try:
			with open(os.path.join(project_name, "PipelineManagerData/Template.dll"), "rb") as read_file:
				template_dictionnary = pickle.load(read_file)
			#add the new template in the dictionnary
			template_dictionnary[template_name] = folder_list
		except:
			#create the new dictionnary instead
			template_dictionnary = {
				template_name : folder_list
			}
		#save the new dictionnary
		try:
			with open(os.path.join(project_name, "PipelineManagerData/Template.dll"), "wb") as save_file:
				pickle.dump(template_dictionnary, save_file)
			print("New template saved!")
			self.reload_template_function()
			return
		except:
			mc.error("Impossible to save the new template!")
			return



	def reload_template_function(self):

		try:
			project_name = mc.textField(self.project_label, query=True, text=True)
			if (project_name == None) or (project_name == "NOne"):
				mc.error("Impossible to get project name!")
				return
		except:
			project_name = self.project_path
		try:
			with open(os.path.join(project_name, "PipelineManagerData/Template.dll"), "rb") as read_file:
				template_dictionnary = pickle.load(read_file)
			mc.textScrollList(self.template_textscrolllist, edit=True, removeAll=True, append=list(template_dictionnary.keys()))
		except:
			mc.error("Impossible to read template file!")
			return



	def create_new_item_template_function(self, event):
		#get informations to create new item architecture
		item_name = mc.textField(self.template_textfield, query=True, text=True)
		template_name = mc.textScrollList(self.template_textscrolllist, query=True, si=True)
		template_type = mc.textScrollList(self.type_list, query=True, si=True)

		if self.letter_verification_function(item_name) != True:
			mc.error("You have to define a name for the new item to create!")
			return
		if template_name == None:
			mc.error("You have to pick a template!")
			return
		template_name = template_name[0]
		if template_type == None:
			mc.error("You have to pick a type!")
			return


		#print(self.settings_dictionnary[template_type[0]])
		if (self.settings[template_type[0]][2] == None) or ("[key]" in self.settings[template_type[0]][2])==False:
			mc.error("You have to define a default folder, with a [key] inside!")
			return
		starting_folder = self.settings[template_type[0]][2]
		while os.path.basename(starting_folder) != "[key]":
			starting_folder = os.path.dirname(starting_folder)

		
		if ("[Origin]" in starting_folder):
			starting_folder = starting_folder.replace("[Origin]",self.project_path)
			
		if ("[key]" in starting_folder):
			starting_folder = starting_folder.replace("[key]",template_type[0])
		if ("[name]" in starting_folder):
			starting_folder = starting_folder.replace("[name]", item_name)

		if ("[mayaProjectName]" in starting_folder):
			starting_folder = starting_folder.replace("[mayaProjectName]", self.additionnal_settings["mayaProjectName"])

		if ("[type]" in starting_folder) or ("[editPublishFolder]" in starting_folder):
			mc.error("Impossible to craete new item with that default folder architecture!")
			return


		print(starting_folder)

		

		#get the template folder list
		try:
			with open(os.path.join(self.project_path, "PipelineManagerData/Template.dll"), "rb") as read_file:
				template_dictionnary = pickle.load(read_file)
		except:
			mc.error("Impossible to read template data!")
			return

		#print(template_name)
		#print(template_dictionnary)

		if (template_name in template_dictionnary) == False:
			mc.error("Impossible to get template informations!")
			return
		else:
			template_folder_list = template_dictionnary[template_name]

			folder_to_create = []
			for folder in template_folder_list:
				folder_full_path = starting_folder+folder
				folder_to_create.append(folder_full_path.replace('\\', '/'))

			#create the folder list
			for folder in folder_to_create:
				try:
					os.mkdir(folder)
					print("Folder created [%s]"%folder)
				except:
					mc.warning("Failed to create folder [%s]"%folder)
					continue




		

		
