from flask import Flask, render_template, request, flash
            
app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN888"

@app.route("/hello")
def index():
	flash("looking for something?")
	return render_template("index.html")

@app.route("/search", methods=["POST","GET"])
def search():

	flash("Search for  " +str(request.form['num_matches'])+", " +str(request.form['search_term']) +" products")
	return render_template("index.html")


if __name__ == "__main__":
	app.run(debug=True)