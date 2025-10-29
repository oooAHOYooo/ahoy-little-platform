# Dashboard Feature - User Collection & Quests

## Overview
A new dashboard page that splits the view into:
- **Left Panel**: User collection with merit badges and achievements
- **Right Panel**: Active quests and upcoming events

## Features Implemented

### Left Dashboard - User Collection
1. **Show Code Entry**
   - Enter codes from live shows to earn merit badges
   - Click "Enter Code" button to open modal
   - API endpoint: `POST /api/gamify/redeem-code`
   - Example codes: `NEWHAVEN2024`, `POETRY2024`, `INDIE2024`

2. **User Stats Summary**
   - Level display
   - Total listening time
   - Badge count

3. **Merit Badges Grid**
   - Shows all earned badges
   - Visual tier indicators (bronze, silver, gold)
   - Badge icons and titles

4. **Achievement Progress**
   - Lists active achievements
   - Progress bars showing completion status
   - Visual checkmarks for completed achievements

5. **Listening Stats**
   - Total listening time
   - Day streak counter
   - Tracks played count

### Right Dashboard - Quests & Up Next
1. **Today's Quests**
   - Lists active daily and weekly quests
   - Progress bars showing quest completion
   - XP rewards displayed
   - Task icons by quest type (play, save, listen, etc.)

2. **Upcoming Shows**
   - Displays upcoming events
   - Event date badges
   - Venue and time information
   - Code availability indicators

3. **Recommended Actions**
   - Quick links to discover new music
   - Watch live shows
   - Browse artists

## API Endpoints

### Get Gamification Data
```
GET /api/me/gamification
```
Returns: badges, quests, achievements, listening stats

### Redeem Show Code
```
POST /api/gamify/redeem-code
Body: { "code": "NEWHAVEN2024" }
```
Returns: success status and badge information

## Files Created/Modified

1. **templates/dashboard.html** - Main dashboard template with left/right layout
2. **blueprints/api/gamify.py** - Added code redemption endpoint
3. **app.py** - Added `/dashboard` route
4. **templates/base.html** - Added dashboard link to navigation

## Code Examples

### Test Codes (for demo)
- `NEWHAVEN2024` - New Haven Attender badge (Bronze)
- `POETRY2024` - Poetry Enthusiast badge (Bronze)
- `INDIE2024` - Indie Music Fan badge (Silver)

### Usage
1. Navigate to `/dashboard` when logged in
2. Click "Enter Code" to redeem a show code
3. View your badge collection on the left
4. Track quest progress on the right

## Future Enhancements
- Add more event-specific codes
- Implement streak rewards
- Add community leaderboards
- Create seasonal badge collections
- Add badge sharing functionality


