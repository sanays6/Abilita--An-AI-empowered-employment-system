import os

base_dir = r"e:\Main projects\Interview Project Naipunnya\InterviewSystem\templates"

templates = {
    "base.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Interview System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">Interview System</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    {% if request.session.role == 'admin' %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'admin_dashboard' %}">Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'admin_logout' %}">Logout</a></li>
                    {% elif request.session.role == 'expert' %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'expert_dashboard' %}">Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'expert_logout' %}">Logout</a></li>
                    {% elif request.session.role == 'user' %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'user_dashboard' %}">Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'user_logout' %}">Logout</a></li>
                    {% else %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'user_login' %}">User Login</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'expert_login' %}">Expert Login</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'admin_login' %}">Admin Login</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>""",

    "users/login.html": """{% extends 'base.html' %}
{% block content %}
<h2>User Login</h2>
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label>Email</label>
        <input type="email" name="email" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Password</label>
        <input type="password" name="password" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Login</button>
    <a href="{% url 'user_signup' %}" class="btn btn-link">Sign Up</a>
</form>
{% endblock %}""",

    "users/signup.html": """{% extends 'base.html' %}
{% block content %}
<h2>User Sign Up</h2>
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label>Name</label>
        <input type="text" name="name" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Email</label>
        <input type="email" name="email" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Password</label>
        <input type="password" name="password" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Sign Up</button>
</form>
{% endblock %}""",

    "users/dashboard.html": """{% extends 'base.html' %}
{% block content %}
<h2>User Dashboard</h2>
<p>Welcome, {{ user.name }}!</p>
{% endblock %}""",

    "domain_expert/login.html": """{% extends 'base.html' %}
{% block content %}
<h2>Domain Expert Login</h2>
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label>Email</label>
        <input type="email" name="email" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Password</label>
        <input type="password" name="password" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Login</button>
</form>
{% endblock %}""",

    "domain_expert/dashboard.html": """{% extends 'base.html' %}
{% block content %}
<h2>Domain Expert Dashboard</h2>
<p>Welcome, {{ expert.name }} ({{ expert.domain }})</p>

<h3>Add Interview Question</h3>
<form method="post" class="mb-4">
    {% csrf_token %}
    <div class="mb-3">
        <textarea name="question_text" class="form-control" required placeholder="Enter question"></textarea>
    </div>
    <button type="submit" class="btn btn-primary">Add Question</button>
</form>

<h3>Questions</h3>
<ul class="list-group">
    {% for q in questions %}
        <li class="list-group-item">{{ q.question_text }}</li>
    {% endfor %}
</ul>
{% endblock %}""",

    "admin_panel/login.html": """{% extends 'base.html' %}
{% block content %}
<h2>Admin Login</h2>
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label>Email</label>
        <input type="email" name="email" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Password</label>
        <input type="password" name="password" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Login</button>
</form>
{% endblock %}""",

    "admin_panel/dashboard.html": """{% extends 'base.html' %}
{% block content %}
<h2>Admin Dashboard</h2>
<div class="list-group mt-4">
    <a href="{% url 'admin_list_users' %}" class="list-group-item list-group-item-action">Users Management</a>
    <a href="{% url 'admin_list_experts' %}" class="list-group-item list-group-item-action">Domain Experts</a>
    <a href="{% url 'admin_generate_aptitude' %}" class="list-group-item list-group-item-action">Generate Aptitude Questions</a>
    <a href="{% url 'admin_list_aptitude' %}" class="list-group-item list-group-item-action">View Aptitude Questions</a>
</div>
{% endblock %}""",

    "admin_panel/users_list.html": """{% extends 'base.html' %}
{% block content %}
<h2>Users List</h2>
<a href="{% url 'admin_dashboard' %}" class="btn btn-secondary mb-3">Back</a>
<table class="table">
    <tr><th>ID</th><th>Name</th><th>Email</th><th>Actions</th></tr>
    {% for usr in users %}
    <tr>
        <td>{{ usr.id }}</td>
        <td>{{ usr.name }}</td>
        <td>{{ usr.email }}</td>
        <td><a href="{% url 'admin_view_user' usr.id %}" class="btn btn-sm btn-info">View</a></td>
    </tr>
    {% endfor %}
</table>
{% endblock %}""",

    "admin_panel/user_details.html": """{% extends 'base.html' %}
{% block content %}
<h2>User Details</h2>
<a href="{% url 'admin_list_users' %}" class="btn btn-secondary mb-3">Back to Users</a>
<ul class="list-group">
    <li class="list-group-item"><strong>Name:</strong> {{ user.name }}</li>
    <li class="list-group-item"><strong>Email:</strong> {{ user.email }}</li>
    <li class="list-group-item"><strong>Selected Domain:</strong> {{ user.selected_domain }}</li>
    <li class="list-group-item"><strong>Created:</strong> {{ user.created_at }}</li>
</ul>
{% endblock %}""",

    "admin_panel/experts_list.html": """{% extends 'base.html' %}
{% block content %}
<h2>Domain Experts</h2>
<a href="{% url 'admin_dashboard' %}" class="btn btn-secondary mb-3">Back</a>
<a href="{% url 'admin_add_expert' %}" class="btn btn-success mb-3 ms-2">Add New Expert</a>
<table class="table">
    <tr><th>ID</th><th>Name</th><th>Domain</th><th>Actions</th></tr>
    {% for ex in experts %}
    <tr>
        <td>{{ ex.id }}</td>
        <td>{{ ex.name }}</td>
        <td>{{ ex.domain }}</td>
        <td>
            <a href="{% url 'admin_edit_expert' ex.id %}" class="btn btn-sm btn-warning">Edit</a>
            <a href="{% url 'admin_delete_expert' ex.id %}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?');">Delete</a>
        </td>
    </tr>
    {% endfor %}
</table>
{% endblock %}""",

    "admin_panel/add_expert.html": """{% extends 'base.html' %}
{% block content %}
<h2>Add Domain Expert</h2>
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label>Name</label><input type="text" name="name" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Email</label><input type="email" name="email" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Password</label><input type="password" name="password" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Domain</label><input type="text" name="domain" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Save</button>
    <a href="{% url 'admin_list_experts' %}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}""",

    "admin_panel/edit_expert.html": """{% extends 'base.html' %}
{% block content %}
<h2>Edit Domain Expert</h2>
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label>Name</label><input type="text" name="name" class="form-control" value="{{ expert.name }}" required>
    </div>
    <div class="mb-3">
        <label>Email</label><input type="email" name="email" class="form-control" value="{{ expert.email }}" required>
    </div>
    <div class="mb-3">
        <label>New Password (leave blank to keep current)</label><input type="password" name="password" class="form-control">
    </div>
    <div class="mb-3">
        <label>Domain</label><input type="text" name="domain" class="form-control" value="{{ expert.domain }}" required>
    </div>
    <button type="submit" class="btn btn-primary">Update</button>
    <a href="{% url 'admin_list_experts' %}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}""",

    "admin_panel/generate_aptitude.html": """{% extends 'base.html' %}
{% block content %}
<h2>Generate Aptitude Questions</h2>
<a href="{% url 'admin_dashboard' %}" class="btn btn-secondary mb-3">Back to Dashboard</a>
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        <label>Domain (e.g., Software Engineering, Python, Mathematics)</label>
        <input type="text" name="domain" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Generate 20 MCQs with AI</button>
</form>
{% endblock %}""",

    "admin_panel/list_aptitude.html": """{% extends 'base.html' %}
{% block content %}
<h2>Aptitude Questions</h2>
<a href="{% url 'admin_dashboard' %}" class="btn btn-secondary mb-3">Back to Dashboard</a>
<a href="{% url 'admin_generate_aptitude' %}" class="btn btn-success mb-3 ms-2">Generate More</a>
<table class="table">
    <tr><th>Domain</th><th>Question</th><th>Correct Answer</th></tr>
    {% for q in questions %}
    <tr>
        <td>{{ q.domain }}</td>
        <td>{{ q.question }}</td>
        <td>{{ q.correct_answer }}</td>
    </tr>
    {% endfor %}
</table>
{% endblock %}"""
}

for rel_path, content in templates.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Templates generated successfully.")
