#coding: utf-8
#PIPELINE MANAGER

#Copyright 2023, Robin Delaporte AKA Quazar, All rights reserved.



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




from Pipo.Modules.PipoM import PipelineApplication 
from Pipo.Modules.PipoShaderM import PipelineShaderApplication



"""
	DEFAULT FOLDER + TEMPLATE SYSTEM
	define new edit files destination path


	DEFAULT FOLDER? + TEMPLATE PATH FOR TYPE

	ex:
	D:/WORK/TEST/CHARACTER/ + /[name]/maya/scenes/[state edit var]/mod/ (path for mod scenes)
							+ /[name]/maya/scenes/[state edit var]/rig/



	TEMPLATE FORMAT 
	[FIRST FOLDER NAME] --> REPLACED BY --> [NAME DEFINED BY USER EACH TIME]
		dir1
			dir2
			dir3
			...
		dir4
			...
		...
"""






class PipelineGuiApplication(PipelineApplication, PipelineShaderApplication):
#class PipelineGuiApplication():

	def __init__(self):
		#define the program folder
		self.program_folder = None
		for path in sys.path:
			if os.path.isdir(os.path.join(path, "Pipo"))==True:
				os.chdir(os.path.join(path, "Pipo"))
				self.program_folder = os.path.join(path, "Pipo")
				mc.warning("Program folder defined")
		if self.program_folder == None:
			mc.warning("The program folder wasn't defined!")
			return

		#check if the module list file exist
		#self.project_path = mc.workspace(query=True, rd=True)
		self.project_path = None
		self.window_width = 750
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
			mc.warning("No informations loaded!")


		#launch the function that check
		#if the shader settings file exists
		#if it doesn't create it

		#self.shader_init_function()

		self.settings = {}
		self.settings_dictionnary = {}
		self.additionnal_settings = {}


		self.settings, self.settings_dictionnary, self.additionnal_settings = self.load_settings_function()
	
		
		
	   
	   
		#except:
		#	mc.warning("Impossible to load settings file!")
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
		self.main_window = mc.window(sizeable=False, title="Pipo - Written by Quazar", width=self.window_width, height=self.window_height)
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

		
		self.project_columns = mc.rowColumnLayout(numberOfColumns=4, parent=self.asset_main_scroll, columnWidth=((1, self.window_width/2)))
		self.project_label = mc.textField(editable=False, backgroundColor=[0.2, 0.2, 0.2], parent=self.project_columns, text=self.project_path)
		mc.button(label="Set Project Folder", parent=self.project_columns, command=partial(self.define_project_path_ui_function, "project"))
		mc.button(label="Set Other Folder", parent=self.project_columns, command=partial(self.define_project_path_ui_function, "folder"))
		self.loading_status = mc.text(label="")
		mc.separator(style="singleDash", height=25, parent=self.asset_main_scroll)


		self.assets_search_frame = mc.frameLayout(label="Search for assets", parent=self.asset_main_scroll, collapsable=True, collapse=False, width=self.window_width)


		self.assets_main_rowcolumn = mc.rowColumnLayout(parent=self.assets_search_frame, numberOfColumns=2, columnWidth=((1, self.window_width/5)))
		self.assets_main_leftcolumn = mc.columnLayout(adjustableColumn=True, parent=self.assets_main_rowcolumn)
		self.assets_main_rightcolumn = mc.columnLayout(adjustableColumn=True, parent=self.assets_main_rowcolumn)





		mc.rowColumnLayout(self.assets_main_rowcolumn, edit=True, adjustableColumn=2)
		if self.project_path !="None":
			for key, value in self.settings.items():
				self.type_list_value.append(key)

		self.note_column = mc.columnLayout(adjustableColumn=True, parent=self.assets_main_rightcolumn)
		self.note_textfield = mc.scrollField(parent=self.note_column, height=80, wordWrap=True, font="plainLabelFont", enterCommand=self.save_note_function)
		self.assets_prod_column = mc.rowColumnLayout(numberOfColumns=4, parent=self.assets_main_rightcolumn, columnWidth=((1, self.window_width/6), (2, self.window_width/6), (3, self.window_width/6)))
		self.type_list=mc.textScrollList(allowMultiSelection=True, height=470,parent=self.assets_prod_column, selectCommand=self.display_new_list_function, append=self.type_list_value)
		self.name_list=mc.textScrollList(allowMultiSelection=True, height=470, parent=self.assets_prod_column, selectCommand=self.display_new_list_function)
		self.kind_list=mc.textScrollList(allowMultiSelection=True, height=470, parent=self.assets_prod_column, selectCommand=self.display_new_list_function, append=self.file_type)
		self.result_list=mc.textScrollList(allowMultiSelection=True, height=470, parent=self.assets_prod_column, doubleClickCommand=partial(self.open_location_function, "folder", "event"), selectCommand=self.search_for_thumbnail_function)

		
		mc.rowColumnLayout(self.assets_prod_column, edit=True, adjustableColumn=4)


		#SEARCHBAR
		self.searchbar_checkbox = mc.checkBox(label="Limit research to project", value=False, parent=self.assets_main_leftcolumn, changeCommand=self.save_additionnal_settings_function)
		self.scenes_checkbox = mc.checkBox(label="Search for 3D Scenes", value=True, parent=self.assets_main_leftcolumn, changeCommand=self.save_additionnal_settings_function)
		self.items_checkbox = mc.checkBox(label="Search for 3D Items", value=False, parent=self.assets_main_leftcolumn, changeCommand=self.save_additionnal_settings_function)
		self.textures_checkbox = mc.checkBox(label="Search for Textures", value=False, parent=self.assets_main_leftcolumn, changeCommand=self.save_additionnal_settings_function)
		self.folder_checkbox = mc.checkBox(label="Use default folder", value=False, parent=self.assets_main_leftcolumn, changeCommand=self.save_additionnal_settings_function)
		self.main_assets_searchbar = mc.textField(parent=self.assets_main_leftcolumn, changeCommand=self.searchbar_function, enterCommand=self.searchbar_function)
		mc.text(label="3D Scene extension", parent=self.assets_main_leftcolumn)
		self.assets_scene_extension_textfield = mc.textField(parent=self.assets_main_leftcolumn, enterCommand=self.save_additionnal_settings_function)
		mc.text(label="3D Exported Items extension", parent=self.assets_main_leftcolumn)
		self.assets_items_extension_textfield = mc.textField(parent=self.assets_main_leftcolumn, enterCommand=self.save_additionnal_settings_function)
		mc.text(label="Textures extension", parent=self.assets_main_leftcolumn)
		self.assets_textures_extension_textfield = mc.textField(parent=self.assets_main_leftcolumn, enterCommand=self.save_additionnal_settings_function)

		#IMAGE BOX
		mc.separator(style="none", height=10)
		self.image_box = mc.image(parent=self.assets_main_leftcolumn, visible=True, backgroundColor=[0.2,0.2,0.2], height=self.window_width/5, width=self.window_width/5)
		mc.button(label="Save Thumbnail", parent=self.assets_main_leftcolumn, command=self.take_picture_function)
		mc.separator(style="none", height=10, parent=self.assets_main_leftcolumn)
		mc.button(label="Save Scene", parent=self.assets_main_leftcolumn, command=self.save_current_scene_function)
		mc.button(label="Set Project", parent=self.assets_main_leftcolumn, command=self.set_project_function)
		mc.button(label="Open scene", parent=self.assets_main_leftcolumn, command=partial(self.open_location_function, "open"))

		#CREATE NEW TEMPLATE
		#SAVE NEW TEMPLATE
		mc.separator(style="none", height=10, parent=self.assets_main_leftcolumn)
		self.template_frame = mc.frameLayout(backgroundColor=(0.492,0.047,0.103),label="Edit Template", parent=self.assets_main_leftcolumn, collapsable=True, collapse=True)
		mc.text(parent=self.template_frame, label="New template name")
		self.template_textfield = mc.textField(parent=self.template_frame)
		mc.button(label="Save new template", parent=self.template_frame, command=self.create_template_function)
		mc.separator(style="none", height=10, parent=self.template_frame)
		self.template_textscrolllist = mc.textScrollList(numberOfRows=5, parent=self.template_frame)
		mc.button(label="Create new item", parent=self.template_frame, command=self.create_new_item_template_function)

		self.reload_template_function()

		#RENAME
		self.assets_rename_frame = mc.frameLayout(backgroundColor=(0.492,0.047,0.103),label = "Rename files", parent=self.assets_main_leftcolumn, collapsable=True, collapse=True)
		mc.text("Content to replace",parent=self.assets_rename_frame)
		self.rename_replace_content = mc.textField(parent=self.assets_rename_frame)
		mc.text("Content to put instead",parent=self.assets_rename_frame)
		self.rename_replaceby_content = mc.textField(parent=self.assets_rename_frame)
		mc.button(label="Rename Files", parent=self.assets_rename_frame, command=self.replace_filename_function)


		

		#IMPORT
		self.assets_import_frame = mc.frameLayout(backgroundColor=(0.492,0.047,0.103),label = "Import files", parent=self.assets_main_leftcolumn, collapsable=True, collapse=True)
		mc.button(label="Import in scene", parent=self.assets_import_frame, command=partial(self.import_in_scene_function, False))
		mc.button(label="Import as reference", parent=self.assets_import_frame, command=partial(self.import_in_scene_function, True))

		#ARCHIVE
		self.assets_archive_frame = mc.frameLayout(backgroundColor=(0.492,0.047,0.103),label="Archive files", parent=self.assets_main_leftcolumn, collapsable=True, collapse=True)
		mc.button(label="Archive in current pipeline", parent=self.assets_archive_frame)
		mc.button(label="Archive in current project", parent=self.assets_archive_frame)


		if (self.project_path != None) and (self.additionnal_settings!= None):
			"""
			mc.checkBox(self.searchbar_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][0])
			mc.checkBox(self.scenes_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][1])
			mc.checkBox(self.items_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][2])
			mc.checkBox(self.textures_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][3])
			mc.checkBox(self.folder_checkbox, edit=True, value=self.additionnal_settings["checkboxValues"][4])"""
			mc.textField(self.assets_scene_extension_textfield, edit=True, text=";".join(self.additionnal_settings["3dSceneExtension"]))
			mc.textField(self.assets_items_extension_textfield, edit=True, text=";".join(self.additionnal_settings["3dItemExtension"]))
			mc.textField(self.assets_textures_extension_textfield, edit=True, text=";".join(self.additionnal_settings["texturesExtension"]))
			"""
				except:
					mc.warning("Impossible to launch GUI Presets on Mai page!")
			"""









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
		self.export_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width*(1/3)), (2, self.window_width*(2/3))), parent=self.export_scroll)

		self.export_leftcolumn = mc.columnLayout(adjustableColumn=True, parent=self.export_rowcolumn)
		self.export_rightcolumn = mc.columnLayout(adjustableColumn=True, parent=self.export_rowcolumn)

		mc.separator(style="none", height=20, parent=self.export_leftcolumn)
		self.export_current_folder_checkbox = mc.checkBox(label="Export in current folder", value=False, parent=self.export_leftcolumn)
		self.export_custom_folder_checkbox = mc.checkBox(label="Export in custom folder", value=False, parent=self.export_leftcolumn)
		self.export_assist_folder_checkbox = mc.checkBox(label="Default folder location assist", value=True, parent=self.export_leftcolumn)
		mc.separator(style="none", height=10, parent=self.export_leftcolumn)

		mc.text(label="Current artist name", parent=self.export_leftcolumn, align="left")
		self.export_artist_name_textfield = mc.textField(parent=self.export_leftcolumn)

		mc.separator(style="none", height=20, parent=self.export_leftcolumn)

		self.export_edit_frame = mc.frameLayout(label="Export edit files", parent=self.export_leftcolumn, collapsable=True, collapse=False)
		mc.text(label="File Name", align="left", parent=self.export_edit_frame)
		self.export_edit_name_checkbox = mc.checkBox(label="Keep same name", value=True, parent=self.export_edit_frame)
		self.export_edit_name_textfield = mc.textField(parent=self.export_edit_frame)

		mc.separator(style="singleDash", height=2, parent=self.export_edit_frame)
		
		mc.text(label="File Version", align="left", parent=self.export_edit_frame)
		#self.export_edit_version_checkbox = mc.checkBox(label="Automatic version check", value=False, parent=self.export_edit_frame)
		self.export_edit_version_intfield = mc.intField(parent=self.export_edit_frame)

		mc.text(label="Sequence number", align="left", parent=self.export_edit_frame)
		self.export_edit_sequence_intfield = mc.intField(parent=self.export_edit_frame)

		mc.text(label="Shot number", align="left", parent=self.export_edit_frame)
		self.export_edit_shot_intfield = mc.intField(parent=self.export_edit_frame)
		
		
		mc.button(label="Export", parent=self.export_edit_frame, command=partial(self.export_edit_function, "standard"))
		mc.button(label="Export selected", parent=self.export_edit_frame, command=partial(self.export_edit_function, "selection"),backgroundColor=(0.492,0.047,0.103))


		self.export_publish_frame = mc.frameLayout(label="Export publish files", parent=self.export_leftcolumn, collapsable=True, collapse=True)
		mc.button(label="Export Publish", parent=self.export_publish_frame, command=self.export_publish_function)
		mc.button(label="Publish selected", parent=self.export_publish_frame,backgroundColor=(0.492,0.047,0.103))



		#textscrolllist of export window
		self.export_right_rowcolumn = mc.rowColumnLayout(numberOfColumns=2, columnWidth=((1, self.window_width*(2/6)), (2, self.window_width*(2/6))), parent=self.export_rightcolumn)
		
		
		self.export_type_textscrolllist = mc.textScrollList(numberOfRows=25, parent=self.export_right_rowcolumn, allowMultiSelection=False, selectCommand=self.update_export_kind_information)
		self.export_kind_textscrolllist = mc.textScrollList(numberOfRows=25, parent=self.export_right_rowcolumn, allowMultiSelection=False)
		if self.settings != None:
			mc.textScrollList(self.export_type_textscrolllist, edit=True, removeAll=True, append=list(self.settings.keys()))


		








	
		self.log_column = mc.columnLayout(adjustableColumn=True, parent=self.tabs, height=self.window_height)
		self.log_scroll = mc.scrollLayout(horizontalScrollBarThickness=16, parent=self.log_column, height=self.window_height, resizeCommand=self.resize_command_function)

		self.log_program_frame = mc.frameLayout(label="Program Log", labelAlign="top", width=self.window_width, collapsable=True, collapse=True,parent=self.log_scroll)
		self.log_list = mc.textScrollList(parent=self.log_program_frame, allowMultiSelection=False, enable=True, height=self.window_height/2, append=self.log_list_content)

		self.log_team_frame = mc.frameLayout(label="Team logs", width=self.window_width, collapsable=True, collapse=True, parent=self.log_scroll)
		self.lost_team_list = mc.textScrollList(parent=self.log_team_frame, allowMultiSelection=False, enable=True, height=self.window_height/2)


		mc.tabLayout(self.tabs, edit=True, tabLabel=((self.prod_column, "PROD ASSETS"), (self.archive_column, "ARCHIVE"), (self.export_column, "EXPORT"), (self.log_column, "LOGS")))






		#globally change window text color
		#create and launch the message thread
		"""
		if self.launch_message_thread != True:
			self.message_thread = threading.Thread(target=self.main_message_thread_function)
			self.message_thread.start()"""

		mc.showWindow()





	







	def update_export_kind_information(self):
		selection = mc.textScrollList(self.export_type_textscrolllist, query=True, si=True)[0]

		#get list of kind in settings
		mc.textScrollList(self.export_kind_textscrolllist, edit=True, removeAll=True, append=self.settings_dictionnary[selection])


	def display_settings_informations_function(self):
		#get the textscrolllist selection
		selection = mc.textScrollList(self.settings_type_list, query=True, si=True)
		if selection != None:
			for key, value in self.settings_dictionnary.items():
				if key == selection[0]:
					try:
						mc.textScrollList(self.settings_type_textscrolllist, edit=True, removeAll=True, append=value)
					except:
						mc.warning("Impossible to display list!")
						pass

			for key, value in self.settings.items():
				#print(key, selection[0])
				if key == selection[0]:
					mc.textField(self.setting_syntax_textfield, edit=True, text=self.settings[key][0])
					mc.textField(self.setting_keyword_textfield, edit=True, text=self.settings[key][1])


					if (value[2] != None):
						mc.button(self.setting_default_folder_button, edit=True, label=value[2])
					else:
						mc.button(self.setting_default_folder_button, edit=True, label="Default Folder")
					"""
					if self.settings[key][2] != None:
						mc.button(self.setting_folder_button, edit=True, label=self.settings[key][2])
					else:
						mc.button(self.setting_folder_button, edit=True, label="None")
					"""



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


	

		

	def export_name_checkbox_function(self, event):
		checkbox_value = mc.checkBox(self.export_name_checkbox, query=True, value=True)
		
		if checkbox_value == True:
			mc.textField(self.export_name_textfield, edit=True, enable=False)
		else:
			mc.textField(self.export_name_textfield, edit=True, enable=True)

	

		

PipelineGuiApplication()