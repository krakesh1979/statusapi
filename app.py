from flask import Flask, jsonify, request
import time
from threading import Lock

app = Flask(__name__)

# In-memory job store for testing/demo only.
# For production, replace this with Redis, MongoDB, PostgreSQL, etc.
jobs = {}
lock = Lock()

JOB_STEPS = [
    {"event": "data_load", "step": "Load Data"},
    {"event": "process_records", "step": "Process Records"},
    {"event": "report_gen", "step": "Generate Report"},
]
TOTAL_DURATION_SEC = 20
STEP_DURATION_SEC = TOTAL_DURATION_SEC / len(JOB_STEPS)


def build_status_payload(elapsed):
    steps = []
    current_step_num = 1

    for i, step_def in enumerate(JOB_STEPS):
        step_start = i * STEP_DURATION_SEC
        step_end = (i + 1) * STEP_DURATION_SEC
        entry = {
            "event": step_def["event"],
            "step": step_def["step"],
        }

        if elapsed >= step_end:
            entry["status"] = "completed"
            entry["duration_ms"] = int(STEP_DURATION_SEC * 1000)
        elif elapsed >= step_start:
            entry["status"] = "in_progress"
            entry["duration_ms"] = int((elapsed - step_start) * 1000)
            current_step_num = i + 1
        else:
            entry["status"] = "pending"

        steps.append(entry)

    if elapsed >= TOTAL_DURATION_SEC:
        return {
            "status": "success",
            "message": "Job completed successfully",
            "progress": 100,
            "steps": steps,
        }

    return {
        "status": "running",
        "message": f"Processing step {current_step_num} of {len(JOB_STEPS)}",
        "progress": int((current_step_num / len(JOB_STEPS)) * 100),
        "steps": steps,
    }


@app.get("/")
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Job status API is running"
    })


@app.post("/api/jobs/<job_id>/start")
def start_job(job_id):
    with lock:
        jobs[job_id] = {
            "start_time": time.time(),
        }

    return jsonify({
        "job_id": job_id,
        "status": "started",
        "status_url": f"/api/jobs/{job_id}/status"
    })


@app.get("/api/jobs/<job_id>/status")
def get_job_status(job_id):
    with lock:
        if job_id not in jobs:
            return jsonify({
                "job_id": job_id,
                "status": "not_found",
                "message": "Job not found. Please start the job first."
            }), 404

        job = jobs[job_id]
        elapsed_override = request.args.get("elapsed")
        if elapsed_override is not None:
            try:
                elapsed = float(elapsed_override)
            except ValueError:
                return jsonify({
                    "job_id": job_id,
                    "status": "bad_request",
                    "message": "Query param 'elapsed' must be a number (seconds)."
                }), 400

            if elapsed < 0:
                return jsonify({
                    "job_id": job_id,
                    "status": "bad_request",
                    "message": "Query param 'elapsed' must be >= 0."
                }), 400
        else:
            elapsed = time.time() - job["start_time"]

        return jsonify(build_status_payload(elapsed))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
