"""
Chart components for the trading markets dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def create_price_history_chart(historical_data):
    """Create a price history chart from historical data"""
    if not historical_data or not historical_data.get('token_histories'):
        return None
    
    token_histories = historical_data['token_histories']
    outcome_token_map = historical_data.get('outcome_token_map', {})
    chart_data = []
    
    # Try to use outcome names if available, else fallback to token id
    for outcome_name, token_id in outcome_token_map.items():
        data = token_histories.get(token_id, [])
        for point in data:
            if 't' in point and 'p' in point:
                timestamp = point['t']
                # Handle different timestamp formats (seconds vs milliseconds)
                if timestamp > 1e12:  # If timestamp is in milliseconds
                    timestamp = timestamp / 1000  # Convert to seconds
                
                chart_data.append({
                    'time': datetime.fromtimestamp(timestamp),
                    'price': float(point['p']),
                    'outcome': outcome_name.capitalize()
                })
    
    # If no outcome map, fallback to token ids as outcome labels
    if not chart_data:
        for token_id, data in token_histories.items():
            for point in (data or []):
                if 't' in point and 'p' in point:
                    timestamp = point['t']
                    # Handle different timestamp formats (seconds vs milliseconds)
                    if timestamp > 1e12:  # If timestamp is in milliseconds
                        timestamp = timestamp / 1000  # Convert to seconds
                    
                    chart_data.append({
                        'time': datetime.fromtimestamp(timestamp),
                        'price': float(point['p']),
                        'outcome': str(token_id)
                    })
    
    if not chart_data:
        return None
    
    df = pd.DataFrame(chart_data)
    df['time'] = pd.to_datetime(df['time'])
    fig = go.Figure()
    color_map = {'Yes': '#10B981', 'No': '#EF4444'}
    
    for outcome in df['outcome'].unique():
        outcome_data = df[df['outcome'] == outcome].sort_values('time')
        fig.add_trace(go.Scatter(
            x=outcome_data['time'].dt.strftime('%Y-%m-%d %H:%M:%S'),
            y=outcome_data['price'],
            mode='lines',
            name=outcome,
            line=dict(
                color=color_map.get(outcome, '#8B5CF6'),
                width=2.5
            )
        ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=10, t=30, b=40),
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.15, 
            xanchor="center", 
            x=0.5,
            bgcolor="rgba(0,0,0,0.8)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
            font=dict(size=10)
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FAFAFA', size=10),
        title=dict(
            text="7-Day Price History",
            font=dict(size=11, color='#FAFAFA'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)',
            title=dict(text="", font=dict(size=9)),
            tickangle=0,
            nticks=4,
            tickformat='%m/%d',
            tickfont=dict(size=8)
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)',
            title=dict(text="Price", font=dict(size=9)),
            tickformat='.2f',
            tickfont=dict(size=8)
        )
    )
    
    return fig


def create_volume_chart(top_markets):
    """Create a volume comparison chart for different markets and platforms"""
    # Log for debugging
    print(f"Creating volume chart with {len(top_markets)} markets")
    
    # Format question string to be more readable in tooltip
    def format_question(q, max_len=40):
        if not q:
            return "Unknown"
        return (q[:max_len] + '...') if len(q) > max_len else q
    
    # Create DataFrame with market data
    market_data = [
        {
            'Market': f"#{i+1}",
            'Volume': market.get('volume_24hr', 0),
            'Platform': market.get('platform', 'Unknown'),
            'Question': format_question(market.get('question')),
            'Full Question': market.get('question', 'Unknown'),
            'Market ID': market.get('id', 'unknown')
        }
        for i, market in enumerate(top_markets)
    ]
    
    # Debug print
    print(f"Market data for chart: {market_data[:2]}")
    
    df = pd.DataFrame(market_data)
    
    # Ensure we have data to display
    if df.empty or df['Volume'].sum() == 0:
        # Create empty figure with message if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No volume data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#FAFAFA")
        )
        return fig
    
    # Create hover template with formatted volume
    hovertemplate = '<b>%{customdata[0]}</b><br>Volume: $%{y:,.0f}<br>Platform: %{customdata[1]}<br>Market ID: %{customdata[2]}'
    
    # Create the figure with separate bars for each platform
    fig = go.Figure()
    
    # Color map for different platforms
    color_map = {
        'Polymarket': '#8B5CF6',  # Purple
        'Kalshi': '#06B6D4',      # Blue
        'Unknown': '#64748B'      # Gray
    }
    
    # Add bars for each platform
    for platform in df['Platform'].unique():
        platform_df = df[df['Platform'] == platform].sort_values('Volume', ascending=False)
        
        fig.add_trace(go.Bar(
            x=platform_df['Market'],
            y=platform_df['Volume'],
            name=platform,
            marker_color=color_map.get(platform, '#64748B'),
            customdata=list(zip(
                platform_df['Full Question'], 
                platform_df['Platform'],
                platform_df['Market ID']
            )),
            hovertemplate=hovertemplate
        ))
    
    # Update layout for better appearance
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=20, t=40, b=60),
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="center", 
            x=0.5,
            bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            font=dict(size=11)
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FAFAFA', size=11),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)',
            title=dict(text="Market Rank", font=dict(size=11)),
            categoryorder='array',
            categoryarray=sorted(df['Market'].unique(), key=lambda x: int(x[1:]))
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)',
            title=dict(text="Volume ($)", font=dict(size=11)),
            tickformat='$,.0f'
        ),
        barmode='group',  # Group bars by market
        bargap=0.15,      # Gap between bars
        bargroupgap=0.1   # Gap between bar groups
    )
    
    # Add data labels on top of the bars for better readability
    for trace in fig.data:
        y_data = trace.y
        x_data = trace.x
        
        for i, (x, y) in enumerate(zip(x_data, y_data)):
            if y > 0:  # Only add annotation if there's actual volume
                fig.add_annotation(
                    x=x,
                    y=y,
                    text=f"${y:,.0f}" if y >= 1000 else f"${y:.0f}",
                    showarrow=False,
                    yshift=10,
                    font=dict(size=9)
                )
    
    return fig


def create_order_book_chart(order_book_data):
    """Create an order book chart showing bids and asks"""
    if not order_book_data or not order_book_data.get('order_books'):
        return None
    
    order_books = order_book_data['order_books']
    
    # Create subplots for each outcome
    from plotly.subplots import make_subplots
    
    num_outcomes = len(order_books)
    if num_outcomes == 0:
        return None
    
    # Standardize outcome names to handle different formats
    # Convert keys to title case for consistent display
    standardized_books = {}
    for outcome, data in order_books.items():
        # Handle different outcome name formats
        std_outcome = outcome
        if isinstance(outcome, str):
            # Convert to title case but preserve common formats
            if outcome.lower() in ["yes", "no", "true", "false"]:
                std_outcome = outcome.title()
            elif "yes" in outcome.lower():
                std_outcome = "Yes"
            elif "no" in outcome.lower():
                std_outcome = "No"
        
        standardized_books[std_outcome] = data
    
    order_books = standardized_books
    
    # For better formatting, keep only Yes and No outcomes if they exist
    if "Yes" in order_books and "No" in order_books:
        filtered_books = {"Yes": order_books["Yes"], "No": order_books["No"]}
        order_books = filtered_books
    
    # Create subplot titles with better formatting
    subplot_titles = []  # We'll use annotations inside the chart instead
    
    # Set up subplots with proper spacing for Yes/No layout
    fig = make_subplots(
        rows=num_outcomes, 
        cols=1,
        vertical_spacing=0.15,
        subplot_titles=None  # No titles, we'll add annotations inside
    )
    
    for idx, (outcome, book_data) in enumerate(order_books.items(), 1):
        bids = book_data.get('bids', [])
        asks = book_data.get('asks', [])
        
        # Process bids (buy orders) - cumulative from highest price down
        bid_prices = []
        bid_sizes = []
        cumulative_bid_size = 0
        
        # Handle different data formats between platforms
        try:
            # Check if this is Kalshi format (list of [price, size]) or Polymarket format (dict)
            if bids and isinstance(bids[0], list):
                # Kalshi format: [[price_str, size_str], ...]
                bid_tuples = []
                for bid in bids:
                    if len(bid) >= 2:
                        try:
                            price = float(bid[0])
                            size = float(bid[1])
                            bid_tuples.append((price, size))
                        except (ValueError, TypeError):
                            continue
                # Sort by price descending (highest first)
                sorted_bids = sorted(bid_tuples, key=lambda x: x[0], reverse=True)
                
                for price, size in sorted_bids:
                    cumulative_bid_size += size
                    bid_prices.append(price)
                    bid_sizes.append(cumulative_bid_size)
                    
            else:
                # Polymarket format: [{'price': ..., 'size': ...}, ...]
                sorted_bids = sorted(bids, key=lambda x: float(x['price']), reverse=True)
                
                for bid in sorted_bids:
                    price = float(bid['price'])
                    size = float(bid['size'])
                    cumulative_bid_size += size
                    bid_prices.append(price)
                    bid_sizes.append(cumulative_bid_size)
                    
        except (KeyError, ValueError, IndexError) as e:
            print(f"Error processing bids for {outcome}: {e}")
            continue
        
        # Process asks (sell orders) - cumulative from lowest price up
        ask_prices = []
        ask_sizes = []
        cumulative_ask_size = 0
        
        # Handle different data formats between platforms
        try:
            # Check if this is Kalshi format (list of [price, size]) or Polymarket format (dict)
            if asks and isinstance(asks[0], list):
                # Kalshi format: [[price_str, size_str], ...]
                ask_tuples = []
                for ask in asks:
                    if len(ask) >= 2:
                        try:
                            price = float(ask[0])
                            size = float(ask[1])
                            ask_tuples.append((price, size))
                        except (ValueError, TypeError):
                            continue
                # Sort by price ascending (lowest first)
                sorted_asks = sorted(ask_tuples, key=lambda x: x[0])
                
                for price, size in sorted_asks:
                    cumulative_ask_size += size
                    ask_prices.append(price)
                    ask_sizes.append(cumulative_ask_size)
                    
            else:
                # Polymarket format: [{'price': ..., 'size': ...}, ...]
                sorted_asks = sorted(asks, key=lambda x: float(x['price']))
                
                for ask in sorted_asks:
                    price = float(ask['price'])
                    size = float(ask['size'])
                    cumulative_ask_size += size
                    ask_prices.append(price)
                    ask_sizes.append(cumulative_ask_size)
                    
        except (KeyError, ValueError, IndexError) as e:
            print(f"Error processing asks for {outcome}: {e}")
            continue
        
        # Add bid side (green, left side)
        if bid_prices and bid_sizes:
            fig.add_trace(
                go.Scatter(
                    x=bid_prices,
                    y=bid_sizes,
                    mode='lines',
                    fill='tozeroy',
                    name=f'{outcome} Bids',
                    line=dict(color='#10B981', width=2),
                    fillcolor='rgba(16, 185, 129, 0.5)',
                    hovertemplate='<b>Price:</b> $%{x:.3f}<br><b>Cumulative Size:</b> %{y:,.0f}<extra></extra>',
                    showlegend=False
                ),
                row=idx, col=1
            )
        
        # Add ask side (red, right side)
        if ask_prices and ask_sizes:
            fig.add_trace(
                go.Scatter(
                    x=ask_prices,
                    y=ask_sizes,
                    mode='lines',
                    fill='tozeroy',
                    name=f'{outcome} Asks',
                    line=dict(color='#EF4444', width=2),
                    fillcolor='rgba(239, 68, 68, 0.5)',
                    hovertemplate='<b>Price:</b> $%{x:.3f}<br><b>Cumulative Size:</b> %{y:,.0f}<extra></extra>',
                    showlegend=False
                ),
                row=idx, col=1
            )
        
        # Add outcome label in the center of the plot (exactly as in screenshot)
        fig.add_annotation(
            text=f"{outcome} Order Book",
            xref=f"x{idx}", yref=f"y{idx}",
            x=0.5, y=0.5,  # Position in the middle of the plot
            showarrow=False,
            font=dict(size=16, color="#FFFFFF", family="Arial, sans-serif"),
            xanchor="center",
            yanchor="middle",
            bgcolor="rgba(0,0,0,0.4)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
            borderpad=4,
            opacity=0.8,
            row=idx, col=1
        )
        
        # Update subplot axes with improved styling matching the screenshot
        fig.update_xaxes(
            title_text="Price ($)" if idx == num_outcomes else None,
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)',
            tickformat='.3f',
            tickfont=dict(size=10, color="#FFFFFF"),
            range=[0, 1],  # Polymarket prices are between 0 and 1
            title_font=dict(size=12, color="#FFFFFF"),
            row=idx, col=1
        )
        
        fig.update_yaxes(
            title_text="Cumulative Size",
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)',
            tickformat=',.0f',
            tickfont=dict(size=10, color="#FFFFFF"),
            title_font=dict(size=12, color="#FFFFFF"),
            row=idx, col=1
        )
        
        # Remove the bottom label since we already have labels in the center
    
    # Update overall layout with improved styling to match the screenshot
    height = max(400, num_outcomes * 350)  # More height per plot for better readability
    
    # Create legend items for the legend at the top - matching the screenshot exactly
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='lines',
            name='Yes Bids',
            line=dict(color='#10B981', width=2),
            showlegend=True
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='lines',
            name='Yes Asks', 
            line=dict(color='#EF4444', width=2),
            showlegend=True
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='lines',
            name='No Bids',
            line=dict(color='#10B981', width=2),
            showlegend=True
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='lines',
            name='No Asks',
            line=dict(color='#EF4444', width=2),
            showlegend=True
        )
    )
    
    fig.update_layout(
        height=height,
        margin=dict(l=60, r=20, t=40, b=60),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.0,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0)",
            borderwidth=0,
            font=dict(size=10, color="#FFFFFF")
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', size=11),
        title=dict(
            text="Order Book - Liquidity Distribution",
            font=dict(size=14, color='#FFFFFF'),
            x=0.5,
            y=0.98,
            xanchor='center',
            yanchor='top'
        ),
        template="plotly_dark"
    )
    
    return fig
