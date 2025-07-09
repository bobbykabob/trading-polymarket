"""
Arbitrage opportunities dashboard page
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the backend components
try:
    from backend.core.monitor import monitor, alert_manager
    from backend.core.config import config
    from backend.data.database import DatabaseManager
    BACKEND_AVAILABLE = True
except ImportError as e:
    st.error(f"Backend modules not available: {e}")
    BACKEND_AVAILABLE = False


def render_arbitrage_dashboard():
    """Main arbitrage dashboard page"""
    st.title("🔄 Arbitrage Opportunities Dashboard")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend system not available. Please check your configuration and dependencies.")
        return
    
    # Control panel
    render_control_panel()
    
    # Monitoring status
    render_monitoring_status()
    
    # Market correlations/similarities (NEW)
    render_market_correlations()
    
    # Current opportunities
    render_current_opportunities()
    
    # Performance metrics
    render_performance_metrics()
    
    # Historical data
    render_historical_analysis()


def render_control_panel():
    """Render the control panel for monitoring"""
    st.subheader("🎛️ Control Panel")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚀 Start Monitoring", type="primary"):
            monitor.start_monitoring()
            st.success("Monitoring started!")
    
    with col2:
        if st.button("⏹️ Stop Monitoring"):
            monitor.stop_monitoring()
            st.info("Monitoring stopped")
    
    with col3:
        if st.button("🔄 Force Update"):
            with st.spinner("Running immediate scan..."):
                opportunities = monitor.force_update()
                st.success(f"Found {len(opportunities)} opportunities")
    
    with col4:
        if st.button("🧹 Cleanup Data"):
            monitor.cleanup_old_data()
            st.info("Old data cleaned up")
    
    # Configuration settings
    with st.expander("⚙️ Configuration Settings"):
        render_config_settings()


def render_config_settings():
    """Render configuration settings"""
    st.subheader("Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Arbitrage Settings**")
        
        min_profit = st.slider(
            "Minimum Profit Threshold (%)",
            min_value=1.0,
            max_value=20.0,
            value=config.get("arbitrage.min_profit_threshold", 0.05) * 100,
            step=0.5
        )
        
        max_position = st.number_input(
            "Maximum Position Size ($)",
            min_value=100,
            max_value=10000,
            value=config.get("arbitrage.max_position_size", 1000),
            step=100
        )
        
        slippage_buffer = st.slider(
            "Slippage Buffer (%)",
            min_value=0.5,
            max_value=5.0,
            value=config.get("arbitrage.slippage_buffer", 0.02) * 100,
            step=0.1
        )
    
    with col2:
        st.write("**Monitoring Settings**")
        
        update_interval = st.slider(
            "Update Interval (seconds)",
            min_value=15,
            max_value=300,
            value=config.get("monitoring.update_interval", 30),
            step=5
        )
        
        batch_size = st.slider(
            "Batch Size",
            min_value=5,
            max_value=50,
            value=config.get("monitoring.batch_size", 20),
            step=5
        )
        
        min_alert_profit = st.slider(
            "Minimum Alert Profit (%)",
            min_value=5.0,
            max_value=50.0,
            value=config.get("alerts.min_profit_for_alert", 0.1) * 100,
            step=1.0
        )
    
    if st.button("💾 Save Configuration"):
        # Update configuration
        config.update_config("arbitrage.min_profit_threshold", min_profit / 100)
        config.update_config("arbitrage.max_position_size", max_position)
        config.update_config("arbitrage.slippage_buffer", slippage_buffer / 100)
        config.update_config("monitoring.update_interval", update_interval)
        config.update_config("monitoring.batch_size", batch_size)
        config.update_config("alerts.min_profit_for_alert", min_alert_profit / 100)
        
        # Update monitor configuration
        monitor.update_config({
            "update_interval": update_interval,
            "batch_size": batch_size
        })
        
        st.success("Configuration updated!")


def render_monitoring_status():
    """Render monitoring status information"""
    st.subheader("📊 Monitoring Status")
    
    status = monitor.get_monitoring_status()
    
    # Status metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        status_color = "🟢" if status["is_running"] else "🔴"
        st.metric("Status", f"{status_color} {'Running' if status['is_running'] else 'Stopped'}")
    
    with col2:
        st.metric("Cycles", status["cycle_count"])
    
    with col3:
        st.metric("Total Opportunities", status["total_opportunities_found"])
    
    with col4:
        st.metric("Current Opportunities", status["current_opportunities"])
    
    with col5:
        avg_time = status["average_cycle_time"]
        st.metric("Avg Cycle Time", f"{avg_time:.2f}s")
    
    # Last update time
    if status["last_update"]:
        time_since = datetime.now() - status["last_update"]
        st.caption(f"Last updated: {time_since.total_seconds():.0f} seconds ago")
    else:
        st.caption("Never updated")


def render_market_correlations():
    """Render market correlations and similarities"""
    st.subheader("🔗 Market Correlations & Similarities")
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("This section shows how markets are matched during the batching process before arbitrage detection.")
        
        with col2:
            if st.button("🔍 Analyze Correlations"):
                with st.spinner("Analyzing market similarities..."):
                    similarities = monitor.get_market_similarities(top_n=20)
                    st.session_state.similarities = similarities
    
    if 'similarities' in st.session_state and st.session_state.similarities:
        render_similarity_analysis(st.session_state.similarities)
    else:
        st.info("👆 Click 'Analyze Correlations' to see how markets are matched during batching.")


def render_similarity_analysis(similarities):
    """Render detailed similarity analysis"""
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score = st.slider(
            "Minimum Similarity Score", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.2, 
            step=0.05
        )
    
    with col2:
        match_type_filter = st.selectbox(
            "Match Type",
            options=["All", "fuzzy", "semantic", "keyword"],
            index=0
        )
    
    with col3:
        show_excluded = st.checkbox("Show Excluded Pairs", value=False)
    
    # Filter similarities
    filtered_similarities = []
    for sim in similarities:
        if sim['overall_score'] >= min_score:
            if match_type_filter == "All" or sim['match_type'] == match_type_filter:
                if show_excluded or not sim['is_excluded']:
                    filtered_similarities.append(sim)
    
    if not filtered_similarities:
        st.warning("No similarities found with the current filters.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pairs", len(filtered_similarities))
    
    with col2:
        avg_score = sum(sim['overall_score'] for sim in filtered_similarities) / len(filtered_similarities)
        st.metric("Avg Similarity", f"{avg_score:.3f}")
    
    with col3:
        excluded_count = sum(1 for sim in filtered_similarities if sim['is_excluded'])
        st.metric("Excluded Pairs", excluded_count)
    
    with col4:
        high_similarity = sum(1 for sim in filtered_similarities if sim['overall_score'] > 0.7)
        st.metric("High Similarity", high_similarity)
    
    # Visualization
    render_similarity_charts(filtered_similarities)
    
    # Detailed table
    render_similarity_table(filtered_similarities)


def render_similarity_charts(similarities):
    """Render similarity visualization charts"""
    
    # Create DataFrame for plotting
    df = pd.DataFrame(similarities)
    
    # Score distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Score Distribution")
        
        fig_hist = px.histogram(
            df, 
            x='overall_score', 
            nbins=20,
            title="Overall Similarity Score Distribution",
            labels={'overall_score': 'Similarity Score', 'count': 'Number of Pairs'}
        )
        fig_hist.update_layout(height=300)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Match Type Distribution")
        
        match_counts = df['match_type'].value_counts()
        fig_pie = px.pie(
            values=match_counts.values,
            names=match_counts.index,
            title="Match Type Distribution"
        )
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Scatter plot of different scoring methods
    st.subheader("📈 Similarity Score Comparison")
    
    fig_scatter = go.Figure()
    
    # Add fuzzy vs semantic scores
    fig_scatter.add_trace(go.Scatter(
        x=df['fuzzy_score'],
        y=df['semantic_score'],
        mode='markers',
        name='Fuzzy vs Semantic',
        text=df['polymarket_question'].str[:50] + '...',
        hovertemplate='<b>Fuzzy Score:</b> %{x:.3f}<br>' +
                     '<b>Semantic Score:</b> %{y:.3f}<br>' +
                     '<b>Question:</b> %{text}<br>' +
                     '<extra></extra>',
        marker=dict(
            size=df['overall_score'] * 20,
            color=df['overall_score'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Overall Score")
        )
    ))
    
    fig_scatter.update_layout(
        title="Fuzzy vs Semantic Similarity Scores",
        xaxis_title="Fuzzy Score",
        yaxis_title="Semantic Score",
        height=400
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)


def render_similarity_table(similarities):
    """Render detailed similarity table"""
    st.subheader("📋 Detailed Similarity Analysis")
    
    # Prepare data for display
    display_data = []
    
    for sim in similarities:
        display_data.append({
            'Polymarket Question': sim['polymarket_question'][:60] + '...' if len(sim['polymarket_question']) > 60 else sim['polymarket_question'],
            'Kalshi Question': sim['kalshi_question'][:60] + '...' if len(sim['kalshi_question']) > 60 else sim['kalshi_question'],
            'Overall Score': f"{sim['overall_score']:.3f}",
            'Fuzzy': f"{sim['fuzzy_score']:.3f}",
            'Semantic': f"{sim['semantic_score']:.3f}",
            'Keyword': f"{sim['keyword_score']:.3f}",
            'Match Type': sim['match_type'],
            'Common Keywords': ', '.join(sim['common_keywords'][:3]) if sim['common_keywords'] else 'None',
            'Similarity Reasons': '; '.join(sim['similarity_reasons'][:2]) if sim['similarity_reasons'] else 'None',
            'Status': '❌ Excluded' if sim['is_excluded'] else '✅ Active'
        })
    
    df_display = pd.DataFrame(display_data)
    
    # Style the dataframe
    styled_df = df_display.style.apply(
        lambda x: ['background-color: #ffcccc' if '❌' in str(x['Status']) else '' for _ in x],
        axis=1
    )
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # Expandable detailed view
    with st.expander("🔍 Detailed Analysis"):
        selected_idx = st.selectbox(
            "Select a pair for detailed analysis:",
            range(len(similarities)),
            format_func=lambda x: f"{similarities[x]['polymarket_question'][:50]}... ↔ {similarities[x]['kalshi_question'][:50]}..."
        )
        
        if selected_idx is not None:
            render_detailed_similarity(similarities[selected_idx])


def render_detailed_similarity(similarity):
    """Render detailed analysis of a single similarity"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Polymarket")
        st.write(f"**Question:** {similarity['polymarket_question']}")
        st.write(f"**Market ID:** {similarity['polymarket_id']}")
        st.write(f"**Yes Price:** ${similarity['polymarket_yes_price']:.3f}")
        st.write(f"**No Price:** ${similarity['polymarket_no_price']:.3f}")
        st.write(f"**Volume:** ${similarity['polymarket_volume']:,.0f}")
    
    with col2:
        st.subheader("📈 Kalshi")
        st.write(f"**Question:** {similarity['kalshi_question']}")
        st.write(f"**Market ID:** {similarity['kalshi_id']}")
        st.write(f"**Yes Price:** ${similarity['kalshi_yes_price']:.3f}")
        st.write(f"**No Price:** ${similarity['kalshi_no_price']:.3f}")
        st.write(f"**Volume:** ${similarity['kalshi_volume']:,.0f}")
    
    # Similarity analysis
    st.subheader("🔍 Similarity Analysis")
    
    # Score breakdown
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Score", f"{similarity['overall_score']:.3f}")
    
    with col2:
        st.metric("Fuzzy Score", f"{similarity['fuzzy_score']:.3f}")
    
    with col3:
        st.metric("Semantic Score", f"{similarity['semantic_score']:.3f}")
    
    with col4:
        st.metric("Keyword Score", f"{similarity['keyword_score']:.3f}")
    
    # Common keywords
    if similarity['common_keywords']:
        st.write("**Common Keywords:**")
        keyword_cols = st.columns(min(len(similarity['common_keywords']), 5))
        for i, keyword in enumerate(similarity['common_keywords'][:5]):
            with keyword_cols[i]:
                st.code(keyword)
    
    # Similarity reasons
    if similarity['similarity_reasons']:
        st.write("**Similarity Reasons:**")
        for reason in similarity['similarity_reasons']:
            st.write(f"• {reason}")
    
    # Status
    if similarity['is_excluded']:
        st.error(f"❌ **Excluded:** {similarity['exclusion_reason']}")
    else:
        st.success("✅ **Active:** This pair is considered for arbitrage detection")
    
    # Price comparison chart
    st.subheader("💰 Price Comparison")
    
    price_data = {
        'Platform': ['Polymarket', 'Kalshi'],
        'Yes Price': [similarity['polymarket_yes_price'], similarity['kalshi_yes_price']],
        'No Price': [similarity['polymarket_no_price'], similarity['kalshi_no_price']]
    }
    
    fig_prices = px.bar(
        pd.DataFrame(price_data),
        x='Platform',
        y=['Yes Price', 'No Price'],
        title="Price Comparison",
        barmode='group'
    )
    
    st.plotly_chart(fig_prices, use_container_width=True)


def render_current_opportunities():
    """Render current arbitrage opportunities"""
    st.subheader("💰 Current Opportunities")
    
    # Get current opportunities from monitor
    try:
        opportunities = monitor.get_current_opportunities()
        
        if not opportunities:
            st.info("No arbitrage opportunities found at the moment.")
            return
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_profit = st.slider(
                "Min Profit %",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5
            )
        
        with col2:
            strategy_filter = st.selectbox(
                "Strategy",
                options=["All"] + list(set(opp.get('strategy', '') for opp in opportunities)),
                index=0
            )
        
        with col3:
            outcome_filter = st.selectbox(
                "Outcome",
                options=["All", "yes", "no"],
                index=0
            )
        
        # Filter opportunities
        filtered_opportunities = []
        for opp in opportunities:
            if opp.get('profit_percentage', 0) * 100 >= min_profit:
                if strategy_filter == "All" or opp.get('strategy') == strategy_filter:
                    if outcome_filter == "All" or opp.get('outcome') == outcome_filter:
                        filtered_opportunities.append(opp)
        
        if not filtered_opportunities:
            st.warning("No opportunities match the current filters.")
            return
        
        # Display opportunities
        for i, opp in enumerate(filtered_opportunities):
            with st.expander(f"💡 Opportunity {i+1}: {opp.get('profit_percentage', 0)*100:.1f}% profit", expanded=i<3):
                render_opportunity_card(opp)
                
    except Exception as e:
        st.error(f"Error loading opportunities: {e}")


def render_opportunity_card(opportunity):
    """Render a single opportunity card"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Polymarket**")
        st.write(f"Question: {opportunity.get('polymarket_question', 'N/A')}")
        st.write(f"Yes Price: ${opportunity.get('poly_yes_price', 0):.3f}")
        st.write(f"No Price: ${opportunity.get('poly_no_price', 0):.3f}")
        st.write(f"Volume: ${opportunity.get('poly_volume', 0):,.0f}")
    
    with col2:
        st.write("**📈 Kalshi**")
        st.write(f"Question: {opportunity.get('kalshi_question', 'N/A')}")
        st.write(f"Yes Price: ${opportunity.get('kalshi_yes_price', 0):.3f}")
        st.write(f"No Price: ${opportunity.get('kalshi_no_price', 0):.3f}")
        st.write(f"Volume: ${opportunity.get('kalshi_volume', 0):,.0f}")
    
    # Opportunity details
    st.write("**💰 Opportunity Details**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        profit_pct = opportunity.get('profit_percentage', 0) * 100
        st.metric("Profit %", f"{profit_pct:.1f}%")
    
    with col2:
        profit_potential = opportunity.get('profit_potential', 0)
        st.metric("Profit $", f"${profit_potential:.2f}")
    
    with col3:
        strategy = opportunity.get('strategy', 'N/A')
        st.metric("Strategy", strategy.replace('_', ' ').title())
    
    with col4:
        outcome = opportunity.get('outcome', 'N/A')
        st.metric("Outcome", outcome.upper())
    
    # Risk metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        required_capital = opportunity.get('required_capital', 0)
        st.metric("Required Capital", f"${required_capital:.2f}")
    
    with col2:
        max_position = opportunity.get('max_position_size', 0)
        st.metric("Max Position", f"${max_position:.2f}")
    
    with col3:
        confidence = opportunity.get('confidence_score', 0)
        st.metric("Confidence", f"{confidence:.1%}")
    
    # Additional details
    if opportunity.get('notes'):
        st.write(f"**Notes:** {opportunity['notes']}")
    
    detected_at = opportunity.get('detected_at')
    if detected_at:
        st.caption(f"Detected at: {detected_at}")


def render_performance_metrics():
    """Render performance metrics"""
    st.subheader("📈 Performance Metrics")
    
    # Time period selector
    time_period = st.selectbox(
        "Select time period:",
        options=[1, 6, 12, 24, 48, 168],  # hours
        format_func=lambda x: f"Last {x} hours" if x < 24 else f"Last {x//24} days",
        index=3  # Default to 24 hours
    )
    
    # Get metrics
    metrics = monitor.get_performance_metrics(time_period)
    
    if not metrics:
        st.info("No performance data available")
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Opportunities", metrics.get("total_opportunities", 0))
    
    with col2:
        st.metric("Total Profit Potential", f"${metrics.get('total_potential_profit', 0):.2f}")
    
    with col3:
        st.metric("Average Profit %", f"{metrics.get('average_profit_percentage', 0):.1%}")
    
    with col4:
        st.metric("Success Rate", f"{metrics.get('success_rate', 0):.1%}")
    
    # Additional metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API Calls", metrics.get("total_api_calls", 0))
    
    with col2:
        st.metric("Avg Processing Time", f"{metrics.get('average_processing_time', 0):.2f}s")
    
    with col3:
        st.metric("Timeframe", f"{time_period} hours")


def render_historical_analysis():
    """Render historical analysis charts"""
    st.subheader("📊 Historical Analysis")
    
    # Get historical data from database
    db = DatabaseManager()
    recent_opportunities = db.get_recent_opportunities(limit=100)
    
    if not recent_opportunities:
        st.info("No historical data available")
        return
    
    # Convert to DataFrame
    df_data = []
    for opp in recent_opportunities:
        df_data.append({
            "detected_at": opp.detected_at,
            "profit_percentage": opp.profit_percentage,
            "profit_potential": opp.profit_potential,
            "strategy": opp.strategy,
            "outcome": opp.outcome,
            "confidence_score": opp.confidence_score,
            "platform_pair": f"{opp.polymarket_id[:8]}...{opp.kalshi_id[:8]}"
        })
    
    df = pd.DataFrame(df_data)
    
    # Time series chart
    st.subheader("📈 Opportunities Over Time")
    
    # Group by hour
    df['hour'] = df['detected_at'].dt.floor('H')
    hourly_stats = df.groupby('hour').agg({
        'profit_percentage': ['count', 'mean', 'sum'],
        'profit_potential': 'sum'
    }).reset_index()
    
    # Flatten column names
    hourly_stats.columns = ['hour', 'opportunity_count', 'avg_profit_pct', 'total_profit_pct', 'total_profit_potential']
    
    # Create time series chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hourly_stats['hour'],
        y=hourly_stats['opportunity_count'],
        name='Opportunities Count',
        line=dict(color='blue')
    ))
    
    fig.add_trace(go.Scatter(
        x=hourly_stats['hour'],
        y=hourly_stats['avg_profit_pct'] * 100,
        name='Avg Profit %',
        yaxis='y2',
        line=dict(color='green')
    ))
    
    fig.update_layout(
        title='Opportunities and Profit Over Time',
        xaxis_title='Time',
        yaxis=dict(title='Opportunity Count', side='left'),
        yaxis2=dict(title='Average Profit %', side='right', overlaying='y'),
        legend=dict(x=0, y=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Strategy breakdown
    st.subheader("🎯 Strategy Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        strategy_counts = df['strategy'].value_counts()
        fig_strategy = px.pie(
            values=strategy_counts.values,
            names=strategy_counts.index,
            title='Opportunities by Strategy'
        )
        st.plotly_chart(fig_strategy, use_container_width=True)
    
    with col2:
        outcome_counts = df['outcome'].value_counts()
        fig_outcome = px.pie(
            values=outcome_counts.values,
            names=outcome_counts.index,
            title='Opportunities by Outcome'
        )
        st.plotly_chart(fig_outcome, use_container_width=True)
    
    # Profit distribution
    st.subheader("💰 Profit Distribution")
    
    fig_profit = px.histogram(
        df,
        x='profit_percentage',
        nbins=20,
        title='Distribution of Profit Percentages',
        labels={'profit_percentage': 'Profit Percentage', 'count': 'Frequency'}
    )
    st.plotly_chart(fig_profit, use_container_width=True)
