#!/usr/bin/env python3
"""
Import Prompts from Text Files to CSV
Reads numbered prompts from .txt files, randomizes them, and writes to unannotated_nlp_prompts.csv
"""
import re
import csv
import random
import argparse
from pathlib import Path
from typing import List, Tuple


def parse_prompt_line(line: str) -> str:
    """
    Parse a line with format "NUMBER. prompt text" and return just the prompt text.
    
    Args:
        line: Line from text file (e.g., "1. I want a sedan...")
    
    Returns:
        Prompt text without the number prefix, or None if line doesn't match format
    """
    # Match pattern: number followed by period and space, then the prompt
    match = re.match(r'^\d+\.\s+(.+)$', line.strip())
    if match:
        return match.group(1).strip()
    return None


def read_prompts_from_file(file_path: Path) -> List[str]:
    """
    Read all prompts from a single text file.
    
    Args:
        file_path: Path to the text file
    
    Returns:
        List of prompt strings
    """
    prompts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                prompt = parse_prompt_line(line)
                if prompt:
                    prompts.append(prompt)
                elif line.strip():  # Non-empty line that didn't match pattern
                    print(f"Warning: Line {line_num} in {file_path.name} doesn't match expected format: {line.strip()[:50]}...")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return prompts


def read_all_prompts(directory: Path) -> List[Tuple[str, str]]:
    """
    Read all prompts from all .txt files in the directory.
    
    Args:
        directory: Directory containing .txt files
    
    Returns:
        List of tuples (source_file, prompt_text)
    """
    all_prompts = []
    txt_files = sorted(directory.glob('*.txt'))
    
    if not txt_files:
        print(f"No .txt files found in {directory}")
        return all_prompts
    
    print(f"Found {len(txt_files)} text file(s):")
    for txt_file in txt_files:
        prompts = read_prompts_from_file(txt_file)
        print(f"  - {txt_file.name}: {len(prompts)} prompts")
        for prompt in prompts:
            all_prompts.append((txt_file.name, prompt))
    
    return all_prompts


def generate_id(index: int, total: int) -> str:
    """
    Generate a sequential ID for a prompt.
    
    Args:
        index: Zero-based index (will be converted to 1-based)
        total: Total number of prompts (for padding calculation)
    
    Returns:
        ID string like "prompt_001"
    """
    # Calculate padding based on total count
    padding = len(str(total))
    prompt_num = index + 1
    return f"prompt_{prompt_num:0{padding}d}"


def write_to_csv(
    prompts: List[str],
    output_path: Path,
    append: bool = False,
    preview: bool = False
) -> None:
    """
    Write prompts to CSV file.
    
    Args:
        prompts: List of prompt strings
        output_path: Path to output CSV file
        append: If True, append to existing file (checking for duplicates)
        preview: If True, only print first 5 rows without writing
    """
    # Read existing IDs if appending
    existing_ids = set()
    if append and output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_ids.add(row.get('id', ''))
            print(f"Found {len(existing_ids)} existing entries in {output_path.name}")
        except Exception as e:
            print(f"Warning: Could not read existing CSV: {e}")
            append = False
    
    # Prepare rows
    rows = []
    total = len(prompts)
    for idx, prompt in enumerate(prompts):
        prompt_id = generate_id(idx, total)
        
        # Skip if ID already exists (when appending)
        if prompt_id in existing_ids:
            print(f"Skipping {prompt_id} (already exists)")
            continue
        
        rows.append({
            'id': prompt_id,
            'prompt': prompt,
            'annotated_json': '',
            'completion_status': ''
        })
    
    if preview:
        print(f"\nPreview (first 5 of {len(rows)} rows):")
        print("-" * 80)
        for i, row in enumerate(rows[:5], 1):
            print(f"{i}. ID: {row['id']}")
            print(f"   Prompt: {row['prompt'][:70]}...")
            print()
        print(f"Total rows to write: {len(rows)}")
        return
    
    # Write to CSV
    mode = 'a' if append else 'w'
    with open(output_path, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'prompt', 'annotated_json', 'completion_status'])
        
        # Write header only if not appending
        if not append:
            writer.writeheader()
        
        writer.writerows(rows)
    
    print(f"\nSuccessfully wrote {len(rows)} prompts to {output_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description='Import numbered prompts from text files into unannotated_nlp_prompts.csv'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for reproducibility (default: random)'
    )
    parser.add_argument(
        '--append',
        action='store_true',
        help='Append to existing CSV (skips duplicate IDs)'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview first 5 rows without writing to file'
    )
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=None,
        help='Directory containing .txt files (default: raw_training_text/)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Output CSV file (default: unannotated_nlp_prompts.csv)'
    )
    
    args = parser.parse_args()
    
    # Set default paths
    script_dir = Path(__file__).parent
    input_dir = args.input_dir or (script_dir / 'raw_training_text')
    output_file = args.output or (script_dir / 'unannotated_nlp_prompts.csv')
    
    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    print(f"Reading prompts from: {input_dir}")
    print(f"Output file: {output_file}")
    print()
    
    # Read all prompts
    prompts_with_source = read_all_prompts(input_dir)
    
    if not prompts_with_source:
        print("No prompts found. Exiting.")
        return 1
    
    # Extract just the prompt text
    prompts = [prompt for _, prompt in prompts_with_source]
    print(f"\nTotal prompts collected: {len(prompts)}")
    
    # Randomize
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")
    else:
        seed = random.randint(1, 1000000)
        random.seed(seed)
        print(f"Using random seed: {seed} (use --seed {seed} to reproduce)")
    
    random.shuffle(prompts)
    print("Prompts randomized")
    
    # Write to CSV
    write_to_csv(prompts, output_file, append=args.append, preview=args.preview)
    
    return 0


if __name__ == '__main__':
    exit(main())

