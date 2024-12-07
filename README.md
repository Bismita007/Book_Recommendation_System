# Running the Project

This document provides step-by-step instructions to set up, run, and test the project based on the provided code and data files.

## Prerequisites

Ensure you have the following installed on your system:

1. **Python** (version 3.8 or higher)
2. **Docker** (optional but recommended for containerized deployment)
3. **Pip** (Python package manager)
4. Required libraries listed in `requirements.txt`

---

## Project Structure

- `static`: Static files (e.g., CSS, JavaScript).
- `templates`: HTML templates for the web application.
- `Comprehensive_Bookstore_Data_Report.pdf`: Pre-generated report document.
- `Dockerfile`: Docker configuration for containerizing the application.
- `app.py`: Entry point for the Flask web application.
- `books.csv`: Raw dataset for books.
- `cleaned_book_suppliers_data.csv`: Cleaned data for book suppliers.
- `cleaned_books_ratings_data.csv`: Cleaned data for book ratings.
- `cleaned_books_sales_data.csv`: Cleaned data for book sales.
- `cleaned_nepali_book_inventory.csv`: Cleaned Nepali book inventory data.
- `evaluation.py`: Script for model evaluation.
- `main.py`: Main application logic script.
- `merged_books_data.csv`: Merged dataset combining all cleaned data.
- `modeling.py`: Script for building and training recommendation models.
- `ratings.csv`: Raw dataset for book ratings.
- `recommendation.py`: Script for generating book recommendations.
- `report_generate.py`: Script to generate reports.
- `requirements.txt`: List of Python dependencies.
- `sales.csv`: Raw dataset for sales.
- `suppliers.csv`: Raw dataset for suppliers.

---

## Setting Up the Environment

### 1. Clone the Repository
```bash
# Clone the repository
$ git clone <repository-url>

# Navigate into the project directory
$ cd <project-directory>
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
$ python3 -m venv venv
$ source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Required Dependencies
```bash
$ pip install -r requirements.txt
```

---

## Running the Application

### 1. Using Python

Run the Flask application locally:
```bash
$ python app.py
```
The application will be available at `http://127.0.0.1:5000/`.

### 2. Using Docker

Build and run the Docker container:
```bash
# Build the Docker image
$ docker build -t bookstore-app .

# Run the Docker container
$ docker run -p 5000:5000 bookstore-app
```
The application will be accessible at `http://localhost:5000/`.

---

## Dataset Preparation

1. Ensure all raw and cleaned datasets (`books.csv`, `ratings.csv`, `suppliers.csv`, `sales.csv`, etc.) are in the root directory.
2. The `report_generate.py` script can be used to preprocess and merge data:
   ```bash
   $ python report_generate.py
   ```

---

## Testing the Application

1. To test the recommendation system, run the `recommendation.py` script:
   ```bash
   $ python recommendation.py
   ```

2. Evaluate the models using `evaluation.py`:
   ```bash
   $ python evaluation.py
   ```

---

## Generating Reports

Run the `report_generate.py` script to generate an updated version of the bookstore report:
```bash
$ python report_generate.py
```
The new report will be saved in the root directory.

---

## Additional Notes

- Logs and debugging information will be output to the console by default.
- Modify `app.py` or the associated scripts if you need to customize the application.
- Ensure you have read/write permissions for the directory when running the scripts, especially when working with data files.

---

## Troubleshooting

- **Dependency Errors:**
  Ensure all dependencies listed in `requirements.txt` are installed.

- **Port Conflicts:**
  If port 5000 is already in use, change the port in `app.py` or the Docker command:
  ```bash
  $ python app.py --port <new-port>
  ```
  ```bash
  $ docker run -p <new-port>:5000 bookstore-app
  ```

- **Data Errors:**
  Verify the format and structure of all datasets before running scripts.

---

For further assistance, refer to the project's README or contact the maintainer.

