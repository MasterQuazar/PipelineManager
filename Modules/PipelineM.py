#coding: utf-8
import maya.cmds as mc
import pymel.core as pm
import os
import ctypes
import sys
import pickle
import json 

from tqdm import tqdm
from datetime import datetime
from functools import partial
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path




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




"""
import PyToolBar_03.Modules.PipelineManagerM
import PyToolBar_03.Modules.PipelineShaderM
import PyToolBar_03.Modules.PipelineM
import imp

imp.reload(PyToolBar_03.Modules.PipelineManagerM)
imp.reload(PyToolBar_03.Modules.PipelineShaderM)
imp.reload(PyToolBar_03.Modules.PipelineM)
"""



class PipelineApplication:




	def load_settings_function(self):
		if (self.project_path == None) or (self.project_path == "None"):
			mc.warning("Impossible to load settings!")
			return
		else:
			
			if type(self.project_path)==list:
				self.project_path = self.project_path[0]
			try:
				
				with open(os.path.join(self.project_path, "PipelineManagerData/PipelineSettings.dll"), "rb") as read_file:
					self.settings = pickle.load(read_file)
					self.settings_dictionnary = pickle.load(read_file)
					self.additionnal_settings = pickle.load(read_file)
				
				print(self.additionnal_settings)
				print("Settings loaded successfully!")
			
			except:
				self.settings, self.settings_dictionnary, self.additionnal_settings = self.create_pipeline_settings_function()
				print("Settings file created in your project!")
				
		return self.settings, self.settings_dictionnary, self.additionnal_settings



	def define_default_folder_function(self):
		#define folder
		key_list = list(self.settings.keys())
		selected_key = key_list[int(mc.textScrollList(self.settings_folder_list, query=True, sii=True)[0])-1]
		

		folder = mc.fileDialog2(fm=3)[0]
		if folder == None:
			folder = "None"
		list_content = self.settings[selected_key]
		list_content[2] = folder

		self.settings[selected_key] = list_content

		folder_list = []

		for key, value in self.settings.items():
			if value[2] == None:
				folder_list.append("None")
			else:
				folder_list.append(value[2])

		mc.textScrollList(self.settings_folder_list, edit=True, removeAll=True, append=folder_list)
		#save the new settings folder
		self.save_settings_file()




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
		mc.textScrollList(self.settings_type_list, edit=True, removeAll=True, append=setting_key_list)
		mc.textScrollList(self.setting_syntax_list, edit=True, removeAll=True, append=setting_value_list)
		mc.textScrollList(self.setting_keyword_list, edit=True, removeAll=True, append=setting_keyword_list)
		mc.textScrollList(self.settings_folder_list, edit=True, removeAll=True, append=setting_default_folder_list)

		





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
				with open(os.path.join(path, "PipelineManagerData/PipelineSettings.dll"), "wb") as save_file:
					pickle.dump(self.settings, save_file)
					pickle.dump(self.settings_dictionnary, save_file)
					pickle.dump(self.additionnal_settings, save_file)
			except AttributeError:
			
				self.create_pipeline_settings_function()
			self.add_log_content_function("Settings file saved successfully")




	def create_pipeline_settings_function(self):
		print("created")
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
			"checkboxValues":[False, True, False, False],
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


		#add content to next list
		"""
		if step_selection != None:
			past_step_list = self.new_step_list
			self.new_step_list = []

			for element in step_selection:
				for key, value in self.settings_dictionnary.items():
					if element == key:
						
						for value_key, value_value in value.items():
							if (value_key in self.new_step_list)==False:
								self.new_step_list.append(value_key)

			if (past_step_list != self.new_step_list):
				mc.textScrollList(self.type_list, edit=True, removeAll=True, append=self.new_step_list)
				mc.textScrollList(self.kind_list, edit=True, removeAll=True)"""


		"""
		if type_selection != None:
			past_type_list = self.new_type_list
			self.new_type_list = []

			for element in type_selection:
				for key, value in self.settings_dictionnary.items():
					#create categorie list	
					for value_key, value_value in value.items():
						if value_key == element:
							if type(value_value) != list:
								value_value = [value_value]
							for item in value_value:
								if (item in self.new_type_list)==False:
									self.new_type_list.append(item)"""


			

		self.search_files_function(type_selection, kind_selection, name_selection)






	def search_files_function(self, type_selection, kind_selection, name_selection):
		"""
		check the selection in all lists
		check the content
		"""
		#do a recurcive selection
		#go from the step_list to take files recurcively column after column


		files_in_folder = []


		past_name_list = self.name_list_value
		self.result_list_value = []
		self.name_list_value = []


		#check content of the current checkbox
		limit_search_checkbox = mc.checkBox(self.searchbar_checkbox, query=True, value=True)

		
		if limit_search_checkbox == True:
			folder_name = (mc.textField(self.project_label, query=True, text=True))
		else:
			folder_name = (mc.workspace(query=True, active=True))
			if (folder_name == None) or (folder_name == "None"):
				mc.error("Impossible because you haven't set a project!")
				return


		
		project_name = os.path.basename(os.path.normpath(mc.textField(self.project_label, query=True, text=True)))

		for r, d, f in os.walk(folder_name):
			if ("PipelineManagerData" in d)==True:
				d.remove("PipelineManagerData")
			
			for file in f:
				files_in_folder.append(os.path.join(r, file))
		
		
		#splited_file = os.path.splitext(os.path.basename(file))[0].split("_")
		
		

		if type_selection != None:
			for ts in type_selection:
				for file in files_in_folder:
					error=False
					name = None
					#get the setting and the syntax linked to it
					syntax = self.settings[ts][0]
					keyword = self.settings[ts][1]

					#check the syntax for each files
					#CHECK FIRST THE TYPE OF THE FILE (INCLUDING THE OVERHALL SYNTAX!!!")
					splited_syntax = syntax.split("_")
					splited_file = os.path.splitext(os.path.basename(file))[0].split("_")


					if self.letter_verification_function(syntax) == False:
						mc.warning("Impossible to search for files because no syntax to search!")
						error = True



					elif len(splited_syntax) != len(splited_file):
						error = True


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
							

					if error==False:
					
						if (name != None) and (name in self.name_list_value)==False:
							self.name_list_value.append(name)


						if name_selection != None:
							if (name != None) and (name in name_selection)==True:
								self.result_list_value.append(file)
						if name_selection == None:
							if (file in self.result_list_value)==False:
								self.result_list_value.append(file)
						


		for i in range(0, len(self.result_list_value)):
			self.result_list_value[i] = (os.path.basename(self.result_list_value[i]))

		mc.textScrollList(self.result_list, edit=True, removeAll=True, append=self.result_list_value)
		
		if past_name_list != self.name_list_value:	
			mc.textScrollList(self.name_list, edit=True, removeAll=True, append=self.name_list_value)



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




	def open_location_function(self):
		#check selection in result textscrolllist
		selection = mc.textScrollList(self.result_list, query=True, si=True)[0]
		#check the location of the file in the pipeline
		pipeline_path = mc.textField(self.project_label, query=True, text=True)
		#go through all the files
		for r, d, f in os.walk(pipeline_path):
			for file in f:
				if os.path.basename(file) == selection:
					#open a browser with the location of that file
					mc.fileDialog2(ds=1, fm=0, dir=r)




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
		for key, value in self.settings.items():
			project_name = value[4]
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

		#get each extension list
		scenes_extension_list = mc.textField(self.assets_scene_extension_textfield, query=True, text=True).split(";")
		items_extension_list = mc.textField(self.assets_items_extension_textfield, query=True, text=True).split(";")
		textures_extension_list = mc.textField(self.assets_textures_extension_textfield, query=True, text=True).split(";")

		self.additionnal_settings["checkboxValues"] = [searchbar_limit, scenes, items, textures]
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





					


		

		
