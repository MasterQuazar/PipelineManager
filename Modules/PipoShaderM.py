#coding: utf-8

#Copyright 2023, Robin Delaporte AKA Quazar, All rights reserved.



import maya.cmds as mc
import pymel.core as pm
import os
import sys
import pickle
import json

from datetime import datetime
from functools import partial
from pathlib import Path










class PipelineShaderApplication:
	"""
	program that looks for texture and connect them to shading nodes

	from any texture:
		create an texture input node (from settings list)
		create an inbetween node
		define a final shading node (during the connexion)
			from the settings you define the input to look for on this node!
			BUT you connect the new texture to this node from the hypershade selection

	IN THE SETTINGS PAGE YOU HAVE TO DEFINE
	for each texture channel (list can be changed!)
		texture input node / texture input node output
		in between node (ex: pxrbump)
		final node output

	for the displace create a pxrdisplace and connect it to the shading engine node
	"""


	"""	
	list of channel
		for each channel define a nomenclature
	"""





	def shader_init_function(self):
		self.texture_folder_path = "None"
		self.texture_extension_list = [".jpg", ".png", ".tiff", ".tif", ".exr"]
		self.texture_connexion_list = {}



		self.add_log_content_function("Shading application launched succesfully")
		#creation of the shader variable depending of the shader engine selected

		"""
		self.current_renderer = mc.getAttr("defaultRenderGlobals.currentRenderer")
		"""

		self.shader_settings_dictionnary = {}
		if type(self.project_path)==list:
			self.project_path = self.project_path[0]	

		if self.project_path != "None":
			if os.path.isfile(os.path.join(self.project_path, "PipelineManagerData/PipelineManagerShadingSettings.dll"))==False:
				self.create_shading_settings_function()
			else:
				#try to get the file
				try:
					with open(os.path.join(self.project_path, "PipelineManagerData/PipelineManagerShadingSettings.dll"),"rb") as read_file:
						self.shader_settings_dictionnary = pickle.load(read_file)
						self.shader_node_list = pickle.load(read_file)
						self.personnal_info = pickle.load(read_file)
					self.add_log_content_function("Shading setting file loaded succesfully")
				except:
		
					self.create_shading_settings_function()

		else:
			mc.warning("Impossible to get the shading settings file!")

			return



	def save_shading_settings_file_function(self):
		if self.project_path == "None":
			mc.error("Impossible to save the settings file\nYou have to set the pipeline folder first")
		else:
			if type(self.project_path)==list:
				self.project_path = self.project_path[0]
			if os.path.isdir(os.path.join(self.project_path, "PipelineManagerData"))==False:
				os.mkdir(os.path.join(self.project_path, "PipelineManagerData"))

			#get current render engine
			try:
				self.current_engine = mc.optionMenu(self.render_engine_menu, query=True, value=True)
			except:
				self.current_engine = None
			try:
				with open(os.path.join(self.project_path, "PipelineManagerData/PipelineManagerShadingSettings.dll"), "wb") as save_file:
					pickle.dump(self.shader_settings_dictionnary, save_file)
					pickle.dump(self.shader_node_list, save_file)
					pickle.dump(self.personnal_info, save_file)
			except AttributeError:
				self.create_shading_settings_function()
			mc.warning("Shading settings file saved succesfully")
			self.add_log_content_function("Shading settings file saved succesfully")




	def create_shading_settings_function(self):
		"""
		RENDERMAN NODES LISTS
		"""
		self.renderman_input_node_list = {
			"PxrTexture":["filename", "resultRGB"],
			"PxrNormalMap":["filename", "resultN"]
		}
		self.renderman_inbetween_node_list = {
			"PxrBump":["inputBump", "resultN"],
			"PxrRemap":["inputRGB", "resultRGB"],
			"PxrHSL":["inputRGB", "resultRGB"],
			"PxrDisplace":["dispScalar", "outColor"]
		}
		self.renderman_final_node_list = {
			"shadingEngine",
			"PxrSurface",
			"PxrLayer"
		}
		#DICTIONNARY FOR SHADERS THAT CONTAIN
		"""
		channel name
		keyword
		origin node
		in-between node
		final node
		"""
		self.shader_node_list = {
			"renderman": [
				self.renderman_input_node_list,
				self.renderman_inbetween_node_list,
				self.renderman_final_node_list
				]
		}



		self.shader_renderman_settings = {
			"DiffuseColor":[["Diffuse", "Color", "Diff"], ["PxrTexture", "filename", "resultRGB"], None, ["PxrSurface", "diffuseColor"]],
			"SpecularRoughness":[["Roughness", "Rough"], ["PxrTexture", "filename", "resultRGB"], ["PxrRemap", "inputRGB", "resultR"], ["PxrSurface", "specularRoughness"]],
			"SpecularColor":[["SpecularColor"], None, None, ["PxrSurface", "specularFaceColor"]],
			"ClearCoatFaceColor":[["ClearCoat"], None, None, ["PxrSurface", "clearCoatFaceColor"]],
			"Normal":[["Normal", "NormalMap"], ["PxrNormalMap", "nodeState", "resultN"], None, ["PxrSurface", "bumpNormal"]],
			"Bump":[["Bump", "Height"], ["PxrTexture", "message", "resultRGB"], ["PxrBump", "inputBump", "resultN"], ["PxrSurface", "bumpNormal"]],
			"Displace":[["Displace", "Displacement", "Disp"],[ "PxrTexture", "frozen", "resultRGB"], ["PxrDisplace", "dispScalar", "outColor"], ["shadingEngine", "displacementShader"]],
		}
		self.personnal_info = {
			"current_render_engine":"renderman",
			"texture_folder_path":"None"
		}



		
		self.shader_settings_dictionnary = {
			"renderman":self.shader_renderman_settings
		}


		#if there is no project folder defined
		#print an error
		if self.project_path != "None":
			if os.path.isdir(self.project_path)==False:

				mc.warning("The saved project path doesn't exist on that computer!\nIt has been replaced by the current one!")
				self.project_path = mc.workspace(query=True, rd=True)


			try:
				if os.path.isdir(os.path.join(self.project_path, "PipelineManagerData"))==False:
					os.mkdir(os.path.join(self.project_path, "PipelineManagerData"))
			except:
				mc.error("Impossible to create the pipelinemanagerdata in your project folder!")
				return
			with open(os.path.join(self.project_path, "PipelineManagerData/PipelineManagerShadingSettings.dll"), "wb") as save_file:
				pickle.dump(self.shader_settings_dictionnary, save_file)
				pickle.dump(self.shader_node_list, save_file)
				pickle.dump(self.personnal_info, save_file)
			self.add_log_content_function("New shading settings file created succesfully")
		else:
			mc.warning("Impossible to create the shader setting file\nYou have to set the pipeline folder before!")
			return

			


	def load_shading_settings_function(self):
		#get the content of the render engine selection
	

		
		#try to take the value from the menu
		#if its impossible it mean that the menu doesn't contain anything
		#SOOOO we take the value from the file!!
		render_engine_selection = mc.optionMenu(self.render_engine_menu, query=True, value=True)



		if self.project_path != "None":
			if render_engine_selection == None:
				render_engine_selection = self.personnal_info["current_render_engine"]
			#create the dictionnary
			#from the personnal info and the shader settings dictionnary
			render_content = self.shader_settings_dictionnary[self.personnal_info["current_render_engine"]]
			for channel in render_content:
				self.texture_connexion_list[channel] = None
	


		channel_list = []
		origin_node_name_list = []
		middle_node_name_list = []
		final_node_name_list = []


		for render_engine, content in self.shader_settings_dictionnary.items():
			try:
				mc.menuItem(parent=self.render_engine_menu, label=str(render_engine))
			except:
				pass

			if render_engine == render_engine_selection:
				#create the channel list


				for channel, content_value in content.items():
					channel_list.append(channel)

				#create the origin node name list and select the defined one if it exist!
				render_node_list = self.shader_node_list[render_engine]




				origin_node_dictionnary = render_node_list[0]
				for node in origin_node_dictionnary:
					origin_node_name_list.append(node)

				middle_node_dictionnary = render_node_list[1]
				for node in middle_node_dictionnary:
					middle_node_name_list.append(node)

				final_node_dictionnary = render_node_list[2]
				for node in final_node_dictionnary:
					final_node_name_list.append(node)

		try:
			if self.personnal_info["texture_folder_path"] != "None":
				mc.textField(self.texture_path_field, edit=True, text=str(self.personnal_info["texture_folder_path"]))
		except:
			pass

		mc.textScrollList(self.channel_textscrolllist, edit=True, removeAll=True, append=channel_list)
		mc.textScrollList(self.origin_node_name_textscrolllist, edit=True, removeAll=True, append=origin_node_name_list)
		mc.textScrollList(self.middle_node_name_textscrolllist, edit=True, removeAll=True, append=middle_node_name_list)
		mc.textScrollList(self.final_node_name_textscrolllist, edit=True, removeAll=True, append=final_node_name_list)
		mc.textScrollList(self.texture_channel_list, edit=True, removeAll=True, append=channel_list)



	def create_example_node_function(self, node_name):
		print(node_name)
		if mc.objExists("%s_shading_settings_node"%node_name)==True and (mc.nodeType("%s_shading_settings_node"%node_name)==node_name):
			mc.delete("%s_shading_settings_node"%node_name)
		if mc.objExists("%s_shading_settings_node"%node_name)==False:
			mc.shadingNode(node_name, n="%s_shading_settings_node"%node_name, asTexture=True)
		attribute_list = mc.listAttr("%s_shading_settings_node"%node_name, connectable=True, visible=True)
		output_list = mc.listAttr("%s_shading_settings_node"%node_name, output=True, connectable=True, visible=True)

		self.add_log_content_function("Example node created to get attribute list [%s_shading_settings_node]"%node_name)

		print("attribute_list", attribute_list)
		print("output_list", output_list)
		return attribute_list, output_list




	def refresh_shading_settings_list_function(self, command):
		#get the selection in the textscrolllist
		render_engine_selection = mc.optionMenu(self.render_engine_menu, query=True, value=True)

		channel_selection = mc.textScrollList(self.channel_textscrolllist, query=True, si=True)	


		#select in the origin node name list the defined node
		for render_engine, content in self.shader_settings_dictionnary.items():
			if render_engine == render_engine_selection:
				for channel, content_value in content.items():
					if command=="channel":
						if channel_selection != None:
							if type(channel_selection) == list:
								channel_selection = channel_selection[0]
							if channel == channel_selection:

								if content_value[1] != None:
									if content_value[1][0] != None:
										mc.textScrollList(self.origin_node_name_textscrolllist, edit=True, selectItem=content_value[1][0])
								
							
								if content_value[2] != None:
									mc.textScrollList(self.middle_node_name_textscrolllist, edit=True, selectItem=content_value[2][0])


								if content_value[3] != None:
									mc.textScrollList(self.final_node_name_textscrolllist, edit=True, selectItem=content_value[3][0])
							#get the keyword list for the channel
							keyword_list = content[channel_selection][0]
							keyword_str = ";".join(keyword_list)
							mc.textField(self.keyword_list_textfield, edit=True, text=keyword_str)







		#ORIGIN NODE MENU CREATION
		node_name_selection = mc.textScrollList(self.origin_node_name_textscrolllist, query=True, si=True)
		
		if node_name_selection != None:
			node_name_selection = node_name_selection[0]

			#check if the check node exist
			origin_input_list, origin_output_list = self.create_example_node_function(node_name_selection)
			mc.textScrollList(self.origin_node_attribute_textscrolllist, edit=True, removeAll=True, append=origin_input_list)
			mc.textScrollList(self.origin_node_output_textscrolllist, edit=True, removeAll=True, append=origin_output_list)

		


		#MIDDLE MODE MENU CREATION
		middle_node_name_selection = mc.textScrollList(self.middle_node_name_textscrolllist, query=True, si=True)
		if middle_node_name_selection != None:
			
			middle_node_name_selection = middle_node_name_selection[0]

			middle_input_list, middle_output_list = self.create_example_node_function(middle_node_name_selection)
			#fill the content of the two others lists
			mc.textScrollList(self.middle_node_input_textscrolllist, edit=True, removeAll=True, append=middle_input_list)
			mc.textScrollList(self.middle_node_output_textscrolllist, edit=True, removeAll=True, append=middle_output_list)



		#FINAL NODE MENU CREATION

		final_node_name_selection = mc.textScrollList(self.final_node_name_textscrolllist, query=True, si=True)
		if final_node_name_selection != None:
			final_node_name_selection = final_node_name_selection[0]

			final_input_list, final_output_list = self.create_example_node_function(final_node_name_selection)

			mc.textScrollList(self.final_node_input_textscrolllist, edit=True, removeAll=True, append=final_input_list)





	
		#check if there are attributes to select in those lists
		for render_engine, content in self.shader_settings_dictionnary.items():
			if render_engine == render_engine_selection:
				for channel, content_value in content.items():
					if node_name_selection != None:
						if (content_value[1] != None):
							if (channel == channel_selection) and (node_name_selection == content_value[1][0]) and ((content_value[1][1] in origin_input_list)==True):
								mc.textScrollList(self.origin_node_attribute_textscrolllist, edit=True, selectItem=content_value[1][1])

							if (channel == channel_selection) and (node_name_selection == content_value[1][0]) and ((content_value[1][2] in origin_output_list)==True):
								mc.textScrollList(self.origin_node_output_textscrolllist, edit=True, selectItem=content_value[1][2])	

					if middle_node_name_selection != None:
						if content_value[2] != None:
							if (channel == channel_selection) and (middle_node_name_selection == content_value[2][0]) and ((content_value[2][1] in middle_input_list)==True):
								mc.textScrollList(self.middle_node_input_textscrolllist, edit=True, selectItem=content_value[2][1])

							if (channel == channel_selection) and (middle_node_name_selection == content_value[2][0]) and ((content_value[2][2] in middle_output_list)==True):
								mc.textScrollList(self.middle_node_output_textscrolllist, edit=True, selectItem=content_value[2][2])


					if final_node_name_selection != None:
						if (content_value[3] != None):
							
							if (channel == channel_selection) and (final_node_name_selection == content_value[3][0]) and ((content_value[3][1] in final_input_list)==True):
								mc.textScrollList(self.final_node_input_textscrolllist, edit=True, selectItem=content_value[3][1])

									

	def change_shading_dictionnary_function(self, command, event):
		
		#get the render engine
		render_engine_selection = mc.optionMenu(self.render_engine_menu, query=True, value=True)

		#get the selection of the channel and the origin node name
		channel_selection = mc.textScrollList(self.channel_textscrolllist, query=True, si=True)

		name_selection = mc.textScrollList(self.origin_node_name_textscrolllist, query=True, si=True)
		origin_node_attribute = mc.textScrollList(self.origin_node_attribute_textscrolllist, query=True, si=True)
		origin_node_output = mc.textScrollList(self.origin_node_output_textscrolllist, query=True, si=True)

		middle_node_name = mc.textScrollList(self.middle_node_name_textscrolllist, query=True, si=True)
		middle_node_input = mc.textScrollList(self.middle_node_input_textscrolllist, query=True, si=True)
		middle_node_output = mc.textScrollList(self.middle_node_output_textscrolllist, query=True, si=True)

		final_node_name = mc.textScrollList(self.final_node_name_textscrolllist, query=True, si=True)
		final_node_input = mc.textScrollList(self.final_node_input_textscrolllist, query=True, si=True)

		if (channel_selection == None):
			mc.error("You have to chose a channel and a node to save new settings!")
			return
		else:
			for render_engine, render_dictionnary in self.shader_settings_dictionnary.items():
				if render_engine == render_engine_selection:
					if type(channel_selection) == list:
						channel_selection = channel_selection[0]

					channel_content = render_dictionnary[channel_selection]
					"""
					channel content possible values
						None (none type)
						[content, content, content]
					"""

					#call a function to create the new setting list
					#replace the old list by the new one in the shading settings dictionnary
					if command == "origin":
						new_channel_content = self.create_shading_list_function(name_selection, origin_node_attribute, origin_node_output)
						channel_content[1] = new_channel_content


					if command == "middle":
						new_channel_content = self.create_shading_list_function(middle_node_name, middle_node_input, middle_node_output)
						channel_content[2] = new_channel_content


					if command == "final":
						new_channel_content = self.create_shading_list_function(final_node_name, final_node_input, "Final")
						channel_content[3] = new_channel_content


					
					"""
					render_dictionnary[channel_selection] = channel_content

					self.shader_settings_dictionnary[render_engine_selection] = render_dictionnary"""
					break
			#save the shading file
			self.save_shading_settings_file_function()
			self.add_log_content_function("[%s] Connexion settings saved succesfully!"%command)



	def create_shading_list_function(self, list1, list2, list3):
		if (list1 == None) and (list2 == None) and (list3 == None):
			return None 
		elif (list1 == None) or (list2 == None) or (list3 == None):
			mc.error("You have to select 3 items or 0!")
			return
		else:
			if list3 != "Final":
				return [list1[0], list2[0], list3[0]]
			else:
				return [list1[0], list2[0]]
			


	def create_new_channel_function(self, event):
		#get the content of the textfield
		#check if the textfield contain something
		new_channel_name = mc.textField(self.new_channel_textfield, query=True, text=True)
		if (self.letter_verification_function(new_channel_name)==False) or (self.letter_verification_function(new_channel_name)==None):
			mc.error("You have to define a name to create a new channel!")
			return
		else:
			current_render_engine = mc.optionMenu(self.render_engine_menu, query=True, value=True)

			#create a new channel in the dictionnary 
			for render_engine, content in self.shader_settings_dictionnary.items():
				if render_engine == current_render_engine:
					render_dictionnary = content

					render_dictionnary[new_channel_name] = [[new_channel_name], None, None, None]

					#then save the new dictionnary and reload informations
					self.shader_settings_dictionnary[render_engine] = render_dictionnary
					self.save_shading_settings_file_function()
					self.load_shading_settings_function()
					self.add_log_content_function("[%s] New texture channel created succesfully!"%new_channel_name)
					break
			


	def delete_existing_channel_function(self, event):
		#take the selection in the channel list
		try:
			channel_selection = mc.textScrollList(self.channel_textscrolllist, query=True, si=True)[0]
		except:
			mc.error("You have to select a channel to delete in the list!")
			return
		current_render_engine = mc.optionMenu(self.render_engine_menu, query=True, value=True)

		for render_engine, content in self.shader_settings_dictionnary.items():
			if render_engine == current_render_engine:
				render_dictionnary = content 
				render_dictionnary.pop(channel_selection)

				self.shader_settings_dictionnary[render_engine] = render_dictionnary
				
				break
		self.texture_connexion_list.pop(channel_selection)
		self.save_shading_settings_file_function()
		self.load_shading_settings_function()
		self.add_log_content_function("[%s] Channel deleted succesfully!"%channel_selection)




	def define_other_texture_folder_function(self, event):
		try:
			new_folder = mc.fileDialog2(fm=3)[0]
		except:
			mc.error("You have to define a folder!")
			return
		#save the new texture path
		self.personnal_info["texture_folder_path"] = str(new_folder)
		self.save_shading_settings_file_function()
		self.load_shading_settings_function()




	def refresh_textures_list_function(self, command):

		"""
		find all the images!!!
			texture folder path (starting point)
			pipeline folder if it's not defined

		get the channel selection (it can be several elements)
			get all the files containing keyword in the name!!!
				if no keyword --> no files!!!

			print name of the folder containing the textures found!!!
		"""
		if self.personnal_info["texture_folder_path"] == "None":
			if (self.project_path == "None") or (self.project_path == None):
				mc.error("Impossible to search for files!\nYou have to define a pipeline folder or a texture folder!")
				return 
			else:
				starting_point=self.project_path
		else:
			starting_point = self.personnal_info["texture_folder_path"]

		channel_selection = mc.textScrollList(self.texture_channel_list, query=True, si=True)


		#get all files (images) in the folder and create a list
		temporary_file_list = []
		for r, d, f in os.walk(starting_point):
			for file in f:
				if (os.path.splitext(file)[1] in self.texture_extension_list)==True:
					temporary_file_list.append((file, r))


		final_file_list = []
		final_path_folder_list = []
		for channel in channel_selection:
			#get keywords in the dictionnary

			for render_engine, content in self.shader_settings_dictionnary.items():
				if render_engine == self.personnal_info["current_render_engine"]:
					#get the keyword list for the actual channel
					for file_channel, file_channel_content in content.items():
						if file_channel == channel:
							#check if one of those keyword in the list
							#is in the filename
							#if it does add if to the final_file_list[]
							for file in temporary_file_list:
								for keyword in file_channel_content[0]:
									if (keyword in file[0])==True:
										if (file[0] in final_file_list)==False:
											final_file_list.append(os.path.join(file[1], file[0]))
											final_path_folder_list.append(file[1])
		if command == "channel":
			#create a single folder list
			final_folder_list=[]
			for path in final_path_folder_list:
				if (os.path.basename(path) in final_folder_list)==False:
					final_folder_list.append(os.path.basename(path))
			selection = mc.textScrollList(self.texture_name_list, query=True, si=True)
			mc.textScrollList(self.texture_name_list, edit=True, removeAll=True, append=final_folder_list)



		"""
		for name selected
			take the final file list and the final path folder list
			remove all elements that are not in the folder name selection
		"""
		if command == "name":
			name_selection = mc.textScrollList(self.texture_name_list, query=True, si=True)

			final_file_list_selected = []

			for i in range(0, len(final_path_folder_list)):
				if (os.path.basename(final_path_folder_list[i]) in name_selection)==True:
					final_file_list_selected.append(os.path.join(final_path_folder_list[i], final_file_list[i]))
			final_file_list = final_file_list_selected
	
		final_file_list = list(set(final_file_list))

		mc.textScrollList(self.texture_found_list, edit=True, removeAll=True, append=final_file_list)




		#last selection
		#depending of the channel selected
		#if a file is already to connect for this channel select it in the final_file_list textscrolllist
		for channel in channel_selection:
			if (self.texture_connexion_list[channel] != None) and (self.texture_connexion_list[channel] in final_file_list)==True:
				mc.textScrollList(self.texture_found_list, edit=True, selectItem=self.texture_connexion_list[channel])




	def select_texture_function(self):
		#go through the dictionnary to get the keyword in the filename
		#take the channel name corresponding to the filename keywords
		render_content = self.shader_settings_dictionnary[self.personnal_info["current_render_engine"]]
		file_selection = mc.textScrollList(self.texture_found_list, query=True, si=True)
		channel_selection = mc.textScrollList(self.texture_channel_list, query=True, si=True)


		"""
		YOU CAN SELECT ONLY ONE IMAGE PER CHANNEL!
		each time you select a texture
			it replace the texture in the dictionnary (at the corresponding channel!)

		and each time time you deselect all files
		and reselect only files that are in the dictionnary
		"""
		for channel in channel_selection:
	
			missing=True
			if file_selection != None:
				channel_data = self.shader_settings_dictionnary[self.personnal_info["current_render_engine"]][channel]

				for file in file_selection:

					for keyword in channel_data[0]:
						if (keyword in file)==True:
							self.texture_connexion_list[channel] = file
							missing=False
			if missing==True:
				self.texture_connexion_list[channel] = None



		if file_selection != None:
			connexion_files = list(self.texture_connexion_list.values())

			for file in file_selection:
				if (file in connexion_files)==False:
					mc.textScrollList(self.texture_found_list, edit=True, deselectItem=file)




	def create_pipeline_shader_function(self, event):
		"""	
		get the current render engine
		get the list of the selected files to connect to the new shader
		"""
		
		if self.personnal_info["current_render_engine"] == "renderman":
			#create a pxrsurface shader
			self.surface_node = mc.shadingNode("PxrSurface", asShader=True)
			#self.shading_node = mc.shadingNode("shadingEngine", asUtility=True)
			#connect the pxrsurface to the shading engine
			#mc.connectAttr("%s.outColor"%self.surface_node, "%s.rman__surface"%self.shading_node)
		
		#go through the list of selected files and try to connect them according to settings file
		for render_engine, content in self.shader_settings_dictionnary.items():
			if render_engine == self.personnal_info["current_render_engine"]:

				for channel, file_to_connect in self.texture_connexion_list.items():
					"""
					check if the file_to_connect == None
					else get the channel and check what are the nodes to create and to connect
						"""
					if file_to_connect != None:
						if (os.path.isfile(file_to_connect)==False):
							mc.warning("%s doesn't exist - Skipped!" % file_to_connect) 
							continue


						else:
							

							channel_settings = content[channel]
							origin = channel_settings[1]
							middle = channel_settings[2]
							end = channel_settings[3]


							#create origin node
							if origin != None:
								origin_node = mc.shadingNode(origin[0], asTexture=True)

								#check if the middle node exist and if not connect the origin
								#node to the destination node! (surface node)
								if middle == None:
									if end != None:
										if end[0] == mc.nodeType(self.surface_node):
											mc.connectAttr("%s.%s"%(origin_node, origin[2]), "%s.%s"%(self.surface_node, end[1]))
									"""
									if end[0] == mc.nodeType(self.shading_node):
										mc.connectAttr("%s.%s"%(origin_node, origin[2]), "%s.%s"%(self.shading_node, end[1]))
									"""
							if middle != None:
								middle_node = mc.shadingNode(middle[0], asTexture=True)

								if origin != None:
									mc.connectAttr("%s.%s"%(origin_node,origin[2]), "%s.%s"%(middle_node, middle[1]))
								if end != None:
									if end[0] == mc.nodeType(self.surface_node):
										mc.connectAttr("%s.%s"%(middle_node, middle[2]), "%s.%s"%(self.surface_node, end[1]))


							file_to_connect = self.detect_udim_function(file_to_connect)
								

							mc.setAttr("%s.%s"%(origin_node, origin[1]), file_to_connect, type="string")
		self.add_log_content_function("Shader created!")

		


	def save_texture_keyword_function(self, event):
		"""
		get the content of the list
		"""

		textfield_content = mc.textField(self.keyword_list_textfield, query=True, text=True)
		textfield_list = textfield_content.split(";")
		#try to detect if all elements in the list are made of something
		for element in textfield_list:
			if (self.letter_verification_function(element)==False) or (self.letter_verification_function(element)==None):
				mc.error("all keyword needs to contain letter or numbers!")
				return
	
		#get the channel selection
		channel_selection = mc.textScrollList(self.channel_textscrolllist, query=True, si=True)[0]

		shader_dictionnary = self.shader_settings_dictionnary[self.personnal_info["current_render_engine"]]
		shader_dictionnary[channel_selection][0] = textfield_list

		self.shader_settings_dictionnary[self.personnal_info["current_render_engine"]] = shader_dictionnary
		self.save_shading_settings_file_function()
		self.load_shading_settings_function()


		self.add_log_content_function("Keyword list saved")




	def detect_udim_function(self, file_to_connect):
		#try to detect presence of udim in the filename
		splited_path = os.path.splitext(file_to_connect)
		splited_filename = splited_path[0].split(".")
		udim = True 
		try:
			int(splited_filename[-1])
		except:
			udim = False 
		if udim == True:
			splited_filename[-1] = "<udim>"
			filename = ".".join(splited_filename)
			file_to_connect = (filename + splited_path[1])
		return file_to_connect.replace(os.sep, "/")




	def use_existing_shader_function(self, event):

		selection = mc.ls(sl=True, sn=True)

		for channel, file_to_connect in self.texture_connexion_list.items():
			if file_to_connect != None:
				#get the end node
				render_dictionnary = self.shader_settings_dictionnary[self.personnal_info["current_render_engine"]]
				#check if the end node for that channel is in the node selection
				destination = render_dictionnary[channel][3]
				
				detected = False
				for item in selection:
					if destination == None:
						mc.error("Impossible to connect to the shader node! You have to select on in the settings!")
						return 
					else:
						if (mc.nodeType(item) == destination[0]):
							detected=True 

							#create the origin node 
							#and the middle node if it exist
							origin = render_dictionnary[channel][1]
							middle = render_dictionnary[channel][2]

							if origin != None:
								origin_node = mc.shadingNode(origin[0], asTexture=True)

								#create put the filename inside the origin node
								file_to_connect = self.detect_udim_function(file_to_connect)
								mc.setAttr("%s.%s"%(origin_node, origin[1]), file_to_connect, type="string")

								if middle == None:
									#connect the origin node to the selected node
									try:
										mc.connectAttr("%s.%s"%(origin_node, origin[2]), "%s.%s"%(item, destination[1]))
									except:
										mc.warning("Impossible to create the connexion [%s ; %s]" % (origin_node, item))

							if middle != None:
								middle_node = mc.shadingNode(middle[0], asTexture=True)
								if origin != None:
									try:
										mc.connectAttr("%s.%s"%(origin_node, origin[2]), "%s.%s"%(middle_node, middle[1]))
									except:
										mc.warning("Impossible to create the connexion [%s ; %s]" % (origin_node, middle_node))
								if destination != None:
									try:
										mc.connectAttr("%s.%s"%(middle_node, middle[2]), "%s.%s"%(item, destination[1]))
									except:
										mc.warning("Impossible to create the connexion [%s ; %s]"%(middle_node, item))
		self.add_log_content_function("Connexion from existing node created!")

			




	


							
							

			
		

	
			

