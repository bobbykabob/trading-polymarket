"""
Real-time monitoring system for arbitrage opportunities
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
from dataclasses import asdict

from backend.core.config import config
from backend.core.market_matcher import MarketMatcher
from backend.core.arbitrage_detector import ArbitrageDetector
from backend.data.database import DatabaseManager
from backend.polymarket_api import PolymarketAPI
from backend.kalshi_api import KalshiAPI


class ArbitrageMonitor:
    """Main monitoring system for arbitrage opportunities"""
    
    def __init__(self):
        self.config = config.get_monitoring_config()
        self.update_interval = self.config.get("update_interval", 30)
        self.batch_size = self.config.get("batch_size", 20)
        self.max_concurrent = self.config.get("max_concurrent", 5)
        
        # Initialize components
        self.polymarket_api = PolymarketAPI()
        self.kalshi_api = KalshiAPI()
        self.market_matcher = MarketMatcher()
        self.arbitrage_detector = ArbitrageDetector()
        self.database = DatabaseManager()
        
        # Monitoring state
        self.is_running = False
        self.monitoring_thread = None
        self.last_update = None
        self.opportunities_cache = []
        self.market_cache = {}
        
        # Performance metrics
        self.cycle_count = 0
        self.total_opportunities_found = 0
        self.total_processing_time = 0
        self.api_calls_made = 0
        
        logging.info("ArbitrageMonitor initialized")
    
    def start_monitoring(self):
        """Start the monitoring system"""
        if self.is_running:
            logging.warning("Monitoring is already running")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logging.info("Arbitrage monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        if not self.is_running:
            logging.warning("Monitoring is not running")
            return
        
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        logging.info("Arbitrage monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                cycle_start = time.time()
                
                # Run monitoring cycle
                opportunities = self._run_monitoring_cycle()
                
                # Update cache
                self.opportunities_cache = opportunities
                self.last_update = datetime.now()
                
                # Update metrics
                self.cycle_count += 1
                self.total_opportunities_found += len(opportunities)
                cycle_time = time.time() - cycle_start
                self.total_processing_time += cycle_time
                
                logging.info(f"Monitoring cycle {self.cycle_count} completed: {len(opportunities)} opportunities found in {cycle_time:.2f}s")
                
                # Sleep until next cycle
                time.sleep(self.update_interval)
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(self.update_interval)
    
    def _run_monitoring_cycle(self) -> List:
        """Run a single monitoring cycle"""
        cycle_start = time.time()
        api_calls = 0
        
        try:
            # Fetch markets from both platforms
            logging.debug("Fetching markets from Polymarket and Kalshi")
            
            polymarket_markets = self.polymarket_api.get_markets(limit=self.batch_size)
            kalshi_markets = self.kalshi_api.get_markets(limit=self.batch_size)
            
            api_calls += 2  # Two API calls made
            
            if not polymarket_markets or not kalshi_markets:
                logging.warning("Failed to fetch markets from one or both platforms")
                return []
            
            # Find market matches
            logging.debug("Finding market matches")
            market_matches = self.market_matcher.find_equivalent_markets(
                polymarket_markets, kalshi_markets
            )
            
            if not market_matches:
                logging.info("No market matches found")
                return []
            
            # Store market pairs in database
            for match in market_matches:
                self.database.store_market_pair(match)
            
            # Prepare market data dictionaries
            polymarket_data = {m.get('id'): m for m in polymarket_markets}
            kalshi_data = {m.get('id'): m for m in kalshi_markets}
            
            # Detect arbitrage opportunities
            logging.debug("Detecting arbitrage opportunities")
            opportunities = self.arbitrage_detector.detect_opportunities(
                market_matches, polymarket_data, kalshi_data
            )
            
            # Store opportunities in database
            for opportunity in opportunities:
                self.database.store_opportunity(opportunity)
            
            # Log monitoring cycle
            cycle_time = time.time() - cycle_start
            self.database.log_monitoring_cycle(
                opportunities_count=len(opportunities),
                markets_analyzed=len(polymarket_markets) + len(kalshi_markets),
                api_calls=api_calls,
                processing_time=cycle_time,
                status="success",
                poly_count=len(polymarket_markets),
                kalshi_count=len(kalshi_markets),
                matched_pairs=len(market_matches)
            )
            
            self.api_calls_made += api_calls
            
            return opportunities
            
        except Exception as e:
            logging.error(f"Error in monitoring cycle: {e}")
            
            # Log error
            cycle_time = time.time() - cycle_start
            self.database.log_monitoring_cycle(
                opportunities_count=0,
                markets_analyzed=0,
                api_calls=api_calls,
                processing_time=cycle_time,
                status="error",
                error_message=str(e)
            )
            
            return []
    
    def get_current_opportunities(self) -> List[Dict[str, Any]]:
        """Get current arbitrage opportunities"""
        try:
            # Return cached opportunities if available
            if self.opportunities_cache:
                return [asdict(opp) for opp in self.opportunities_cache]
            
            # Otherwise try to get from database
            opportunities = self.database.get_recent_opportunities(limit=50)
            return [asdict(opp) for opp in opportunities]
            
        except Exception as e:
            logging.error(f"Error getting current opportunities: {e}")
            return []
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "is_running": self.is_running,
            "last_update": self.last_update,
            "cycle_count": self.cycle_count,
            "total_opportunities_found": self.total_opportunities_found,
            "current_opportunities": len(self.opportunities_cache),
            "average_cycle_time": self.total_processing_time / max(self.cycle_count, 1),
            "api_calls_made": self.api_calls_made,
            "cached_markets": len(self.market_cache)
        }
    
    def get_performance_metrics(self, time_period_hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for the specified time period"""
        try:
            # Calculate time threshold
            time_threshold = datetime.now() - timedelta(hours=time_period_hours)
            
            # Get opportunities from database
            opportunities = self.database.get_opportunities_since(time_threshold)
            
            if not opportunities:
                return {}
            
            # Calculate metrics
            total_opportunities = len(opportunities)
            total_potential_profit = sum(opp.profit_potential for opp in opportunities)
            total_profit_percentage = sum(opp.profit_percentage for opp in opportunities)
            average_profit_percentage = total_profit_percentage / total_opportunities if total_opportunities > 0 else 0
            
            # Calculate success rate (opportunities with profit > min threshold)
            min_threshold = self.config.get("min_profit_threshold", 0.05)
            successful_opportunities = sum(1 for opp in opportunities if opp.profit_percentage >= min_threshold)
            success_rate = successful_opportunities / total_opportunities if total_opportunities > 0 else 0
            
            # API and processing metrics
            avg_processing_time = self.total_processing_time / max(self.cycle_count, 1)
            
            return {
                "total_opportunities": total_opportunities,
                "total_potential_profit": total_potential_profit,
                "average_profit_percentage": average_profit_percentage,
                "success_rate": success_rate,
                "total_api_calls": self.api_calls_made,
                "average_processing_time": avg_processing_time,
                "time_period_hours": time_period_hours,
                "opportunities_per_hour": total_opportunities / time_period_hours if time_period_hours > 0 else 0,
                "avg_confidence": sum(opp.confidence_score for opp in opportunities) / total_opportunities if total_opportunities > 0 else 0,
                "max_profit_opportunity": max(opp.profit_percentage for opp in opportunities) if opportunities else 0,
                "min_profit_opportunity": min(opp.profit_percentage for opp in opportunities) if opportunities else 0
            }
            
        except Exception as e:
            logging.error(f"Error getting performance metrics: {e}")
            return {}
    
    def get_market_similarities(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Get detailed market similarity information for correlation display"""
        try:
            # Get fresh market data
            polymarket_data = self.polymarket_api.get_markets()
            kalshi_data = self.kalshi_api.get_markets()
            
            if not polymarket_data or not kalshi_data:
                logging.warning("No market data available for similarity analysis")
                return []
            
            # Get similarity information
            similarities = self.market_matcher.get_market_similarities(
                polymarket_data, 
                kalshi_data, 
                top_n=top_n
            )
            
            # Convert to serializable format
            result = []
            for sim in similarities:
                result.append({
                    'polymarket_question': sim.polymarket_market.get('question', ''),
                    'kalshi_question': sim.kalshi_market.get('question', ''),
                    'polymarket_id': sim.polymarket_market.get('id', ''),
                    'kalshi_id': sim.kalshi_market.get('id', ''),
                    'fuzzy_score': sim.fuzzy_score,
                    'semantic_score': sim.semantic_score,
                    'keyword_score': sim.keyword_score,
                    'overall_score': sim.overall_score,
                    'match_type': sim.match_type,
                    'common_keywords': sim.common_keywords,
                    'similarity_reasons': sim.similarity_reasons,
                    'is_excluded': sim.is_excluded,
                    'exclusion_reason': sim.exclusion_reason,
                    'polymarket_yes_price': sim.polymarket_market.get('yes_price', 0),
                    'polymarket_no_price': sim.polymarket_market.get('no_price', 0),
                    'kalshi_yes_price': sim.kalshi_market.get('yes_price', 0),
                    'kalshi_no_price': sim.kalshi_market.get('no_price', 0),
                    'polymarket_volume': sim.polymarket_market.get('volume', 0),
                    'kalshi_volume': sim.kalshi_market.get('volume', 0)
                })
            
            return result
            
        except Exception as e:
            logging.error(f"Error getting market similarities: {e}")
            return []
    
    def force_update(self) -> List:
        """Force an immediate monitoring cycle"""
        logging.info("Forcing immediate monitoring cycle")
        return self._run_monitoring_cycle()
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update monitoring configuration"""
        for key, value in new_config.items():
            if hasattr(self, key):
                setattr(self, key, value)
                config.update_config(f"monitoring.{key}", value)
        
        logging.info(f"Updated monitoring config: {new_config}")
    
    def get_top_opportunities(self, limit: int = 10) -> List:
        """Get top arbitrage opportunities"""
        opportunities = self.get_current_opportunities()
        
        # Sort by profit potential (descending)
        opportunities.sort(key=lambda x: x.profit_potential, reverse=True)
        
        return opportunities[:limit]
    
    def get_opportunity_by_markets(self, polymarket_id: str, kalshi_id: str) -> Optional[Any]:
        """Get specific opportunity by market IDs"""
        for opportunity in self.opportunities_cache:
            if (opportunity.polymarket_id == polymarket_id and 
                opportunity.kalshi_id == kalshi_id):
                return opportunity
        return None
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data from database"""
        logging.info(f"Cleaning up data older than {days_to_keep} days")
        self.database.cleanup_old_records(days_to_keep)


class AlertManager:
    """Manages alerts for arbitrage opportunities"""
    
    def __init__(self):
        self.alert_config = config.get("alerts", {})
        self.cooldown_period = config.get("arbitrage.alert_cooldown", 300)  # 5 minutes
        self.min_profit_for_alert = self.alert_config.get("min_profit_for_alert", 0.1)
        
        # Track sent alerts to prevent spam
        self.sent_alerts = {}
        
        logging.info("AlertManager initialized")
    
    def check_and_send_alerts(self, opportunities: List):
        """Check opportunities and send alerts if needed"""
        current_time = datetime.now()
        
        for opportunity in opportunities:
            # Check if opportunity meets alert criteria
            if not self._should_send_alert(opportunity, current_time):
                continue
            
            # Send alert
            self._send_alert(opportunity)
            
            # Record alert
            alert_key = f"{opportunity.polymarket_id}_{opportunity.kalshi_id}_{opportunity.outcome}"
            self.sent_alerts[alert_key] = current_time
    
    def _should_send_alert(self, opportunity, current_time: datetime) -> bool:
        """Check if an alert should be sent for this opportunity"""
        # Check minimum profit threshold
        if opportunity.profit_percentage < self.min_profit_for_alert:
            return False
        
        # Check cooldown period
        alert_key = f"{opportunity.polymarket_id}_{opportunity.kalshi_id}_{opportunity.outcome}"
        last_alert = self.sent_alerts.get(alert_key)
        
        if last_alert:
            time_since_last = (current_time - last_alert).total_seconds()
            if time_since_last < self.cooldown_period:
                return False
        
        return True
    
    def _send_alert(self, opportunity):
        """Send alert for an opportunity"""
        alert_message = self._format_alert_message(opportunity)
        
        # Log alert (basic implementation)
        logging.warning(f"ARBITRAGE ALERT: {alert_message}")
        
        # TODO: Implement email, SMS, webhook alerts based on config
        # if self.alert_config.get("email_enabled"):
        #     self._send_email_alert(alert_message)
        # if self.alert_config.get("sms_enabled"):
        #     self._send_sms_alert(alert_message)
        # if self.alert_config.get("webhook_enabled"):
        #     self._send_webhook_alert(opportunity)
    
    def _format_alert_message(self, opportunity) -> str:
        """Format alert message"""
        return (
            f"Arbitrage opportunity detected! "
            f"Profit: {opportunity.profit_percentage:.1%} "
            f"({opportunity.profit_potential:.2f} USD) "
            f"Strategy: {opportunity.strategy} "
            f"Outcome: {opportunity.outcome} "
            f"Confidence: {opportunity.confidence_score:.1%}"
        )


# Global monitor instance
monitor = ArbitrageMonitor()
alert_manager = AlertManager()
