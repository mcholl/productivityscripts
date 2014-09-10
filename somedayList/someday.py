## DayOne Task Extractor
# Harvest tasks written in Day One, and write them to TaskPaper
#Note: depends on lxml (pip install lxml) version = 3.3.1

from datetime import date, datetime, tzinfo, timedelta, time
import os, sys
import ConfigParser
from lxml import etree
import markdown
import webbrowser
import codecs


class DayOneHarvester:

	def __init__(self):
		self.output_file = "~/Dropbox/Documents/TaskPaper/somedaylist.taskpaper"
		self.dayone_directory = "~/Dropbox/Apps/Day One/Journal.dayone/entries"
		self.ini_file = 'taskextractor.ini'
		self.disp = 'Someday Items:'

		self.output_file = os.path.expanduser(self.output_file)
		self.found_someday_entries = {}
		self.found_tasks = {}

	#Used to sort the directories in the last modified order
	#http://stackoverflow.com/questions/4500564/directory-listing-based-on-time
	def sorted_ls(self, path):
	    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
	    return list(sorted(os.listdir(path), key=mtime, reverse=True))
	    
	def newly_modified_files(self, last_run_time):
	    n = 0;
	    files = self.sorted_ls(os.path.expanduser(self.dayone_directory))
	    for fl in files:
	        raw_mod_time = os.path.getmtime(os.path.join(os.path.expanduser(self.dayone_directory),fl))
	        mod_time = datetime.utcfromtimestamp(raw_mod_time)
	        if mod_time < last_run_time:
	            break
	        n=n+1
	    return files[0:n]

	def read_element_value(self, root, xpath_selector ):
	    #http://lxml.de/xpathxslt.html
	    find_node = etree.XPath(xpath_selector)
	    found_node = find_node(root)
	    
	    if len(found_node) == 0:
	    	return ""
	    
	    #print "NODE SLELECTED WITH {0}".format(xpath_selector)
	    thevalue =found_node[0].text
	    
	    return thevalue

	def process_new_entries_since(self, last_run_time):
		#Iterates through all DayOne entries since the last run time	
		for fl in self.newly_modified_files(last_run_time):
			try:
				entry_file = ''
				nFoundTask = 0

				#For debugging, showing the file
				mod_time = datetime.utcfromtimestamp(os.path.getmtime(os.path.join(os.path.expanduser(self.dayone_directory),fl)))
				# print fl, datetime.strftime(mod_time, "%b %d %Y %H:%M")

				entry_file = open(os.path.join(os.path.expanduser(self.dayone_directory),fl), 'rb')
				#(Why didn't DayOne be nice and do <key item=""UUID"> or even <UUID>xxx</UUID> Grrr!!!


				tree = etree.parse( entry_file )
				#uuid = read_element_value( tree, "//key[text()='UUID']/../string")
				body = self.read_element_value( tree, "//key[text()='Entry Text']/../string")

				if body is None:
					continue

				#Now, extract only lines that begin with @ and isn't already @done
				for line in body.split("\n"):
					if "#someday" in line.strip().lower():
						self.found_someday_link(fl, body)

					if line.lstrip().startswith("@"):
						if "@done" not in line.lower():
						    self.found_task(fl, line, nFoundTask)
						    nFoundTask = nFoundTask + 1


			except:
			    print "Error parsing lines"
			    print entry_file
			    print "Unexpected error:", sys.exc_info()
	                    
	def get_markdown(self):
		#Prints out the Markdown version of the Someday List and Task List

		somedaylist = '\n'.join( "- [%s](dayone://edit?entryId=%s)" % (task, link) for (link, task) in self.found_someday_entries.iteritems() )
		somedaylist = "Someday List:\n"+somedaylist

		#tasklist = '\n'.join( "- [%s](dayone://edit?entryId=%s)" % (task, link) for (link, task) in self.found_tasks.iteritems() )
		tasklist = "\nTasks:\n"
		for link in self.found_tasks.keys():
			for task in self.found_tasks[link]:
				msg = " - [{0}](dayone://edit?entryId={1})\n".format(self.found_tasks[link][task], link)
				tasklist = tasklist + msg


		return somedaylist+tasklist

		#TODO: The lists are prettier if I can separate out the references from the tasks - and that is easily doable as below.  Problem? The Markdown isn't working...
		# return '\n'.join(self.found_someday_entries)
		# disp = '\n'.join( "    - [%s]()" % task for task in self.found_someday_entries.values() )
		# notes = '\n'.join( "  [%s]: (dayone://edit?entryId=%s)" % (task, link) for (link, task) in self.found_someday_entries.iteritems() )
		# return "Items:\n\n"+disp + " \n\nReferences:\n\n" + notes

	def save_markdown(self, output_file_name):
		output_file = codecs.open(output_file_name, "w", 
                          encoding="utf-8", 
                          errors="xmlcharrefreplace"
		)
		output_file.write(self.get_markdown())


	def generate_html(self, html_output_file):

		disp = self.get_markdown()
		print disp
		html = markdown.markdown(disp)

		output_file = codecs.open(html_output_file, "w", 
                          encoding="utf-8", 
                          errors="xmlcharrefreplace"
		)
		output_file.write(html)

	def get_last_run(self, harvester):
	    config = ConfigParser.ConfigParser()
	    config.read(self.ini_file)
	    if 'last_run' not in config.sections():
	        cfg = open(self.ini_file,'w')
	        config.add_section('last_run')
	        config.write(cfg)
	        cfg.close()
	    
	    try:
	    	lr = config.get('last_run', harvester)
	    except ConfigParser.NoOptionError:
	    	print "No default set"
	        lr= 'Jan 1 1970 12:00'

	    return datetime.strptime(lr, "%b %d %Y %H:%M")
	        
	def set_last_run(self, harvester):
	    config = ConfigParser.ConfigParser()
	    config.read(self.ini_file)
	    
	    cfg = open(self.ini_file,'w')
	    last_run = config.set('last_run', harvester, datetime.now().strftime("%b %d %Y %H:%M"))
	    config.write(cfg)
	    cfg.close()

	def print_found_entries(self, fl, line):
	    print "[{0}](dayone://edit?entryId={1})".format(line.trim(), fl.replace(".doentry",""))


	#Someday Harvester
	#This script will search through all of my journal entries,
	#find any entry tagged #someday
	#verify there is no @done tag 
	#create a wiki link to the entry
	#save it in the someday list, if it isn't already there [examine the link]

	def found_someday_link(self, fl, body):	
		#If I found a #someday tag in the file, process it
		#title is the first line in the entry
	    try:
	        #TODO: Search the file for an @trigger tag...
	        #TODO: Store the task syntax from the references at the bottom separately - that way, when I display, I can print the references at the end
	        task = body.split("\n")[0]
	        link = fl.replace(".doentry","")

	        # msg = "- [{0}]()\n\t[{0}]: dayone://edit?entryId={1}".format(task, link)

	        #Note: Technically, this is backwards. If I try to have multiple tasks in a entry, this will break.  But, it reads better if I dsplay the dictionary :)
	        self.found_someday_entries[link] = task

	    except:
	        print "Error appending from {1} to file {0}".format(self.output_file, fl)
	        print "Unexpected error:", sys.exc_info()


	#Task Extractor.  Theses functions pull out tasks - lines that start with an @Context

	def found_task(self, fl, line, nTask):
		try:
			sep = line.split(" ")
			context = sep[0]
			task = line[len(context)+1:]    
			link = fl.replace(".doentry","")

			# print "Found Task"
			# print "{0} ==> {2}: {1}".format(link, line, nTask)

			tskEntry = {}
			if self.found_tasks.get(link, None) is None:
				tskEntry[0] = task
			else:
				tskEntry = self.found_tasks.get(link, None)
				tskEntry[nTask] = task

			self.found_tasks[link] = tskEntry
		except:
			print "=================================="
			print "Error adding task to found_tasks"
			print "{0} ==> {2}: {1}".format(link, line, nTask)
			print "Unexpected error:", sys.exc_info()
			print "=================================="


if __name__ == '__main__':
	someday_html = './someday'

	#Read all Day One entries since the last run
	#last_run_time = datetime.strptime(last_run, "%b %d %Y %H:%M")
	dp = DayOneHarvester()

	last_run_time = dp.get_last_run('day_one')
	print "Checking files modified since {0}".format(last_run_time)
	dp.process_new_entries_since(last_run_time)

	#print dp.found_someday_entries
	#print dp.found_tasks
	dp.save_markdown(someday_html+".md")
	dp.generate_html(someday_html+".html")
	webbrowser.open('file://' + os.path.realpath(someday_html))

	dp.set_last_run('day_one')
	print "Done"
