from flask import render_template
from app import app


@app.errorhandler(403)
@app.errorhandler(404)
def handler(e):
    return render_template("error.html", error=e)
