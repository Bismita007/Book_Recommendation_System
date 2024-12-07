from threading import Thread
from flask import Flask, render_template, redirect, url_for, request, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from evaluation import evaluate_and_generate_data
from recommendation import hybrid_recommendation, books, user_item_matrix, user_similarity_df, book_similarity_df
import os
import pandas as pd
from report_generate import generate_reports
import time
from modeling import data_modeling
app = Flask(__name__)
app.secret_key = 'password'  # Replace with a strong secret key

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Mock user database
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Create a mock user
users = {'admin': User(id=1, username='admin', password='admin')}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

# Function to load datasets
def load_data():
    print("Loading datasets from CSV files...")
    sales_data = pd.read_csv('sales.csv')
    inventory_data = pd.read_csv('books.csv')
    supplier_data = pd.read_csv('suppliers.csv')
    ratings_data = pd.read_csv('ratings.csv')
    return sales_data, inventory_data, supplier_data, ratings_data

# Load all datasets at startup
sales_data, inventory_data, supplier_data, ratings_data = load_data()

# Function to analyze data issues
def analyze_data_issues(df):
    issues = {
        "Missing Values": df.isnull().sum().to_dict(),
        "Duplicate Entries": df.duplicated().sum(),
        "Sample Data": df.head(15).to_dict(orient="records")
    }
    return issues

# Function to clean data
def clean_data(df, cleaning_option):
    if cleaning_option == 'remove_duplicates':
        df = df.drop_duplicates()
    elif cleaning_option == 'fill_missing':
        df = df.fillna(df.mean(numeric_only=True))
    elif cleaning_option == 'remove_missing':
        df = df.dropna()
    return df

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)
        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    selected_data = None
    data_issues = None
    dataset_name = None
    action = None
    cleaning_option = None
    cleaned_data = None

    if request.method == 'POST':
        dataset_name = request.form['dataset']
        action = request.form['action']

        if dataset_name == 'sales':
            dataset = sales_data
        elif dataset_name == 'books':
            dataset = inventory_data
        elif dataset_name == 'suppliers':
            dataset = supplier_data
        elif dataset_name == 'ratings':
            dataset = ratings_data
        else:
            dataset = None

        if dataset is not None:
            if action == 'view_data':
                selected_data = dataset.head(10).to_dict(orient="records")
            elif action == 'view_issues':
                data_issues = analyze_data_issues(dataset)
            elif action == 'clean_data':
                cleaning_option = request.form['cleaning_option']
                cleaned_data = clean_data(dataset, cleaning_option)
                selected_data = cleaned_data.head(10).to_dict(orient="records")
    return render_template(
        "index.html",
        dataset_name=dataset_name,
        selected_data=selected_data,
        data_issues=data_issues,
        action=action,
        cleaning_option=cleaning_option
    )

@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    generate_reports()
    report_file = "Comprehensive_Bookstore_Data_Report.pdf"
    if os.path.exists(report_file):
        return send_file(report_file, as_attachment=True)
    else:
        return "Error: Report file not generated", 500

@app.route('/view_report')
@login_required
def view_report():
    report_path = os.path.join(app.root_path, 'Comprehensive_Bookstore_Data_Report.pdf')
    return send_file(report_path, as_attachment=False)

@app.route('/data_modeling')
def data_modeling_route(run_data_modeling=None):
    # Start the background thread to handle data modeling
    thread = Thread(target=data_modeling)
    thread.start()
    # Display the results after completion
    user_item_matrix_sample, books_metadata_sample = data_modeling()

    # Limit to 10 rows each
    user_item_matrix_sample = user_item_matrix_sample.head(10)
    # Limit columns to the first 10 columns for collaborative filtering table
    user_item_matrix_sample = user_item_matrix_sample.iloc[:, :15]
    books_metadata_sample = books_metadata_sample.head(10)

    # Prepare the HTML to display the results
    content_filtering_table = books_metadata_sample.to_html(classes='table table-striped table-bordered')
    collaborative_filtering_table = user_item_matrix_sample.to_html(classes='table table-striped table-bordered')

    return render_template('data_modeling.html',
                           content_filtering=content_filtering_table,
                           collaborative_filtering=collaborative_filtering_table)

@app.route('/evaluation')
def evaluation():
    evaluation_data = evaluate_and_generate_data()
    return render_template('evaluationresult.html', data=evaluation_data)

@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    if request.method == 'POST':
        input_value = request.form['input_value']
        result_count = int(request.form['result_count'])
        try:
            recommendations = hybrid_recommendation(input_value, books, user_item_matrix, user_similarity_df, book_similarity_df, top_n=result_count)
            return render_template('recommendation.html', recommendations=recommendations)
        except Exception as e:
            error = f"An error occurred: {str(e)}"
            return render_template('recommendation.html', error=error)
    return render_template('recommendation.html')
if __name__ == "__main__":
    app.run(debug=True)
