import matplotlib.pyplot as plt
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import Expense
import base64
import io
from scipy.ndimage import gaussian_filter
import numpy as np

def generate_plot(engine, annotate=True):
    # Define your SQLAlchemy classes and create a database connection
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()


    # Get all expenses ordered by date
    expenses = session.query(Expense).order_by(Expense.date).all()

    # Calculate daily account balance changes
    dates = [expense.date for expense in expenses]
    # Reformat to DD.MM.YYYY
    dates = [date.strftime('%d.%m.%Y') for date in dates]
    # Remove the year
    dates = [date[:-5] for date in dates]
    prices = [-expense.price //100 for expense in expenses]
    balance_changes = [sum(prices[:i+1]) for i in range(len(prices))]
    usages = [expense.usage for expense in expenses]
    
    y_smooth = gaussian_filter(balance_changes, sigma=1)
    # Create a graph
    plt.figure(figsize=(10, 6))
    plt.step(dates, y_smooth, where='pre', marker='o', linestyle='-', label='Account Balance Change (€)')
    plt.xlabel('Date')
    plt.ylabel('Account Balance Change (€)')
    plt.title('Account Balance Change Over Time')
    plt.grid(True)

    # Customize the appearance
    plt.tight_layout()


    if annotate:
        # Add labels for usage
        for i, usage in enumerate(usages):
            plt.annotate(usage, (dates[i], balance_changes[i]), fontsize=8, ha='left', va='bottom', rotation=20)


    # Save the plot as a PNG image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Encode the image to base64
    img_base64 = base64.b64encode(buffer.read()).decode()
    buffer.close()

    return img_base64, sum(prices)

