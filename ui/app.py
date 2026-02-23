#!/usr/bin/env python3
"""
Anti-Ransomware Protection System - Web UI
Real-time monitoring dashboard with token management
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Research'))

from week4_protected_monitor import ProtectedMonitor, TokenSession
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'anti-ransomware-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global monitor instance
monitor = None
monitor_thread = None

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current protection status"""
    if not monitor:
        return jsonify({'error': 'Monitor not started'}), 400
    
    return jsonify({
        'protected_path': monitor.protected_path,
        'token_valid': monitor.session.is_valid() if monitor.session else False,
        'token_expires': monitor.session.expires_at.isoformat() if monitor.session and monitor.session.is_valid() else None,
        'stats': {
            'blocked': monitor.blocked_count,
            'allowed': monitor.allowed_count
        }
    })

@app.route('/api/token/generate', methods=['POST'])
def generate_token():
    """Generate new token"""
    if not monitor:
        return jsonify({'error': 'Monitor not started'}), 400
    
    data = request.json
    password = data.get('password', '')
    
    if not password:
        return jsonify({'error': 'Password required'}), 400
    
    token = monitor.generate_token(password)
    
    socketio.emit('token_generated', {
        'token': token,
        'expires_at': monitor.session.expires_at.isoformat()
    })
    
    return jsonify({
        'token': token,
        'expires_at': monitor.session.expires_at.isoformat()
    })

@app.route('/api/events')
def get_events():
    """Get recent events from database"""
    if not monitor:
        return jsonify({'error': 'Monitor not started'}), 400
    
    # Query last 50 events
    cursor = monitor.db_conn.cursor()
    cursor.execute("""
        SELECT filepath, event_type, timestamp, hash_before, hash_after, 
               entropy_before, entropy_after
        FROM file_events
        ORDER BY timestamp DESC
        LIMIT 50
    """)
    
    events = []
    for row in cursor.fetchall():
        events.append({
            'filepath': row[0],
            'event_type': row[1],
            'timestamp': row[2],
            'hash_before': row[3],
            'hash_after': row[4],
            'entropy_before': row[5],
            'entropy_after': row[6]
        })
    
    return jsonify({'events': events})

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    emit('connected', {'message': 'Connected to Anti-Ransomware Monitor'})

@socketio.on('start_monitor')
def handle_start_monitor(data):
    """Start monitoring a directory"""
    global monitor, monitor_thread
    
    path = data.get('path', '')
    if not path or not os.path.exists(path):
        emit('error', {'message': 'Invalid path'})
        return
    
    if monitor:
        emit('error', {'message': 'Monitor already running'})
        return
    
    monitor = ProtectedMonitor(path)
    emit('monitor_started', {'path': path})

@socketio.on('stop_monitor')
def handle_stop_monitor():
    """Stop monitoring"""
    global monitor
    
    if monitor:
        monitor.stop()
        monitor = None
        emit('monitor_stopped', {})

def broadcast_events():
    """Background thread to broadcast file events"""
    while True:
        if monitor and monitor.session and monitor.session.is_valid():
            # Broadcast token status
            socketio.emit('token_status', {
                'valid': True,
                'expires_at': monitor.session.expires_at.isoformat()
            })
        else:
            socketio.emit('token_status', {'valid': False})
        
        time.sleep(1)

if __name__ == '__main__':
    # Start background thread
    thread = threading.Thread(target=broadcast_events, daemon=True)
    thread.start()
    
    print("=" * 60)
    print("Anti-Ransomware Protection System - Web UI")
    print("=" * 60)
    print("\nOpen browser: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
