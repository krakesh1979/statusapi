from flask import Flask, jsonify
import time
from threading import Lock

app = Flask(__name__)

# In-memory job store for testing/demo only.
# For production, replace this with Redis, MongoDB, PostgreSQL, etc.
jobs = {}
lock = Lock()


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
            "status": "pending",
            "progress": 0,
            "message": "Job started"
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
        elapsed = time.time() - job["start_time"]

        if elapsed < 10:
            job["status"] = "running"
            job["progress"] = int((elapsed / 20) * 100)
            job["message"] = f"Processing... {int(elapsed)}s elapsed"

        elif elapsed < 20:
            job["status"] = "running"
            job["progress"] = int((elapsed / 20) * 100)
            job["message"] = f"Still processing... {int(elapsed)}s elapsed"

        else:
            job["status"] = "success"
            job["progress"] = 100
            job["message"] = "Job completed successfully"
            job["result"] = {
                "data": "final output"
            }

        return jsonify({
            "job_id": job_id,
            "status": job["status"],
            "progress": job["progress"],
            "message": job["message"],
            "result": job.get("result")
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
