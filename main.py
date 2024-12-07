import pandas as pd
import random


# Function to load data from CSV files
def load_data():
    print("Loading datasets from CSV files...")
    sales_data = pd.read_csv('sales.csv')
    inventory_data = pd.read_csv('books.csv')
    supplier_data = pd.read_csv('suppliers.csv')
    ratings_data = pd.read_csv('ratings.csv')
    return sales_data, inventory_data, supplier_data, ratings_data


# Function to select fields from the datasets
def select_fields(sales_data, inventory_data, supplier_data):
    print("Selecting fields for Sales Records from sales.csv")
    selected_sales_data = sales_data[
        ['Transaction Date', 'Book Title', 'ISBN', 'Customer ID', 'Quantity', 'Price (NPR)']]

    print("Selecting fields for Inventory Data (from books.csv)")
    selected_inventory_data = inventory_data[
        ['Book Title', 'Author', 'ISBN', 'Genre', 'Publication Year', 'Language', 'Stock']]

    print("Selecting fields for Supplier Invoices (from suppliers.csv)")
    selected_supplier_data = supplier_data[['Order Date', 'Book Title', 'ISBN', 'Cost Price (NPR)', 'Supplier']]

    return selected_sales_data, selected_inventory_data, selected_supplier_data


# Function to display data issues
def display_data_issues(df, name, cleaned=False):
    print(f"\n--- {name} Data Issues {'(Cleaned)' if cleaned else ''} ---")
    print("Missing Values:\n", df.isnull().sum())
    print("\nDuplicate Entries:", df.duplicated().sum())
    if not cleaned:
        print("\nSample Data Before Cleaning:\n", df.head(15).to_string(index=False))
    else:
        print("\nSample Data After Cleaning:\n", df.head(15).to_string(index=False))


# Function to clean sales data
def clean_sales_data(sales_data):
    print("Started Cleaning the Sales Data")
    display_data_issues(sales_data, "Sales")

    # Fill missing Customer IDs
    missing_customer_count = sales_data['Customer ID'].isnull().sum()
    random_customer_ids = ['C' + str(random.randint(1000, 9999)) for _ in range(missing_customer_count)]
    sales_data.loc[sales_data['Customer ID'].isnull(), 'Customer ID'] = random_customer_ids

    # Standardize date format
    sales_data['Transaction Date'] = pd.to_datetime(sales_data['Transaction Date'], errors='coerce')
    sales_data['Transaction Date'].fillna(pd.Timestamp('2018-01-01'), inplace=True)
    sales_data['Transaction Date'] = sales_data['Transaction Date'].dt.strftime('%Y-%m-%d')
    sales_data.sort_values(by='Transaction Date', inplace=True)

    # Fill missing Quantity and Price
    sales_data['Quantity'].fillna(0, inplace=True)
    sales_data['Quantity'] = sales_data['Quantity'].astype(float)
    sales_data['Price (NPR)'].fillna(0, inplace=True)
    sales_data['Price (NPR)'] = sales_data['Price (NPR)'].astype(float)

    # Remove duplicates
    sales_data.drop_duplicates(subset=['Transaction Date', 'Book Title', 'ISBN', 'Quantity'], inplace=True)

    # Display cleaned data issues
    display_data_issues(sales_data, "Sales", cleaned=True)


# Function to clean supplier data
def clean_supplier_data(supplier_data):
    print("Started Cleaning the Supplier Data")
    display_data_issues(supplier_data, "Supplier")

    # Replace missing Order Dates and ISBNs
    supplier_data['Order Date'].fillna('2018-01-01', inplace=True)
    supplier_data['Order Date'] = pd.to_datetime(supplier_data['Order Date'], errors='coerce').dt.strftime('%Y-%m-%d')
    supplier_data.sort_values(by='Order Date', inplace=True)
    supplier_data['ISBN'].fillna(generate_random_isbn, inplace=True)

    # Fill missing Quantity, Cost Price, and Supplier names
    supplier_data['Quantity'].fillna(0, inplace=True)
    supplier_data['Quantity'] = supplier_data['Quantity'].astype(float)
    supplier_data['Cost Price (NPR)'].fillna(0, inplace=True)
    supplier_data['Cost Price (NPR)'] = supplier_data['Cost Price (NPR)'].astype(float)
    supplier_data['Supplier'].fillna('Unknown Supplier', inplace=True)

    # Remove duplicates
    supplier_data.drop_duplicates(subset=['Order Date', 'Book Title', 'ISBN', 'Quantity', 'Cost Price (NPR)'],
                                  inplace=True)

    # Display cleaned data issues
    display_data_issues(supplier_data, "Supplier", cleaned=True)


# Function to clean inventory data
def clean_inventory_data(inventory_data):
    print("Started Cleaning the Inventory Data")
    display_data_issues(inventory_data, "Inventory")

    # Clean the inventory data
    inventory_data.drop_duplicates(inplace=True)
    inventory_data['Author'].fillna('Unknown Author', inplace=True)
    inventory_data['Price (NPR)'].fillna(0, inplace=True)
    inventory_data['Price (NPR)'] = inventory_data['Price (NPR)'].astype(float)
    inventory_data['Reorder Point'].fillna(0, inplace=True)
    inventory_data['Reorder Point'] = inventory_data['Reorder Point'].astype(float)
    inventory_data['Stock'].fillna(0, inplace=True)

    # Handle missing ISBNs
    missing_isbn_count = inventory_data['ISBN'].isnull().sum()
    if missing_isbn_count > 0:
        random_isbns = ['978-' + str(random.randint(1000000000, 9999999999)) for _ in range(missing_isbn_count)]
        inventory_data.loc[inventory_data['ISBN'].isnull(), 'ISBN'] = random_isbns

    # Replace missing Publishers
    inventory_data['Publisher'].fillna('Unknown Publisher', inplace=True)

    # Ensure Price and Reorder Point are numeric
    inventory_data['Price (NPR)'] = inventory_data['Price (NPR)'].astype(float)
    inventory_data['Reorder Point'] = inventory_data['Reorder Point'].astype(int)

    # Display cleaned data issues
    display_data_issues(inventory_data, "Inventory", cleaned=True)

#Function to clean Ratings Data

def cleaning_ratings_data(ratings_file, output_file):

    # Ensure the 'Review Date' column is in datetime format
    ratings_data['Review Date'] = pd.to_datetime(ratings_data['Review Date'], errors='coerce')

    # Sort the DataFrame by 'Review Date'
    sorted_ratings = ratings_data.sort_values(by='Review Date')

    # Save the sorted DataFrame to a new CSV file
    sorted_ratings.to_csv(output_file, index=False)
    sorted_output_file = 'cleaned_books_ratings_data.csv'
    print(f"Sorted ratings data saved to {output_file}.")



# Function to save cleaned data
def save_cleaned_data(df, filename):
    df.to_csv(filename, index=False)
    print(f"Cleaned data saved to {filename}")


# Function to generate random ISBNs
def generate_random_isbn():
    return f"978-{random.randint(1000000000, 9999999999)}"


# Main execution block
if __name__ == "__main__":
    print("Task 3.1: Selecting Data")

    # Load data
    sales_data, inventory_data, supplier_data, ratings_data = load_data()

    # Select fields
    selected_sales_data, selected_inventory_data, selected_supplier_data = select_fields(sales_data, inventory_data,supplier_data)

    # Clean data
    clean_sales_data(sales_data)
    clean_supplier_data(supplier_data)
    clean_inventory_data(inventory_data)
    sorted_output_file = 'cleaned_books_ratings_data.csv'
    cleaning_ratings_data(ratings_data, sorted_output_file)
    # Save cleaned data
    save_cleaned_data(inventory_data, 'cleaned_nepali_book_inventory.csv')
    save_cleaned_data(sales_data, 'cleaned_books_sales_data.csv')
    save_cleaned_data(supplier_data, 'cleaned_book_suppliers_data.csv')

    # Generate reports and merge datasets
    print("Data Generation Report")
    from report_generate import generate_reports
    generate_reports()

