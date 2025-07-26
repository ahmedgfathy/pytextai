#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word Frequency Analyzer
=======================

A Python script that extracts and counts alphabetic words from one or multiple UTF-8 text files.
Ignores numbers, emojis, punctuation, and special characters.

Author: GitHub Copilot
Created: July 25, 2025
"""

import re
import os
import sys
import glob
from collections import Counter
from pathlib import Path


class WordFrequencyAnalyzer:
    """
    A class to analyze word frequency in text files.
    """
    
    def __init__(self):
        # Match English and Arabic words only
        self.word_pattern = re.compile(r'\b[a-zA-Z\u0600-\u06FF]+\b')
        self.emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]')
        self.number_pattern = re.compile(r'\d+')
        
    def clean_and_tokenize(self, text):
        """
        Clean text and extract alphabetic words only (English and Arabic).
        
        Args:
            text (str): Raw text to process
        Returns:
            list: List of cleaned alphabetic words (English/Arabic) in lowercase
        """
        # Remove emojis
        text = self.emoji_pattern.sub('', text)
        
        # Remove numbers (including phone numbers, years, etc.)
        text = self.number_pattern.sub('', text)
        
        # Extract words only (ignore punctuation and symbols)
        # This regex finds word boundaries and captures only alphabetic characters
        words = self.word_pattern.findall(text.lower())
        
        # Filter out empty strings and single characters if desired
        words = [word for word in words if len(word) > 1]  # Optional: ignore single letters
        
        return words
    
    def process_single_file(self, file_path):
        """
        Process a single text file and extract words.
        
        Args:
            file_path (str): Path to the input text file
            
        Returns:
            list: List of words from the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                raw_text = file.read()
                print(f"✅ Successfully read file: {file_path}")
                return self.clean_and_tokenize(raw_text)
        except FileNotFoundError:
            print(f"❌ Error: File not found - {file_path}")
            return []
        except UnicodeDecodeError:
            print(f"❌ Error: Unable to decode file as UTF-8 - {file_path}")
            return []
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {str(e)}")
            return []
    
    def process_multiple_files(self, file_paths):
        """
        Process multiple text files and combine word extraction.
        
        Args:
            file_paths (list): List of file paths to process
            
        Returns:
            list: Combined list of words from all files
        """
        all_words = []
        
        for file_path in file_paths:
            if os.path.isfile(file_path):
                words = self.process_single_file(file_path)
                all_words.extend(words)
                print(f"📊 Extracted {len(words):,} words from {os.path.basename(file_path)}")
            else:
                print(f"⚠️  Skipping non-existent file: {file_path}")
        
        return all_words
    
    def count_and_sort_words(self, words):
        """
        Count word frequency and sort by frequency (descending).
        
        Args:
            words (list): List of words to count
            
        Returns:
            list: List of tuples (word, count) sorted by frequency
        """
        word_counts = Counter(words)
        sorted_word_counts = word_counts.most_common()
        return sorted_word_counts
    
    def write_results(self, word_counts, output_path):
        """
        Write word frequency results to a file.
        
        Args:
            word_counts (list): List of tuples (word, count)
            output_path (str): Path to output file
        """
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_path, 'w', encoding='utf-8') as out_file:
                for word, count in word_counts:
                    out_file.write(f"{word}: {count}\n")
            
            print(f"✅ Results written to: {output_path}")
            print(f"📊 Total unique words: {len(word_counts):,}")
            
            # Print top 10 words as preview
            if word_counts:
                print("\n🔝 Top 10 most frequent words:")
                for i, (word, count) in enumerate(word_counts[:10], 1):
                    print(f"  {i:2d}. {word}: {count:,}")
                    
        except Exception as e:
            print(f"❌ Error writing to file {output_path}: {str(e)}")
    
    def analyze_files(self, input_paths, output_path="word_frequency_results.txt"):
        """
        Main method to analyze word frequency in files.
        
        Args:
            input_paths (str or list): Single file path, list of paths, or glob pattern
            output_path (str): Path to output file
        """
        print("🔍 Word Frequency Analyzer")
        print("=" * 50)
        
        # Handle different input types
        if isinstance(input_paths, str):
            if '*' in input_paths or '?' in input_paths:
                # Handle glob patterns
                file_paths = glob.glob(input_paths)
                if not file_paths:
                    print(f"❌ No files found matching pattern: {input_paths}")
                    return
            else:
                # Single file
                file_paths = [input_paths]
        elif isinstance(input_paths, list):
            file_paths = input_paths
        else:
            print("❌ Error: Invalid input format. Use string or list of strings.")
            return
        
        print(f"📁 Processing {len(file_paths)} file(s)...")
        
        # Process files
        all_words = self.process_multiple_files(file_paths)
        
        if not all_words:
            print("❌ No words extracted from any files.")
            return
        
        print(f"\n📊 Total words extracted: {len(all_words):,}")
        
        # Count and sort words
        word_counts = self.count_and_sort_words(all_words)
        
        # Write results
        self.write_results(word_counts, output_path)
        
        return word_counts


def main():
    """
    Main function with command-line interface.
    """
    analyzer = WordFrequencyAnalyzer()
    
    # Command line usage
    if len(sys.argv) < 2:
        print("📖 Usage Examples:")
        print("  python word_frequency_analyzer.py input.txt")
        print("  python word_frequency_analyzer.py input.txt output.txt")
        print("  python word_frequency_analyzer.py 'whatsapp_chat_exports/*.txt'")
        print("  python word_frequency_analyzer.py file1.txt file2.txt file3.txt")
        print("\n🔧 Programmatic Usage:")
        print("  analyzer = WordFrequencyAnalyzer()")
        print("  analyzer.analyze_files('input.txt', 'output.txt')")
        print("  analyzer.analyze_files(['file1.txt', 'file2.txt'])")
        return
    
    # Parse command line arguments
    input_files = sys.argv[1:-1] if len(sys.argv) > 2 and not sys.argv[-1].endswith('.txt') else sys.argv[1:]
    output_file = sys.argv[-1] if len(sys.argv) > 2 and sys.argv[-1].endswith('.txt') and len(sys.argv) > 2 else "word_frequency_results.txt"
    
    # Handle single file with custom output
    if len(sys.argv) == 3:
        input_files = [sys.argv[1]]
        output_file = sys.argv[2]
    
    # Run analysis
    analyzer.analyze_files(input_files, output_file)


# Example usage functions for different scenarios
def example_single_file():
    """Example: Process a single file"""
    analyzer = WordFrequencyAnalyzer()
    analyzer.analyze_files("whatsapp_chats.csv", "single_file_word_freq.txt")


def example_multiple_files():
    """Example: Process multiple specific files"""
    analyzer = WordFrequencyAnalyzer()
    files = [
        "README.md",
        "TECHNICAL.md",
        "simple_parser.py"
    ]
    analyzer.analyze_files(files, "multiple_files_word_freq.txt")


def example_glob_pattern():
    """Example: Process files using glob pattern"""
    analyzer = WordFrequencyAnalyzer()
    analyzer.analyze_files("whatsapp_chat_exports/*.txt", "whatsapp_chats_word_freq.txt")


def example_all_text_files():
    """Example: Process all text files in current directory"""
    analyzer = WordFrequencyAnalyzer()
    analyzer.analyze_files("*.txt", "all_text_files_word_freq.txt")


if __name__ == "__main__":
    main()
