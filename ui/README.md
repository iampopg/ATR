# Anti-Ransomware Protection System - Web UI

Modern web-based dashboard for real-time monitoring and token management.

## Features

- **Real-time Monitoring**: Live file operation tracking via WebSocket
- **Token Management**: Generate and manage 10-minute session tokens
- **Statistics Dashboard**: View blocked vs allowed operations
- **Event Log**: See recent file access attempts with timestamps
- **Responsive Design**: Works on desktop and mobile

## Installation

```bash
cd ui

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Start the web server
python app.py
```

Open browser: **http://localhost:5000**

## Dashboard Sections

### 1. Protection Status
- Monitor status (Active/Inactive)
- Token validity and expiration time
- Real-time status updates

### 2. Statistics
- Blocked operations count (red)
- Allowed operations count (green)
- Updates every 2 seconds

### 3. Token Management
- Enter password to generate token
- Token displayed in monospace font
- 10-minute validity period
- Auto-refresh on expiration

### 4. Monitor Control
- Enter directory path to protect
- Start/Stop monitoring buttons
- Path validation

### 5. Events Log
- Recent file operations
- Color-coded by type (blocked/allowed)
- Timestamps and file paths
- Scrollable list (last 50 events)

## Technology Stack

- **Backend**: Flask + Flask-SocketIO
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Real-time**: Socket.IO WebSocket
- **Integration**: Week 4 Protected Monitor

## API Endpoints

### GET /api/status
Returns current protection status and statistics.

**Response:**
```json
{
  "protected_path": "/path/to/protected",
  "token_valid": true,
  "token_expires": "2026-01-27T15:30:00",
  "stats": {
    "blocked": 5,
    "allowed": 12
  }
}
```

### POST /api/token/generate
Generate new session token.

**Request:**
```json
{
  "password": "your_password"
}
```

**Response:**
```json
{
  "token": "a1b2c3d4e5f6...",
  "expires_at": "2026-01-27T15:30:00"
}
```

### GET /api/events
Get recent file events from database.

**Response:**
```json
{
  "events": [
    {
      "filepath": "/path/to/file.txt",
      "event_type": "modified",
      "timestamp": "2026-01-27 15:20:00",
      "hash_before": "abc123...",
      "hash_after": "def456...",
      "entropy_before": 5.2,
      "entropy_after": 7.8
    }
  ]
}
```

## WebSocket Events

### Client → Server

- `start_monitor` - Start monitoring directory
- `stop_monitor` - Stop monitoring

### Server → Client

- `connected` - Connection established
- `token_generated` - New token created
- `token_status` - Token validity update (every 1s)
- `monitor_started` - Monitoring started
- `monitor_stopped` - Monitoring stopped

## Color Scheme

- **Primary**: #667eea (Purple)
- **Success**: #10b981 (Green)
- **Danger**: #ef4444 (Red)
- **Background**: Linear gradient purple

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

```bash
# Run in debug mode
python app.py

# The server will auto-reload on code changes
```

## Future Enhancements (Month 2)

- [ ] User authentication
- [ ] Multiple directory monitoring
- [ ] Export events to CSV
- [ ] Email/SMS alerts
- [ ] Dark mode toggle
- [ ] Performance graphs
- [ ] Threat intelligence integration

## Screenshots

Dashboard shows:
- Protection status with live indicators
- Real-time statistics
- Token management interface
- Event log with color coding

## Notes

- UI runs on port 5000 by default
- Requires Week 4 Protected Monitor to be functional
- WebSocket connection required for real-time updates
- Token expires after 10 minutes (configurable)

## Troubleshooting

**Port already in use:**
```bash
# Change port in app.py
socketio.run(app, host='0.0.0.0', port=5001)
```

**WebSocket not connecting:**
- Check firewall settings
- Ensure Flask-SocketIO is installed
- Try different browser

**Monitor not starting:**
- Verify path exists
- Check file permissions
- Review console logs
