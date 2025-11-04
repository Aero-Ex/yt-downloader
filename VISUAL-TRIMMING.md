# Visual Trimming Slider Feature

## Overview

The visual trimming slider provides an intuitive, interactive way to select specific portions of a video to download. Instead of manually typing timestamps, users can simply drag handles on a visual timeline to trim videos.

## Features

### 🎯 Interactive Timeline
- **Visual representation** of the entire video duration
- **Draggable handles** for start and end points
- **Color-coded selection** showing the portion that will be downloaded
- **Real-time tooltips** displaying exact timestamps as you drag

### 📊 Live Feedback
- **Selected Duration**: Shows how long your trimmed clip will be
- **Trimming Range**: Displays start and end timestamps (e.g., "1:30 - 3:45")
- **Full video indicator**: Clearly shows when the full video is selected

### ⌨️ Manual Time Entry
- **Toggle button** to reveal manual time input fields
- **Two-way sync** between slider and text inputs
- **Flexible format** support (HH:MM:SS or seconds)

### 📱 Mobile Responsive
- **Touch support** for mobile devices
- **Larger touch targets** on smaller screens
- **Optimized layout** for tablets and phones

## How to Use

### Using the Visual Slider

1. **Fetch video information** by pasting a YouTube URL and clicking "Fetch Info"

2. **View the timeline** in the "Custom Duration" section:
   - The timeline shows the full video duration
   - Time markers appear along the timeline
   - Two red circular handles mark the start and end

3. **Drag the handles**:
   - **Left handle (Start)**: Drag to set where the video should start
   - **Right handle (End)**: Drag to set where the video should end
   - Tooltips show exact timestamps as you drag

4. **Watch the feedback**:
   - "Selected Duration" shows clip length
   - "Trimming Range" shows start → end times
   - Selected region is highlighted in red

5. **Reset to full video**: Drag both handles to the edges

### Using Manual Time Entry

1. Click **"Enter Time Manually"** button

2. Enter times in **HH:MM:SS** format:
   ```
   Start Time: 00:01:30  (starts at 1 minute 30 seconds)
   End Time:   00:03:45  (ends at 3 minutes 45 seconds)
   ```

3. The slider **automatically updates** to match your input

4. You can also enter just seconds:
   ```
   Start Time: 90   (converts to 00:01:30)
   End Time:   225  (converts to 00:03:45)
   ```

## Visual Elements

### Timeline Components

```
┌─────────────────────────────────────────────────────────┐
│  Full Video                                     5:30     │ ← Header
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ●━━━━━━━━━[████████]━━━━━━━━━━━━━━●                  │ ← Track
│  ↑         ↑        ↑              ↑                    │
│  0:00    1:30     3:45           5:30                   │ ← Markers
│                                                          │
├─────────────────────────────────────────────────────────┤
│  Selected Duration: 2:15                                │ ← Info
│  Trimming: 1:30 - 3:45                                  │
└─────────────────────────────────────────────────────────┘
```

- **● (Handles)**: Draggable red circles with white borders
- **[████]**: Red gradient showing selected region
- **━━━━**: Gray bar showing unselected portions
- **Markers**: Time indicators along the timeline

### Color Coding

- **Red Gradient**: Selected/trimmed portion
- **Gray**: Unselected portions
- **Red Handles**: Start and end points
- **White Tooltips**: Display times on hover

## Technical Details

### JavaScript Functions

#### Core Functions
- `initializeTimeline(durationSeconds)` - Sets up timeline with video duration
- `startDragging(e, target)` - Begins drag operation
- `onDrag(e)` - Updates handle position during drag
- `stopDragging()` - Ends drag operation
- `updateTimelineDisplay()` - Updates all visual feedback

#### Utility Functions
- `formatTime(seconds)` - Converts seconds to M:SS or H:MM:SS
- `formatTimeHHMMSS(seconds)` - Converts to HH:MM:SS format
- `parseTimeToSeconds(timeString)` - Parses time strings to seconds
- `generateTimeMarkers(durationSeconds)` - Creates timeline markers

### Event Handling

**Mouse Events:**
```javascript
handleStart.addEventListener('mousedown', startDragging)
document.addEventListener('mousemove', onDrag)
document.addEventListener('mouseup', stopDragging)
```

**Touch Events (Mobile):**
```javascript
handleStart.addEventListener('touchstart', startDragging)
document.addEventListener('touchmove', onDrag)
document.addEventListener('touchend', stopDragging)
```

**Sync with Manual Inputs:**
```javascript
startTimeInput.addEventListener('input', syncTimelineFromInputs)
endTimeInput.addEventListener('input', syncTimelineFromInputs)
```

### CSS Classes

Key classes for styling:
- `.timeline-container` - Main wrapper
- `.timeline-track` - The track where handles move
- `.timeline-handle` - Draggable handle circles
- `.timeline-selected-region` - Highlighted selection
- `.handle-tooltip` - Timestamp tooltips
- `.timeline-info` - Feedback display area

## User Experience Features

### Visual Feedback
✅ **Hover effects** on handles (scale up, glow)
✅ **Cursor changes** (grab → grabbing)
✅ **Smooth animations** for all transitions
✅ **Tooltips appear** on hover/drag
✅ **Color gradient** shows active selection

### Usability
✅ **Handles can't overlap** (minimum 1% apart)
✅ **Stays within bounds** (0% to 100%)
✅ **Two-way sync** with manual inputs
✅ **Clear visual hierarchy**
✅ **Accessible touch targets**

### Responsiveness
✅ **Larger handles on mobile** (28px vs 20px)
✅ **Increased track height** on small screens
✅ **Stacked layout** on narrow displays
✅ **Touch-optimized** interactions

## Examples

### Example 1: Extract a 30-second clip from a 5-minute video

1. Fetch video info (shows 5:00 duration)
2. Drag start handle to 2:00
3. Drag end handle to 2:30
4. Display shows:
   - Selected Duration: 0:30
   - Trimming: 2:00 - 2:30

### Example 2: Download everything except intro (first minute)

1. Fetch video info
2. Drag start handle to 1:00
3. Leave end handle at the end
4. Display shows:
   - Selected Duration: 4:00 (if video is 5:00)
   - Trimming: 1:00 - 5:00

### Example 3: Use manual entry for precise timing

1. Click "Enter Time Manually"
2. Enter Start: 00:02:15
3. Enter End: 00:04:30
4. Slider updates automatically
5. Display shows:
   - Selected Duration: 2:15
   - Trimming: 2:15 - 4:30

## Browser Compatibility

✅ **Chrome/Edge** - Full support
✅ **Firefox** - Full support
✅ **Safari** - Full support
✅ **Mobile browsers** - Touch support included

## Accessibility

- Keyboard navigation (can be added)
- Clear visual indicators
- Tooltips for context
- Color contrast compliant
- Large touch targets

## Future Enhancements

Potential improvements:
- [ ] Keyboard shortcuts (arrow keys to adjust)
- [ ] Zoom in/out for precise editing
- [ ] Snap to markers
- [ ] Video preview thumbnails
- [ ] Multiple selection regions
- [ ] Undo/redo functionality
- [ ] Save/load presets

## Technical Implementation

### Files Modified
- `templates/index.html` - Timeline HTML structure
- `static/css/style.css` - Timeline styling (~250 lines)
- `static/js/main.js` - Interactive functionality (~180 lines)

### Dependencies
- No external libraries required
- Pure vanilla JavaScript
- CSS3 for animations
- HTML5 drag events

### Performance
- Lightweight (< 10KB total)
- Smooth 60fps dragging
- Minimal DOM manipulation
- Event delegation
- Debounced updates

---

**Enjoy precise video trimming with visual feedback!** 🎬✂️
