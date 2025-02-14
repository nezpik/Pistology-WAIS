from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class ContextItem:
    type: str
    content: Any
    timestamp: str
    source_agent: str
    relevance_score: float = 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)

class ContextManager:
    def __init__(self):
        self.context_store = {}
        self.agent_contexts = {}
        self.shared_knowledge = []
        
    def add_context(self, conversation_id: str, context_item: ContextItem) -> None:
        """Add a new context item to the conversation."""
        if conversation_id not in self.context_store:
            self.context_store[conversation_id] = []
            
        self.context_store[conversation_id].append(context_item.to_dict())
        
        # Update shared knowledge if relevance is high
        if context_item.relevance_score > 0.8:
            self.shared_knowledge.append(context_item.to_dict())
            
    def get_relevant_context(self, conversation_id: str, query: str, max_items: int = 5) -> List[Dict]:
        """Get context items relevant to the current query."""
        if conversation_id not in self.context_store:
            return []
            
        # Implement context relevance scoring
        scored_items = [
            (item, self._calculate_relevance(item, query))
            for item in self.context_store[conversation_id]
        ]
        
        # Sort by relevance and return top items
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in scored_items[:max_items]]
        
    def update_agent_context(self, agent_id: str, context_update: Dict) -> None:
        """Update context for a specific agent."""
        if agent_id not in self.agent_contexts:
            self.agent_contexts[agent_id] = {}
            
        self.agent_contexts[agent_id].update(context_update)
        
    def get_agent_context(self, agent_id: str) -> Optional[Dict]:
        """Get the current context for an agent."""
        return self.agent_contexts.get(agent_id)
        
    def merge_contexts(self, context_items: List[Dict]) -> Dict:
        """Merge multiple context items into a consolidated view."""
        merged = {
            'summary': [],
            'key_points': set(),
            'decisions': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        for item in context_items:
            if 'content' in item:
                content = item['content']
                if isinstance(content, dict):
                    # Extract key points
                    if 'key_points' in content:
                        merged['key_points'].update(content['key_points'])
                    
                    # Collect decisions
                    if 'decisions' in content:
                        merged['decisions'].extend(content['decisions'])
                        
                    # Add to summary if relevant
                    if 'summary' in content:
                        merged['summary'].append(content['summary'])
                        
        # Convert set to list for JSON serialization
        merged['key_points'] = list(merged['key_points'])
        
        return merged
        
    def _calculate_relevance(self, item: Dict, query: str) -> float:
        """Calculate relevance score between context item and query."""
        # Implement relevance calculation logic
        # This is a simplified version - in practice, you might want to use
        # more sophisticated NLP techniques
        
        relevance = 0.0
        if 'content' in item:
            content = item['content']
            if isinstance(content, dict):
                # Check key points
                if 'key_points' in content:
                    for point in content['key_points']:
                        if any(term in point.lower() for term in query.lower().split()):
                            relevance += 0.3
                            
                # Check summary
                if 'summary' in content:
                    if any(term in content['summary'].lower() for term in query.lower().split()):
                        relevance += 0.4
                        
            elif isinstance(content, str):
                if any(term in content.lower() for term in query.lower().split()):
                    relevance += 0.5
                    
        return min(1.0, relevance)
        
    def prune_old_contexts(self, max_age_hours: int = 24) -> None:
        """Remove context items older than specified age."""
        current_time = datetime.utcnow()
        
        for conv_id in self.context_store:
            self.context_store[conv_id] = [
                item for item in self.context_store[conv_id]
                if self._is_recent(item['timestamp'], current_time, max_age_hours)
            ]
            
    def _is_recent(self, timestamp_str: str, current_time: datetime, max_age_hours: int) -> bool:
        """Check if a timestamp is within the specified age limit."""
        item_time = datetime.fromisoformat(timestamp_str)
        age = current_time - item_time
        return age.total_seconds() < (max_age_hours * 3600)
