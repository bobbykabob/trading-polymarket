"""
Test script for the improved order book chart UI
"""

import sys
import os
# Add project to path
sys.path.append(os.path.dirname(__file__))

from frontend.charts import create_order_book_chart
import plotly.io as pio

def test_order_book_chart_ui():
    # Create realistic sample order book data
    sample_order_book_data = {
        'market_id': 'market1',
        'order_books': {
            'Yes': {
                'token_id': 'token1',
                'bids': [
                    {'price': '0.98', 'size': '100000'},
                    {'price': '0.95', 'size': '200000'},
                    {'price': '0.90', 'size': '350000'},
                    {'price': '0.85', 'size': '400000'},
                    {'price': '0.80', 'size': '500000'},
                    {'price': '0.70', 'size': '600000'},
                    {'price': '0.65', 'size': '700000'},
                    {'price': '0.60', 'size': '800000'},
                    {'price': '0.50', 'size': '1000000'},
                ],
                'asks': [
                    {'price': '0.99', 'size': '120000'},
                    {'price': '0.997', 'size': '180000'},
                    {'price': '0.999', 'size': '250000'},
                    {'price': '0.9999', 'size': '450000'},
                ]
            },
            'No': {
                'token_id': 'token2',
                'bids': [
                    {'price': '0.35', 'size': '120000'},
                    {'price': '0.30', 'size': '180000'},
                    {'price': '0.25', 'size': '250000'},
                    {'price': '0.20', 'size': '300000'},
                    {'price': '0.15', 'size': '450000'},
                    {'price': '0.10', 'size': '550000'},
                    {'price': '0.05', 'size': '650000'},
                    {'price': '0.01', 'size': '900000'},
                ],
                'asks': [
                    {'price': '0.37', 'size': '100000'},
                    {'price': '0.40', 'size': '200000'},
                    {'price': '0.45', 'size': '350000'},
                    {'price': '0.50', 'size': '450000'},
                    {'price': '0.55', 'size': '550000'},
                    {'price': '0.60', 'size': '700000'},
                ]
            }
        }
    }
    
    print("Creating order book chart with UI improvements...")
    
    # Try to create chart
    chart = create_order_book_chart(sample_order_book_data)
    
    # Output chart details
    print(f"Chart created: {chart is not None}")
    if chart:
        print(f"Chart type: {type(chart)}")
        print(f"Chart data traces: {len(chart.data)}")
        print(f"Chart height: {chart.layout.height}")
        
        # Save to HTML file for inspection
        try:
            pio.write_html(chart, file="test_order_book_ui.html", auto_open=False)
            print("Chart saved to test_order_book_ui.html for inspection")
        except Exception as e:
            print(f"Could not save chart: {e}")
    
    return chart is not None

if __name__ == "__main__":
    print("Testing order book chart UI improvements...")
    success = test_order_book_chart_ui()
    print(f"Test completed: {'SUCCESS' if success else 'FAILED'}")
