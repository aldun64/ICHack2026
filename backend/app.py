from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging

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

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get all data from the sample table"""
    logger.info('GET /api/data requested')
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM sample_data')
        data = cur.fetchall()
        cur.close()
        conn.close()
        logger.info(f'Retrieved {len(data)} records from sample_data')
        return jsonify(data), 200
    except Exception as e:
        logger.error(f'GET /api/data failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['POST'])
def create_data():
    """Create a new entry in the sample table"""
    from flask import request
    logger.info('POST /api/data requested')
    try:
        data = request.get_json()
        logger.info(f'Creating new entry: {data}')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO sample_data (name, description) VALUES (%s, %s) RETURNING id',
            (data.get('name'), data.get('description'))
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f'Successfully created entry with id: {new_id}')
        return jsonify({'id': new_id, 'message': 'Data created successfully'}), 201
    except Exception as e:
        logger.error(f'POST /api/data failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
