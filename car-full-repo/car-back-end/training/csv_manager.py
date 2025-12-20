"""
CSV Manager - Handles loading and updating annotation CSV files
"""
import csv
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class CSVManager:
    """Manages CSV file for prompts and annotations"""
    
    def __init__(self, csv_path: Path):
        self.csv_path = Path(csv_path)
        self.rows: List[Dict[str, str]] = []
    
    def load(self) -> List[Dict[str, str]]:
        """
        Load CSV file and return rows as list of dictionaries
        
        Expected columns: id, prompt, annotated_json, completion_status
        (id is optional but will be preserved if present)
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        self.rows = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.rows.append(row)
        
        return self.rows
    
    def find_next_incomplete(self) -> Optional[Tuple[int, Dict[str, str]]]:
        """
        Find the first row that is not completed
        
        Returns:
            Tuple of (row_index, row_dict) or None if all complete
        """
        if not self.rows:
            self.load()
        
        # Completed statuses: true, 1, yes, completed, complete
        # Incomplete statuses: false, 0, no, incomplete, empty
        completed_statuses = ('true', '1', 'yes', 'completed', 'complete')
        
        for idx, row in enumerate(self.rows):
            completion_status = row.get('completion_status', '').strip().lower()
            if completion_status not in completed_statuses:
                return (idx, row)
        
        return None
    
    def update_row(self, row_index: int, annotated_json: dict, completed: bool = True):
        """
        Update a row with annotated JSON and completion status
        
        Args:
            row_index: Index of row to update
            annotated_json: The annotated JSON object
            completed: Whether annotation is complete
        
        Note: Preserves all existing columns (e.g., 'id') when updating
        """
        if row_index >= len(self.rows):
            raise IndexError(f"Row index {row_index} out of range")
        
        # Update the row (preserves all existing columns like 'id')
        self.rows[row_index]['annotated_json'] = json.dumps(annotated_json, indent=2)
        # Use 'complete' for completed, 'incomplete' for incomplete (matches CSV format)
        self.rows[row_index]['completion_status'] = 'complete' if completed else 'incomplete'
    
    def save(self):
        """
        Save updated rows back to CSV file
        
        Preserves all columns including 'id' if present
        """
        if not self.rows:
            return
        
        # Get fieldnames from first row (preserves column order including 'id')
        fieldnames = list(self.rows[0].keys())
        
        with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.rows)
    
    def get_annotated_json(self, row_index: int) -> Optional[dict]:
        """
        Get the annotated JSON from a row, if it exists
        
        Returns:
            Parsed JSON dict or None if empty/invalid
        """
        if row_index >= len(self.rows):
            return None
        
        json_str = self.rows[row_index].get('annotated_json', '').strip()
        if not json_str:
            return None
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None


