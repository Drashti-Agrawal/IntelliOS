# main.py
import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
import logging
from logging_config import setup_logging
from log_fetcher import fetch_windows_event_logs
from regex_parsers import parse_with_regex
from llm_layer import parse_with_llm

# Set up the logger
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='IntelliOS Log Processing System')
    parser.add_argument(
        '--log-level', 
        type=str, 
        choices=['1', '2'],
        default='1',
        help='Logging level: 1=minimal, 2=comprehensive'
    )
    parser.add_argument(
        '--channel', 
        type=str, 
        default='System',
        help='Windows Event Log channel to process (default: System)'
    )
    parser.add_argument(
        '--hours', 
        type=int, 
        default=24,
        help='Process logs from the last N hours (default: 24)'
    )
    parser.add_argument(
        '--limit', 
        type=int, 
        default=None,
        help='Limit the number of logs to process'
    )
    parser.add_argument(
        '--print-logs',
        action='store_true',
        help='Print the parsed logs at the end of processing'
    )
    return parser.parse_args()

def process_logs(log_channel, fetch_since, limit=None):
    """
    Orchestrates the fetching and parsing of Windows Event Logs.
    
    Args:
        log_channel: The Windows Event Log channel to process
        fetch_since: Datetime indicating how far back to fetch logs
        limit: Maximum number of logs to process
    """
    parsed_logs = []
    total_logs = 0
    regex_parsed = 0
    llm_parsed = 0
    
    logger.info(f"Starting log processing for channel '{log_channel}' since {fetch_since}")
    
    # The Funnel Logic
    for provider, message in fetch_windows_event_logs(log_channel, fetch_since):
        total_logs += 1
        
        # Apply limit if specified
        if limit is not None and total_logs > limit:
            logger.info(f"Reached log processing limit of {limit}")
            break
        
        # Layer 1: Try Regex first
        structured_log = parse_with_regex(provider, message)
        
        # Layer 2: Fallback to LLM if Regex fails
        if structured_log is None:
            logger.info(f"Regex failed for provider '{provider}'. Trying LLM...")
            # Using hardcoded GROQ_API_KEY for demonstration purposes
            structured_log = parse_with_llm(provider, message)
            if structured_log:
                llm_parsed += 1
                logger.info(f"Successfully parsed log from '{provider}' with LLM.")
        else:
            regex_parsed += 1
        
        if structured_log:
            parsed_logs.append(structured_log)

    # Log processing summary
    logger.info(f"\nProcessing summary:")
    logger.info(f"Total logs processed: {total_logs}")
    if total_logs > 0:
        logger.info(f"Parsed with regex: {regex_parsed} ({regex_parsed/total_logs*100:.1f}%)")
        logger.info(f"Parsed with LLM: {llm_parsed} ({llm_parsed/total_logs*100:.1f}%)")
        logger.info(f"Failed to parse: {total_logs - regex_parsed - llm_parsed} ({(total_logs - regex_parsed - llm_parsed)/total_logs*100:.1f}%)")
        logger.info(f"Total successfully parsed: {len(parsed_logs)} ({len(parsed_logs)/total_logs*100:.1f}%)")
    
    # In a real app, you would save this to a file or database
    logger.debug("Parsed logs:")
    for log in parsed_logs[:10]:  # Print only first 10 logs to avoid overwhelming the log file
        logger.debug(log)
    
    if len(parsed_logs) > 10:
        logger.debug(f"... and {len(parsed_logs) - 10} more logs")
    
    return parsed_logs


if __name__ == "__main__":
    args = parse_arguments()
    
    # Setup logging based on command line argument
    setup_logging(args.log_level)
    
    # Display banner
    logger.info("=" * 80)
    logger.info("IntelliOS Log Processing System")
    logger.info("=" * 80)
    logger.info(f"Logging level: {'MINIMAL' if args.log_level == '1' else 'COMPREHENSIVE'}")
    
    # Calculate the start time for log fetching
    fetch_since = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    
    # Process logs
    parsed_logs = process_logs(args.channel, fetch_since, args.limit)
    
    # Print logs if requested
    if args.print_logs:
        print("\nParsed Logs:")
        for i, log in enumerate(parsed_logs, 1):
            print(f"\n{i}. {log}")
    
    logger.info("Log processing complete.")
    logger.info("=" * 80)
