"""
Enhanced service layer for comprehensive agent performance evaluation using configuration
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import re
import statistics

from .models import ConversationData, ConversationResponse, Tweet, Classification
from .config_loader import config_loader, KPIConfig
from .service import ConversationAnalysisService


class EnhancedPerformanceAnalysisService:
    """Enhanced service for comprehensive agent performance analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_loader = config_loader
        self.base_service = ConversationAnalysisService()
        
        # Load configuration
        try:
            self.config = self.config_loader.load_config()
            self.logger.info("Configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def analyze_conversation_comprehensive(self, conversation_data: ConversationData) -> Dict[str, Any]:
        """
        Perform comprehensive analysis based on configuration
        
        Args:
            conversation_data: Input conversation data
            
        Returns:
            Dictionary with comprehensive performance metrics
        """
        results = {
            "conversation_id": getattr(conversation_data, 'conversation_id', 'unknown'),
            "analysis_timestamp": datetime.now().isoformat(),
            "categories": {}
        }
        
        # Analyze each category
        for category_key in self.config_loader.get_all_categories():
            category_results = self._analyze_category(conversation_data, category_key)
            results["categories"][category_key] = category_results
        
        # Calculate overall scores
        results["overall_performance"] = self._calculate_overall_performance(results["categories"])
        
        return results
    
    def _analyze_category(self, conversation_data: ConversationData, category: str) -> Dict[str, Any]:
        """Analyze a specific category"""
        category_kpis = self.config_loader.get_category_kpis(category)
        category_results = {
            "category_name": category,
            "kpis": {},
            "category_score": 0.0,
            "compliance_status": "Unknown"
        }
        
        total_score = 0.0
        total_kpis = 0
        compliant_kpis = 0
        
        for kpi_name, kpi_config in category_kpis.items():
            kpi_result = self._analyze_kpi(conversation_data, kpi_name, kpi_config, category)
            category_results["kpis"][kpi_name] = kpi_result
            
            if kpi_result["score"] is not None:
                total_score += kpi_result["score"]
                total_kpis += 1
                
                if kpi_result["meets_target"]:
                    compliant_kpis += 1
        
        # Calculate category score and compliance
        if total_kpis > 0:
            category_results["category_score"] = total_score / total_kpis
            compliance_rate = compliant_kpis / total_kpis
            
            if compliance_rate >= 0.9:
                category_results["compliance_status"] = "Excellent"
            elif compliance_rate >= 0.7:
                category_results["compliance_status"] = "Good"
            elif compliance_rate >= 0.5:
                category_results["compliance_status"] = "Moderate"
            else:
                category_results["compliance_status"] = "Needs Improvement"
        
        return category_results
    
    def _analyze_kpi(self, conversation_data: ConversationData, kpi_name: str, 
                    kpi_config: KPIConfig, category: str) -> Dict[str, Any]:
        """Analyze a specific KPI"""
        
        kpi_result = {
            "kpi_name": kpi_config.name,
            "description": kpi_config.description,
            "score": None,
            "normalized_score": None,
            "meets_target": False,
            "interpretation": "Unknown",
            "sub_scores": {},
            "recommendations": []
        }
        
        try:
            # Route to appropriate analysis method based on KPI
            if category == "accuracy_compliance":
                score = self._analyze_accuracy_compliance_kpi(conversation_data, kpi_name, kpi_config)
            elif category == "empathy_communication":
                score = self._analyze_empathy_communication_kpi(conversation_data, kpi_name, kpi_config)
            elif category == "efficiency_resolution":
                score = self._analyze_efficiency_resolution_kpi(conversation_data, kpi_name, kpi_config)
            else:
                self.logger.warning(f"Unknown category: {category}")
                return kpi_result
            
            # Normalize score to 0-1 range for comparison
            scale_range = kpi_config.scale.range
            if len(scale_range) == 2:
                min_val, max_val = scale_range
                normalized_score = (score - min_val) / (max_val - min_val) if max_val != min_val else 0.0
                normalized_score = max(0.0, min(1.0, normalized_score))  # Clamp to [0,1]
            else:
                normalized_score = score
            
            kpi_result.update({
                "score": score,
                "normalized_score": normalized_score,
                "meets_target": self.config_loader.evaluate_target_compliance(score, kpi_config.target),
                "interpretation": self.config_loader.get_interpretation(score, kpi_config)
            })
            
            # Generate recommendations
            kpi_result["recommendations"] = self._generate_recommendations(kpi_name, score, kpi_config)
            
        except Exception as e:
            self.logger.error(f"Error analyzing KPI {kpi_name}: {e}")
            kpi_result["error"] = str(e)
        
        return kpi_result
    
    def _analyze_accuracy_compliance_kpi(self, conversation_data: ConversationData, 
                                       kpi_name: str, kpi_config: KPIConfig) -> float:
        """Analyze accuracy and compliance KPIs"""
        
        if kpi_name == "resolution_completeness":
            return self._calculate_resolution_completeness(conversation_data)
        elif kpi_name == "accuracy_automated_responses":
            return self._calculate_automated_response_accuracy(conversation_data)
        else:
            self.logger.warning(f"Unknown accuracy/compliance KPI: {kpi_name}")
            return 0.0
    
    def _analyze_empathy_communication_kpi(self, conversation_data: ConversationData,
                                         kpi_name: str, kpi_config: KPIConfig) -> float:
        """Analyze empathy and communication KPIs"""
        
        if kpi_name == "empathy_score":
            return self._calculate_empathy_score(conversation_data, kpi_config)
        elif kpi_name == "sentiment_shift":
            return self._calculate_sentiment_shift(conversation_data)
        elif kpi_name == "clarity_language":
            return self._calculate_language_clarity(conversation_data, kpi_config)
        elif kpi_name == "cultural_sensitivity":
            return self._calculate_cultural_sensitivity(conversation_data)
        elif kpi_name == "adaptability_quotient":
            return self._calculate_adaptability_quotient(conversation_data)
        elif kpi_name == "conversation_flow":
            return self._calculate_conversation_flow(conversation_data)
        else:
            self.logger.warning(f"Unknown empathy/communication KPI: {kpi_name}")
            return 0.0
    
    def _analyze_efficiency_resolution_kpi(self, conversation_data: ConversationData,
                                         kpi_name: str, kpi_config: KPIConfig) -> float:
        """Analyze efficiency and resolution KPIs"""
        
        if kpi_name == "followup_necessity":
            return self._calculate_followup_necessity(conversation_data)
        elif kpi_name == "customer_effort_score":
            return self._calculate_customer_effort_score(conversation_data)
        elif kpi_name == "first_response_accuracy":
            return self._calculate_first_response_accuracy(conversation_data)
        elif kpi_name == "csat_resolution":
            return self._calculate_csat_resolution(conversation_data)
        elif kpi_name == "escalation_rate":
            return self._calculate_escalation_rate(conversation_data)
        elif kpi_name == "customer_effort_reduction":
            return self._calculate_effort_reduction(conversation_data)
        else:
            self.logger.warning(f"Unknown efficiency/resolution KPI: {kpi_name}")
            return 0.0
    
    # KPI Calculation Methods
    
    def _calculate_resolution_completeness(self, conversation_data: ConversationData) -> float:
        """Calculate resolution completeness (binary: 0 or 1)"""
        tweets = conversation_data.tweets
        classification = conversation_data.classification
        
        # Check for resolution indicators
        service_tweets = [t for t in tweets if t.role == "Service Provider"]
        if not service_tweets:
            return 0.0
        
        last_service_text = service_tweets[-1].text.lower()
        resolution_keywords = [
            "resolved", "fixed", "solved", "completed", "closed",
            "thank you", "glad to help", "issue has been", "problem is solved"
        ]
        
        if any(keyword in last_service_text for keyword in resolution_keywords):
            return 1.0
        
        # Check if customer expressed satisfaction
        customer_tweets = [t for t in tweets if t.role == "Customer"]
        if customer_tweets:
            last_customer_text = customer_tweets[-1].text.lower()
            satisfaction_keywords = ["thank", "thanks", "great", "perfect", "good"]
            if any(keyword in last_customer_text for keyword in satisfaction_keywords):
                return 1.0
        
        return 0.0
    
    def _calculate_automated_response_accuracy(self, conversation_data: ConversationData) -> float:
        """Calculate accuracy of automated responses"""
        # This would typically require additional data about which responses were automated
        # For now, we'll use a heuristic based on response patterns
        tweets = conversation_data.tweets
        service_tweets = [t for t in tweets if t.role == "Service Provider"]
        
        if not service_tweets:
            return 100.0
        
        # Simple heuristic - check for template-like responses
        accurate_responses = 0
        total_responses = len(service_tweets)
        
        for tweet in service_tweets:
            # Check if response is relevant to customer query
            # This is a simplified implementation
            if len(tweet.text) > 20 and not tweet.text.isupper():
                accurate_responses += 1
        
        return (accurate_responses / total_responses) * 100.0 if total_responses > 0 else 100.0
    
    def _calculate_empathy_score(self, conversation_data: ConversationData, kpi_config: KPIConfig) -> float:
        """Calculate comprehensive empathy score"""
        # Use existing empathy calculation from base service
        base_metrics = self.base_service._calculate_performance_metrics(conversation_data)
        
        # For now, use the sentiment-based approach from base service
        # In a full implementation, this would analyze sub-factors
        sentiment = conversation_data.classification.sentiment
        
        if sentiment == "Positive":
            return 8.5  # Strong empathy
        elif sentiment == "Neutral":
            return 6.0  # Moderate empathy
        else:
            return 4.0  # Limited empathy (but room for improvement)
    
    def _calculate_sentiment_shift(self, conversation_data: ConversationData) -> float:
        """Calculate sentiment shift from beginning to end"""
        tweets = conversation_data.tweets
        if len(tweets) < 2:
            return 0.0
        
        # Simplified approach - assume first customer tweet is initial sentiment
        # and classification sentiment is final sentiment
        initial_sentiment = self._analyze_tweet_sentiment(tweets[0].text)
        final_sentiment = self._sentiment_to_numeric(conversation_data.classification.sentiment)
        
        return final_sentiment - initial_sentiment
    
    def _calculate_language_clarity(self, conversation_data: ConversationData, kpi_config: KPIConfig) -> float:
        """Calculate language clarity score"""
        service_tweets = [t for t in conversation_data.tweets if t.role == "Service Provider"]
        if not service_tweets:
            return 5.0
        
        total_score = 0.0
        for tweet in service_tweets:
            # Simple readability heuristics
            text = tweet.text
            words = text.split()
            sentences = text.split('.')
            
            # Average word length (shorter is generally more readable)
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            readability_score = max(1, 10 - (avg_word_length - 4))  # Optimal around 4 chars per word
            
            # Sentence length (shorter sentences are clearer)
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            sentence_score = max(1, 10 - (avg_sentence_length - 15) / 5)  # Optimal around 15 words
            
            # Combined score
            tweet_score = (readability_score + sentence_score) / 2
            total_score += tweet_score
        
        return total_score / len(service_tweets)
    
    def _calculate_cultural_sensitivity(self, conversation_data: ConversationData) -> float:
        """Calculate cultural sensitivity index"""
        # Simplified implementation - check for inclusive language
        service_tweets = [t for t in conversation_data.tweets if t.role == "Service Provider"]
        if not service_tweets:
            return 4.0
        
        # Check for respectful language patterns
        total_score = 0.0
        for tweet in service_tweets:
            text = tweet.text.lower()
            score = 3.0  # Base score
            
            # Positive indicators
            if any(word in text for word in ["please", "thank you", "appreciate", "understand"]):
                score += 1.0
            
            # Negative indicators
            if any(word in text for word in ["must", "should", "cannot", "impossible"]):
                score -= 0.5
            
            total_score += min(5.0, max(1.0, score))
        
        return total_score / len(service_tweets)
    
    def _calculate_adaptability_quotient(self, conversation_data: ConversationData) -> float:
        """Calculate adaptability quotient"""
        # Check if responses adapt to customer's communication style
        tweets = conversation_data.tweets
        if len(tweets) < 2:
            return 50.0
        
        # Simple heuristic - check if service provider adjusts tone/style
        customer_tweets = [t for t in tweets if t.role == "Customer"]
        service_tweets = [t for t in tweets if t.role == "Service Provider"]
        
        if not customer_tweets or not service_tweets:
            return 70.0
        
        # Check if service provider uses similar language complexity
        customer_avg_length = statistics.mean(len(t.text.split()) for t in customer_tweets)
        service_avg_length = statistics.mean(len(t.text.split()) for t in service_tweets)
        
        # Score based on how well the lengths match (adaptation)
        length_diff = abs(customer_avg_length - service_avg_length)
        adaptability_score = max(50, 100 - (length_diff * 5))
        
        return min(100.0, adaptability_score)
    
    def _calculate_conversation_flow(self, conversation_data: ConversationData) -> float:
        """Calculate conversation flow smoothness"""
        tweets = conversation_data.tweets
        if len(tweets) < 2:
            return 3.0
        
        # Check for logical flow, minimal repetition
        flow_score = 4.0  # Base score
        
        # Check for repetitive content
        texts = [t.text.lower() for t in tweets]
        for i in range(len(texts) - 1):
            similarity = self._calculate_text_similarity(texts[i], texts[i + 1])
            if similarity > 0.7:  # High similarity indicates repetition
                flow_score -= 0.5
        
        return max(1.0, min(5.0, flow_score))
    
    def _calculate_followup_necessity(self, conversation_data: ConversationData) -> float:
        """Calculate follow-up necessity (binary: 0 or 1)"""
        # Check if conversation seems complete
        resolution_complete = self._calculate_resolution_completeness(conversation_data)
        
        if resolution_complete == 1.0:
            return 0.0  # No follow-up needed
        
        # Check for pending actions mentioned
        service_tweets = [t for t in conversation_data.tweets if t.role == "Service Provider"]
        if service_tweets:
            last_service_text = service_tweets[-1].text.lower()
            followup_indicators = [
                "follow up", "get back", "contact you", "will call", 
                "send you", "email you", "reach out"
            ]
            
            if any(indicator in last_service_text for indicator in followup_indicators):
                return 1.0  # Follow-up needed
        
        return 0.0  # No explicit follow-up mentioned
    
    def _calculate_customer_effort_score(self, conversation_data: ConversationData) -> float:
        """Calculate customer effort score"""
        tweets = conversation_data.tweets
        customer_tweets = [t for t in tweets if t.role == "Customer"]
        
        # Base score on number of customer interactions
        customer_interactions = len(customer_tweets)
        
        if customer_interactions == 1:
            return 1.0  # Very low effort
        elif customer_interactions <= 3:
            return 2.0  # Low effort
        elif customer_interactions <= 5:
            return 4.0  # Moderate effort
        else:
            return 6.0  # High effort
    
    def _calculate_first_response_accuracy(self, conversation_data: ConversationData) -> float:
        """Calculate first response accuracy"""
        tweets = conversation_data.tweets
        service_tweets = [t for t in tweets if t.role == "Service Provider"]
        
        if not service_tweets:
            return 0.0
        
        # Analyze first service provider response
        first_response = service_tweets[0].text.lower()
        
        # Check if it addresses the customer's concern
        customer_tweets = [t for t in tweets if t.role == "Customer"]
        if customer_tweets:
            customer_concern = customer_tweets[0].text.lower()
            
            # Simple keyword matching approach
            customer_keywords = set(customer_concern.split())
            response_keywords = set(first_response.split())
            
            # Calculate overlap
            overlap = len(customer_keywords.intersection(response_keywords))
            total_customer_words = len(customer_keywords)
            
            if total_customer_words > 0:
                accuracy = (overlap / total_customer_words) * 100
                return min(100.0, max(50.0, accuracy))  # At least 50% for trying
        
        return 75.0  # Default reasonable score
    
    def _calculate_csat_resolution(self, conversation_data: ConversationData) -> float:
        """Calculate customer satisfaction with resolution"""
        # This would typically come from customer feedback
        # For now, estimate based on resolution and sentiment
        
        resolution_complete = self._calculate_resolution_completeness(conversation_data)
        sentiment = conversation_data.classification.sentiment
        
        if resolution_complete == 1.0:
            if sentiment == "Positive":
                return 5.0
            elif sentiment == "Neutral":
                return 4.0
            else:
                return 3.5
        else:
            if sentiment == "Positive":
                return 4.0
            elif sentiment == "Neutral":
                return 3.0
            else:
                return 2.0
    
    def _calculate_escalation_rate(self, conversation_data: ConversationData) -> float:
        """Calculate escalation rate for this conversation"""
        # Check for escalation indicators
        tweets = conversation_data.tweets
        all_text = " ".join(t.text.lower() for t in tweets)
        
        escalation_keywords = [
            "manager", "supervisor", "escalate", "transfer", 
            "higher level", "someone else", "specialist"
        ]
        
        if any(keyword in all_text for keyword in escalation_keywords):
            return 100.0  # This conversation was escalated
        else:
            return 0.0  # No escalation needed
    
    def _calculate_effort_reduction(self, conversation_data: ConversationData) -> float:
        """Calculate customer effort reduction rate"""
        # This would require historical data for comparison
        # For now, return a placeholder based on current efficiency
        
        customer_effort = self._calculate_customer_effort_score(conversation_data)
        
        # Assume improvement if effort is low
        if customer_effort <= 2.0:
            return -15.0  # 15% reduction in effort
        elif customer_effort <= 4.0:
            return -5.0   # 5% reduction
        else:
            return 5.0    # 5% increase (needs improvement)
    
    # Helper methods
    
    def _analyze_tweet_sentiment(self, text: str) -> float:
        """Analyze sentiment of a tweet (simplified)"""
        text = text.lower()
        positive_words = ["good", "great", "excellent", "thank", "appreciate", "love", "perfect"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible", "disappointed"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 0.5
        elif negative_count > positive_count:
            return -0.5
        else:
            return 0.0
    
    def _sentiment_to_numeric(self, sentiment: str) -> float:
        """Convert sentiment string to numeric value"""
        sentiment_mapping = {
            "Positive": 0.5,
            "Neutral": 0.0,
            "Negative": -0.5
        }
        return sentiment_mapping.get(sentiment, 0.0)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simplified)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _generate_recommendations(self, kpi_name: str, score: float, kpi_config: KPIConfig) -> List[str]:
        """Generate recommendations based on KPI performance"""
        recommendations = []
        
        target_met = self.config_loader.evaluate_target_compliance(score, kpi_config.target)
        
        if not target_met:
            if kpi_name == "empathy_score":
                recommendations.extend([
                    "Use more empathetic language to acknowledge customer emotions",
                    "Include phrases like 'I understand your frustration'",
                    "Personalize responses by using the customer's name"
                ])
            elif kpi_name == "clarity_language":
                recommendations.extend([
                    "Use shorter, simpler sentences",
                    "Avoid technical jargon without explanation",
                    "Break complex information into smaller chunks"
                ])
            elif kpi_name == "resolution_completeness":
                recommendations.extend([
                    "Ensure all customer concerns are addressed",
                    "Ask for confirmation that the issue is resolved",
                    "Provide clear next steps if applicable"
                ])
            elif kpi_name == "customer_effort_score":
                recommendations.extend([
                    "Streamline the resolution process",
                    "Provide information proactively",
                    "Reduce the number of back-and-forth interactions"
                ])
            else:
                recommendations.append(f"Focus on improving {kpi_config.name} to meet the target of {kpi_config.target.description}")
        else:
            recommendations.append(f"Excellent performance in {kpi_config.name}! Keep up the good work.")
        
        return recommendations
    
    def _calculate_overall_performance(self, categories: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance across all categories"""
        total_score = 0.0
        total_categories = 0
        compliant_categories = 0
        
        category_scores = {}
        
        for category_name, category_data in categories.items():
            if "category_score" in category_data and category_data["category_score"] > 0:
                score = category_data["category_score"]
                category_scores[category_name] = score
                total_score += score
                total_categories += 1
                
                if category_data.get("compliance_status") in ["Excellent", "Good"]:
                    compliant_categories += 1
        
        overall_score = total_score / total_categories if total_categories > 0 else 0.0
        compliance_rate = compliant_categories / total_categories if total_categories > 0 else 0.0
        
        # Determine overall rating
        if overall_score >= 8.0 and compliance_rate >= 0.8:
            overall_rating = "Exceptional"
        elif overall_score >= 7.0 and compliance_rate >= 0.7:
            overall_rating = "Strong"
        elif overall_score >= 6.0 and compliance_rate >= 0.5:
            overall_rating = "Satisfactory"
        elif overall_score >= 4.0:
            overall_rating = "Needs Improvement"
        else:
            overall_rating = "Poor"
        
        return {
            "overall_score": overall_score,
            "compliance_rate": compliance_rate,
            "overall_rating": overall_rating,
            "category_scores": category_scores,
            "total_categories_evaluated": total_categories
        }


# Global enhanced service instance
enhanced_service = EnhancedPerformanceAnalysisService()
