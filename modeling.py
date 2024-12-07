import pandas as pd
import time
from matplotlib import pyplot as plt

# Function to execute data modeling tasks
def data_modeling():
    # Load data
    ratings = pd.read_csv('cleaned_books_ratings_data.csv')
    books = pd.read_csv('cleaned_nepali_book_inventory.csv')
    sales = pd.read_csv('cleaned_books_sales_data.csv')
    suppliers = pd.read_csv('cleaned_book_suppliers_data.csv')

    # Step 1: Prepare User-Item Matrix for Collaborative Filtering
    ratings = ratings.groupby(['Customer ID', 'ISBN'], as_index=False)['Rating'].mean()
    user_item_matrix = ratings.pivot(index='Customer ID', columns='ISBN', values='Rating').fillna(0)

    # Step 2: Merge Books Metadata for Content-Based Filtering
    if 'ISBN' not in books.columns:
        raise ValueError("books.csv must contain an 'ISBN' column for merging.")
    books_metadata = books.merge(sales, on='ISBN', how='left').merge(suppliers, on='ISBN', how='left')

     # Get 20 sample rows for both collaborative and content-based data
    user_item_matrix_sample = user_item_matrix.head(10)
    books_metadata_sample = books_metadata.head(10)

    # Save the merged file to the project directory
    merged_file = books_metadata.merge(user_item_matrix, left_on='ISBN', right_index=True, how='left')
    merged_file.to_csv('merged_books_data.csv', index=False)

    # Return results for displaying
    return user_item_matrix_sample, books_metadata_sample
