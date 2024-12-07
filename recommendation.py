import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Load and prepare data
def load_data():
    books = pd.read_csv('cleaned_nepali_book_inventory.csv')
    ratings = pd.read_csv('cleaned_books_ratings_data.csv')

    ratings = ratings.groupby(['Customer ID', 'ISBN'], as_index=False)['Rating'].mean()
    user_item_matrix = ratings.pivot(index='Customer ID', columns='ISBN', values='Rating').fillna(0)

    user_similarity = cosine_similarity(user_item_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

    book_features = pd.get_dummies(books[['ISBN', 'Author', 'Genre']].set_index('ISBN'))
    book_similarity = cosine_similarity(book_features)
    book_similarity_df = pd.DataFrame(book_similarity, index=book_features.index, columns=book_features.index)

    return books, user_item_matrix, user_similarity_df, book_similarity_df


# Collaborative filtering recommendation
def collaborative_filtering(customer_id, user_item_matrix, user_similarity_df, books, top_n):
    if customer_id not in user_item_matrix.index:
        return []

    user_mean = user_item_matrix.mean(axis=1)
    user_diff = user_item_matrix.sub(user_mean, axis=0).fillna(0)
    weighted_sum = user_similarity_df.dot(user_diff)
    predicted_ratings = user_mean[customer_id] + weighted_sum.loc[customer_id] / np.abs(
        user_similarity_df.loc[customer_id]).sum()

    recommended_books = predicted_ratings.sort_values(ascending=False).head(top_n).index.tolist()
    return books[books['ISBN'].isin(recommended_books)].to_dict(orient='records')


# Content-based recommendation
def content_based_filtering(isbn, book_similarity_df, books, top_n):
    if isbn not in book_similarity_df.columns:
        return []
    similar_books = book_similarity_df[isbn].sort_values(ascending=False).head(top_n + 1).index.tolist()
    similar_books.remove(isbn)
    return books[books['ISBN'].isin(similar_books)].to_dict(orient='records')


# Hybrid recommendation
def hybrid_recommendation(input_value, books, user_item_matrix, user_similarity_df, book_similarity_df, top_n):
    if input_value.startswith('C'):  # Customer ID
        collaborative_recs = collaborative_filtering(input_value, user_item_matrix, user_similarity_df, books, top_n)
        if collaborative_recs:
            content_recs = content_based_filtering(collaborative_recs[0]['ISBN'], book_similarity_df, books, top_n)
            hybrid_recs = collaborative_recs[:top_n // 2] + content_recs[:top_n - top_n // 2]
            return hybrid_recs[:top_n]
        else:
            return []
    else:  # ISBN
        content_recs = content_based_filtering(input_value, book_similarity_df, books, top_n)
        if content_recs:
            high_raters = user_item_matrix[input_value].sort_values(ascending=False).head(1).index
            if len(high_raters) > 0:
                collaborative_recs = collaborative_filtering(high_raters[0], user_item_matrix, user_similarity_df,
                                                             books, top_n)
                hybrid_recs = content_recs[:top_n // 2] + collaborative_recs[:top_n - top_n // 2]
                return hybrid_recs[:top_n]
            else:
                return content_recs[:top_n]
        else:
            return []


# Load data once
books, user_item_matrix, user_similarity_df, book_similarity_df = load_data()