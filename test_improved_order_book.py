"""
Test script for the improved order book chart functionality
Handles various outcome types
"""

import sys
import os
# Add project to path
sys.path.append(os.path.dirname(__file__))

from frontend.charts import create_order_book_chart
import plotly.io as pio

def test_improved_order_book_chart():
    # Create sample order book data with various outcome names
    sample_order_book_data = {
        'market_id': 'market1',
        'order_books': {
            'Yes': {
                'token_id': 'token1',
                'bids': [
                    {'price': '0.65', 'size': '100'},
                    {'price': '0.64', 'size': '200'},
                    {'price': '0.62', 'size': '150'},
                    {'price': '0.60', 'size': '300'},
                ],
                'asks': [
                    {'price': '0.67', 'size': '120'},
                    {'price': '0.68', 'size': '180'},
                    {'price': '0.70', 'size': '250'},
                    {'price': '0.72', 'size': '200'},
                ]
            },
            'No': {
                'token_id': 'token2',
                'bids': [
                    {'price': '0.35', 'size': '120'},
                    {'price': '0.34', 'size': '180'},
                    {'price': '0.32', 'size': '150'},
                    {'price': '0.30', 'size': '300'},
                ],
                'asks': [
                    {'price': '0.37', 'size': '100'},
                    {'price': '0.38', 'size': '200'},
                    {'price': '0.40', 'size': '250'},
                    {'price': '0.42', 'size': '220'},
                ]
            },
            # Add an outcome with a different format
            'outcome_3': {
                'token_id': 'token3',
                'bids': [
                    {'price': '0.55', 'size': '150'},
                    {'price': '0.50', 'size': '250'},
                ],
                'asks': [
                    {'price': '0.60', 'size': '180'},
                    {'price': '0.65', 'size': '220'},
                ]
            }
        }
    }
    
    print("Creating improved order book chart with various outcome types...")
    
    # Try to create chart
    chart = create_order_book_chart(sample_order_book_data)
    
    # Output chart details
    print(f"Chart created: {chart is not None}")
    if chart:
        print(f"Chart type: {type(chart)}")
        print(f"Chart data: {len(chart.data)} traces")
        
        # Save to HTML file for inspection
        try:
            pio.write_html(chart, file="test_improved_order_book.html", auto_open=False)
            print("Chart saved to test_improved_order_book.html for inspection")
        except Exception as e:
            print(f"Could not save chart: {e}")
    
    return chart is not None

if __name__ == "__main__":
    print("Testing improved order book chart...")
    success = test_improved_order_book_chart()
    print(f"Test completed: {'SUCCESS' if success else 'FAILED'}")
