import re
from dateutil import parser
from datetime import *
import sys

class CalendarItem():
	tag_name = None
	line = None
	the_date = None
	is_done = False

	def display(self):
		try:
			if self.is_done:
				print "Finished item: {0}".format(self.line)
			else:
				print "{1},    {0}".format(self.line, self.tag_name, self.the_date.strftime("%c"))
		except:
			print "Unexpected error:", sys.exc_info()
			print self.line

class TaskParser():

	def __init__(self):
		self.calitems = {}

	def parse_file(self, filename):
		is_under_date_project = False
		project_indentation_level = 0
		date_project_date = None 
		#datetime(1900, 1, 1, 0, 0, 0).date()

		print "Reading File: {0}".format(filename)

		f = open(filename, 'r')
		for line in f:
			#Verify there is text on the line
			if line.strip() == "":
				continue

			#Look for @tag(date) lines
			the_task, tag_name, the_date = self.extract_dated_lines(line)
			if not the_task is None:
				# print "Found Task {0}".format(line)
				self.save_line(the_task, tag_name, the_date)
				continue

			# line = line.join('%-5s' % item for item in line.split('\t'))
			# print "LINE =>{0}".format(line)
			indentation = len(line) - len(line.lstrip())
			line = line.rstrip()

			#Look for lines in a project that is just a date
			if is_under_date_project:

				#Verify the indentation is further to the left than the project.
				if indentation > project_indentation_level:
					#It is indented further than the project, so its ok
					the_date = date_project_date
					tag_name = ""
					self.save_line(line, tag_name, the_date)
				else:
					is_under_date_project = False
					date_project_date = None

			# If the project is a date (e.g. "Monday, May 13:"), set the flags
			if (line.rstrip().endswith(":")):
				#Examine the Project to see if it's a dated project.
				project_name = line.strip()[:-1]
				#print "Looking at level {1} project ->{0}<-".format(project_name, indentation)

				date_project_date = self.extract_date(project_name)
				is_under_date_project = not (date_project_date is None)

		print "File read: {0}".format(filename)

	def extract_dated_lines(self, line):
		#This function processes lines that have any @tag(date), and returns the line if there is a dated tag

		#Regexes
		tag_regex = re.compile('\@(.*?)\((.*?)\)')
		tag_today = re.compile('\@today', re.IGNORECASE)

		#Look for lines that have date tags in them (e.g.  My Task @due(Wednesday) )
		found_tags = tag_regex.findall(line)
		for found_tag in found_tags:
			tag_name = found_tag[0]
			if tag_name.lower() == "done":
				if len(found_tags) > 1:
					#TODO: Make sure this isn't the only tag found before discarding it.  The done date is the best date I'd have in those circumstances.
					continue

			dt_string = found_tag[1]

			the_date = self.extract_date(dt_string)
			if not the_date is None:
				return line, tag_name, the_date

		#Special Tag handling for @today
		if tag_today.search(line) is not None:
			return line, "", date.today()


		#If nothing valud was found, return Nones
		return None, None, None

	def save_line(self, line, tag_name, the_date):
		#Saves the line to a date in the calendar

		if not line.lstrip()[0:1] == "-":
			#We only want to save tasks - not projects or notes.
			return

		#Strip out the dash, and the tag that gave me the date
		line = line.lstrip()[1:].lstrip()

		regex_string = "\@"+tag_name+"\(.*?\)"
		regex_remove_tag = re.compile(regex_string)
		line = regex_remove_tag.sub("", line)

		line = line.rstrip()

		c = CalendarItem()
		c.the_date = the_date
		c.line = line
		c.tag_name = tag_name

		if "done" in line.lower():
			c.is_done = True

		if not the_date in self.calitems:
			self.calitems[the_date] = []

		self.calitems[the_date].append(c)

	def extract_date(self, dt_string):
		#Given a dt_string that is potentially a date, returns a date time object matching the string

		try:
			#dateutil's parser catches a heck of a lot, including 'Wednesday' and the like :)
			dt = parser.parse(dt_string, dayfirst=False, yearfirst=False)
			return dt.date() 
		except TypeError:
			#Here I catch things that the parse can't, usually bogus dates
			return None
		except ValueError:
			return None

	def display(self):
		# print "Displaying"
		for dt in self.calitems.keys():
			try:
				print "\n=== Items on {0} ===".format(dt.strftime("%c"))
				for c in self.calitems[dt]:
					c.display()
			except:
				print "Unexpected error:", sys.exc_info()
				print dt

if __name__ == '__main__':
	tp = TaskParser()
	tp.parse_file('testdata/projects.taskpaper')
	tp.display()