"""
API routes for the health statistics web service.
"""

import json
from flask import request, jsonify
from app import webserver
from app.data_ingestor import DataIngestor

# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    """Handle POST requests to the post endpoint."""
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)
    else:
        # Method Not Allowed
        return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    """Get the results for a specific job ID."""
    print(f"JobID is {job_id}")
    result_file = f"results/{job_id}.json"

    # Check if the job_id is valid
    job_id = int(job_id)
    if job_id not in webserver.tasks_runner.job_status:
        return jsonify({"status": "error", "reason": "Invalid job_id"}), 400

    # Check the status of the job
    job_status = webserver.tasks_runner.job_status[job_id]
    if job_status == "running":
        return jsonify({"status": "running"}), 200
    elif job_status == "error":
        return jsonify({"status": "error", "reason": "Task failed"}), 400

    # Read the result file if the job is done
    try:
        with open(result_file, "r", encoding="utf-8") as f:
            result_data = json.load(f)
        return jsonify({"status": "done", "data": result_data}), 200
    except (IOError, json.JSONDecodeError) as e:
        return jsonify({"status": "error", "reason": f"Failed to read result: {e}"}), 400

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """Handle requests for state means."""
    if webserver.tasks_runner.shutdown_event.is_set():
        return jsonify({"status": "error", "reason": "shutting down"})

    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing 'question' in request"}), 400

    job_id = webserver.job_counter
    webserver.job_counter += 1

    task = webserver.data_ingestor.get_states_mean
    task_data = {'question': question}
    webserver.tasks_runner.add_task((job_id, task, task_data))

    return jsonify({"status": "submitted", "job_id": job_id})

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """Handle requests for a specific state's mean."""
    if webserver.tasks_runner.shutdown_event.is_set():
        return jsonify({"status": "error", "reason": "shutting down"})

    data = request.json
    question = data.get("question")
    state = data.get("state")
    if not question or not state:
        return jsonify({"error": "Missing 'question' or 'state' in request"}), 400

    job_id = webserver.job_counter
    webserver.job_counter += 1

    task = webserver.data_ingestor.get_state_mean
    task_data = {'question': question, 'state': state}
    webserver.tasks_runner.add_task((job_id, task, task_data))

    return jsonify({"status": "submitted", "job_id": job_id})

@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """Handle requests for the best 5 states."""
    if webserver.tasks_runner.shutdown_event.is_set():
        return jsonify({"status": "error", "reason": "shutting down"})

    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing 'question' in request"}), 400

    job_id = webserver.job_counter
    webserver.job_counter += 1

    task = webserver.data_ingestor.get_best5
    task_data = {'question': question}
    webserver.tasks_runner.add_task((job_id, task, task_data))

    return jsonify({"status": "submitted", "job_id": job_id})

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """Handle requests for the worst 5 states."""
    if webserver.tasks_runner.shutdown_event.is_set():
        return jsonify({"status": "error", "reason": "shutting down"}), 400

    data = request.json
    question = data.get("question")
    if not question:
        webserver.logger.error("Missing 'question' in request")
        return jsonify({"error": "Missing 'question' in request"}), 400

    job_id = webserver.job_counter
    webserver.job_counter += 1

    task = webserver.data_ingestor.get_worst5
    task_data = {'question': question}
    webserver.tasks_runner.add_task((job_id, task, task_data))

    return jsonify({"status": "submitted", "job_id": job_id}), 200

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    if webserver.tasks_runner.shutdown_event.is_set():
        return jsonify({"status": "error", "reason": "shutting down"}), 400

    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing 'question' in request"}), 400

    job_id = webserver.job_counter
    webserver.job_counter += 1

    task = webserver.data_ingestor.get_global_mean
    task_data = {'question': question}
    webserver.tasks_runner.add_task((job_id, task, task_data))

    return jsonify({"status": "submitted", "job_id": job_id}), 200

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    if webserver.tasks_runner.shutdown_event.is_set():
        return jsonify({"status": "error", "reason": "shutting down"}), 400

    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing 'question' in request"}), 400

    job_id = webserver.job_counter
    webserver.job_counter += 1

    task = webserver.data_ingestor.get_diff_from_mean
    task_data = {'question': question}
    webserver.tasks_runner.add_task((job_id, task, task_data))

    return jsonify({"status": "submitted", "job_id": job_id}), 200

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    if webserver.tasks_runner.shutdown_event.is_set():
        return jsonify({"status": "error", "reason": "shutting down"}), 400

    data = request.json
    question = data.get("question")
    state = data.get("state")
    if not question or not state:
        return jsonify({"error": "Missing 'question' or 'state' in request"}), 400

    job_id = webserver.job_counter
    webserver.job_counter += 1

    task = webserver.data_ingestor.get_state_diff_from_mean
    task_data = {'question': question, 'state': state}
    webserver.tasks_runner.add_task((job_id, task, task_data))

    return jsonify({"status": "submitted", "job_id": job_id}), 200

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """Handle requests for means by category."""
    if webserver.tasks_runner.shutdown_event.is_set():
        return jsonify({"status": "error", "reason": "shutting down"}), 400

    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing 'question' in request"}), 400

    job_id = webserver.job_counter
    webserver.job_counter += 1

    task = webserver.data_ingestor.get_mean_by_category
    task_data = {'question': question}
    webserver.tasks_runner.add_task((job_id, task, task_data))

    return jsonify({"status": "submitted", "job_id": job_id}), 200

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """Handle requests for state-specific means by category."""
    if webserver.tasks_runner.shutdown_event.is_set():
        return jsonify({"status": "error", "reason": "shutting down"}), 400

    data = request.json
    question = data.get("question")
    state = data.get("state")
    if not question or not state:
        return jsonify({"error": "Missing 'question' or 'state' in request"}), 400

    job_id = webserver.job_counter
    webserver.job_counter += 1

    task = webserver.data_ingestor.get_state_mean_by_category
    task_data = {'question': question, 'state': state}
    webserver.tasks_runner.add_task((job_id, task, task_data))

    return jsonify({"status": "submitted", "job_id": job_id}), 200

# You can check localhost in your browser to see what this displays
@webserver.route('/index')
def index():
    """Display available API routes."""
    routes = get_defined_routes()
    msg = "Hello, World!\nInteract with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

def get_defined_routes():
    """Get a list of all defined API routes."""
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes

def init_routes(webserver):
    """
    Initialize the routes for the Flask application.

    Args:
        webserver: The Flask application instance.
    """
    @webserver.route('/api/start', methods=['POST'])
    def start():
        """
        Start a new task to process the data.

        Returns:
            A JSON response containing the job ID and status.
        """
        webserver.job_counter += 1
        job_id = webserver.job_counter
        webserver.tasks_runner.add_task(job_id)
        return jsonify({"job_id": job_id, "status": "started"})

    @webserver.route('/api/status/<int:job_id>', methods=['GET'])
    def status(job_id):
        """
        Get the status of a job.

        Args:
            job_id: The ID of the job to check.

        Returns:
            A JSON response containing the job status.
        """
        return jsonify(webserver.tasks_runner.get_status(job_id))

    @webserver.route('/api/results/<int:job_id>', methods=['GET'])
    def results(job_id):
        """
        Get the results of a job.

        Args:
            job_id: The ID of the job to get results for.

        Returns:
            A JSON response containing the job results.
        """
        return jsonify(webserver.tasks_runner.get_results(job_id))
