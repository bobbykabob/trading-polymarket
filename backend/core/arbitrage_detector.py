"""
Arbitrage detection engine for identifying profitable opportunities
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import math

from backend.core.config import config
from backend.core.market_matcher import MarketMatch


@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity"""
    polymarket_id: str
    kalshi_id: str
    polymarket_question: str
    kalshi_question: str
    
    # Price information
    poly_yes_price: float
    poly_no_price: float
    kalshi_yes_price: float
    kalshi_no_price: float
    
    # Volume information
    poly_volume: float
    kalshi_volume: float
    
    # Opportunity metrics
    profit_potential: float
    profit_percentage: float
    required_capital: float
    max_position_size: float
    
    # Strategy information
    strategy: str  # "buy_poly_sell_kalshi" or "buy_kalshi_sell_poly"
    outcome: str   # "yes" or "no"
    
    # Risk metrics
    slippage_adjusted_profit: float
    fee_adjusted_profit: float
    confidence_score: float
    
    # Metadata
    detected_at: datetime
    expires_at: Optional[datetime] = None
    match_confidence: float = 0.0
    notes: str = ""


class ArbitrageDetector:
    """Detects arbitrage opportunities between Polymarket and Kalshi"""
    
    def __init__(self):
        self.config = config.get_arbitrage_config()
        self.poly_config = config.get_platform_config("polymarket")
        self.kalshi_config = config.get_platform_config("kalshi")
        self.min_profit_threshold = self.config.get("min_profit_threshold", 0.05)
        self.max_position_size = self.config.get("max_position_size", 1000)
        self.slippage_buffer = self.config.get("slippage_buffer", 0.02)
        
    def detect_opportunities(self, market_matches: List[MarketMatch], 
                           polymarket_data: Dict[str, Dict], 
                           kalshi_data: Dict[str, Dict]) -> List[ArbitrageOpportunity]:
        """Detect arbitrage opportunities from matched markets"""
        opportunities = []
        
        for match in market_matches:
            poly_market = polymarket_data.get(match.polymarket_id)
            kalshi_market = kalshi_data.get(match.kalshi_id)
            
            if not poly_market or not kalshi_market:
                continue
                
            # Calculate opportunities for this market pair
            market_opportunities = self._analyze_market_pair(match, poly_market, kalshi_market)
            opportunities.extend(market_opportunities)
        
        # Filter and rank opportunities
        filtered_opportunities = self._filter_opportunities(opportunities)
        ranked_opportunities = self._rank_opportunities(filtered_opportunities)
        
        logging.info(f"Detected {len(ranked_opportunities)} arbitrage opportunities")
        return ranked_opportunities
    
    def _analyze_market_pair(self, match: MarketMatch, 
                           poly_market: Dict, kalshi_market: Dict) -> List[ArbitrageOpportunity]:
        """Analyze a specific market pair for arbitrage opportunities"""
        opportunities = []
        
        # Extract price data
        poly_yes = poly_market.get('yes_price', 0)
        poly_no = poly_market.get('no_price', 0)
        kalshi_yes = kalshi_market.get('yes_price', 0)
        kalshi_no = kalshi_market.get('no_price', 0)
        
        # Skip if we don't have complete price data
        if not all([poly_yes, poly_no, kalshi_yes, kalshi_no]):
            return opportunities
        
        # Ensure prices are in valid range
        if not self._validate_prices(poly_yes, poly_no, kalshi_yes, kalshi_no):
            return opportunities
        
        # Volume data
        poly_volume = poly_market.get('volume_24hr', 0)
        kalshi_volume = kalshi_market.get('volume_24hr', 0)
        
        # Check minimum volume requirements
        if (poly_volume < self.poly_config.get("min_volume", 100) or 
            kalshi_volume < self.kalshi_config.get("min_volume", 50)):
            return opportunities
        
        # Check for YES token arbitrage opportunities
        yes_opportunities = self._check_outcome_arbitrage(
            match, poly_market, kalshi_market, "yes",
            poly_yes, kalshi_yes, poly_volume, kalshi_volume
        )
        opportunities.extend(yes_opportunities)
        
        # Check for NO token arbitrage opportunities
        no_opportunities = self._check_outcome_arbitrage(
            match, poly_market, kalshi_market, "no",
            poly_no, kalshi_no, poly_volume, kalshi_volume
        )
        opportunities.extend(no_opportunities)
        
        return opportunities
    
    def _check_outcome_arbitrage(self, match: MarketMatch, poly_market: Dict, 
                               kalshi_market: Dict, outcome: str,
                               poly_price: float, kalshi_price: float,
                               poly_volume: float, kalshi_volume: float) -> List[ArbitrageOpportunity]:
        """Check for arbitrage opportunities for a specific outcome"""
        opportunities = []
        
        # Calculate potential profits in both directions
        
        # Strategy 1: Buy on Polymarket, sell on Kalshi
        if poly_price < kalshi_price:
            profit_1 = self._calculate_profit(
                buy_price=poly_price,
                sell_price=kalshi_price,
                buy_platform="polymarket",
                sell_platform="kalshi",
                volume=min(poly_volume, kalshi_volume)
            )
            
            if profit_1 and profit_1["profit_percentage"] >= self.min_profit_threshold:
                opportunity = ArbitrageOpportunity(
                    polymarket_id=match.polymarket_id,
                    kalshi_id=match.kalshi_id,
                    polymarket_question=match.polymarket_question,
                    kalshi_question=match.kalshi_question,
                    poly_yes_price=poly_market.get('yes_price', 0),
                    poly_no_price=poly_market.get('no_price', 0),
                    kalshi_yes_price=kalshi_market.get('yes_price', 0),
                    kalshi_no_price=kalshi_market.get('no_price', 0),
                    poly_volume=poly_volume,
                    kalshi_volume=kalshi_volume,
                    profit_potential=profit_1["profit_potential"],
                    profit_percentage=profit_1["profit_percentage"],
                    required_capital=profit_1["required_capital"],
                    max_position_size=profit_1["max_position_size"],
                    strategy="buy_poly_sell_kalshi",
                    outcome=outcome,
                    slippage_adjusted_profit=profit_1["slippage_adjusted_profit"],
                    fee_adjusted_profit=profit_1["fee_adjusted_profit"],
                    confidence_score=self._calculate_confidence_score(profit_1, match.confidence),
                    detected_at=datetime.now(),
                    match_confidence=match.confidence,
                    notes=f"Buy {outcome} on Polymarket @ ${poly_price:.3f}, sell on Kalshi @ ${kalshi_price:.3f}"
                )
                opportunities.append(opportunity)
        
        # Strategy 2: Buy on Kalshi, sell on Polymarket
        if kalshi_price < poly_price:
            profit_2 = self._calculate_profit(
                buy_price=kalshi_price,
                sell_price=poly_price,
                buy_platform="kalshi",
                sell_platform="polymarket",
                volume=min(poly_volume, kalshi_volume)
            )
            
            if profit_2 and profit_2["profit_percentage"] >= self.min_profit_threshold:
                opportunity = ArbitrageOpportunity(
                    polymarket_id=match.polymarket_id,
                    kalshi_id=match.kalshi_id,
                    polymarket_question=match.polymarket_question,
                    kalshi_question=match.kalshi_question,
                    poly_yes_price=poly_market.get('yes_price', 0),
                    poly_no_price=poly_market.get('no_price', 0),
                    kalshi_yes_price=kalshi_market.get('yes_price', 0),
                    kalshi_no_price=kalshi_market.get('no_price', 0),
                    poly_volume=poly_volume,
                    kalshi_volume=kalshi_volume,
                    profit_potential=profit_2["profit_potential"],
                    profit_percentage=profit_2["profit_percentage"],
                    required_capital=profit_2["required_capital"],
                    max_position_size=profit_2["max_position_size"],
                    strategy="buy_kalshi_sell_poly",
                    outcome=outcome,
                    slippage_adjusted_profit=profit_2["slippage_adjusted_profit"],
                    fee_adjusted_profit=profit_2["fee_adjusted_profit"],
                    confidence_score=self._calculate_confidence_score(profit_2, match.confidence),
                    detected_at=datetime.now(),
                    match_confidence=match.confidence,
                    notes=f"Buy {outcome} on Kalshi @ ${kalshi_price:.3f}, sell on Polymarket @ ${poly_price:.3f}"
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def _calculate_profit(self, buy_price: float, sell_price: float,
                         buy_platform: str, sell_platform: str,
                         volume: float) -> Optional[Dict[str, Any]]:
        """Calculate profit metrics for a trade"""
        try:
            # Get platform fee rates
            buy_fee_rate = self.poly_config.get("fee_rate", 0.02) if buy_platform == "polymarket" else self.kalshi_config.get("fee_rate", 0.01)
            sell_fee_rate = self.poly_config.get("fee_rate", 0.02) if sell_platform == "polymarket" else self.kalshi_config.get("fee_rate", 0.01)
            
            # Calculate gross profit per unit
            gross_profit_per_unit = sell_price - buy_price
            
            # Calculate fees
            buy_fee = buy_price * buy_fee_rate
            sell_fee = sell_price * sell_fee_rate
            total_fees = buy_fee + sell_fee
            
            # Net profit per unit after fees
            net_profit_per_unit = gross_profit_per_unit - total_fees
            
            # Calculate slippage adjustment
            slippage_adjustment = (buy_price + sell_price) * self.slippage_buffer / 2
            slippage_adjusted_profit = net_profit_per_unit - slippage_adjustment
            
            # Calculate position size based on volume and capital limits
            max_position_by_volume = min(volume * 0.1, 1000)  # Max 10% of volume or $1000
            max_position_by_capital = self.max_position_size
            max_position_size = min(max_position_by_volume, max_position_by_capital)
            
            # Calculate required capital
            required_capital = buy_price * (max_position_size / buy_price)
            
            # Calculate total profits
            gross_profit_total = gross_profit_per_unit * (max_position_size / buy_price)
            net_profit_total = net_profit_per_unit * (max_position_size / buy_price)
            slippage_adjusted_total = slippage_adjusted_profit * (max_position_size / buy_price)
            
            # Calculate profit percentages
            profit_percentage = (net_profit_per_unit / buy_price) if buy_price > 0 else 0
            
            return {
                "profit_potential": net_profit_total,
                "profit_percentage": profit_percentage,
                "required_capital": required_capital,
                "max_position_size": max_position_size,
                "slippage_adjusted_profit": slippage_adjusted_total,
                "fee_adjusted_profit": net_profit_total,
                "gross_profit": gross_profit_total,
                "total_fees": total_fees * (max_position_size / buy_price),
                "buy_fee_rate": buy_fee_rate,
                "sell_fee_rate": sell_fee_rate
            }
            
        except Exception as e:
            logging.error(f"Error calculating profit: {e}")
            return None
    
    def _validate_prices(self, poly_yes: float, poly_no: float, 
                        kalshi_yes: float, kalshi_no: float) -> bool:
        """Validate that prices are reasonable"""
        prices = [poly_yes, poly_no, kalshi_yes, kalshi_no]
        
        # Check if all prices are positive and within reasonable range
        if not all(0 < price <= 1.0 for price in prices):
            return False
            
        # Check if YES + NO prices are approximately 1.0 (within tolerance)
        poly_sum = poly_yes + poly_no
        kalshi_sum = kalshi_yes + kalshi_no
        
        if not (0.95 <= poly_sum <= 1.05 and 0.95 <= kalshi_sum <= 1.05):
            return False
            
        return True
    
    def _calculate_confidence_score(self, profit_data: Dict, match_confidence: float) -> float:
        """Calculate confidence score for an opportunity"""
        # Base confidence from market matching
        base_confidence = match_confidence
        
        # Adjust based on profit margin (higher profit = higher confidence)
        profit_factor = min(profit_data["profit_percentage"] / 0.1, 1.0)  # Cap at 10% profit
        
        # Adjust based on volume (higher volume = higher confidence)
        volume_factor = min(profit_data["max_position_size"] / 1000, 1.0)
        
        # Adjust based on slippage buffer (lower slippage impact = higher confidence)
        slippage_factor = max(0.1, profit_data["slippage_adjusted_profit"] / profit_data["profit_potential"])
        
        # Combine factors
        confidence = base_confidence * profit_factor * volume_factor * slippage_factor
        
        return min(confidence, 1.0)
    
    def _filter_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Filter opportunities based on minimum criteria"""
        filtered = []
        
        for opp in opportunities:
            # Check minimum profit threshold
            if opp.profit_percentage < self.min_profit_threshold:
                continue
                
            # Check minimum capital requirement
            if opp.required_capital < 10:  # Minimum $10 trade
                continue
                
            # Check confidence score
            if opp.confidence_score < 0.5:  # Minimum 50% confidence
                continue
                
            # Check if opportunity is still valid (not expired)
            if opp.expires_at and datetime.now() > opp.expires_at:
                continue
                
            filtered.append(opp)
        
        return filtered
    
    def _rank_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Rank opportunities by attractiveness"""
        # Calculate ranking score for each opportunity
        for opp in opportunities:
            # Score is weighted combination of:
            # - Profit percentage (40%)
            # - Confidence score (30%)
            # - Position size (20%)
            # - Match confidence (10%)
            
            profit_score = min(opp.profit_percentage / 0.2, 1.0)  # Normalize to 20% max
            confidence_score = opp.confidence_score
            position_score = min(opp.max_position_size / 1000, 1.0)  # Normalize to $1000 max
            match_score = opp.match_confidence
            
            ranking_score = (
                profit_score * 0.4 +
                confidence_score * 0.3 +
                position_score * 0.2 +
                match_score * 0.1
            )
            
            # Store ranking score in notes for reference
            opp.notes += f" | Rank: {ranking_score:.3f}"
        
        # Sort by ranking score (descending)
        opportunities.sort(key=lambda x: float(x.notes.split("Rank: ")[1].split("|")[0]), reverse=True)
        
        return opportunities
    
    def get_opportunity_summary(self, opportunities: List[ArbitrageOpportunity]) -> Dict[str, Any]:
        """Get summary statistics for opportunities"""
        if not opportunities:
            return {
                "total_opportunities": 0,
                "total_potential_profit": 0,
                "average_profit_percentage": 0,
                "highest_profit_opportunity": None,
                "total_required_capital": 0
            }
        
        total_profit = sum(opp.profit_potential for opp in opportunities)
        avg_profit_pct = sum(opp.profit_percentage for opp in opportunities) / len(opportunities)
        highest_profit = max(opportunities, key=lambda x: x.profit_potential)
        total_capital = sum(opp.required_capital for opp in opportunities)
        
        return {
            "total_opportunities": len(opportunities),
            "total_potential_profit": total_profit,
            "average_profit_percentage": avg_profit_pct,
            "highest_profit_opportunity": highest_profit,
            "total_required_capital": total_capital,
            "by_strategy": {
                "buy_poly_sell_kalshi": len([o for o in opportunities if o.strategy == "buy_poly_sell_kalshi"]),
                "buy_kalshi_sell_poly": len([o for o in opportunities if o.strategy == "buy_kalshi_sell_poly"])
            },
            "by_outcome": {
                "yes": len([o for o in opportunities if o.outcome == "yes"]),
                "no": len([o for o in opportunities if o.outcome == "no"])
            }
        }
