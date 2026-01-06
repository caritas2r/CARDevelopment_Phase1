#!/usr/bin/env python3
"""
Simple prompt viewer - displays prompts from CSV with keyboard navigation
- Space: Next prompt
- Number + Enter: Jump to prompt number
"""
import csv
import tkinter as tk
from pathlib import Path
from typing import List, Dict

class PromptViewer:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.prompts: List[Dict[str, str]] = []
        self.current_index = 0
        self.number_buffer = ""
        
        # Load prompts
        self.load_prompts()
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Prompt Viewer")
        self.root.geometry("900x400")
        self.root.resizable(True, True)
        
        # Center window
        self.root.update_idletasks()
        width = 900
        height = 400
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Prompt number label
        self.number_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 12, "bold"),
            fg="gray"
        )
        self.number_label.pack(anchor="w", pady=(0, 10))
        
        # Prompt text display
        self.text_widget = tk.Text(
            main_frame,
            wrap=tk.WORD,
            font=("Arial", 14),
            bg="#f5f5f5",
            fg="#333333",
            padx=15,
            pady=15,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Instructions label
        instructions = tk.Label(
            main_frame,
            text="Space: Next prompt | Number + Enter: Jump to prompt",
            font=("Arial", 9),
            fg="gray"
        )
        instructions.pack(pady=(10, 0))
        
        # Bind keyboard events
        self.root.bind('<KeyPress-space>', self.on_space)
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<Return>', self.on_enter)
        
        # Focus on window to receive keyboard events
        self.root.focus_set()
        
        # Display first prompt
        self.display_current_prompt()
    
    def load_prompts(self):
        """Load prompts from CSV file"""
        if not self.csv_path.exists():
            print(f"Error: CSV file not found: {self.csv_path}")
            return
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    prompt_text = row.get('prompt', '').strip()
                    if prompt_text:
                        self.prompts.append({
                            'id': row.get('id', '').strip(),
                            'prompt': prompt_text
                        })
        except Exception as e:
            print(f"Error loading prompts: {e}")
    
    def display_current_prompt(self):
        """Display the current prompt"""
        if not self.prompts:
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", "No prompts found in CSV file.")
            self.number_label.config(text="")
            return
        
        if 0 <= self.current_index < len(self.prompts):
            prompt_data = self.prompts[self.current_index]
            prompt_id = prompt_data.get('id', '')
            prompt_text = prompt_data.get('prompt', '')
            
            # Update number label
            self.number_label.config(text=f"Prompt {self.current_index + 1} of {len(self.prompts)}" + (f" (ID: {prompt_id})" if prompt_id else ""))
            
            # Update text
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", prompt_text)
            
            # Scroll to top
            self.text_widget.see("1.0")
    
    def on_space(self, event):
        """Handle spacebar - go to next prompt"""
        if self.current_index < len(self.prompts) - 1:
            self.current_index += 1
            self.display_current_prompt()
        return "break"
    
    def on_key_press(self, event):
        """Handle number key presses - build number buffer"""
        if event.char.isdigit():
            self.number_buffer += event.char
            return "break"
        # Clear buffer on non-digit
        if event.keysym not in ['Return', 'space']:
            self.number_buffer = ""
    
    def on_enter(self, event):
        """Handle Enter - jump to prompt number if number buffer has value"""
        if self.number_buffer:
            try:
                prompt_num = int(self.number_buffer)
                # Convert to 0-based index
                index = prompt_num - 1
                if 0 <= index < len(self.prompts):
                    self.current_index = index
                    self.display_current_prompt()
                else:
                    print(f"Prompt number {prompt_num} out of range (1-{len(self.prompts)})")
            except ValueError:
                pass
            finally:
                self.number_buffer = ""
        return "break"
    
    def run(self):
        """Start the viewer"""
        self.root.mainloop()


def main():
    """Main entry point"""
    import sys
    
    # Default to unannotated CSV
    training_dir = Path(__file__).parent
    default_csv = training_dir / "unannotated_nlp_prompts.csv"
    
    # Allow custom CSV path as argument
    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1])
    else:
        csv_path = default_csv
    
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        print(f"Usage: python prompt_viewer.py [path_to_csv]")
        return
    
    viewer = PromptViewer(csv_path)
    viewer.run()


if __name__ == '__main__':
    main()


