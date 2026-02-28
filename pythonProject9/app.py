from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def show_user_profile():
  return render_template('views.html')


if __name__ =="__main__":
    app.run(debug=True)