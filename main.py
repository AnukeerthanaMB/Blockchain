import base64
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, send_file
from index import BlockChain
import json
from tkinter import *
from werkzeug.wsgi import wrap_file


app = Flask(__name__)
app.secret_key = "alkdjfalkdjf"


@app.route("/")
def welcome():
		return render_template('welcome.html')



@app.route("/home")
def home():
	if session.get("user"):
		return render_template('home.html')
	else:
		flash("Please login to access Verifier")
		return redirect(url_for('login'))



@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		user = request.form["username"]
		pswd = request.form["password"]

		if user == "Admin":
			if pswd == "password":
				session["user"] = "Admin"
				return redirect(url_for("admin"))
		
		
		else:
			flash("Invalid Login details")
			return redirect(url_for('login'))
	else:
		return render_template('login.html')


@app.route("/verify/<kid>", methods=["GET"])
def verify(kid):
		return render_template('verify.html', keyId=kid)


def getBlockByKey(key):
	with open('./NODES/N1/blockchain.json', 'r') as bfile:
		n1_data = str(bfile.read())
	with open('./NODES/N2/blockchain.json', 'r') as bfile:
		n2_data = str(bfile.read())
	with open('./NODES/N3/blockchain.json', 'r') as bfile:
		n3_data = str(bfile.read())
	with open('./NODES/N4/blockchain.json', 'r') as bfile:
		n4_data = str(bfile.read())

	pd = str(key)

	if (pd in n1_data) and (pd in n2_data) and (pd in n3_data) and (pd in n4_data):

		with open('./NODES/N1/blockchain.json', 'r') as bfile:
			for x in bfile:
				if pd in x:
					a = json.loads(x)["data"]
					b = a.replace("'", "\"")
					data = json.loads(b)
					department = data["Department"]
					student_name = data["Studentname"]
					academic_year = data["AcademicYear"]
					regnum = data["RegNum"]
					joining_date = data["JoiningDate"]
					end_date = data["EndDate"]
					mark = data["Mark"]
					certfile = data["CertificateFile"]
					personality = data["Personality"]

		return {
			"department": department,
			"student_name": student_name,
			"academic_year": academic_year,
			"regnum": regnum,
			"joining_date": joining_date,
			"end_date": end_date,
			"mark": mark,
			"certfile": certfile,
			"personality": personality,
		}


@app.route("/verify", methods=["POST"])
def success():

	key = request.form["keyId"]
	block = getBlockByKey(key=key)	
	
	if block:
		return render_template('success.html',keyId=key, department=block["department"], studentname=block["student_name"], academicyear=block["academic_year"], regnum=block["regnum"], joiningdate=block["joining_date"], enddate=block["end_date"], mark=block["mark"], certfile=block["certfile"], personality=block["personality"])
	else:
		return render_template('fraud.html')


@app.route("/addcertificate", methods=["POST", "GET"])
def addcertificate():
	
	if request.method == "POST":
		file = request.files['certfile']
		if not file.filename.endswith('.pdf'):
			flash("only pdf are supported")
			return redirect(url_for('certificate'))	
		
		department	 = request.form["department"]
		studentname	 = request.form["studentname"]
		academicyear = request.form["academicyear"]
		regnum = request.form["regnum"]
		joiningdate = request.form["joiningdate"]
		enddate= request.form["enddate"]
		mark= request.form["mark"]
		  
		certfile = base64.b64encode(file.read()).decode()

		personality = request.form["personality"]

		
		print(department, studentname, academicyear, regnum, joiningdate, enddate, mark, certfile, personality)
		bc = BlockChain()
		bc.addCertificate(department, studentname, academicyear, regnum, joiningdate, enddate, mark, certfile, personality)
		
		flash("Certificate added successfully to the Blockchain")
		# return render_template('home.html')
		return redirect(url_for('home'))
	else:
		# return render_template('home.html')
		return redirect(url_for('home'))


@app.route("/admin")
def admin():
	if session["user"] == "Admin":
		return render_template('admin.html')
	else:
		return redirect(url_for('login'))


@app.route("/verifyNodes")
def verifyNodes():
	bc = BlockChain()
	isBV = bc.isBlockchainValid()

	if isBV:
		flash("All Nodes of Blockchain are valid")
		return redirect(url_for('home'))
	else:
		flash("Blockchain Nodes are not valid")
		return redirect(url_for('admin'))


@app.route("/certificate")
def certificate():
	return render_template('CertificatePage.html')



@app.route("/logout")
def logout():
	session["user"] = ""
	return redirect(url_for('login'))


@app.route("/files/<path:keyId>", methods=["POST","GET"])
def files(keyId):
	if request.method == 'POST' or  request.method == 'GET':
		block = getBlockByKey(key=keyId)
		bytes = BytesIO(base64.b64decode(block["certfile"]))
		
		return send_file(bytes, attachment_filename='test.pdf', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
    session["user"] = ""



