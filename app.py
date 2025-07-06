import os
from flask import Flask, request, render_template_string, redirect, flash, url_for, send_file, session
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed for flash messages and sessions

# Azure Storage setup
CONNECT_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "DefaultEndpointsProtocol=https;AccountName=nadir885;AccountKey=Av9I/QAydE8gn5eBoIi8Nx4CUuRCRwbwIQ5Pq6nC+aODKucZHs+FvML9FN2ZSTV41idEvn0JTifB+AStTovBgw==;EndpointSuffix=core.windows.net")
CONTAINER_NAME = "newapp"
blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Demo credentials (for real app, use a database)
DEMO_USER = "admin"
DEMO_PASS = "password123"

HTML = """
<!doctype html>
<html lang="en">
<head>
    <title>Azure Blob Uploader</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8fafc; }
        .container { max-width: 800px; margin-top: 40px; }
        .file-list { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1 class="mb-3 text-primary">Azure Blob Uploader</h1>
        <p class="lead">Upload, download, and manage blobs in Azure!</p>
    </div>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="alert alert-info" role="alert">
          {{ messages[0] }}
        </div>
      {% endif %}
    {% endwith %}
    {% if not session.get('logged_in') %}
        <form method="post" action="{{ url_for('login') }}" class="mb-4">
            <div class="input-group">
                <input type="text" name="username" class="form-control" placeholder="Username" required>
                <input type="password" name="password" class="form-control" placeholder="Password" required>
                <button type="submit" class="btn btn-primary">Login</button>
            </div>
        </form>
    {% else %}
        <form method="post" enctype="multipart/form-data" class="d-flex flex-column flex-md-row gap-2 mb-4">
            <input type="file" name="file" class="form-control" required>
            <button type="submit" class="btn btn-primary">Upload</button>
            <a href="{{ url_for('logout') }}" class="btn btn-secondary">Logout</a>
        </form>
        <div class="file-list shadow-sm">
            <h5 class="mb-3 text-secondary">Files in Azure Blob Storage:</h5>
            {% if blobs %}
            <table class="table table-sm align-middle">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Size</th>
                        <th>Last Modified</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                {% for blob in blobs %}
                    <tr>
                        <td>{{ blob['name'] }}</td>
                        <td>{{ blob['size'] }} bytes</td>
                        <td>{{ blob['last_modified'] }}</td>
                        <td>
                            <a href="{{ url_for('download_file', filename=blob['name']) }}" class="btn btn-sm btn-success">Download</a>
                            <a href="{{ url_for('delete_file', filename=blob['name']) }}" class="btn btn-sm btn-danger" onclick="return confirm('Delete {{ blob['name'] }}?')">Delete</a>
                        </td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
            {% else %}
                <p class="text-muted">No files found. Start by uploading one!</p>
            {% endif %}
        </div>
    {% endif %}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if not session.get('logged_in'):
        return render_template_string(HTML)
    if request.method == "POST":
        f = request.files['file']
        if f:
            try:
                container_client.upload_blob(f.filename, f, overwrite=True)
                flash(f"'{f.filename}' uploaded successfully!")
            except Exception as e:
                flash(f"Upload failed: {str(e)}")
        else:
            flash("No file selected.")
        return redirect(url_for('upload_file'))
    blobs = []
    for blob in container_client.list_blobs():
        blobs.append({
            "name": blob.name,
            "size": blob.size,
            "last_modified": blob.last_modified.strftime('%Y-%m-%d %H:%M:%S')
        })
    return render_template_string(HTML, blobs=blobs)

@app.route("/download/<filename>")
def download_file(filename):
    if not session.get('logged_in'):
        flash("Please log in to download files.")
        return redirect(url_for('upload_file'))
    downloader = container_client.download_blob(filename)
    stream = BytesIO()
    downloader.readinto(stream)
    stream.seek(0)
    return send_file(stream, as_attachment=True, download_name=filename)

@app.route("/delete/<filename>")
def delete_file(filename):
    if not session.get('logged_in'):
        flash("Please log in to delete files.")
        return redirect(url_for('upload_file'))
    try:
        container_client.delete_blob(filename)
        flash(f"Deleted '{filename}'.")
    except Exception as e:
        flash(f"Delete failed: {str(e)}")
    return redirect(url_for('upload_file'))

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == DEMO_USER and password == DEMO_PASS:
        session['logged_in'] = True
        flash("Logged in successfully!")
    else:
        flash("Invalid credentials.")
    return redirect(url_for('upload_file'))

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash("Logged out.")
    return redirect(url_for('upload_file'))

if __name__ == "__main__":
    app.run(debug=True)