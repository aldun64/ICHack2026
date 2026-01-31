from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'hackathon_db')
DB_USER = os.getenv('DB_USER', 'hackathon_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'hackathon_password')

def get_db_connection():
    """Create a connection to the PostgreSQL database"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info('Health check requested')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        logger.info('Health check passed')
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# =====================
# SOCIALS ENDPOINTS
# =====================

@app.route('/api/socials', methods=['GET'])
def get_socials():
    """Get all socials, optionally filtered by status"""
    logger.info('GET /api/socials requested')
    try:
        status = request.args.get('status')
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if status:
            cur.execute('SELECT * FROM socials WHERE status = %s ORDER BY event_date DESC', (status,))
        else:
            cur.execute('SELECT * FROM socials ORDER BY event_date DESC')

        socials = cur.fetchall()
        cur.close()
        conn.close()
        logger.info(f'Retrieved {len(socials)} socials')
        return jsonify(socials), 200
    except Exception as e:
        logger.error(f'GET /api/socials failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/socials/<int:social_id>', methods=['GET'])
def get_social(social_id):
    """Get a specific social with attendance details"""
    logger.info(f'GET /api/socials/{social_id} requested')
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get social details
        cur.execute('SELECT * FROM socials WHERE id = %s', (social_id,))
        social = cur.fetchone()

        if not social:
            return jsonify({'error': 'Social not found'}), 404

        # Get attendance details
        cur.execute('''
            SELECT discord_id, rsvp_status, actual_attended, rsvp_date
            FROM social_attendance
            WHERE social_id = %s
            ORDER BY rsvp_date DESC
        ''', (social_id,))
        attendance = cur.fetchall()

        cur.close()
        conn.close()

        social['attendees'] = attendance
        logger.info(f'Retrieved social {social_id} with {len(attendance)} attendees')
        return jsonify(social), 200
    except Exception as e:
        logger.error(f'GET /api/socials/{social_id} failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/socials', methods=['POST'])
def create_social():
    """Create a new social event"""
    logger.info('POST /api/socials requested')
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()

        # Ensure user exists in discord_users table
        discord_id = data.get('created_by')
        username = data.get('created_by_username', f'User_{discord_id}')

        cur.execute('''
            INSERT INTO discord_users (discord_id, username)
            VALUES (%s, %s)
            ON CONFLICT (discord_id) DO NOTHING
        ''', (discord_id, username))

        cur.execute('''
            INSERT INTO socials (name, description, location, event_date, created_by, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, description, location, event_date, status, group_points, created_at
        ''', (
            data.get('name'),
            data.get('description'),
            data.get('location'),
            data.get('event_date'),
            discord_id,
            data.get('status', 'planned')
        ))

        new_social = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f'Created social {new_social[0]}: {new_social[1]}')
        return jsonify({
            'id': new_social[0],
            'name': new_social[1],
            'description': new_social[2],
            'location': new_social[3],
            'event_date': new_social[4],
            'status': new_social[5],
            'group_points': new_social[6],
            'created_at': str(new_social[7]),
            'message': 'Social created successfully'
        }), 201
    except Exception as e:
        logger.error(f'POST /api/socials failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/socials/<int:social_id>', methods=['PUT'])
def update_social(social_id):
    """Update a social event status or details"""
    logger.info(f'PUT /api/socials/{social_id} requested')
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()

        updates = []
        params = []

        if 'status' in data:
            updates.append('status = %s')
            params.append(data['status'])
        if 'name' in data:
            updates.append('name = %s')
            params.append(data['name'])
        if 'location' in data:
            updates.append('location = %s')
            params.append(data['location'])
        if 'description' in data:
            updates.append('description = %s')
            params.append(data['description'])
        if 'event_date' in data:
            updates.append('event_date = %s')
            params.append(data['event_date'])
        if 'group_points' in data:
            updates.append('group_points = %s')
            params.append(data['group_points'])

        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400

        params.append(social_id)
        query = f"UPDATE socials SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f'Updated social {social_id}')
        return jsonify({'message': 'Social updated successfully'}), 200
    except Exception as e:
        logger.error(f'PUT /api/socials/{social_id} failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

# =====================
# ATTENDANCE ENDPOINTS
# =====================

@app.route('/api/socials/<int:social_id>/attendance', methods=['POST'])
def add_attendance(social_id):
    """Add or update attendance for a user at a social"""
    logger.info(f'POST /api/socials/{social_id}/attendance requested')
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()

        discord_id = data.get('discord_id')
        rsvp_status = data.get('rsvp_status', 'attending')

        # Ensure user exists
        username = data.get('username', f'User_{discord_id}')
        cur.execute('''
            INSERT INTO discord_users (discord_id, username)
            VALUES (%s, %s)
            ON CONFLICT (discord_id) DO NOTHING
        ''', (discord_id, username))

        # Insert or update attendance
        cur.execute('''
            INSERT INTO social_attendance (social_id, discord_id, rsvp_status, rsvp_date)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (social_id, discord_id)
            DO UPDATE SET rsvp_status = EXCLUDED.rsvp_status, updated_at = NOW()
        ''', (social_id, discord_id, rsvp_status))

        conn.commit()
        cur.close()
        conn.close()

        logger.info(f'Added attendance for user {discord_id} to social {social_id}')
        return jsonify({'message': 'Attendance recorded'}), 201
    except Exception as e:
        logger.error(f'POST /api/socials/{social_id}/attendance failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/socials/<int:social_id>/attendance/<int:discord_id>', methods=['PUT'])
def update_attendance(social_id, discord_id):
    """Update attendance status or mark as actually attended"""
    logger.info(f'PUT /api/socials/{social_id}/attendance/{discord_id} requested')
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()

        updates = []
        params = []

        if 'rsvp_status' in data:
            updates.append('rsvp_status = %s')
            params.append(data['rsvp_status'])
        if 'actual_attended' in data:
            updates.append('actual_attended = %s')
            params.append(data['actual_attended'])

        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400

        updates.append('updated_at = NOW()')
        params.extend([social_id, discord_id])

        query = f"UPDATE social_attendance SET {', '.join(updates)} WHERE social_id = %s AND discord_id = %s"
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f'Updated attendance for user {discord_id} at social {social_id}')
        return jsonify({'message': 'Attendance updated'}), 200
    except Exception as e:
        logger.error(f'PUT /api/socials/{social_id}/attendance/{discord_id} failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

# =====================
# STATS/METRICS ENDPOINTS
# =====================

@app.route('/api/stats/group', methods=['GET'])
def get_group_stats():
    """Get group-wide statistics"""
    logger.info('GET /api/stats/group requested')
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Total points
        cur.execute('SELECT SUM(group_points) as total_points FROM socials WHERE status = %s', ('completed',))
        total_points = cur.fetchone()['total_points'] or 0

        # Completed socials
        cur.execute('SELECT COUNT(*) as count FROM socials WHERE status = %s', ('completed',))
        completed_socials = cur.fetchone()['count']

        # Upcoming socials
        cur.execute('SELECT COUNT(*) as count FROM socials WHERE status = %s', ('planned',))
        upcoming_socials = cur.fetchone()['count']

        # Total attendees across all events
        cur.execute('SELECT COUNT(*) as count FROM social_attendance')
        total_attendances = cur.fetchone()['count']

        cur.close()
        conn.close()

        return jsonify({
            'total_group_points': total_points,
            'completed_socials': completed_socials,
            'upcoming_socials': upcoming_socials,
            'total_attendances': total_attendances
        }), 200
    except Exception as e:
        logger.error(f'GET /api/stats/group failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/user/<int:discord_id>', methods=['GET'])
def get_user_stats(discord_id):
    """Get user statistics"""
    logger.info(f'GET /api/stats/user/{discord_id} requested')
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # User info
        cur.execute('SELECT username, display_name FROM discord_users WHERE discord_id = %s', (discord_id,))
        user = cur.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # RSVPs
        cur.execute('SELECT COUNT(*) as count FROM social_attendance WHERE discord_id = %s', (discord_id,))
        total_rsvps = cur.fetchone()['count']

        # Actual attendances
        cur.execute('SELECT COUNT(*) as count FROM social_attendance WHERE discord_id = %s AND actual_attended = TRUE', (discord_id,))
        attended = cur.fetchone()['count']

        # Upcoming socials user is attending
        cur.execute('''
            SELECT COUNT(*) as count
            FROM social_attendance sa
            JOIN socials s ON sa.social_id = s.id
            WHERE sa.discord_id = %s AND s.status IN ('planned', 'ongoing')
        ''', (discord_id,))
        upcoming = cur.fetchone()['count']

        cur.close()
        conn.close()

        return jsonify({
            'discord_id': discord_id,
            'username': user['username'],
            'display_name': user['display_name'],
            'total_rsvps': total_rsvps,
            'attended': attended,
            'upcoming': upcoming
        }), 200
    except Exception as e:
        logger.error(f'GET /api/stats/user/{discord_id} failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

# =====================
# AVAILABILITY/SCHEDULING ENDPOINTS
# =====================

@app.route('/api/users/by-username/<username>', methods=['GET'])
def get_user_by_username(username):
    """Get user by username"""
    logger.info(f'GET /api/users/by-username/{username} requested')
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT discord_id, username, display_name FROM discord_users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user), 200
    except Exception as e:
        logger.error(f'GET /api/users/by-username/{username} failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/socials/<int:social_id>/availability', methods=['POST'])
def submit_availability(social_id):
    """Submit availability for a user at a social event"""
    logger.info(f'POST /api/socials/{social_id}/availability requested')
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()

        username = data.get('username')
        discord_id = data.get('discord_id')
        availability_slots = data.get('availability_slots')

        if not username or not discord_id:
            return jsonify({'error': 'Username and discord_id are required'}), 400

        # Ensure user exists
        cur.execute('''
            INSERT INTO discord_users (discord_id, username)
            VALUES (%s, %s)
            ON CONFLICT (discord_id) DO UPDATE SET username = EXCLUDED.username
        ''', (discord_id, username))

        # Insert or update availability
        import json
        cur.execute('''
            INSERT INTO social_attendance (social_id, discord_id, availability_submitted, availability_slots, rsvp_date)
            VALUES (%s, %s, TRUE, %s, NOW())
            ON CONFLICT (social_id, discord_id)
            DO UPDATE SET availability_submitted = TRUE, availability_slots = EXCLUDED.availability_slots, updated_at = NOW()
        ''', (social_id, discord_id, json.dumps(availability_slots)))

        conn.commit()
        cur.close()
        conn.close()

        logger.info(f'Submitted availability for user {username} ({discord_id}) to social {social_id}')
        return jsonify({'message': 'Availability submitted successfully'}), 201
    except Exception as e:
        logger.error(f'POST /api/socials/{social_id}/availability failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/socials/<int:social_id>/availability', methods=['GET'])
def get_availability_summary(social_id):
    """Get availability summary for a social event"""
    logger.info(f'GET /api/socials/{social_id}/availability requested')
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get all availability submissions for this event
        cur.execute('''
            SELECT sa.discord_id, du.username, sa.availability_slots, sa.rsvp_status
            FROM social_attendance sa
            JOIN discord_users du ON sa.discord_id = du.discord_id
            WHERE sa.social_id = %s AND sa.availability_submitted = TRUE
            ORDER BY sa.updated_at DESC
        ''', (social_id,))

        availabilities = cur.fetchall()
        cur.close()
        conn.close()

        logger.info(f'Retrieved availability for social {social_id} ({len(availabilities)} submissions)')
        return jsonify({
            'social_id': social_id,
            'submissions': availabilities,
            'count': len(availabilities)
        }), 200
    except Exception as e:
        logger.error(f'GET /api/socials/{social_id}/availability failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
