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
from vector_db import VectorDBManager

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
    parser.add_argument(
        '--use-vector-db',
        action='store_true',
        help='Store parsed logs in vector database'
    )
    parser.add_argument(
        '--query-vector-db',
        type=str,
        help='Query the vector database with the given text'
    )
    parser.add_argument(
        '--query-results',
        type=int,
        default=5,
        help='Number of results to return when querying the vector database'
    )
    parser.add_argument(
        '--clear-vector-db',
        action='store_true',
        help='Clear all logs from the vector database'
    )
    parser.add_argument(
        '--topic-matches',
        type=int,
        default=3,
        help='Number of topic matches to show for each log'
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
    
    # Initialize vector database manager if needed
    if args.use_vector_db or args.query_vector_db or args.clear_vector_db:
        logger.info("Initializing Vector Database")
        vector_db = VectorDBManager()
    
    # Clear vector database if requested
    if args.clear_vector_db:
        logger.info("Clearing vector database")
        if vector_db.clear_collection():
            print("Vector database cleared successfully")
        else:
            print("Failed to clear vector database")
        logger.info("Vector database clearing complete.")
        logger.info("=" * 80)
        sys.exit(0)
    
    # If we're just querying the vector database, skip log processing
    if args.query_vector_db:
        logger.info(f"Querying vector database with: '{args.query_vector_db}'")
        results = vector_db.query_logs(args.query_vector_db, args.query_results)
        
        print(f"\nFound {len(results)} logs matching query: '{args.query_vector_db}'\n")
        for i, log in enumerate(results, 1):
            print(f"{i}. {log}")
        
        # Get stats
        stats = vector_db.get_stats()
        print(f"\nVector Database Stats: {stats}")
        
        logger.info("Query complete.")
        logger.info("=" * 80)
        sys.exit(0)
    
    # Calculate the start time for log fetching
    fetch_since = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    
    # Process logs
    parsed_logs = process_logs(args.channel, fetch_since, args.limit)
    
    # Print logs if requested
    if args.print_logs:
        print("\nParsed Logs:")
        for i, log in enumerate(parsed_logs, 1):
            print(f"\n{i}. {log}")
    
    # Store logs in vector database if requested
    if args.use_vector_db and parsed_logs:
        logger.info(f"Storing {len(parsed_logs)} logs in vector database")
        enriched_logs = vector_db.add_logs(parsed_logs)
        
        # Print logs with topic matches
        if args.print_logs:
            print("\nLogs with Topic Matches:")
            for i, log in enumerate(enriched_logs, 1):
                print(f"\n{i}. {log['event_type']}: {log['summary']}")
                
                if 'topic_matches' in log:
                    print("  Topic Matches:")
                    for match in log['topic_matches']:
                        print(f"    - {match['topic']} (Score: {match['score']}): {match['description']}")
                
                print("  Full Log:")
                for key, value in log.items():
                    if key != 'topic_matches':  # We already printed this above
                        print(f"    {key}: {value}")
        
        # Get stats
        stats = vector_db.get_stats()
        logger.info(f"Vector Database Stats: {stats}")
    # Print logs if requested and we didn't already print them with topic matches
    elif args.print_logs:
        print("\nParsed Logs:")
        for i, log in enumerate(parsed_logs, 1):
            print(f"\n{i}. {log}")
    
    logger.info("Log processing complete.")
    logger.info("=" * 80)
