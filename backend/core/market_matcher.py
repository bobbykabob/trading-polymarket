"""
Market matching engine for finding equivalent markets across platforms
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from fuzzywuzzy import fuzz
import yaml
import re
from pathlib import Path
import os

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available, using fallback matching")

from backend.core.config import config


@dataclass
class MarketSimilarity:
    """Detailed similarity information for correlation display"""
    polymarket_market: Dict[str, Any]
    kalshi_market: Dict[str, Any]
    fuzzy_score: float
    semantic_score: float
    keyword_score: float
    overall_score: float
    match_type: str
    common_keywords: List[str]
    similarity_reasons: List[str]
    is_excluded: bool = False
    exclusion_reason: str = ""


@dataclass
class MarketMatch:
    """Represents a matched pair of markets"""
    polymarket_id: str
    kalshi_id: str
    polymarket_question: str
    kalshi_question: str
    confidence: float
    match_type: str  # "manual", "fuzzy", "semantic", "keyword"
    notes: str = ""


class MarketMatcher:
    """Handles market matching across platforms"""
    
    def __init__(self):
        self.config = config.get_arbitrage_config()
        self.matching_config = config.get("market_matching", {})
        self.manual_pairs = self._load_manual_pairs()
        self.excluded_pairs = self._load_excluded_pairs()
        self.sentence_model = None
        
        # Initialize semantic model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                model_name = self.matching_config.get("semantic_model", "all-MiniLM-L6-v2")
                self.sentence_model = SentenceTransformer(model_name)
                logging.info(f"Loaded semantic model: {model_name}")
            except Exception as e:
                logging.warning(f"Failed to load semantic model: {e}")
    
    def _load_manual_pairs(self) -> Dict[str, Dict[str, Any]]:
        """Load manually configured market pairs"""
        try:
            project_root = Path(__file__).parent.parent.parent
            pairs_path = project_root / "config" / "market_pairs.yaml"
            
            if not pairs_path.exists():
                return {}
                
            with open(pairs_path, 'r') as f:
                data = yaml.safe_load(f)
                
            pairs = {}
            for pair in data.get("pairs", []):
                key = f"{pair['polymarket_id']}_{pair['kalshi_id']}"
                pairs[key] = pair
                
            logging.info(f"Loaded {len(pairs)} manual market pairs")
            return pairs
            
        except Exception as e:
            logging.error(f"Error loading manual pairs: {e}")
            return {}
    
    def _load_excluded_pairs(self) -> Dict[str, Dict[str, Any]]:
        """Load excluded market pairs"""
        try:
            project_root = Path(__file__).parent.parent.parent
            pairs_path = project_root / "config" / "market_pairs.yaml"
            
            if not pairs_path.exists():
                return {}
                
            with open(pairs_path, 'r') as f:
                data = yaml.safe_load(f)
                
            excluded = {}
            for pair in data.get("excluded", []):
                key = f"{pair['polymarket_id']}_{pair['kalshi_id']}"
                excluded[key] = pair
                
            logging.info(f"Loaded {len(excluded)} excluded market pairs")
            return excluded
            
        except Exception as e:
            logging.error(f"Error loading excluded pairs: {e}")
            return {}
    
    def find_equivalent_markets(self, polymarket_markets: List[Dict], 
                               kalshi_markets: List[Dict]) -> List[MarketMatch]:
        """Find equivalent markets between platforms"""
        matches = []
        
        # First, check manual pairs
        manual_matches = self._find_manual_matches(polymarket_markets, kalshi_markets)
        matches.extend(manual_matches)
        
        # Get IDs of already matched markets
        matched_poly_ids = {m.polymarket_id for m in matches}
        matched_kalshi_ids = {m.kalshi_id for m in matches}
        
        # Filter out already matched markets
        remaining_poly = [m for m in polymarket_markets if m.get('id') not in matched_poly_ids]
        remaining_kalshi = [m for m in kalshi_markets if m.get('id') not in matched_kalshi_ids]
        
        # Find automatic matches
        auto_matches = self._find_automatic_matches(remaining_poly, remaining_kalshi)
        matches.extend(auto_matches)
        
        logging.info(f"Found {len(matches)} market matches ({len(manual_matches)} manual, {len(auto_matches)} automatic)")
        return matches
    
    def get_market_similarities(self, polymarket_markets: List[Dict], 
                               kalshi_markets: List[Dict], 
                               top_n: int = 10) -> List[MarketSimilarity]:
        """Get detailed similarity information for market correlation display"""
        similarities = []
        
        for poly_market in polymarket_markets:
            poly_id = poly_market.get('id')
            poly_question = poly_market.get('question', '')
            
            for kalshi_market in kalshi_markets:
                kalshi_id = kalshi_market.get('id')
                kalshi_question = kalshi_market.get('question', '')
                
                # Skip if this pair is excluded
                is_excluded = self._is_excluded_pair(poly_id, kalshi_id)
                exclusion_reason = ""
                if is_excluded:
                    exclusion_reason = self.excluded_pairs.get(f"{poly_id}_{kalshi_id}", {}).get('reason', 'Manually excluded')
                
                # Calculate all similarity scores
                fuzzy_score = self._fuzzy_match(poly_question, kalshi_question)
                semantic_score = self._semantic_match(poly_question, kalshi_question)
                keyword_score = self._keyword_match(poly_question, kalshi_question)
                
                # Calculate overall score (weighted average)
                overall_score = (
                    fuzzy_score * 0.4 + 
                    semantic_score * 0.4 + 
                    keyword_score * 0.2
                )
                
                # Determine match type
                best_score = max(fuzzy_score, semantic_score, keyword_score)
                if best_score == fuzzy_score:
                    match_type = "fuzzy"
                elif best_score == semantic_score:
                    match_type = "semantic"
                else:
                    match_type = "keyword"
                
                # Extract common keywords and similarity reasons
                common_keywords = self._extract_common_keywords(poly_question, kalshi_question)
                similarity_reasons = self._generate_similarity_reasons(
                    poly_question, kalshi_question, fuzzy_score, semantic_score, keyword_score
                )
                
                similarity = MarketSimilarity(
                    polymarket_market=poly_market,
                    kalshi_market=kalshi_market,
                    fuzzy_score=fuzzy_score,
                    semantic_score=semantic_score,
                    keyword_score=keyword_score,
                    overall_score=overall_score,
                    match_type=match_type,
                    common_keywords=common_keywords,
                    similarity_reasons=similarity_reasons,
                    is_excluded=is_excluded,
                    exclusion_reason=exclusion_reason
                )
                similarities.append(similarity)
        
        # Sort by overall score and return top N
        similarities.sort(key=lambda x: x.overall_score, reverse=True)
        return similarities[:top_n]
    
    def _find_manual_matches(self, polymarket_markets: List[Dict], 
                            kalshi_markets: List[Dict]) -> List[MarketMatch]:
        """Find manually configured market matches"""
        matches = []
        
        # Create lookup dictionaries
        poly_lookup = {m.get('id'): m for m in polymarket_markets}
        kalshi_lookup = {m.get('id'): m for m in kalshi_markets}
        
        for pair_data in self.manual_pairs.values():
            poly_id = pair_data['polymarket_id']
            kalshi_id = pair_data['kalshi_id']
            
            poly_market = poly_lookup.get(poly_id)
            kalshi_market = kalshi_lookup.get(kalshi_id)
            
            if poly_market and kalshi_market:
                match = MarketMatch(
                    polymarket_id=poly_id,
                    kalshi_id=kalshi_id,
                    polymarket_question=poly_market.get('question', ''),
                    kalshi_question=kalshi_market.get('question', ''),
                    confidence=pair_data.get('confidence', 1.0),
                    match_type="manual",
                    notes=pair_data.get('notes', '')
                )
                matches.append(match)
                
        return matches
    
    def _find_automatic_matches(self, polymarket_markets: List[Dict], 
                               kalshi_markets: List[Dict]) -> List[MarketMatch]:
        """Find automatic market matches using fuzzy and semantic matching"""
        matches = []
        threshold = self.matching_config.get("similarity_threshold", 0.8)
        
        for poly_market in polymarket_markets:
            poly_id = poly_market.get('id')
            poly_question = poly_market.get('question', '')
            
            if not poly_id or not poly_question:
                continue
                
            best_match = None
            best_score = 0
            best_method = ""
            
            for kalshi_market in kalshi_markets:
                kalshi_id = kalshi_market.get('id')
                kalshi_question = kalshi_market.get('question', '')
                
                if not kalshi_id or not kalshi_question:
                    continue
                
                # Check if this pair is excluded
                if self._is_excluded_pair(poly_id, kalshi_id):
                    continue
                
                # Try fuzzy matching
                fuzzy_score = self._fuzzy_match(poly_question, kalshi_question)
                if fuzzy_score > best_score:
                    best_score = fuzzy_score
                    best_match = kalshi_market
                    best_method = "fuzzy"
                
                # Try semantic matching if available
                if self.sentence_model:
                    semantic_score = self._semantic_match(poly_question, kalshi_question)
                    if semantic_score > best_score:
                        best_score = semantic_score
                        best_match = kalshi_market
                        best_method = "semantic"
                
                # Try keyword matching
                keyword_score = self._keyword_match(poly_question, kalshi_question)
                if keyword_score > best_score:
                    best_score = keyword_score
                    best_match = kalshi_market
                    best_method = "keyword"
            
            # Add match if confidence is above threshold
            if best_match and best_score >= threshold:
                match = MarketMatch(
                    polymarket_id=poly_id,
                    kalshi_id=best_match['id'],
                    polymarket_question=poly_question,
                    kalshi_question=best_match.get('question', ''),
                    confidence=best_score,
                    match_type=best_method,
                    notes=f"Auto-matched using {best_method} (score: {best_score:.3f})"
                )
                matches.append(match)
                
        return matches
    
    def _is_excluded_pair(self, poly_id: str, kalshi_id: str) -> bool:
        """Check if a pair is in the excluded list"""
        key = f"{poly_id}_{kalshi_id}"
        return key in self.excluded_pairs
    
    def _fuzzy_match(self, question1: str, question2: str) -> float:
        """Calculate fuzzy string similarity"""
        try:
            # Clean questions
            q1 = self._clean_question(question1)
            q2 = self._clean_question(question2)
            
            # Use token sort ratio for better matching
            score = fuzz.token_sort_ratio(q1, q2)
            return score / 100.0  # Convert to 0-1 scale
            
        except Exception as e:
            logging.error(f"Error in fuzzy matching: {e}")
            return 0.0
    
    def _semantic_match(self, question1: str, question2: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        try:
            if not self.sentence_model:
                return 0.0
                
            # Clean questions
            q1 = self._clean_question(question1)
            q2 = self._clean_question(question2)
            
            # Get embeddings
            embeddings = self.sentence_model.encode([q1, q2])
            
            # Calculate cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            return float(similarity)
            
        except Exception as e:
            logging.error(f"Error in semantic matching: {e}")
            return 0.0
    
    def _keyword_match(self, question1: str, question2: str) -> float:
        """Calculate keyword-based similarity"""
        try:
            # Clean and tokenize
            q1_words = set(self._clean_question(question1).lower().split())
            q2_words = set(self._clean_question(question2).lower().split())
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'will', 'be', 'is', 'are', 'was', 'were'}
            q1_words = q1_words - stop_words
            q2_words = q2_words - stop_words
            
            if not q1_words or not q2_words:
                return 0.0
            
            # Calculate Jaccard similarity
            intersection = len(q1_words & q2_words)
            union = len(q1_words | q2_words)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logging.error(f"Error in keyword matching: {e}")
            return 0.0
    
    def _clean_question(self, question: str) -> str:
        """Clean and normalize question text"""
        # Remove extra whitespace
        question = re.sub(r'\s+', ' ', question.strip())
        
        # Remove special characters but keep letters, numbers, and basic punctuation
        question = re.sub(r'[^\w\s\?\.\!\-\:]', '', question)
        
        # Normalize common variations
        question = question.replace('2024', '24')
        question = question.replace('2025', '25')
        
        return question
    
    def add_manual_pair(self, polymarket_id: str, kalshi_id: str, 
                       confidence: float = 1.0, notes: str = ""):
        """Add a new manual market pair"""
        try:
            project_root = Path(__file__).parent.parent.parent
            pairs_path = project_root / "config" / "market_pairs.yaml"
            
            # Load existing data
            data = {"pairs": [], "excluded": []}
            if pairs_path.exists():
                with open(pairs_path, 'r') as f:
                    data = yaml.safe_load(f) or data
            
            # Add new pair
            new_pair = {
                "polymarket_id": polymarket_id,
                "kalshi_id": kalshi_id,
                "confidence": confidence,
                "notes": notes
            }
            data["pairs"].append(new_pair)
            
            # Save back to file
            with open(pairs_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            # Update in-memory cache
            key = f"{polymarket_id}_{kalshi_id}"
            self.manual_pairs[key] = new_pair
            
            logging.info(f"Added manual pair: {polymarket_id} <-> {kalshi_id}")
            
        except Exception as e:
            logging.error(f"Error adding manual pair: {e}")
    
    def remove_manual_pair(self, polymarket_id: str, kalshi_id: str):
        """Remove a manual market pair"""
        try:
            project_root = Path(__file__).parent.parent.parent
            pairs_path = project_root / "config" / "market_pairs.yaml"
            
            # Load existing data
            if not pairs_path.exists():
                return
                
            with open(pairs_path, 'r') as f:
                data = yaml.safe_load(f) or {"pairs": [], "excluded": []}
            
            # Remove the pair
            data["pairs"] = [p for p in data["pairs"] 
                           if not (p["polymarket_id"] == polymarket_id and p["kalshi_id"] == kalshi_id)]
            
            # Save back to file
            with open(pairs_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            # Update in-memory cache
            key = f"{polymarket_id}_{kalshi_id}"
            self.manual_pairs.pop(key, None)
            
            logging.info(f"Removed manual pair: {polymarket_id} <-> {kalshi_id}")
            
        except Exception as e:
            logging.error(f"Error removing manual pair: {e}")
    
    def _extract_common_keywords(self, question1: str, question2: str) -> List[str]:
        """Extract common keywords between two questions"""
        try:
            # Clean and tokenize questions
            q1_clean = self._clean_question(question1).lower()
            q2_clean = self._clean_question(question2).lower()
            
            # Split into words and remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'will', 'be', 'is', 'are', 'was', 'were'}
            
            words1 = set(word for word in q1_clean.split() if word not in stop_words and len(word) > 2)
            words2 = set(word for word in q2_clean.split() if word not in stop_words and len(word) > 2)
            
            common = words1.intersection(words2)
            return sorted(list(common))
            
        except Exception as e:
            logging.error(f"Error extracting common keywords: {e}")
            return []
    
    def _generate_similarity_reasons(self, question1: str, question2: str, 
                                   fuzzy_score: float, semantic_score: float, 
                                   keyword_score: float) -> List[str]:
        """Generate human-readable reasons for similarity"""
        reasons = []
        
        try:
            # Fuzzy matching reasons
            if fuzzy_score > 0.8:
                reasons.append("Very similar wording and structure")
            elif fuzzy_score > 0.6:
                reasons.append("Similar wording with some differences")
            elif fuzzy_score > 0.4:
                reasons.append("Some common phrases detected")
            
            # Semantic matching reasons
            if semantic_score > 0.8:
                reasons.append("Very similar meaning and context")
            elif semantic_score > 0.6:
                reasons.append("Similar conceptual meaning")
            elif semantic_score > 0.4:
                reasons.append("Some semantic overlap")
            
            # Keyword matching reasons
            if keyword_score > 0.7:
                reasons.append("Many shared keywords")
            elif keyword_score > 0.5:
                reasons.append("Several common keywords")
            elif keyword_score > 0.3:
                reasons.append("Some shared keywords")
            
            # Add specific pattern matching
            q1_lower = question1.lower()
            q2_lower = question2.lower()
            
            # Check for similar patterns
            if any(pattern in q1_lower and pattern in q2_lower for pattern in ['election', 'vote', 'win', 'president']):
                reasons.append("Both relate to elections/politics")
            elif any(pattern in q1_lower and pattern in q2_lower for pattern in ['price', 'market', 'stock', 'crypto']):
                reasons.append("Both relate to financial markets")
            elif any(pattern in q1_lower and pattern in q2_lower for pattern in ['sports', 'team', 'game', 'season']):
                reasons.append("Both relate to sports events")
            
        except Exception as e:
            logging.error(f"Error generating similarity reasons: {e}")
            reasons.append("Error analyzing similarity")
        
        return reasons if reasons else ["Low similarity detected"]
