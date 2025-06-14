import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.config import settings

class JSONDatabase:
    def __init__(self):
        self.data_dir = settings.data_dir
        self.files = {
            'users': os.path.join(self.data_dir, 'users.json'),
            'courses': os.path.join(self.data_dir, 'courses.json'),
            'tutorials': os.path.join(self.data_dir, 'tutorials.json'),
            'articles': os.path.join(self.data_dir, 'articles.json'),
            'quizzes': os.path.join(self.data_dir, 'quizzes.json'),
            'enrollments': os.path.join(self.data_dir, 'enrollments.json'),
            'completions': os.path.join(self.data_dir, 'completions.json'),
            'bookmarks': os.path.join(self.data_dir, 'bookmarks.json'),
            'likes': os.path.join(self.data_dir, 'likes.json'),
            'quiz_attempts': os.path.join(self.data_dir, 'quiz_attempts.json'),
        }
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with empty data if they don't exist"""
        for file_path in self.files.values():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def _load_data(self, table: str) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        if table not in self.files:
            return []
        
        try:
            with open(self.files[table], 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, table: str, data: List[Dict[str, Any]]):
        """Save data to JSON file"""
        if table not in self.files:
            return
        
        with open(self.files[table], 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _get_next_id(self, table: str) -> int:
        """Get next available ID for a table"""
        data = self._load_data(table)
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1
    
    def create(self, table: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item in the table"""
        data = self._load_data(table)
        item['id'] = self._get_next_id(table)
        item['created_at'] = datetime.now().isoformat()
        item['updated_at'] = datetime.now().isoformat()
        data.append(item)
        self._save_data(table, data)
        return item
    
    def read(self, table: str, item_id: int) -> Optional[Dict[str, Any]]:
        """Read an item by ID"""
        data = self._load_data(table)
        for item in data:
            if item.get('id') == item_id:
                return item
        return None
    
    def read_all(self, table: str) -> List[Dict[str, Any]]:
        """Read all items from a table"""
        return self._load_data(table)
    
    def update(self, table: str, item_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an item by ID"""
        data = self._load_data(table)
        for i, item in enumerate(data):
            if item.get('id') == item_id:
                data[i].update(updates)
                data[i]['updated_at'] = datetime.now().isoformat()
                self._save_data(table, data)
                return data[i]
        return None
    
    def delete(self, table: str, item_id: int) -> bool:
        """Delete an item by ID"""
        data = self._load_data(table)
        for i, item in enumerate(data):
            if item.get('id') == item_id:
                data.pop(i)
                self._save_data(table, data)
                return True
        return False
    
    def find_by_field(self, table: str, field: str, value: Any) -> List[Dict[str, Any]]:
        """Find items by a specific field value"""
        data = self._load_data(table)
        return [item for item in data if item.get(field) == value]
    
    def find_one_by_field(self, table: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Find one item by a specific field value"""
        results = self.find_by_field(table, field, value)
        return results[0] if results else None
    
    def search(self, table: str, search_term: str, fields: List[str]) -> List[Dict[str, Any]]:
        """Search items by multiple fields"""
        data = self._load_data(table)
        results = []
        search_term = search_term.lower()
        
        for item in data:
            for field in fields:
                if field in item and search_term in str(item[field]).lower():
                    results.append(item)
                    break
        
        return results

# Global database instance
db = JSONDatabase() 