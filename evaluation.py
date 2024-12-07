import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error

# Save plots directory
PLOT_DIR = "static/plots"

if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

def evaluate_and_generate_data():
    # Load datasets
    books = pd.read_csv('cleaned_nepali_book_inventory.csv')
    ratings = pd.read_csv('cleaned_books_ratings_data.csv')

    # Aggregate ratings (if duplicates exist)
    ratings = ratings.groupby(['Customer ID', 'ISBN'], as_index=False)['Rating'].mean()

    # User-Item Matrix
    user_item_matrix = ratings.pivot(index='Customer ID', columns='ISBN', values='Rating').fillna(0)

    # Train-Test Split
    train_data, test_data = train_test_split(ratings, test_size=0.2, random_state=42)

    # Cosine Similarity
    user_similarity = cosine_similarity(user_item_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

    # Predict Ratings
    def predict_ratings(user_item_matrix, similarity_matrix):
        user_mean = user_item_matrix.mean(axis=1)
        user_diff = user_item_matrix.sub(user_mean, axis=0)

        user_mean_array = user_mean.values.reshape(-1, 1)
        user_diff_array = user_diff.fillna(0).values

        similarity_matrix = similarity_matrix.values if isinstance(similarity_matrix, pd.DataFrame) else similarity_matrix

        weighted_sum = similarity_matrix.dot(user_diff_array)
        predictions = user_mean_array + weighted_sum / np.abs(similarity_matrix).sum(axis=1).reshape(-1, 1)
        predictions_df = pd.DataFrame(predictions, index=user_item_matrix.index, columns=user_item_matrix.columns)
        return predictions_df

    predicted_ratings = predict_ratings(user_item_matrix, user_similarity_df)

    # Evaluation Metrics
    test_user_item_matrix = test_data.pivot(index='Customer ID', columns='ISBN', values='Rating')

    def get_rmse(predictions, actual):
        predictions = pd.DataFrame(predictions)
        actual = pd.DataFrame(actual)

        common_indices = predictions.index.intersection(actual.index)
        common_columns = predictions.columns.intersection(actual.columns)

        if len(common_indices) == 0 or len(common_columns) == 0:
            return None

        predictions = predictions.loc[common_indices, common_columns]
        actual = actual.loc[common_indices, common_columns]

        mask = (actual != 0).any(axis=1)
        predictions = predictions[mask]
        actual = actual[mask]

        if predictions.empty or actual.empty:
            return None

        y_true = actual.values.flatten()
        y_pred = predictions.values.flatten()

        mask = ~np.isnan(y_true) & ~np.isnan(y_pred)
        y_true = y_true[mask]
        y_pred = y_pred[mask]

        return np.sqrt(mean_squared_error(y_true, y_pred))

    rmse = get_rmse(predicted_ratings, test_user_item_matrix)

    # Diagnostics
    total_ratings = len(ratings)
    unique_users = ratings['Customer ID'].nunique()
    unique_books = ratings['ISBN'].nunique()
    sparsity = 1 - (total_ratings / (unique_users * unique_books))

    # Save Graphs
    def save_graph(data, filename, title, xlabel, ylabel):
        plt.figure()
        data.plot(kind='bar', figsize=(10, 6))
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        filepath = os.path.join(PLOT_DIR, filename)
        plt.savefig(filepath)
        plt.close()
        return filepath

    # User Distribution
    user_dist = ratings.groupby('Customer ID')['Rating'].count()
    user_dist_graph = save_graph(user_dist, 'user_distribution.png', 'User Rating Distribution', 'Users', 'Number of Ratings')

    # Book Distribution
    book_dist = ratings.groupby('ISBN')['Rating'].count()
    book_dist_graph = save_graph(book_dist, 'book_distribution.png', 'Book Rating Distribution', 'Books', 'Number of Ratings')

    # Results to pass to the template
    return {
        "rmse": rmse,
        "total_ratings": total_ratings,
        "unique_users": unique_users,
        "unique_books": unique_books,
        "sparsity": sparsity,
        "user_dist_graph": user_dist_graph,
        "book_dist_graph": book_dist_graph
    }
