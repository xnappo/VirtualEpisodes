# flask_app.py

from flask import Flask, request, render_template
import os
import subprocess
import sys
import threading
import time
import yaml
from datetime import datetime

app = Flask(__name__)
_last_auto_runs = {}


def load_config():
  with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file) or {}
  networks = config.get("networks", [])
  return config, networks


def save_config(config):
  with open("config.yaml", "w") as config_file:
    yaml.safe_dump(config, config_file, sort_keys=False)


def format_last_run(config):
  last_run = config.get("autoVirtualLastRun")
  if not last_run:
    return "Never"
  timestamp = last_run.get("timestamp")
  status = last_run.get("status", "unknown")
  if not timestamp:
    return "Unknown"
  return f"{timestamp} ({status})"


def update_last_run(config, status):
  config["autoVirtualLastRun"] = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "status": status,
  }
  save_config(config)


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


def run_auto_virtual():
  result = subprocess.run(
    [sys.executable, "autoVirtual.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
  )
  return result.stdout or "", result.returncode


def normalize_schedule_times(schedule_text):
  if not schedule_text:
    return []
  times = []
  for raw in schedule_text.split(","):
    value = raw.strip()
    if not value:
      continue
    try:
      parsed = datetime.strptime(value, "%H:%M")
      times.append(parsed.strftime("%H:%M"))
    except ValueError:
      continue
  return sorted(set(times))


def scheduler_loop():
  while True:
    try:
      config, _ = load_config()
      schedule = config.get("autoVirtualSchedule", [])
      now = datetime.now().strftime("%H:%M")
      today = datetime.now().strftime("%Y-%m-%d")
      if now in schedule:
        last_key = f"{today}-{now}"
        if not _last_auto_runs.get(last_key):
          _last_auto_runs[last_key] = True
          _, return_code = run_auto_virtual()
          status = "success" if return_code == 0 else "failed"
          update_last_run(config, status)
      time.sleep(30)
    except Exception:
      time.sleep(30)

@app.route('/')
def form():
  config, networks = load_config()
  schedule_times = config.get("autoVirtualSchedule", [])
  last_auto_run = format_last_run(config)
  return render_template(
    'form.html',
    networks=networks,
    output=None,
    needs_mapping=False,
    not_found_message=None,
    suggestions=[],
    schedule_times=", ".join(schedule_times),
    schedule_message=None,
    auto_output=None,
    last_auto_run=last_auto_run,
  )

@app.route('/run_script', methods=['POST'])
def run_script():
  input_data = request.form['input_data'].strip()
  output, unmapped_network, not_found_message, suggestions = run_add_virtual(input_data)
  config, networks = load_config()
  schedule_times = config.get("autoVirtualSchedule", [])
  last_auto_run = format_last_run(config)
  if unmapped_network:
    message = f'Network "{unmapped_network}" is not mapped.'
    return render_template(
      'form.html',
      networks=networks,
      output=output,
      needs_mapping=True,
      unmapped_network=unmapped_network,
      show_name=input_data,
      show_map_key=input_data,
      message=message,
      not_found_message=not_found_message,
      suggestions=suggestions,
      schedule_times=", ".join(schedule_times),
      schedule_message=None,
      auto_output=None,
      last_auto_run=last_auto_run,
    )
  return render_template(
    'form.html',
    networks=networks,
    output=output,
    needs_mapping=False,
    not_found_message=not_found_message,
    suggestions=suggestions,
    show_name=input_data,
    schedule_times=", ".join(schedule_times),
    schedule_message=None,
    auto_output=None,
    last_auto_run=last_auto_run,
  )


@app.route('/map_network', methods=['POST'])
def map_network():
  show_name = request.form['show_name'].strip()
  unmapped_network = request.form['unmapped_network'].strip()
  mapped_network = request.form['mapped_network'].strip()

  config, networks = load_config()
  schedule_times = config.get("autoVirtualSchedule", [])
  last_auto_run = format_last_run(config)
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
    show_map_key=show_name,
    message=message,
    not_found_message=not_found_message,
    suggestions=suggestions,
    schedule_times=", ".join(schedule_times),
    schedule_message=None,
    auto_output=None,
    last_auto_run=last_auto_run,
  )

@app.route('/map_show', methods=['POST'])
def map_show():
  show_name = request.form['show_name'].strip()
  show_map_key = request.form['show_map_key'].strip() or show_name
  mapped_network = request.form['mapped_network'].strip()

  config, networks = load_config()
  schedule_times = config.get("autoVirtualSchedule", [])
  last_auto_run = format_last_run(config)
  if not config.get('showMaps'):
    config['showMaps'] = {}
  config['showMaps'][show_map_key] = mapped_network
  save_config(config)

  output, new_unmapped, not_found_message, suggestions = run_add_virtual(show_name)
  message = f'Show "{show_map_key}" mapped to "{mapped_network}" and re-ran.'
  needs_mapping = False
  if new_unmapped:
    needs_mapping = True
    message = f'Network "{new_unmapped}" is not mapped.'

  return render_template(
    'form.html',
    networks=networks,
    output=output,
    needs_mapping=needs_mapping,
    unmapped_network=new_unmapped,
    show_name=show_name,
    show_map_key=show_map_key,
    message=message,
    not_found_message=not_found_message,
    suggestions=suggestions,
    schedule_times=", ".join(schedule_times),
    schedule_message=None,
    auto_output=None,
    last_auto_run=last_auto_run,
  )

@app.route('/run_movie_script', methods=['POST'])
def run_movie_script():
  movie_data = request.form['movie_data'].strip()
  movie_source = request.form['movie_source']
  output = run_add_movie(movie_data, movie_source)
  config, networks = load_config()
  schedule_times = config.get("autoVirtualSchedule", [])
  last_auto_run = format_last_run(config)
  return render_template(
    'form.html',
    networks=networks,
    output=output,
    needs_mapping=False,
    message='Movie added.',
    not_found_message=None,
    suggestions=[],
    schedule_times=", ".join(schedule_times),
    schedule_message=None,
    auto_output=None,
    last_auto_run=last_auto_run,
  )


@app.route('/schedule_update', methods=['POST'])
def schedule_update():
  schedule_text = request.form.get('schedule_times', '')
  normalized = normalize_schedule_times(schedule_text)
  config, networks = load_config()
  config['autoVirtualSchedule'] = normalized
  save_config(config)
  last_auto_run = format_last_run(config)
  message = 'Schedule updated.' if normalized else 'Schedule cleared.'
  return render_template(
    'form.html',
    networks=networks,
    output=None,
    needs_mapping=False,
    not_found_message=None,
    suggestions=[],
    schedule_times=", ".join(normalized),
    schedule_message=message,
    auto_output=None,
    last_auto_run=last_auto_run,
  )


@app.route('/run_auto_virtual', methods=['POST'])
def run_auto_virtual_now():
  output, return_code = run_auto_virtual()
  config, networks = load_config()
  status = "success" if return_code == 0 else "failed"
  update_last_run(config, status)
  schedule_times = config.get("autoVirtualSchedule", [])
  last_auto_run = format_last_run(config)
  return render_template(
    'form.html',
    networks=networks,
    output=None,
    needs_mapping=False,
    not_found_message=None,
    suggestions=[],
    schedule_times=", ".join(schedule_times),
    schedule_message='AutoVirtual run completed.',
    auto_output=output,
    last_auto_run=last_auto_run,
  )

if __name__ == '__main__':
  run_main = os.environ.get("WERKZEUG_RUN_MAIN")
  if run_main is None or run_main == "true":
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
  app.run(host='0.0.0.0', port=8086)