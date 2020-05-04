#!usr/bin/python3
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import re
#install pyserial lib
import serial
from time import gmtime, strftime, localtime
import csv
import shutil
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

import glob
import os
import dropbox

number_of_run=0

fig, ax1 = plt.subplots(2,1, sharex=True)
#fig.autofmt_xdate()
xfmt = mdates.DateFormatter('%d-%H:%M')  															# special thing for reformat date; use only hours and minutes
fig.subplots_adjust(top=0.97, left=0.05, right=0.97, bottom=0.065, hspace=0.0, wspace=0.19)			# spacers for subplots 0.28


def dropbox_download ():
	
	global list_of_files

	list_of_files=[]
	
	dbx = dropbox.Dropbox('iNMphzXEo8AAAAAAAAAAECRNABNoukVIv0vN2oaJjcH4XOvufztzq9moBSiBOKYp')
	entries = dbx.files_list_folder('/data2').entries
	#print(number_of_run)

	if number_of_run>=1:
		entries = entries[-2:]																		# take two last files; in order do not download all files each times; 

	for entry in entries:																			
		if isinstance(entry, dropbox.files.FileMetadata):  											# this entry is a file
			md, res = dbx.files_download(entry.path_lower)
			list_of_files.append(md.name)  															# this is the metadata for the downloaded file
			with open(os.path.join("Logs/",list_of_files[-1]), "wb") as f:
				f.write(res.content)
			
	
	print("Download completed")


def animate (i):

	global number_of_run

	dropbox_download();
	
	number_of_run = number_of_run + 1																	# for download only last two files

	df_last_last = pd.read_csv(os.path.join("Logs/", list_of_files[-2]), sep="\t", header=None)
	df_last = pd.read_csv(os.path.join("Logs/", list_of_files[-1]), sep="\t", header=None)
	df = pd.concat([df_last_last, df_last], ignore_index=True)

	date=pd.DatetimeIndex(df[0]+" " +df[1]) 
	df[6]=df[6].replace("< 1", 0.1).astype(np.float64)													# some problem with type of data in column 7

	ax1[0].clear()
	ax1[1].clear()

	text_pressure = ("Current Pressure [psi]: " + str(df[2].iloc[-1]))
	text_level = ("Current Heater Power [W]: " + str(df[3].iloc[-1]))

	ax1[0].plot(date[-600:], df[2][-600:],color="red", alpha=1,label="Pressure")
	ax1[1].plot(date[-600:], df[3][-600:], color="red",alpha=1,label="Heater Power")

	min_p = min(df[2][-600:])
	max_p = max(df[2][-600:])
	ax1[0].text(0.7285, 0.96, text_pressure, transform = ax1[0].transAxes, fontsize=16, fontweight='bold',verticalalignment='top')
	ax1[0].set_xlabel('Time [Day-H:M]',weight="bold", fontsize=16)
	ax1[0].tick_params(labelsize=15)
	ax1[0].set_ylabel('Pressure [Psi]',weight="bold", fontsize=16)
	ax1[0].set_ylim(min_p-max_p*0.17, max_p*1.17)
	ax1[0].grid(True,linestyle='--', linewidth=0.4)  
	ax1[0].legend(bbox_to_anchor=(0.01, 0.89, 1., .102), prop=dict(weight='bold',size=16), loc='lower left', ncol=2, borderaxespad=0.) # mode="expand"
	ax1[0].xaxis.set_major_formatter(xfmt)

	min_h = min(df[3][-600:])
	max_h = max(df[3][-600:])	
	ax1[1].text(0.73, 0.96, text_level, transform = ax1[1].transAxes, fontsize=16, fontweight='bold',verticalalignment='top')
	ax1[1].set_xlabel('Time [Day-H:M]',weight="bold", fontsize=16)
	ax1[1].set_ylabel('Heater Power [W]',weight="bold", fontsize=16)
	ax1[1].tick_params(labelsize=15)
	ax1[1].set_ylim(min_h-max_h*0.17, max_h*1.17)
	ax1[1].grid(True,linestyle='--', linewidth=0.4)  
	ax1[1].legend(bbox_to_anchor=(0.01, 0.89, 1., .102), prop=dict(weight='bold',size=16), loc='lower left', ncol=2, borderaxespad=0.)

	ax1[0].fill_between(date[-600:], -0.35, df[2][-600:], where=df[7][-600:].to_numpy()=="Running", facecolor="green", alpha=0.15)
	ax1[1].fill_between(date[-600:], -0.2, df[3][-600:], where=df[7][-600:].to_numpy()=="Running", facecolor="green", alpha=0.15)
	ax1[1].xaxis.set_major_formatter(xfmt)    

	fig.align_labels()


def Main():
	""" This is a function to show animated plot """
	ani = animation.FuncAnimation(fig, animate, interval=180000)
	plt.show()
	

Main()