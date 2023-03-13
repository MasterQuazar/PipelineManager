#coding: utf-8
#PIPELINE MANAGER



#archive documentation : https://realpython.com/python-zipfile/
#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
import threading
import maya.cmds as mc
import pymel.core as pm
import os  
import ctypes
import sys
import pickle

from time import sleep
from functools import partial
from datetime import datetime






def onMayaDroppedPythonFile(*args):
	#create the path for all the functions
	path = '/'.join(__file__.replace("", "/").split("/")[:-1])
	sys.path.append(path)
"""
if (os.getcwd() in sys.path)==False:
	sys.path.append(os.getcwd())
"""




from PipelineManager.Modules.PipelineM import PipelineApplication 
from PipelineManager.Modules.PipelineShaderM import PipelineShaderApplication



"""
check if project list exists
	add project to list
		when the program launch check if program exists
	if project doesn't exist don't load them

"""






class PipelineGuiApplication(PipelineApplication, PipelineShaderApplication):
#class PipelineGuiApplication():

	def __init__(self):
		#define the program folder
		self.program_folder = None
		for path in sys.path:
			if os.path.isdir(os.path.join(path, "PipelineManager"))==True:
				os.chdir(os.path.join(path, "PipelineManager"))
				self.program_folder = os.path.join(path, "PipelineManager")
				mc.warning("Program folder defined")
		if self.program_folder == None:
			mc.warning("The program folder wasn't defined!")
			return

		#check if the module list file exist
		self.project_path = mc.workspace(query=True, rd=True)

		self.window_width = 650
		self.window_height=700

		letter = 'abcdefghijklmnopqrstuvwxyz'
		figure = '0123456789'

		self.list_letter = list(letter)
		self.list_capital = list(letter.upper())
		self.list_figure = list(figure)
		
		self.folder_path = os.getcwd()

		self.item_type_list = [
			".ma",
			".mb",
			".obj",
			".tex",
			".exr",
			".tif",
			".png",
			".vdb"]

		self.log_list_content = []
		self.settings = {}

		self.texture_to_connect_list = []
		#load settings stored in files
		#if the file doesn't exist
		#create a new file with default settings
		#check the current project of maya



		if os.path.isfile("Data/PipelineData.dll")==True:
			try:
				with open("Data/PipelineData.dll", "rb") as read_file:
					self.project_path = pickle.load(read_file)
				if type(self.project_path)==list:
					self.project_path = self.project_path[0]
				if os.path.isdir(self.project_path)==False:
					mc.warning("The saved project folder doesn't exist with the same path on that computer!")
					self.project_path = "None"
				else:
					mc.warning("Project Path loaded!")

			except:
				mc.error("Impossible to read the pipeline data file!")
				self.project_path = "None"
		else:
			self.project_path = "None"



		self.publish_step_list = [
			"Delete unused nodes",
			"Hide all joints", 
			"Unkey all controllers attributes (t, r, s)",
			"Importing all references in current scene",
			"Reset all controllers position",
			"Delete all namespaces in the current scene",
			]

		#launch the function that check
		#if the shader settings file exists
		#if it doesn't create it

		#self.shader_init_function()


		
		try:
			self.settings, self.settings_dictionnary = self.load_settings_function()
		except:
			mc.warning("Impossible to load settings file!")
		#self.add_log_content_function("Settings loaded")
	

		#IMPORTANTS VARIABLES
		self.receive_notification = True
		self.message_thread_status = True
		self.window_name = None

		self.pack_function_list = {}


		self.file_type = ["mod", "rig", "groom", "cloth", "lookdev", "layout", "camera", "anim", "render", "compositing"]
		self.variable_list = ["[key]", "[project]", "[type]", "[state]", "[version]", "[sqversion]", "[shversion]"]
		self.default_folder_list = []
		self.new_step_list = []
		self.new_type_list = []
		self.name_list_value = []
		self.type_list_value = []
		self.file_list_value = []
		self.result_list_value = []
		self.previous_log_team = []
		self.launch_message_thread = False

		self.build_pipeline_interface_function()








	
	def resize_command_function(self):
		#get the window width
		width = mc.window(self.main_window, query=True, width=True)
		height= mc.window(self.main_window, query=True, height=True)

		
		
			
	
		







	def build_pipeline_interface_function(self):
		self.main_window = mc.window(sizeable=False, title="PipelineManager - By Quazar", width=self.window_width, height=self.window_height)
		self.scrollbar = mc.scrollLayout(width=self.window_width + 40, parent=self.main_window, resizeCommand=self.resize_command_function)
		self.main_column = mc.columnLayout(adjustableColumn=True, parent=self.scrollbar)
		self.add_log_content_function("Interface built")
		#self.main_window = mc.window(title="PipelineManager", sizeable=True, height=self.window_height, width=self.window_width)
		self.pack_function_list["Pipeline"] = ["PipelineManagerTool"]


		#self.main_column = mc.columnLayout(adjustableColumn=True)
		self.PipelineManagerTool = mc.frameLayout(visible=True, parent=self.main_column, label="PipelineManagerTool", labelAlign="top", width=self.window_width, collapsable=True, collapse=True, backgroundColor=(0.592,0.047,0.203))

		self.form_pipeline = mc.formLayout(parent=self.PipelineManagerTool)
		self.tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5, parent=self.form_pipeline)
		mc.formLayout(self.form_pipeline, edit=True, attachForm=((self.tabs,"top",0), (self.tabs, "bottom",0),(self.tabs,"left",0),(self.tabs,"right",0)))

		"""
		ASSETS
		character, props, sets, fx
		mod, rig, groom, cloth, lookdev, alembic
		
		SHOTS
		sequence, shots
		layout, camera, matte painting, anim, render

		POSTPROD
		sequence, shots
		renders, compositing
		"""
		#main scroll layout of the asset page
		self.prod_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		self.asset_main_scroll = mc.scrollLayout(horizontalScrollBarThickness=1, width=self.window_width+16, parent=self.prod_column, resizeCommand=self.resize_command_function, height=self.window_height)
		


		#DEFINE PROJECT FOLDER
		mc.separator(style="none", height=15, parent=self.asset_main_scroll)

		
		self.project_columns = mc.rowColumnLayout(numberOfColumns=3, parent=self.asset_main_scroll, columnWidth=((1, self.window_width/2)))
		self.project_label = mc.textField(editable=False, backgroundColor=[0.2, 0.2, 0.2], parent=self.project_columns, text=self.project_path)
		mc.button(label="Set Project Folder", parent=self.project_columns, command=partial(self.define_project_path_ui_function, "project"))
		mc.button(label="Set Other Folder", parent=self.project_columns, command=partial(self.define_project_path_ui_function, "folder"))
		mc.separator(style="singleDash", height=25, parent=self.asset_main_scroll)


		self.assets_search_frame = mc.frameLayout(label="Search for assets", parent=self.asset_main_scroll, collapsable=True, collapse=False, width=self.window_width)
		self.assets_search_frame_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width/2), (2, self.window_width/2)), parent=self.assets_search_frame)

		
		self.main_assets_searchbar = mc.textField(parent=self.assets_search_frame_rowcolumn, changeCommand=self.searchbar_function)
		self.searchbar_checkbox = mc.checkBox(align="right",label="Limit research to current project", value=False, parent=self.assets_search_frame_rowcolumn)
		self.image_box = mc.image(parent=self.assets_search_frame_rowcolumn, visible=True, backgroundColor=[0.2,0.2,0.2], height=self.window_width/4)
		
		


		#self.prod_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.assets_search_frame,height=self.window_height/2)	
		self.prod_columns = mc.rowColumnLayout(numberOfColumns=5 , columnWidth=((1, self.window_width/5), (2, self.window_width/5),(3, self.window_width/5)),parent=self.assets_search_frame)

		mc.text(label="Kind", parent=self.prod_columns, align="left")
		mc.text(label="Name", parent=self.prod_columns, align="left")
		mc.text(label="File Type", parent=self.prod_columns, align="left")
		mc.text(label="Files Found", parent=self.prod_columns, align="left")
		mc.text(label="", parent=self.prod_columns)


		#create textscrolllist lists
		if self.project_path !="None":
			for key, value in self.settings.items():
				self.type_list_value.append(key)
			"""
			for key, value in self.settings_dictionnary.items():
		
				self.type_list_value.append(key)"""

		self.type_list = mc.textScrollList(allowMultiSelection=True, parent=self.prod_columns, height=self.window_height/2, selectCommand=self.display_new_list_function, append=self.type_list_value)
		self.name_list = mc.textScrollList(allowMultiSelection=True, parent=self.prod_columns, height=self.window_height/2, selectCommand=self.display_new_list_function)
		self.kind_list = mc.textScrollList(allowMultiSelection=True, parent=self.prod_columns, height=self.window_height/2, selectCommand=self.display_new_list_function, append=self.file_type)
		self.result_list = mc.textScrollList(allowMultiSelection=True, parent=self.prod_columns, height=self.window_height/2, doubleClickCommand=self.open_location_function, selectCommand=self.search_for_thumbnail_function)
		#self.result_scrollbar = mc.scrollLayout(parent=self.result_list, sah=False, horizontalScrollBarThickness=16)


		self.rename_rowcolumn = mc.rowColumnLayout(parent=self.assets_search_frame, numberOfColumns=3, columnWidth=((1, self.window_width/3), (2, self.window_width/3), (3, self.window_width/3)))
		mc.text(label="Content to replace", parent=self.rename_rowcolumn)
		mc.text(label="Content to put instead", parent=self.rename_rowcolumn)
		mc.text(label="", parent=self.rename_rowcolumn)
		self.rename_replace_content = mc.textField(parent=self.rename_rowcolumn)
		self.rename_replaceby_content = mc.textField(parent=self.rename_rowcolumn)
		mc.button(label="Rename", parent=self.rename_rowcolumn, command=self.replace_filename_function)
		#IMPORT FILES
		mc.separator(parent=self.assets_search_frame, style="none", height=10)
		self.import_rowcolumn = mc.rowColumnLayout(parent=self.assets_search_frame, numberOfColumns=2, columnAlign=((1, "left"), (2, "right")), columnWidth=((1, self.window_width/2), (2, self.window_width/2)))
		mc.button(label="Save Scene", parent=self.import_rowcolumn, command=self.save_current_scene_function)
		mc.button(label="Save thumbnail", parent=self.import_rowcolumn, command=self.take_picture_function)
		mc.button(label="Set Project", parent=self.import_rowcolumn, command=self.set_project_function)
		mc.button(label="Open File", parent=self.import_rowcolumn, command=self.open_file_function)
		mc.button(label="Import in scene", parent=self.import_rowcolumn, command=partial(self.import_in_scene_function, False))
		mc.button(label="Import as reference", parent=self.import_rowcolumn, command=partial(self.import_in_scene_function, True))	
		mc.button(label="Archive in project", parent=self.import_rowcolumn, command=self.archive_in_project_function)









		"""
		INSTEAD OF DELETING FILES
		OR IF SOME FILES ARE TOO HEAVY TO BE TRANSPORTED
		"""
		self.archive_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		self.archive_rowcolumn = mc.rowColumnLayout(numberOfColumns=3, columnWidth=((1, self.window_width/2), (2, self.window_width/2)))
		mc.button(label="Clear Project Archive", parent=self.archive_rowcolumn)
		mc.button(label="Delete Project Archive", parent=self.archive_rowcolumn)



	








		self.export_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		self.export_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.export_column, height=self.window_height, resizeCommand=self.resize_command_function)
		self.export_edit_frame = mc.frameLayout(label="Save new edit file", width=self.window_width, parent=self.export_scroll, collapse=True, collapsable=True)
		"""
		save a new scene
		
		to export edit and publish files
		IF STATE KEYWORD ISNT IN NOMENCLATURE SETTINGS ADD published to the [name] keyword
			if state keyword isn't in nomenclature but version yes, replace version by publish!!!
			
		- type name
			to check the syntax of the edit / publish file!
		- project name
		- keyword
		- name
		- type of scenes
		- state 

			clean tool
				import refs
				delete all namespaces
				export this file as a new file (publish file)

				IF RIGGING
					delete unused nodes
					check position of all controllers
					sks hidden?
					(check gesse documentation)

				delete volume aggregates from renderman if there is volume aggregates

		"""
		self.export_edit_rowcolumn1 = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width/2), (2, self.window_width/2)), parent=self.export_edit_frame)
		self.export_edit_column1 = mc.columnLayout(adjustableColumn=True, parent=self.export_edit_rowcolumn1)
		self.export_edit_column2 = mc.columnLayout(adjustableColumn=True, parent=self.export_edit_rowcolumn1)

		mc.text(label="Name of the file", parent=self.export_edit_column1)
		self.export_edit_name_textfield = mc.textField(parent=self.export_edit_column1)

		#mc.text(label="File Kind", parent=self.export_edit_column1)

		self.export_edit_kind_textscrolllist = mc.textScrollList(parent=self.export_edit_column1, numberOfRows=20, allowMultiSelection=False,selectCommand=self.export_edit_display_version_field_function)
		

		self.export_edit_type_textscrolllist = mc.textScrollList(numberOfRows=22.5, parent=self.export_edit_column2, allowMultiSelection=False)	
		
		self.export_edit_defaultfolder_checkbox = mc.checkBox(label="Use default folder settings", parent=self.export_edit_column1)
		mc.separator(style="singleDash", height=35, parent=self.export_edit_column1)
		mc.text(label="File Version", parent=self.export_edit_column1)
		self.export_edit_fileversion = mc.intField(parent=self.export_edit_column1)
		mc.text(label="Sequence Version", parent=self.export_edit_column1)
		self.export_edit_sqversion = mc.intField(parent=self.export_edit_column1)
		mc.text(label="Shot Version", parent=self.export_edit_column1)
		self.export_edit_shotversion = mc.intField(parent=self.export_edit_column1)

		mc.button(label="Export Edit File", parent=self.export_edit_column1, command=self.export_edit_file_function)





		self.export_publish_frame = mc.frameLayout(label="Save publish file", width=self.window_width, parent=self.export_scroll, collapse=False, collapsable=True)
		self.export_publish_rowcolumn1 = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width/2), (2, self.window_width/2)), parent=self.export_publish_frame)
		self.export_publish_column1 = mc.columnLayout(adjustableColumn=True, parent=self.export_publish_rowcolumn1)
		self.export_publish_column2 = mc.columnLayout(adjustableColumn=True, parent=self.export_publish_rowcolumn1)

		self.export_publish_textscrolllist = mc.textScrollList(parent=self.export_publish_column2, numberOfRows=20, allowMultiSelection=True, append=self.publish_step_list)

		self.export_publish_checkbox = mc.checkBox(label="Use current file name", parent=self.export_publish_column1, value=True, changeCommand=self.enable_publish_file_name_function)
		mc.separator(style="none", height=15, parent=self.export_publish_column1)
		mc.text(label="Publish file name", parent=self.export_publish_column1, align="left")
		self.export_publish_textfield = mc.textField(parent=self.export_publish_column1, enable=False)

		self.export_publish_samelocation_checkbox = mc.checkBox(parent=self.export_publish_column1, label="Export in same folder", value=True, changeCommand=self.export_publish_samelocation_function)
		self.export_publish_searchlocation_checkbox = mc.checkBox(parent=self.export_publish_column1, label="Search for export folder", value=False, changeCommand=self.export_publish_searchlocation_function)

		mc.separator(style="none", height=50, parent=self.export_publish_column1)
		mc.button(label="Export publish file", parent=self.export_publish_column1, command=self.export_publish_function)

		self.refresh_export_type_list_function()
		self.export_edit_display_version_field_function()








		self.settings_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs)
		#create two list (left and right)
		#LEFT --> NAME OF THE SETTING
		#RIGHT --> VALUE OF THE SYNTAX
		self.settings_main_scroll = mc.scrollLayout(horizontalScrollBarThickness=8, parent=self.settings_column, resizeCommand=self.resize_command_function, width=self.window_width,height=self.window_height)

		self.settings_file_frame = mc.frameLayout(label="Files settings", parent=self.settings_main_scroll, width=self.window_width, collapsable=True, collapse=False)
		self.settings_file_scroll = mc.scrollLayout(horizontalScrollBarThickness=8, parent=self.settings_file_frame, height=self.window_height)
		self.setting_rowcolumn1 = mc.rowColumnLayout(numberOfColumns=4, parent=self.settings_file_scroll, columnWidth=((1, self.window_width/6), (2, self.window_width/6), (3, self.window_width/6), (4, self.window_width/2)))
		mc.text(label="Type name", parent=self.setting_rowcolumn1)
		mc.text(label="Type syntax", parent=self.setting_rowcolumn1)
		mc.text(label="Type keyword", parent=self.setting_rowcolumn1)
		mc.text(label="Type default folder", parent=self.setting_rowcolumn1)

		#create the setting key list
		setting_key_list = []
		setting_value_list = []
		setting_default_folder_list = []
		setting_keyword_list = []


		for setting_key, setting_value in self.settings.items():
			setting_key_list.append(setting_key)
			setting_value_list.append(setting_value[0])
			setting_keyword_list.append(setting_value[1])

			if setting_value[2] == None:
				setting_default_folder_list.append("None")
			else:
				setting_default_folder_list.append(setting_value[2])

		self.setting_type_list = mc.textScrollList(allowMultiSelection=False, parent=self.setting_rowcolumn1, append=setting_key_list, selectCommand=self.add_type_list_function)
		self.setting_syntax_list = mc.textScrollList(allowMultiSelection=False, parent=self.setting_rowcolumn1, append=setting_value_list, selectCommand=self.add_content_in_textfield_function)
		self.setting_keyword_list = mc.textScrollList(allowMultiSelection=False, parent=self.setting_rowcolumn1, append=setting_keyword_list)
		self.settings_folder_list = mc.textScrollList(allowMultiSelection=False, parent=self.setting_rowcolumn1, append=setting_default_folder_list, selectCommand=self.define_default_folder_function)

		mc.separator(style="none", height=30, parent=self.settings_file_scroll)
		self.settings_project_folder_column = mc.columnLayout(adjustableColumn=True, parent=self.settings_file_scroll, width=self.window_width/2)
		mc.text(label="Common maya project name", parent=self.settings_project_folder_column)
		self.settings_project_folder_textfield = mc.textField(parent=self.settings_project_folder_column)
		mc.button(label="Save Common maya project name", parent=self.settings_project_folder_column, command=self.save_project_name_function)


		mc.separator(style="none", height=20, parent=self.settings_file_scroll)
		self.settings_folder_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width/2), (2, self.window_width/2)), parent=self.settings_file_scroll)
		mc.text(label="Edit folder name", parent=self.settings_folder_rowcolumn)
		mc.text(label="Publish folder name", parent=self.settings_folder_rowcolumn)
		self.settings_editfolder_textfield = mc.textField(parent=self.settings_folder_rowcolumn)
		self.settings_publishfolder_textfield = mc.textField(parent=self.settings_folder_rowcolumn)
		self.settings_folder_column = mc.columnLayout(parent=self.settings_folder_rowcolumn, adjustableColumn=True)
		mc.button(label="Save folder preset", parent=self.settings_file_scroll, width=self.window_width, command=self.save_folder_preset_function)
		mc.separator(style="none", height=40, parent=self.settings_file_scroll)

		for key, value in self.settings.items():
			mc.textField(self.settings_project_folder_textfield, edit=True, text=value[4])
			if type(value[3]) == list:
				if value[3][0] != None:
					mc.textField(self.settings_editfolder_textfield, edit=True, text=str(value[3][0]))
					
				if value[3][1] != None:
					mc.textField(self.settings_publishfolder_textfield, edit=True, text=str(value[3][1]))
					
				break




		self.setting_rowcolumn2 = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width/2), (2, self.window_width/2)), parent=self.settings_file_scroll)
		
		






		#define current type list
		self.settings_type_textscrolllist = mc.textScrollList(allowMultiSelection=True, numberOfRows=6, parent=self.setting_rowcolumn2, selectCommand=self.select_type_function)
		self.settings_type_columnlayout = mc.columnLayout(adjustableColumn=True, parent=self.setting_rowcolumn2)
		#create type
		#delete type
		#ren type
		#reset
		mc.text(label="File kind Name", parent=self.settings_type_columnlayout)
		self.settings_type_textfield = mc.textField(self.settings_type_columnlayout)
		mc.button(label="Create File Kind", parent=self.settings_type_columnlayout, command=self.create_file_kind_function)
		mc.button(label="Delete File Kind", parent=self.settings_type_columnlayout, command=self.delete_file_kind_function)
		mc.button(label="Rename File Kind", parent=self.settings_type_columnlayout, command=self.rename_file_kind_function)
	
		mc.text(label="New type name", parent=self.setting_rowcolumn2)
		mc.text(label="New type keyword", parent=self.setting_rowcolumn2)
		self.settings_create_type_textfield = mc.textField(parent=self.setting_rowcolumn2)
		self.settings_create_keyword_textfield = mc.textField(parent=self.setting_rowcolumn2)



		self.setting_rowcolumn2button = mc.rowColumnLayout(numberOfColumns=3, parent=self.settings_file_scroll, columnWidth=((1, self.window_width/3), (2, self.window_width/3), (3, self.window_width/3)))
		
		mc.button(label="Save\nkeyword", parent=self.setting_rowcolumn2button, command=self.save_keyword_function)
		mc.button(label="Create\nnew type", parent=self.setting_rowcolumn2button, command=self.create_type_function)
		mc.button(label="Delete type", parent=self.setting_rowcolumn2button, command=self.delete_type_function)


		self.setting_rowcolumn3 = mc.rowColumnLayout(numberOfColumns=3, parent=self.settings_file_scroll, width=self.window_width, columnWidth=((1, self.window_width/2-10), (2, self.window_width/4-10), (3, self.window_width/4-10)))
		mc.text(label="New setting syntax", parent=self.setting_rowcolumn3)
		mc.text(label="", parent=self.setting_rowcolumn3)
		mc.text(label="", parent=self.setting_rowcolumn3)

		self.setting_syntax_textfield = mc.textField(parent=self.setting_rowcolumn3)
		mc.button(label="Save syntax", parent=self.setting_rowcolumn3, command=self.save_new_syntax_function)
		mc.button(label="Reset default", parent=self.setting_rowcolumn3, command=self.reset_default_syntax_function)














		self.log_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs, height=self.window_height)
		self.log_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.log_column, height=self.window_height, resizeCommand=self.resize_command_function)

		self.log_program_frame = mc.frameLayout(label="Program Log", labelAlign="top", width=self.window_width, collapsable=True, collapse=True,parent=self.log_scroll)
		self.log_list = mc.textScrollList(parent=self.log_program_frame, allowMultiSelection=False, enable=True, height=self.window_height/2, append=self.log_list_content)

		self.log_team_frame = mc.frameLayout(label="Team logs", width=self.window_width, collapsable=True, collapse=True, parent=self.log_scroll)
		self.lost_team_list = mc.textScrollList(parent=self.log_team_frame, allowMultiSelection=False, enable=True, height=self.window_height/2)


		mc.tabLayout(self.tabs, edit=True, tabLabel=((self.prod_column, "PROD ASSETS"), (self.archive_column, "ARCHIVE"), (self.export_column, "EXPORT"), (self.settings_column, "SETTINGS"), (self.log_column, "LOGS")))






		
		#create and launch the message thread
		"""
		if self.launch_message_thread != True:
			self.message_thread = threading.Thread(target=self.main_message_thread_function)
			self.message_thread.start()"""

		mc.showWindow()



	def export_publish_samelocation_function(self, event):
		search_folder = mc.checkBox(self.export_publish_searchlocation_checkbox, query=True, value=True)
		if search_folder == True:
			mc.checkBox(self.export_publish_searchlocation_checkbox, edit=True, value=False)
	def export_publish_searchlocation_function(self, event):
		same_folder = mc.checkBox(self.export_publish_samelocation_checkbox, query=True, value=True)
		if same_folder == True:
			mc.checkBox(self.export_publish_samelocation_checkbox, edit=True, value=False)

		

	


	def enable_publish_file_name_function(self, event):
		if mc.checkBox(self.export_publish_checkbox, query=True, value=True)==True:
			mc.textField(self.export_publish_textfield, edit=True, enable=False)
		else:
			mc.textField(self.export_publish_textfield, edit=True, enable=True)





	def refresh_export_type_list_function(self):
		#take the content
		type_list = []
		try:
			for kind, content in self.settings_dictionnary.items():
				type_list.append(kind)
		except:
			pass
		mc.textScrollList(self.export_edit_kind_textscrolllist, edit=True, removeAll=True, append=type_list)






	def export_edit_display_version_field_function(self):
		#query the value of the current item selected in the option menu
		try:
			selection = mc.textScrollList(self.export_edit_kind_textscrolllist, query=True, si=True)[0]
		except:
			return
		#check in dictionnary settings if the current selection contain [version], [shotversion] or [seqversion]
		for kind, content in self.settings.items():
			syntax = content[0].split("_")

			if kind == selection:
				if ("[version]" in syntax)==False:
					mc.intField(self.export_edit_fileversion, edit=True, enable=False)
				else:
					mc.intField(self.export_edit_fileversion, edit=True, enable=True)

				if ("[shversion]" in syntax)==False:
					mc.intField(self.export_edit_shotversion, edit=True, enable=False)
				else:
					mc.intField(self.export_edit_shotversion, edit=True, enable=True)

				if ("[sqversion]" in syntax)==False:
					mc.intField(self.export_edit_sqversion, edit=True, enable=False)
				else:
					mc.intField(self.export_edit_sqversion, edit=True, enable=True)

				#print(type_list)
				type_list = self.settings_dictionnary[kind]
				mc.textScrollList(self.export_edit_type_textscrolllist, edit=True, removeAll=True, append=type_list)

				return

				"""
				for element in type_list:
					mc.menuItem(self.export_edit_type_menu, label=element)"""





	def select_type_function(self):
		#take the first item of the selection
		selection = mc.textScrollList(self.settings_type_textscrolllist, query=True, si=True)[0]
		mc.textField(self.settings_type_textfield, edit=True, text=selection)

		

	def add_type_list_function(self):
		#get the first item of the selection
		try:
			selection = mc.textScrollList(self.setting_type_list, query=True, si=True)[0]	
		except:
			mc.error("You have to select something!")
			return
		else:
			mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True, append=self.settings_dictionnary[selection])



	def add_content_in_textfield_function(self):
		selection = mc.textScrollList(self.setting_syntax_list, query=True, si=True)[0]
		mc.textField(self.setting_syntax_textfield, edit=True, text=selection)


	def delete_settings_interface_item_function(self):
		for key in self.settings:
			#DELETE GRAPHIC INTERFACE
			self.button_name = "%s_button"%key
			
			try:
				mc.deleteUI(globals()[self.button_name], control=True)
			except:
				pass

	
	def create_settings_interface_item_function(self):
		name_list = []
		syntax_list = []
		keyword_list = []
		folder_list = []

		print("\nUPDATE\n")

		for key, value in self.settings.items():
			print(key, value)
			

			name_list.append(key)
			syntax_list.append(value[0])
			keyword_list.append(value[1])

			if value[2] == None:
				folder_list.append("None")
			else:
				folder_list.append(value[2])

		mc.textScrollList(self.setting_type_list, edit=True, removeAll=True, append=name_list)
		mc.textScrollList(self.setting_syntax_list, edit=True, removeAll=True, append=syntax_list)
		mc.textScrollList(self.setting_keyword_list, edit=True, removeAll=True, append=keyword_list)
		mc.textScrollList(self.settings_folder_list, edit=True, removeAll=True, append=folder_list)
		mc.textScrollList(self.type_list, edit=True, removeAll=True, append=name_list)

	

		

	def export_name_checkbox_function(self, event):
		checkbox_value = mc.checkBox(self.export_name_checkbox, query=True, value=True)
		
		if checkbox_value == True:
			mc.textField(self.export_name_textfield, edit=True, enable=False)
		else:
			mc.textField(self.export_name_textfield, edit=True, enable=True)

	

		

PipelineGuiApplication()