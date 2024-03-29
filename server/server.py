import os
from flask import Flask, flash, request, redirect, url_for, send_file, render_template
from werkzeug.utils import secure_filename
from affinitychecker import affinity_check
from emailscraper import email_check

UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
   return '.' in filename and \
          filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
       # check if the post request has the file part
       if 'file' not in request.files:
         flash('No file part')
         return redirect(request.url)
       file = request.files['file']
       # if user does not select file, browser also
       # submit an empty part without filename
       if file.filename == '':
         flash('No selected file')
         return redirect(request.url)
       if file and allowed_file(file.filename):
         filename = secure_filename(file.filename)
         filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
         file.save(filePath)
         return send_file(affinity_check(email_check((filePath))))
         # return redirect(request.url)
   return render_template('base.html')

if __name__ == '__main__':
   app.debug = True
   app.run(port=8080)