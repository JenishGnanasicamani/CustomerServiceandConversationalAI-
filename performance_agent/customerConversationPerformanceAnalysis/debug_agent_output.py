#!/usr/bin/env python3
"""
Debug script to examine agent output structure and patterns
"""

import pymongo
import json
import re

def main():
    # Connect to MongoDB
    client = pymongo.MongoClient('mongodb+srv://cia_db_user:qG5hStEqWkvAHrVJ@capstone-project.yyfpvqh.mongodb.net/?retryWrites=true&w=majority&appName=CAPSTONE-PROJECT')
    db = client['csai']
    collection = db['agentic_analysis']

    # Get the latest analysis record
    latest_record = collection.find().sort('analysis_timestamp', -1).limit(1)

    for record in latest_record:
        agent_output = record.get('agent_output', '')
        
        print('='*80)
        print('FULL AGENT OUTPUT:')
        print('='*80)
        print(agent_output)
        print()
        
        print('='*80)
        print('OUTPUT STRUCTURE ANALYSIS:')
        print('='*80)
        
        # Look for different patterns that might contain KPI information
        patterns_to_check = [
            (r'## (.+?)\n', 'Headers with ##'),
            (r'\*\*(.+?)\*\*', 'Bold text'),
            (r'Score: ([0-9.]+)/([0-9.]+)', 'Score patterns'),
            (r'Category: (.+)', 'Category patterns'),
            (r'KPI: (.+)', 'KPI patterns'),
            (r'Analysis: (.+)', 'Analysis patterns'),
            (r'- (.+?): ([0-9.]+)/([0-9.]+)', 'Bullet point scores'),
            (r'([A-Z][a-zA-Z\s]+): ([0-9.]+)/([0-9.]+)', 'KPI name with scores'),
        ]
        
        for pattern, description in patterns_to_check:
            matches = re.findall(pattern, agent_output)
            print(f'{description}: {len(matches)} matches')
            for i, match in enumerate(matches[:3]):  # Show first 3 matches
                print(f'  {i+1}. {match}')
            print()
            
        # Check for JSON-like structures
        print('Looking for JSON structures...')
        json_pattern = r'\{[^{}]*\}'
        json_matches = re.findall(json_pattern, agent_output)
        print(f'Found {len(json_matches)} potential JSON structures')
        for i, match in enumerate(json_matches[:2]):
            print(f'  {i+1}. {match[:100]}...')
        print()
        
        # Check for structured sections
        print('Looking for structured sections...')
        if 'Response Quality' in agent_output:
            print('✓ Found Response Quality section')
        if 'Communication Style' in agent_output:
            print('✓ Found Communication Style section')
        if 'Problem Resolution' in agent_output:
            print('✓ Found Problem Resolution section')
        if 'Efficiency' in agent_output:
            print('✓ Found Efficiency section')
            
        # Extract actual KPI scores manually
        print('\nManual Score Extraction:')
        print('-' * 40)
        
        # Look for lines that contain scores
        lines = agent_output.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'([0-9.]+)/([0-9.]+)', line):
                print(f'Line {i}: {line.strip()}')
    
    client.close()

if __name__ == '__main__':
    main()
