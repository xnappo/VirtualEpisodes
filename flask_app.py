# flask_app.py

from flask import Flask, request, render_template
import subprocess
import addVirtual
import yaml

app = Flask(__name__)

# Load YAML configuration
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)
    networks = config.get("networks", [])

@app.route('/')
def form():
    return render_template('form.html', networks=networks)

@app.route('/run_script', methods=['POST'])
def run_script():
  input_data = request.form['input_data']
  result = subprocess.run(['python3','addVirtual.py',input_data],stdout=subprocess.PIPE)
  output = result.stdout.decode('latin-1').split('\n')
  output = '<br>'.join(output)
  return output

@app.route('/run_movie_script', methods=['POST'])
def run_movie_script():
  movie_data = request.form['movie_data']
  movie_source = request.form['movie_source']
  result = subprocess.run(['python3','addMovieVirtual.py',movie_data, movie_source],stdout=subprocess.PIPE)
  output = result.stdout.decode('latin-1').split('\n')
  output = '<br>'.join(output)
  return output

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8086)