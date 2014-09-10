from flask import Flask
from flask import render_template
import webbrowser
from caltasks import *


app = Flask(__name__)

@app.route('/threeview/')
@app.route('/threeview/{center_date}/')
def threeview():
	#TODO: Use today's date as the default
	context = {}
	context['center_date'] = '2014-08-26'

	context['overdue'] = {}
	# context['current'] = ["Task 1","Task 2"]#{}
	context['current'] = []
	context['future'] = {}

	tp = TaskParser()
	tp.parse_file('testdata/projects.taskpaper')

	for dt in tp.calitems.keys():
		try:
			for c in tp.calitems[dt]:
				block = 'current'
				#if dt < center_date:
				#	block = 'overdue'	
				#elif dt == center_date:
				# 	block = 'current'
				#elif dt > center_date:
				#	block = 'future'	
				#else:
				#	block='undefined'


				msg = "{0} {1}".format(c.tag_name, c.line)

				context[block].append(msg)

		except:
			msg = "Unexpected error:", sys.exc_info()
			context['messages'].append(msg) 

	return render_template('threeview.html', context=context)



if __name__ == '__main__':
	webbrowser.open('http://127.0.0.1:5000/threeview/')
	app.run(debug=True)
