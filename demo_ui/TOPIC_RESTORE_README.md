# Topic-Based Restore Feature

## Overview
Each topic card now includes a **Restore button** that allows you to restore system state based on the activities captured in that specific topic.

## Features

### 🔄 Topic Card Restore Button
- Located on each topic card in the main view
- Appears next to the "View Details" button
- Primary (highlighted) button for easy access
- Analyzes topic data and restores relevant apps and URLs

### 🎯 Detailed View Restore Button
When viewing topic details:
- **🔄 Restore Topic** button in the action bar
- **❌ Close** button to exit detail view
- Shows restoration summary with app and URL counts

## How It Works

### 1. Topic Card Restore
```
Click 🔄 Restore on any topic card
    ↓
System analyzes topic logs
    ↓
Identifies unique apps and URLs
    ↓
Calls restore_state() function
    ↓
Shows success message
```

### 2. What Gets Restored
Based on the topic's logged activities:
- **Applications**: Apps that were active during logged events
- **Browser Tabs**: URLs that were accessed
- **State Context**: Related system state from that topic

### 3. Restoration Summary
After clicking restore, you'll see:
- Number of unique apps to restore
- Number of unique URLs to restore
- Success/error message

## Usage Examples

### Example 1: Restore Web Development Session
1. Find the "💻 Web Development" topic card
2. Click "🔄 Restore" button
3. System restores:
   - VS Code
   - Browser tabs (GitHub, documentation, etc.)
   - Terminal windows
   - Development tools

### Example 2: Restore Browser Activity
1. Click on "🌐 Browser Activity" topic
2. View details showing all browsing history
3. Click "🔄 Restore Topic" in the detail view
4. All previously open tabs are restored

### Example 3: Restore Application Lifecycle
1. Find "🚀 Application Lifecycle" topic
2. Click "🔄 Restore" 
3. All applications that were launched are restored

## Technical Details

### Restore Function Imports
The UI tries multiple restore implementations:
```python
# Try 1: Mac-specific restore
from restore_state_mac import restore_state

# Try 2: Windows restore modules
from app_restore import restore_applications
from browser_restore import restore_browsers
```

### Data Analysis
Before restoring, the system analyzes topic logs:
```python
apps = set()  # Unique applications
urls = set()  # Unique URLs

for log in logs[:50]:  # Top 50 logs
    if log.get('app_name'):
        apps.add(log.get('app_name'))
    if log.get('url'):
        urls.add(log.get('url'))
```

### Restoration Process
1. **Data Collection**: Extract apps and URLs from topic logs
2. **Deduplication**: Remove duplicates
3. **Restoration**: Call appropriate restore functions
4. **Feedback**: Show success/error messages

## UI Components

### Topic Card Button Layout
```
┌─────────────────────────────────────┐
│ 🎯 Topic Name              [10 logs]│
├─────────────────────────────────────┤
│ [View Details]  [🔄 Restore]        │
└─────────────────────────────────────┘
```

### Detail View Button Layout
```
┌─────────────────────────────────────┐
│ 📊 Showing 20 of 50 logs            │
│ [🔄 Restore Topic]  [❌ Close]      │
└─────────────────────────────────────┘
```

## Error Handling

### No Restore Function Available
```
⚠️ Restore function not available
Feature coming soon!
```

### No Data in Topic
```
⚠️ No data available for [Topic Name]
```

### Restoration Failed
```
❌ Restore failed: [Error message]
```

## Benefits

✅ **Topic-Specific Restoration**: Restore only what's relevant to each topic
✅ **Quick Access**: One-click restore from topic cards
✅ **Smart Analysis**: Automatically identifies what to restore
✅ **Feedback**: Clear messages about what's being restored
✅ **Flexible**: Works with multiple restore implementations
✅ **Safe**: Shows preview before restoring

## Customization

### Adjust Number of Logs Analyzed
Edit the limit in the restore button code:
```python
topic_data = get_local_ddna_topic(topic, limit=50)  # Analyze 50 logs
```

### Filter What Gets Restored
Add filtering logic:
```python
# Only restore Chrome
if 'chrome' in log.get('app_name', '').lower():
    apps.add(log.get('app_name'))
```

## Future Enhancements

Potential improvements:
- [ ] Preview before restore (show modal with items)
- [ ] Selective restore (choose which apps/URLs)
- [ ] Restore scheduling (restore at specific time)
- [ ] Partial restore (apps only, or URLs only)
- [ ] Restore profiles (save common restore patterns)
- [ ] Undo restore functionality

## Best Practices

1. **Review First**: Click "View Details" to see what's in a topic before restoring
2. **Start Small**: Test with topics that have fewer items first
3. **Close Existing**: Close apps before restoring to avoid conflicts
4. **Regular Captures**: More recent captures = more accurate restores
5. **Topic Selection**: Choose the most relevant topic for your workflow

## Integration with Other Features

### Works With:
- ✅ Live Capture: Restore recently captured states
- ✅ Topic View: See details before restoring
- ✅ Search: Find and restore specific activities
- ✅ Workspace Management: Complement workspace restore

### Complements:
- Workspace restore (restores entire workspace)
- Manual capture (capture specific states to restore later)
- Topic filtering (restore filtered subsets)

---

**Created:** October 15, 2025
**Status:** ✅ Fully Implemented
**Location:** `demo_ui/ui.py`
**Lines:** 478-519 (topic cards), 550-585 (detail view)
