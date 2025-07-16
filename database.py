
import os
import psycopg2
from psycopg2 import pool
import bcrypt
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create connection pool
        self.connection_pool = pool.SimpleConnectionPool(
            1, 10, 
            self.database_url.replace('.us-east-2', '-pooler.us-east-2')
        )
        self.init_database()
    
    def get_connection(self):
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        self.connection_pool.putconn(conn)
    
    def init_database(self):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            
            # Create users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'Initiator', 'Production Head', 'Operator', 'User', 'Approver')),
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Create forms table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS forms (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    form_data JSON NOT NULL,
                    created_by INTEGER REFERENCES users(id),
                    current_status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'in_review')),
                    current_step INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create approvals table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS approvals (
                    id SERIAL PRIMARY KEY,
                    form_id INTEGER REFERENCES forms(id),
                    user_id INTEGER REFERENCES users(id),
                    step_number INTEGER NOT NULL,
                    action VARCHAR(10) CHECK (action IN ('approved', 'rejected')),
                    comments TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create audit_log table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create default admin user if not exists
            cur.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
            admin_count = cur.fetchone()[0]
            
            if admin_count == 0:
                admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("""
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
            cur.execute("""
                SELECT id, username, password_hash, role, is_active 
                FROM users WHERE username = %s
            """, (username,))
            
            user = cur.fetchone()
            if user and user[4] and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                return {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3]
                }
            return None
        finally:
            cur.close()
            self.return_connection(conn)
    
    def log_action(self, user_id, action, details=""):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO audit_log (user_id, action, details)
                VALUES (%s, %s, %s)
            """, (user_id, action, details))
            conn.commit()
        finally:
            cur.close()
            self.return_connection(conn)
