from flask import Flask
from flask import render_template
import webbrowser
app = Flask(__name__)

@app.route('/')
def hello_world():
	return "<h1>Hello,</H1><h5>world!</h5>"

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name='world'):
	return render_template('test.html', name=name)

if __name__ == '__main__':
	webbrowser.open('http://127.0.0.1:5000/hello')
	app.run(debug=True)
