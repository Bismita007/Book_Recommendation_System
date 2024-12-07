import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
from datetime import datetime


def generate_reports():
    # Load datasets
    suppliers_data = pd.read_csv("cleaned_book_suppliers_data.csv")
    sales_data = pd.read_csv("cleaned_books_sales_data.csv")
    inventory_data = pd.read_csv("cleaned_nepali_book_inventory.csv")
    ratings_data = pd.read_csv("ratings.csv")

    # Merge sales_data with inventory_data to include Genre
    sales_data = sales_data.merge(inventory_data[['Book Title', 'Genre']], on="Book Title", how="left")

    # Convert Transaction Date to datetime
    sales_data['Transaction Date'] = pd.to_datetime(sales_data['Transaction Date'])

    # Create output folder for charts
    if not os.path.exists("charts"):
        os.makedirs("charts")

    # Calculate revenue
    sales_data['Revenue'] = sales_data['Quantity'] * sales_data['Price (NPR)']

    # 1. Book Popularity Score
    book_popularity = sales_data.groupby('Book Title')['Quantity'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    book_popularity.plot(kind='bar', color='skyblue')
    plt.title("Top 10 Books by Popularity Score")
    plt.xlabel("Book Title")
    plt.ylabel("Total Quantity Sold")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("charts/book_popularity.png")
    plt.close()

    # 2. Customer Purchase Frequency
    customer_frequency = sales_data.groupby('Customer ID')['Quantity'].sum()
    customer_classification = pd.cut(customer_frequency,
                                     bins=[0, 5, 15, float('inf')],
                                     labels=['occasional', 'regular', 'frequent'])
    classification_counts = customer_classification.value_counts()
    plt.figure(figsize=(6, 6))
    classification_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140,
                               colors=['lightgreen', 'lightblue', 'salmon'])
    plt.title("Customer Purchase Frequency Classification")
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig("charts/customer_frequency.png")
    plt.close()

    # 3. Seasonal Sales Trends
    seasonal_trends = sales_data.groupby(sales_data['Transaction Date'].dt.month)['Quantity'].sum()
    plt.figure(figsize=(8, 5))
    seasonal_trends.plot(kind='line', marker='o', color='purple')
    plt.title("Seasonal Sales Trends")
    plt.xlabel("Month")
    plt.ylabel("Total Quantity Sold")
    plt.xticks(range(1, 13))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("charts/seasonal_trends.png")
    plt.close()

    # 4. Genre Performance Summary
    genre_sales = sales_data.groupby('Genre')['Revenue'].sum()
    plt.figure(figsize=(10, 6))
    genre_sales.plot(kind='bar', color='coral')
    plt.title("Total Revenue by Genre")
    plt.xlabel("Genre")
    plt.ylabel("Revenue (NPR)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("charts/genre_sales.png")
    plt.close()

    # 5. Monthly Report (Detailed)
    monthly_sales = sales_data.groupby(sales_data['Transaction Date'].dt.to_period('M')).agg({
        'Revenue': 'sum',
        'Quantity': 'sum',
        'Book Title': lambda x: x.value_counts().index[0]  # Most sold book
    }).reset_index()
    monthly_sales['Transaction Date'] = monthly_sales['Transaction Date'].dt.to_timestamp()

    fig, ax1 = plt.subplots(figsize=(15, 8))
    ax2 = ax1.twinx()

    ax1.bar(monthly_sales['Transaction Date'], monthly_sales['Revenue'], color='blue', alpha=0.7, label='Revenue')
    ax2.plot(monthly_sales['Transaction Date'], monthly_sales['Quantity'], color='red', label='Quantity')

    ax1.set_xlabel('Month')
    ax1.set_ylabel('Revenue (NPR)', color='blue')
    ax2.set_ylabel('Quantity Sold', color='red')

    plt.title('Monthly Sales Report')
    fig.legend(loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

    plt.tight_layout()
    plt.savefig("charts/monthly_sales_detailed.png")
    plt.close()

    # 6. Yearly Report (Detailed)
    yearly_sales = sales_data.groupby(sales_data['Transaction Date'].dt.year).agg({
        'Revenue': 'sum',
        'Quantity': 'sum',
        'Book Title': lambda x: x.value_counts().index[0]  # Most sold book
    }).reset_index()

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    ax1.bar(yearly_sales['Transaction Date'], yearly_sales['Revenue'], color='green', alpha=0.7, label='Revenue')
    ax2.plot(yearly_sales['Transaction Date'], yearly_sales['Quantity'], color='orange', label='Quantity')

    ax1.set_xlabel('Year')
    ax1.set_ylabel('Revenue (NPR)', color='green')
    ax2.set_ylabel('Quantity Sold', color='orange')

    plt.title('Yearly Sales Report')
    fig.legend(loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)

    plt.tight_layout()
    plt.savefig("charts/yearly_sales_detailed.png")
    plt.close()

    # 7. Monthly Top Sold Book Report
    monthly_top_books = sales_data.groupby(sales_data['Transaction Date'].dt.to_period('M')).apply(
        lambda x: x.loc[x['Quantity'].idxmax()]
    )[['Transaction Date', 'Book Title', 'Quantity']].reset_index(drop=True)
    monthly_top_books['Transaction Date'] = pd.to_datetime(monthly_top_books['Transaction Date'], errors='coerce')

    plt.figure(figsize=(15, 8))
    plt.bar(monthly_top_books['Transaction Date'], monthly_top_books['Quantity'], color='purple')
    plt.title("Monthly Top Sold Book")
    plt.xlabel("Month")
    plt.ylabel("Quantity Sold")
    plt.xticks(rotation=45, ha="right")
    for i, row in monthly_top_books.iterrows():
        plt.text(row['Transaction Date'], row['Quantity'], row['Book Title'],
                 ha='center', va='bottom', rotation=90, fontsize=8)
    plt.tight_layout()
    plt.savefig("charts/monthly_top_book.png")
    plt.close()

    # 8. Yearly Top Sold Book
    yearly_top_books = sales_data.groupby(sales_data['Transaction Date'].dt.year).apply(
        lambda x: x.loc[x['Quantity'].idxmax()]
    )[['Transaction Date', 'Book Title', 'Quantity']].reset_index(drop=True)

    plt.figure(figsize=(12, 6))
    plt.bar(yearly_top_books['Transaction Date'], yearly_top_books['Quantity'], color='blue')
    plt.title("Yearly Top Sold Book")
    plt.xlabel("Year")
    plt.ylabel("Quantity Sold")
    for i, row in yearly_top_books.iterrows():
        plt.text(row['Transaction Date'], row['Quantity'], row['Book Title'],
                 ha='center', va='bottom', rotation=90, fontsize=10)
    plt.tight_layout()
    plt.savefig("charts/yearly_top_book.png")
    plt.close()

    # 9. Top Rated Books
    top_rated_books = ratings_data.groupby('Book Title')['Rating'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    top_rated_books.plot(kind='bar', color='gold')
    plt.title("Top 10 Rated Books")
    plt.xlabel("Book Title")
    plt.ylabel("Average Rating")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("charts/top_rated_books.png")
    plt.close()

    # 10. Overall Top Sold Book Report
    overall_top_books = sales_data.groupby('Book Title')['Quantity'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    overall_top_books.plot(kind='bar', color='red')
    plt.title("Overall Top 10 Sold Books")
    plt.xlabel("Book Title")
    plt.ylabel("Total Quantity Sold")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("charts/overall_top_books.png")
    plt.close()

    # 11. Highest Purchased Books Report (by Revenue)
    highest_revenue_books = sales_data.groupby('Book Title')['Revenue'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    highest_revenue_books.plot(kind='bar', color='cyan')
    plt.title("Top 10 Books by Revenue")
    plt.xlabel("Book Title")
    plt.ylabel("Total Revenue (NPR)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("charts/highest_revenue_books.png")
    plt.close()

    # 12. Highest Sold Genre
    genre_quantity = sales_data.groupby('Genre')['Quantity'].sum().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    genre_quantity.plot(kind='bar', color='magenta')
    plt.title("Genres by Total Quantity Sold")
    plt.xlabel("Genre")
    plt.ylabel("Total Quantity Sold")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("charts/highest_sold_genre.png")
    plt.close()

    # Generate PDF Report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Comprehensive Bookstore Data Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")

    # Monthly Report
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Monthly Sales Report", ln=True)
    pdf.image("charts/monthly_sales_detailed.png", x=10, w=190)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, "Monthly Details:", ln=True)
    for _, row in monthly_sales.iterrows():
        pdf.cell(0, 10, f"{row['Transaction Date'].strftime('%Y-%m')}: Revenue: {row['Revenue']:.2f} NPR, "
                        f"Quantity: {row['Quantity']}, Top Book: {row['Book Title']}", ln=True)

    # Yearly Report
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Yearly Sales Report", ln=True)
    pdf.image("charts/yearly_sales_detailed.png", x=10, w=190)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, "Yearly Details:", ln=True)
    for _, row in yearly_sales.iterrows():
        pdf.cell(0, 10, f"{int(row['Transaction Date'])}: Revenue: {row['Revenue']:.2f} NPR, "
                        f"Quantity: {row['Quantity']}, Top Book: {row['Book Title']}", ln=True)

    # Monthly Top Sold Book
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Monthly Top Sold Book", ln=True)
    pdf.image("charts/monthly_top_book.png", x=10, w=190)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, "Monthly Top Books:", ln=True)
    for _, row in monthly_top_books.iterrows():
        pdf.cell(0, 10, f"{row['Transaction Date'].strftime('%Y-%m')}: {row['Book Title']} "
                        f"(Quantity: {row['Quantity']})", ln=True)

    # Yearly Top Sold Book
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Yearly Top Sold Book", ln=True)
    pdf.image("charts/yearly_top_book.png", x=10, w=190)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, "Yearly Top Books:", ln=True)
    for _, row in yearly_top_books.iterrows():
        pdf.cell(0, 10, f"{row['Transaction Date'].strftime('%Y')}: {row['Book Title']} "
                        f"(Quantity: {row['Quantity']})", ln=True)

    # Other reports
    reports = [
        ("Book Popularity Score", "book_popularity.png"),
        ("Customer Purchase Frequency", "customer_frequency.png"),
        ("Seasonal Sales Trends", "seasonal_trends.png"),
        ("Genre Performance Summary", "genre_sales.png"),
        ("Top Rated Books", "top_rated_books.png"),
        ("Overall Top Sold Books", "overall_top_books.png"),
        ("Highest Revenue Books", "highest_revenue_books.png"),
        ("Highest Sold Genre", "highest_sold_genre.png")
    ]

    for title, image in reports:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.image(f"charts/{image}", x=10, w=190)

    # Save the PDF
    pdf.output("Comprehensive_Bookstore_Data_Report.pdf")

    # Cleanup the generated charts
    for file in os.listdir("charts"):
        os.remove(os.path.join("charts", file))
    os.rmdir("charts")

    print("Comprehensive PDF report generated successfully as 'Comprehensive_Bookstore_Data_Report.pdf'.")
    print("##########################################################################################################")
    print("Data Integraton and Formatting Starts from here")
    print("##########################################################################################################")


# Call the function to generate reports
generate_reports()