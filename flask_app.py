# flask_app.py

from flask import Flask, request, render_template
import os
import subprocess
import sys
import yaml

app = Flask(__name__)


def load_config():
  with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file) or {}
  networks = config.get("networks", [])
  return config, networks


def save_config(config):
  with open("config.yaml", "w") as config_file:
    yaml.safe_dump(config, config_file, sort_keys=False)


def run_add_virtual(show_name):
  env = dict(os.environ)
  env["AUTOVIRTUAL_WEB"] = "1"
  result = subprocess.run(
    [sys.executable, "addVirtual.py", show_name],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    env=env,
  )
  raw_output = result.stdout or ""
  unmapped_network = None
  not_found_message = None
  suggestions = []
  cleaned_lines = []
  in_not_found = False

  for line in raw_output.splitlines():
    if line.startswith("UNMAPPED_NETWORK:"):
      unmapped_network = line.split(":", 1)[1].strip()
      continue

    if "not found" in line.lower():
      not_found_message = line.strip()
      in_not_found = True
      continue

    if in_not_found:
      stripped = line.strip()
      if not stripped:
        continue
      if "[" in stripped and "]" in stripped:
        title = stripped[:stripped.rfind("[")].strip()
        network = stripped[stripped.rfind("[") + 1:stripped.rfind("]")].strip()
        suggestions.append({"title": title, "network": network})
        continue
      if "following series" in stripped:
        continue

    cleaned_lines.append(line)

  suggestions = list(reversed(suggestions))
  output = "\n".join(cleaned_lines)
  return output, unmapped_network, not_found_message, suggestions


def run_add_movie(movie_name, movie_source):
  result = subprocess.run(
    [sys.executable, "addMovieVirtual.py", movie_name, movie_source],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
  )
  return result.stdout or ""

@app.route('/')
def form():
  _, networks = load_config()
  return render_template(
    'form.html',
    networks=networks,
    output=None,
    needs_mapping=False,
    not_found_message=None,
    suggestions=[],
  )

@app.route('/run_script', methods=['POST'])
def run_script():
  input_data = request.form['input_data'].strip()
  output, unmapped_network, not_found_message, suggestions = run_add_virtual(input_data)
  _, networks = load_config()
  if unmapped_network:
    message = f'Network "{unmapped_network}" is not mapped.'
    return render_template(
      'form.html',
      networks=networks,
      output=output,
      needs_mapping=True,
      unmapped_network=unmapped_network,
      show_name=input_data,
      message=message,
      not_found_message=not_found_message,
      suggestions=suggestions,
    )
  return render_template(
    'form.html',
    networks=networks,
    output=output,
    needs_mapping=False,
    not_found_message=not_found_message,
    suggestions=suggestions,
    show_name=input_data,
  )


@app.route('/map_network', methods=['POST'])
def map_network():
  show_name = request.form['show_name'].strip()
  unmapped_network = request.form['unmapped_network'].strip()
  mapped_network = request.form['mapped_network'].strip()

  config, networks = load_config()
  if not config.get('networkMaps'):
    config['networkMaps'] = {}
  config['networkMaps'][unmapped_network] = mapped_network
  save_config(config)

  output, new_unmapped, not_found_message, suggestions = run_add_virtual(show_name)
  message = f'Mapped "{unmapped_network}" to "{mapped_network}" and re-ran.'
  needs_mapping = False
  if new_unmapped:
    needs_mapping = True
    message = f'Network "{new_unmapped}" is not mapped.'

  return render_template(
    'form.html',
    networks=networks,
    output=output,
    needs_mapping=needs_mapping,
    unmapped_network=new_unmapped or unmapped_network,
    show_name=show_name,
    message=message,
    not_found_message=not_found_message,
    suggestions=suggestions,
  )

@app.route('/run_movie_script', methods=['POST'])
def run_movie_script():
  movie_data = request.form['movie_data'].strip()
  movie_source = request.form['movie_source']
  output = run_add_movie(movie_data, movie_source)
  _, networks = load_config()
  return render_template(
    'form.html',
    networks=networks,
    output=output,
    needs_mapping=False,
    message='Movie added.',
    not_found_message=None,
    suggestions=[],
  )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086)