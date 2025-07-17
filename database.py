
import os
import mysql.connector
from mysql.connector import pooling
import bcrypt
from datetime import datetime


class DatabaseManager:
    def __init__(self, database_url=None):
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        self.connection_pool = None
        
        if self.database_url:
            self.connect_to_database()

    def connect_to_database(self):
        try:
            # Parse DATABASE_URL for MySQL
            if self.database_url.startswith('mysql://'):
                # Parse mysql://user:password@host:port/database
                import urllib.parse
                parsed = urllib.parse.urlparse(self.database_url)
                
                config = {
                    'host': parsed.hostname,
                    'port': parsed.port or 3306,
                    'user': parsed.username,
                    'password': parsed.password,
                    'database': parsed.path[1:] if parsed.path else None,
                    'autocommit': False
                }
            else:
                # Fallback to individual environment variables
                config = {
                    'host': os.environ.get('DB_HOST', 'localhost'),
                    'port': int(os.environ.get('DB_PORT', 3306)),
                    'user': os.environ.get('DB_USER', 'root'),
                    'password': os.environ.get('DB_PASSWORD', ''),
                    'database': os.environ.get('DB_NAME', 'forms_db'),
                    'autocommit': False
                }
            
            # Create connection pool
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=10,
                pool_reset_session=True,
                **config
            )
            
            self.init_database()
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

    def is_connected(self):
        return self.connection_pool is not None

    def get_connection(self):
        if not self.connection_pool:
            raise RuntimeError("Database not connected")
        return self.connection_pool.get_connection()

    def return_connection(self, conn):
        conn.close()

    def init_database(self):
        conn = self.get_connection()
        try:
            cur = conn.cursor()

            # Create users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('Admin', 'Initiator', 'Production Head', 'Operator', 'User', 'Approver') NOT NULL,
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            # Create forms table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS forms (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    form_data JSON NOT NULL,
                    created_by INT,
                    current_status ENUM('pending', 'approved', 'rejected', 'in_review') DEFAULT 'pending',
                    current_step INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)

            # Create approvals table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS approvals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    form_id INT,
                    user_id INT,
                    step_number INT NOT NULL,
                    action ENUM('approved', 'rejected'),
                    comments TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (form_id) REFERENCES forms(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Create audit_log table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Create default admin user if not exists
            cur.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
            admin_count = cur.fetchone()[0]

            if admin_count == 0:
                admin_password = bcrypt.hashpw(
                    'admin123'.encode('utf-8'),
                    bcrypt.gensalt()).decode('utf-8')
                cur.execute(
                    """
                    INSERT INTO users (username, password_hash, role, email)
                    VALUES (%s, %s, %s, %s)
                """, ('admin', admin_password, 'Admin', 'admin@company.com'))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            self.return_connection(conn)

    def authenticate_user(self, username, password):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, username, password_hash, role, is_active 
                FROM users WHERE username = %s
            """, (username,))

            user = cur.fetchone()
            if user and user[4] and bcrypt.checkpw(password.encode('utf-8'),
                                                   user[2].encode('utf-8')):
                return {'id': user[0], 'username': user[1], 'role': user[3]}
            return None
        finally:
            cur.close()
            self.return_connection(conn)

    def log_action(self, user_id, action, details=""):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO audit_log (user_id, action, details)
                VALUES (%s, %s, %s)
            """, (user_id, action, details))
            conn.commit()
        finally:
            cur.close()
            self.return_connection(conn)
