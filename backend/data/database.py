"""
Database models for the arbitrage platform
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import logging

Base = declarative_base()


class ArbitrageOpportunityModel(Base):
    """Database model for arbitrage opportunities"""
    __tablename__ = 'arbitrage_opportunities'
    
    id = Column(Integer, primary_key=True)
    polymarket_id = Column(String(100), nullable=False)
    kalshi_id = Column(String(100), nullable=False)
    polymarket_question = Column(Text)
    kalshi_question = Column(Text)
    
    # Price data
    poly_yes_price = Column(Float)
    poly_no_price = Column(Float)
    kalshi_yes_price = Column(Float)
    kalshi_no_price = Column(Float)
    
    # Volume data
    poly_volume = Column(Float)
    kalshi_volume = Column(Float)
    
    # Opportunity metrics
    profit_potential = Column(Float)
    profit_percentage = Column(Float)
    required_capital = Column(Float)
    max_position_size = Column(Float)
    
    # Strategy
    strategy = Column(String(50))
    outcome = Column(String(10))
    
    # Risk metrics
    slippage_adjusted_profit = Column(Float)
    fee_adjusted_profit = Column(Float)
    confidence_score = Column(Float)
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Metadata
    match_confidence = Column(Float)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)


class MarketPairModel(Base):
    """Database model for market pairs"""
    __tablename__ = 'market_pairs'
    
    id = Column(Integer, primary_key=True)
    polymarket_id = Column(String(100), nullable=False)
    kalshi_id = Column(String(100), nullable=False)
    polymarket_question = Column(Text)
    kalshi_question = Column(Text)
    
    confidence = Column(Float)
    match_type = Column(String(20))  # manual, fuzzy, semantic, keyword
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    is_active = Column(Boolean, default=True)
    notes = Column(Text)


class TradingPerformanceModel(Base):
    """Database model for tracking trading performance"""
    __tablename__ = 'trading_performance'
    
    id = Column(Integer, primary_key=True)
    opportunity_id = Column(Integer)  # Links to ArbitrageOpportunityModel
    
    # Trade execution data
    executed_at = Column(DateTime)
    position_size = Column(Float)
    actual_profit = Column(Float)
    actual_profit_percentage = Column(Float)
    
    # Platform data
    poly_trade_executed = Column(Boolean, default=False)
    kalshi_trade_executed = Column(Boolean, default=False)
    
    # Execution metrics
    execution_time_seconds = Column(Float)
    slippage_experienced = Column(Float)
    fees_paid = Column(Float)
    
    # Status
    status = Column(String(20))  # pending, executed, failed, cancelled
    notes = Column(Text)


class MonitoringLogModel(Base):
    """Database model for monitoring logs"""
    __tablename__ = 'monitoring_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Metrics
    opportunities_detected = Column(Integer)
    markets_analyzed = Column(Integer)
    api_calls_made = Column(Integer)
    processing_time_seconds = Column(Float)
    
    # Status
    status = Column(String(20))  # success, error, warning
    error_message = Column(Text)
    
    # Platform data
    polymarket_markets_count = Column(Integer)
    kalshi_markets_count = Column(Integer)
    matched_pairs_count = Column(Integer)


class DatabaseManager:
    """Database manager for the arbitrage platform"""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            from backend.core.config import config
            db_config = config.get_database_config()
            database_url = f"sqlite:///{db_config.get('path', 'data/arbitrage.db')}"
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self.create_tables()
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Error creating database tables: {e}")
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def store_opportunity(self, opportunity):
        """Store an arbitrage opportunity in the database"""
        try:
            session = self.get_session()
            
            db_opportunity = ArbitrageOpportunityModel(
                polymarket_id=opportunity.polymarket_id,
                kalshi_id=opportunity.kalshi_id,
                polymarket_question=opportunity.polymarket_question,
                kalshi_question=opportunity.kalshi_question,
                poly_yes_price=opportunity.poly_yes_price,
                poly_no_price=opportunity.poly_no_price,
                kalshi_yes_price=opportunity.kalshi_yes_price,
                kalshi_no_price=opportunity.kalshi_no_price,
                poly_volume=opportunity.poly_volume,
                kalshi_volume=opportunity.kalshi_volume,
                profit_potential=opportunity.profit_potential,
                profit_percentage=opportunity.profit_percentage,
                required_capital=opportunity.required_capital,
                max_position_size=opportunity.max_position_size,
                strategy=opportunity.strategy,
                outcome=opportunity.outcome,
                slippage_adjusted_profit=opportunity.slippage_adjusted_profit,
                fee_adjusted_profit=opportunity.fee_adjusted_profit,
                confidence_score=opportunity.confidence_score,
                detected_at=opportunity.detected_at,
                expires_at=opportunity.expires_at,
                match_confidence=opportunity.match_confidence,
                notes=opportunity.notes
            )
            
            session.add(db_opportunity)
            session.commit()
            session.close()
            
            logging.debug(f"Stored opportunity: {opportunity.polymarket_id} <-> {opportunity.kalshi_id}")
            return db_opportunity.id
            
        except Exception as e:
            logging.error(f"Error storing opportunity: {e}")
            if session:
                session.rollback()
                session.close()
            return None
    
    def get_recent_opportunities(self, limit: int = 50):
        """Get recent arbitrage opportunities"""
        try:
            session = self.get_session()
            
            opportunities = session.query(ArbitrageOpportunityModel)\
                .filter(ArbitrageOpportunityModel.is_active == True)\
                .order_by(ArbitrageOpportunityModel.detected_at.desc())\
                .limit(limit)\
                .all()
            
            session.close()
            return opportunities
            
        except Exception as e:
            logging.error(f"Error retrieving opportunities: {e}")
            return []
    
    def get_opportunities_since(self, since_time: datetime):
        """Get opportunities detected since the specified time"""
        try:
            session = self.get_session()
            
            opportunities = session.query(ArbitrageOpportunityModel)\
                .filter(ArbitrageOpportunityModel.detected_at >= since_time)\
                .order_by(ArbitrageOpportunityModel.detected_at.desc())\
                .all()
            
            session.close()
            return opportunities
            
        except Exception as e:
            logging.error(f"Error retrieving opportunities since {since_time}: {e}")
            return []
    
    def get_performance_metrics(self, timeframe_hours: int = 24):
        """Get performance metrics for the specified timeframe"""
        try:
            session = self.get_session()
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
            
            # Get opportunities in timeframe
            opportunities = session.query(ArbitrageOpportunityModel)\
                .filter(ArbitrageOpportunityModel.detected_at >= cutoff_time)\
                .all()
            
            # Get monitoring logs
            logs = session.query(MonitoringLogModel)\
                .filter(MonitoringLogModel.timestamp >= cutoff_time)\
                .all()
            
            session.close()
            
            # Calculate metrics
            total_opportunities = len(opportunities)
            total_potential_profit = sum(opp.profit_potential for opp in opportunities)
            avg_profit_percentage = sum(opp.profit_percentage for opp in opportunities) / total_opportunities if total_opportunities > 0 else 0
            
            total_api_calls = sum(log.api_calls_made for log in logs if log.api_calls_made)
            avg_processing_time = sum(log.processing_time_seconds for log in logs if log.processing_time_seconds) / len(logs) if logs else 0
            
            return {
                'timeframe_hours': timeframe_hours,
                'total_opportunities': total_opportunities,
                'total_potential_profit': total_potential_profit,
                'average_profit_percentage': avg_profit_percentage,
                'total_api_calls': total_api_calls,
                'average_processing_time': avg_processing_time,
                'success_rate': len([log for log in logs if log.status == 'success']) / len(logs) if logs else 0
            }
            
        except Exception as e:
            logging.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def store_market_pair(self, match):
        """Store a market pair in the database"""
        try:
            session = self.get_session()
            
            # Check if pair already exists
            existing = session.query(MarketPairModel)\
                .filter(MarketPairModel.polymarket_id == match.polymarket_id)\
                .filter(MarketPairModel.kalshi_id == match.kalshi_id)\
                .first()
            
            if existing:
                # Update existing pair
                existing.confidence = match.confidence
                existing.match_type = match.match_type
                existing.updated_at = datetime.utcnow()
                existing.notes = match.notes
            else:
                # Create new pair
                db_pair = MarketPairModel(
                    polymarket_id=match.polymarket_id,
                    kalshi_id=match.kalshi_id,
                    polymarket_question=match.polymarket_question,
                    kalshi_question=match.kalshi_question,
                    confidence=match.confidence,
                    match_type=match.match_type,
                    notes=match.notes
                )
                session.add(db_pair)
            
            session.commit()
            session.close()
            
            logging.debug(f"Stored market pair: {match.polymarket_id} <-> {match.kalshi_id}")
            
        except Exception as e:
            logging.error(f"Error storing market pair: {e}")
            if session:
                session.rollback()
                session.close()
    
    def log_monitoring_cycle(self, opportunities_count: int, markets_analyzed: int, 
                           api_calls: int, processing_time: float, status: str = "success", 
                           error_message: str = None, poly_count: int = 0, 
                           kalshi_count: int = 0, matched_pairs: int = 0):
        """Log a monitoring cycle"""
        try:
            session = self.get_session()
            
            log_entry = MonitoringLogModel(
                opportunities_detected=opportunities_count,
                markets_analyzed=markets_analyzed,
                api_calls_made=api_calls,
                processing_time_seconds=processing_time,
                status=status,
                error_message=error_message,
                polymarket_markets_count=poly_count,
                kalshi_markets_count=kalshi_count,
                matched_pairs_count=matched_pairs
            )
            
            session.add(log_entry)
            session.commit()
            session.close()
            
            logging.debug(f"Logged monitoring cycle: {opportunities_count} opportunities, {processing_time:.2f}s")
            
        except Exception as e:
            logging.error(f"Error logging monitoring cycle: {e}")
            if session:
                session.rollback()
                session.close()
    
    def cleanup_old_records(self, days_to_keep: int = 30):
        """Clean up old records from the database"""
        try:
            session = self.get_session()
            
            cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old opportunities
            old_opportunities = session.query(ArbitrageOpportunityModel)\
                .filter(ArbitrageOpportunityModel.detected_at < cutoff_time)\
                .delete()
            
            # Delete old monitoring logs
            old_logs = session.query(MonitoringLogModel)\
                .filter(MonitoringLogModel.timestamp < cutoff_time)\
                .delete()
            
            session.commit()
            session.close()
            
            logging.info(f"Cleaned up {old_opportunities} old opportunities and {old_logs} old logs")
            
        except Exception as e:
            logging.error(f"Error cleaning up old records: {e}")
            if session:
                session.rollback()
                session.close()
