# log_fetcher.py
from datetime import datetime, timezone
import win32evtlog
import logging

# Set up logger
logger = logging.getLogger(__name__)

def fetch_windows_event_logs(channel: str, start_time_utc: datetime):
    """
    Fetches and yields log messages from a specified Windows Event Log channel.
    This version includes robust error handling and logging.
    """
    logger.info(f"Opening event log channel: '{channel}'")
    server = 'localhost'
    try:
        hand = win32evtlog.OpenEventLog(server, channel)
    except Exception as e:
        logger.error(f"Failed to open event log '{channel}' on '{server}': {e}")
        return

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    total_events_yielded = 0
    
    try:
        while True:
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            if not events:
                logger.info("No more events to read from the log.")
                break
            
            logger.debug(f"Read a chunk of {len(events)} events.")

            for event in events:
                # Defensive check for the event object itself
                if not event:
                    logger.warning("Encountered an empty event object, skipping.")
                    continue

                # Check if StringInserts is None, which can happen.
                if event.StringInserts is None:
                    logger.debug(f"Skipping event from '{event.SourceName}' (ID: {event.EventID}) because it has no message strings (StringInserts is None).")
                    continue

                event_time = event.TimeGenerated.replace(tzinfo=timezone.utc)
                if event_time >= start_time_utc:
                    message = ' '.join(map(str, event.StringInserts))
                    logger.debug(f"Yielding event from '{event.SourceName}' at {event_time}. Message: {message[:100]}...")
                    yield event.SourceName, message
                    total_events_yielded += 1
                else:
                    # We are reading backwards; if we pass the start time, we can stop.
                    logger.info(f"Reached event at {event_time}, which is before the desired start time of {start_time_utc}. Stopping.")
                    # Break the inner loop
                    break
            else:
                # This 'else' belongs to the 'for' loop. It runs if the loop completes without a 'break'.
                continue
            # This 'break' is for the 'while' loop, executed if the inner 'for' loop was broken.
            break

    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching logs from '{channel}': {e}")
    finally:
        logger.info(f"Finished fetching logs from '{channel}'. Total events yielded: {total_events_yielded}.")
        if 'hand' in locals() and hand:
            win32evtlog.CloseEventLog(hand)
            logger.info("Event log handle closed.")
