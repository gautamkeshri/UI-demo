import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
import mysql.connector
from database import DatabaseManager

class FormApprovalApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Form Approval System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')

        self.db = DatabaseManager()
        self.current_user = None

        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Check if database is connected
        if not self.db.is_connected():
            self.show_database_config()
        else:
            self.show_login()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_database_config(self):
        self.clear_frame()

        # Database configuration frame
        config_frame = ttk.LabelFrame(self.main_frame, text="Database Configuration", padding=20)
        config_frame.pack(expand=True)

        ttk.Label(config_frame, text="Please configure your database connection:", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(config_frame, text="Host:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.host_entry = ttk.Entry(config_frame, width=30)
        self.host_entry.grid(row=1, column=1, padx=5, pady=5)
        self.host_entry.insert(0, "localhost")

        ttk.Label(config_frame, text="Port:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.port_entry = ttk.Entry(config_frame, width=30)
        self.port_entry.grid(row=2, column=1, padx=5, pady=5)
        self.port_entry.insert(0, "3306")

        ttk.Label(config_frame, text="Database Name:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.dbname_entry = ttk.Entry(config_frame, width=30)
        self.dbname_entry.grid(row=3, column=1, padx=5, pady=5)
        self.dbname_entry.insert(0, "forms_db")

        ttk.Label(config_frame, text="Username:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.db_username_entry = ttk.Entry(config_frame, width=30)
        self.db_username_entry.grid(row=4, column=1, padx=5, pady=5)
        self.db_username_entry.insert(0, "root")

        ttk.Label(config_frame, text="Password:").grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.db_password_entry = ttk.Entry(config_frame, show="*", width=30)
        self.db_password_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Button(config_frame, text="Test Connection", 
                  command=self.test_database_connection).grid(row=6, column=0, pady=10)
        ttk.Button(config_frame, text="Connect", 
                  command=self.connect_database).grid(row=6, column=1, pady=10)

        # Alternative: Use DATABASE_URL
        ttk.Separator(config_frame, orient='horizontal').grid(row=7, column=0, columnspan=2, 
                                                             sticky='ew', pady=20)

        ttk.Label(config_frame, text="Or enter DATABASE_URL directly:").grid(row=8, column=0, 
                                                                            columnspan=2, pady=5)
        self.database_url_entry = ttk.Entry(config_frame, width=60)
        self.database_url_entry.grid(row=9, column=0, columnspan=2, padx=5, pady=5)
        self.database_url_entry.insert(0, "mysql://username:password@host:port/database_name")

        ttk.Button(config_frame, text="Connect with URL", 
                  command=self.connect_with_url).grid(row=10, column=0, columnspan=2, pady=10)

        # Instructions
        info_frame = ttk.LabelFrame(self.main_frame, text="Instructions", padding=10)
        info_frame.pack(pady=10, fill='x')

        instructions = """
For MySQL database:
1. Go to the Secrets tab and add DATABASE_URL environment variable
2. Or use the database configuration above with your MySQL details
3. Make sure your MySQL service is running

Example DATABASE_URL format:
mysql://username:password@host:port/database_name

For local MySQL: mysql://root:password@localhost:3306/forms_db
        """
        ttk.Label(info_frame, text=instructions, justify='left').pack()

    def test_database_connection(self):
        try:
            host = self.host_entry.get().strip()
            port = self.port_entry.get().strip()
            dbname = self.dbname_entry.get().strip()
            username = self.db_username_entry.get().strip()
            password = self.db_password_entry.get().strip()

            if not all([host, port, dbname, username]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            # Test connection
            conn = mysql.connector.connect(
                host=host,
                port=int(port),
                user=username,
                password=password,
                database=dbname
            )
            conn.close()

            messagebox.showinfo("Success", "Database connection successful!")

        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database:\n{str(e)}")

    def connect_database(self):
        try:
            host = self.host_entry.get().strip()
            port = self.port_entry.get().strip()
            dbname = self.dbname_entry.get().strip()
            username = self.db_username_entry.get().strip()
            password = self.db_password_entry.get().strip()

            if not all([host, port, dbname, username]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            import urllib.parse
            encoded_password = urllib.parse.quote(password, safe='')
            database_url = f"mysql://{username}:{encoded_password}@{host}:{port}/{dbname}"

            # Create new database manager with the URL
            self.db = DatabaseManager(database_url)

            # Try to connect and get detailed error if it fails
            try:
                if self.db.connect_to_database():
                    # Check if tables exist
                    if self.check_tables_exist():
                        messagebox.showinfo("Success", "Connected to database successfully!")
                        self.show_login()
                    else:
                        # Ask user if they want to create tables
                        result = messagebox.askyesno("Tables Not Found", 
                                                   "Database connected successfully, but required tables are missing.\n\n"
                                                   "Would you like to create the required tables now?")
                        if result:
                            self.create_tables()
                        else:
                            self.show_login()
                else:
                    messagebox.showerror("Error", "Failed to connect to database. Please check your connection details.")
            except Exception as db_error:
                messagebox.showerror("Database Connection Error", f"Failed to connect to database:\n{str(db_error)}")

        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database:\n{str(e)}")

    def connect_with_url(self):
        try:
            database_url = self.database_url_entry.get().strip()

            if not database_url:
                messagebox.showerror("Error", "Please enter a DATABASE_URL")
                return

            # Create new database manager with the URL
            self.db = DatabaseManager(database_url)

            # Try to connect and get detailed error if it fails
            try:
                if self.db.connect_to_database():
                    # Check if tables exist
                    if self.check_tables_exist():
                        messagebox.showinfo("Success", "Connected to database successfully!")
                        self.show_login()
                    else:
                        # Ask user if they want to create tables
                        result = messagebox.askyesno("Tables Not Found", 
                                                   "Database connected successfully, but required tables are missing.\n\n"
                                                   "Would you like to create the required tables now?")
                        if result:
                            self.create_tables()
                        else:
                            self.show_login()
                else:
                    messagebox.showerror("Error", "Failed to connect to database. Please check your connection details.")
            except Exception as db_error:
                messagebox.showerror("Database Connection Error", f"Failed to connect to database:\n{str(db_error)}")

        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database:\n{str(e)}")
    
    def check_tables_exist(self):
        required_tables = ['users', 'forms', 'approvals', 'audit_log']
        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SHOW TABLES")
            tables = [table[0] for table in cur.fetchall()]
            return all(table in tables for table in required_tables)
        except Exception as e:
            print(f"Error checking tables: {e}")
            return False
        finally:
            if conn:
                cur.close()
                self.db.return_connection(conn)

    def create_tables(self):
        conn = self.db.get_connection()
        try:
            cur = conn.cursor()

            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    email VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Forms table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS forms (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    form_data JSON,
                    created_by INT NOT NULL,
                    current_status VARCHAR(50) DEFAULT 'pending',
                    current_step INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)

            # Approvals table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS approvals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    form_id INT NOT NULL,
                    user_id INT NOT NULL,
                    step_number INT NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    comments TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (form_id) REFERENCES forms(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Audit log table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    action VARCHAR(255) NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            conn.commit()
            messagebox.showinfo("Success", "Tables created successfully!")
            self.show_login()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to create tables: {str(e)}")
        finally:
            cur.close()
            self.db.return_connection(conn)

    def show_login(self):
        self.clear_frame()

        # Login frame
        login_frame = ttk.LabelFrame(self.main_frame, text="Login", padding=20)
        login_frame.pack(expand=True)

        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.username_entry = ttk.Entry(login_frame, width=25)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*", width=25)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)

        # Default credentials info
        info_frame = ttk.LabelFrame(self.main_frame, text="Default Admin Credentials", padding=10)
        info_frame.pack(pady=10)
        ttk.Label(info_frame, text="Username: admin").pack()
        ttk.Label(info_frame, text="Password: admin123").pack()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user
            self.db.log_action(user['id'], f"User logged in")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def show_dashboard(self):
        self.clear_frame()

        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(header_frame, text=f"Welcome, {self.current_user['username']} ({self.current_user['role']})", 
                 font=('Arial', 14, 'bold')).pack(side='left')
        ttk.Button(header_frame, text="Logout", command=self.logout).pack(side='right')

        # Navigation
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.pack(fill='x', pady=(0, 10))

        role = self.current_user['role']

        if role in ['Initiator']:
            ttk.Button(nav_frame, text="Create Form", command=self.show_create_form).pack(side='left', padx=5)

        if role in ['User', 'Approver', 'Production Head']:
            ttk.Button(nav_frame, text="Pending Approvals", command=self.show_pending_approvals).pack(side='left', padx=5)

        if role == 'Admin':
            ttk.Button(nav_frame, text="User Management", command=self.show_user_management).pack(side='left', padx=5)
            ttk.Button(nav_frame, text="Audit Log", command=self.show_audit_log).pack(side='left', padx=5)

        ttk.Button(nav_frame, text="My Forms", command=self.show_my_forms).pack(side='left', padx=5)

        # Content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill='both', expand=True)

        self.show_pending_approvals()

    def show_create_form(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        form_frame = ttk.LabelFrame(self.content_frame, text="Create New Form", padding=10)
        form_frame.pack(fill='both', expand=True)

        ttk.Label(form_frame, text="Form Title:").grid(row=0, column=0, sticky='w', pady=5)
        self.form_title = ttk.Entry(form_frame, width=50)
        self.form_title.grid(row=0, column=1, sticky='w', pady=5)

        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky='nw', pady=5)
        self.form_description = scrolledtext.ScrolledText(form_frame, width=50, height=3)
        self.form_description.grid(row=1, column=1, sticky='w', pady=5)

        ttk.Label(form_frame, text="Form Data (JSON):").grid(row=2, column=0, sticky='nw', pady=5)
        self.form_data = scrolledtext.ScrolledText(form_frame, width=50, height=10)
        self.form_data.grid(row=2, column=1, sticky='w', pady=5)

        # Sample form data
        sample_data = {
            "project_name": "",
            "budget": "",
            "deadline": "",
            "team_members": "",
            "description": ""
        }
        self.form_data.insert('1.0', json.dumps(sample_data, indent=2))

        ttk.Button(form_frame, text="Submit Form", command=self.submit_form).grid(row=3, column=1, sticky='w', pady=10)

    def submit_form(self):
        title = self.form_title.get().strip()
        description = self.form_description.get('1.0', 'end').strip()
        form_data_text = self.form_data.get('1.0', 'end').strip()

        if not title or not form_data_text:
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        try:
            form_data = json.loads(form_data_text)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in form data")
            return

        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO forms (title, description, form_data, created_by)
                VALUES (%s, %s, %s, %s)
            """, (title, description, json.dumps(form_data), self.current_user['id']))
            conn.commit()

            self.db.log_action(self.current_user['id'], f"Created form: {title}")
            messagebox.showinfo("Success", "Form submitted successfully!")
            self.show_my_forms()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to submit form: {str(e)}")
        finally:
            cur.close()
            self.db.return_connection(conn)

    def show_pending_approvals(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        approvals_frame = ttk.LabelFrame(self.content_frame, text="Pending Approvals", padding=10)
        approvals_frame.pack(fill='both', expand=True)

        # Create treeview
        columns = ('ID', 'Title', 'Created By', 'Status', 'Step', 'Created')
        tree = ttk.Treeview(approvals_frame, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Get pending forms based on role
        role = self.current_user['role']
        step_mapping = {
            'User': 2,
            'Approver': 3,
            'Production Head': 4
        }

        if role in step_mapping:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT f.id, f.title, u.username, f.current_status, f.current_step, f.created_at
                    FROM forms f
                    JOIN users u ON f.created_by = u.id
                    WHERE f.current_step = %s AND f.current_status = 'pending'
                """, (step_mapping[role],))

                forms = cur.fetchall()
                for form in forms:
                    tree.insert('', 'end', values=form)
            finally:
                cur.close()
                self.db.return_connection(conn)

        tree.pack(fill='both', expand=True)

        # Buttons
        button_frame = ttk.Frame(approvals_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="View/Approve", 
                  command=lambda: self.view_form_for_approval(tree)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.show_pending_approvals).pack(side='left', padx=5)

    def view_form_for_approval(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a form to view")
            return

        form_id = tree.item(selection[0])['values'][0]
        self.show_approval_dialog(form_id)

    def show_approval_dialog(self, form_id):
        dialog = tk.Toplevel(self.root)
        dialog.title("Form Approval")
        dialog.geometry("600x500")

        # Get form details
        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT f.title, f.description, f.form_data, u.username, f.created_at
                FROM forms f
                JOIN users u ON f.created_by = u.id
                WHERE f.id = %s
            """, (form_id,))

            form = cur.fetchone()
            if not form:
                messagebox.showerror("Error", "Form not found")
                dialog.destroy()
                return

            # Display form details
            ttk.Label(dialog, text=f"Title: {form[0]}", font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=5)
            ttk.Label(dialog, text=f"Created by: {form[3]}").pack(anchor='w', padx=10)
            ttk.Label(dialog, text=f"Created: {form[4]}").pack(anchor='w', padx=10)

            ttk.Label(dialog, text="Description:").pack(anchor='w', padx=10, pady=(10, 0))
            desc_text = scrolledtext.ScrolledText(dialog, height=3, width=70)
            desc_text.pack(padx=10, pady=5)
            desc_text.insert('1.0', form[1])
            desc_text.config(state='disabled')

            ttk.Label(dialog, text="Form Data:").pack(anchor='w', padx=10, pady=(10, 0))
            data_text = scrolledtext.ScrolledText(dialog, height=8, width=70)
            data_text.pack(padx=10, pady=5)
            data_text.insert('1.0', json.dumps(json.loads(form[2]), indent=2))
            data_text.config(state='disabled')

            # Previous approvals
            ttk.Label(dialog, text="Previous Approvals:").pack(anchor='w', padx=10, pady=(10, 0))
            approvals_text = scrolledtext.ScrolledText(dialog, height=4, width=70)
            approvals_text.pack(padx=10, pady=5)

            cur.execute("""
                SELECT u.username, a.action, a.comments, a.timestamp
                FROM approvals a
                JOIN users u ON a.user_id = u.id
                WHERE a.form_id = %s
                ORDER BY a.timestamp
            """, (form_id,))

            approvals = cur.fetchall()
            for approval in approvals:
                approvals_text.insert('end', f"{approval[3]} - {approval[0]} {approval[1]}: {approval[2] or 'No comments'}\n")
            approvals_text.config(state='disabled')

            # Comments
            ttk.Label(dialog, text="Your Comments:").pack(anchor='w', padx=10, pady=(10, 0))
            comments_entry = scrolledtext.ScrolledText(dialog, height=3, width=70)
            comments_entry.pack(padx=10, pady=5)

            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=10)

            ttk.Button(button_frame, text="Approve", 
                      command=lambda: self.process_approval(form_id, 'approved', comments_entry.get('1.0', 'end').strip(), dialog)).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Reject", 
                      command=lambda: self.process_approval(form_id, 'rejected', comments_entry.get('1.0', 'end').strip(), dialog)).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)

        finally:
            cur.close()
            self.db.return_connection(conn)

    def process_approval(self, form_id, action, comments, dialog):
        role = self.current_user['role']
        step_mapping = {
            'User': 2,
            'Approver': 3,
            'Production Head': 4
        }

        current_step = step_mapping[role]
        next_step = current_step + 1 if action == 'approved' else current_step
        final_status = 'approved' if action == 'approved' and role == 'Production Head' else ('rejected' if action == 'rejected' else 'pending')

        conn = self.db.get_connection()
        try:
            cur = conn.cursor()

            # Record approval
            cur.execute("""
                INSERT INTO approvals (form_id, user_id, step_number, action, comments)
                VALUES (%s, %s, %s, %s, %s)
            """, (form_id, self.current_user['id'], current_step, action, comments))

            # Update form status
            if action == 'rejected' or (action == 'approved' and role == 'Production Head'):
                cur.execute("""
                    UPDATE forms SET current_status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (final_status, form_id))
            elif action == 'approved':
                cur.execute("""
                    UPDATE forms SET current_step = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (next_step, form_id))

            conn.commit()
            self.db.log_action(self.current_user['id'], f"Form {form_id} {action} with comments: {comments}")

            messagebox.showinfo("Success", f"Form {action} successfully!")
            dialog.destroy()
            self.show_pending_approvals()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to process approval: {str(e)}")
        finally:
            cur.close()
            self.db.return_connection(conn)

    def show_my_forms(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        forms_frame = ttk.LabelFrame(self.content_frame, text="My Forms", padding=10)
        forms_frame.pack(fill='both', expand=True)

        # Create treeview
        columns = ('ID', 'Title', 'Status', 'Step', 'Created', 'Updated')
        tree = ttk.Treeview(forms_frame, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Get user's forms
        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, title, current_status, current_step, created_at, updated_at
                FROM forms
                WHERE created_by = %s
                ORDER BY updated_at DESC
            """, (self.current_user['id'],))

            forms = cur.fetchall()
            for form in forms:
                tree.insert('', 'end', values=form)
        finally:
            cur.close()
            self.db.return_connection(conn)

        tree.pack(fill='both', expand=True)

    def show_user_management(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        users_frame = ttk.LabelFrame(self.content_frame, text="User Management", padding=10)
        users_frame.pack(fill='both', expand=True)

        # Create user form
        form_frame = ttk.Frame(users_frame)
        form_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        username_entry = ttk.Entry(form_frame)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Password:").grid(row=0, column=2, padx=5, pady=5)
        password_entry = ttk.Entry(form_frame, show="*")
        password_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Role:").grid(row=1, column=0, padx=5, pady=5)
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(form_frame, textvariable=role_var, 
                                 values=['Admin', 'Initiator', 'Production Head', 'Operator', 'User', 'Approver'])
        role_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=1, column=2, padx=5, pady=5)
        email_entry = ttk.Entry(form_frame)
        email_entry.grid(row=1, column=3, padx=5, pady=5)

        def create_user():
            if not all([username_entry.get(), password_entry.get(), role_var.get()]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            import bcrypt
            password_hash = bcrypt.hashpw(password_entry.get().encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO users (username, password_hash, role, email)
                    VALUES (%s, %s, %s, %s)
                """, (username_entry.get(), password_hash, role_var.get(), email_entry.get()))
                conn.commit()

                messagebox.showinfo("Success", "User created successfully!")
                username_entry.delete(0, 'end')
                password_entry.delete(0, 'end')
                email_entry.delete(0, 'end')
                role_var.set('')
                self.show_user_management()

            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Failed to create user: {str(e)}")
            finally:
                cur.close()
                self.db.return_connection(conn)

        ttk.Button(form_frame, text="Create User", command=create_user).grid(row=2, column=1, pady=10)

        # Users list
        columns = ('ID', 'Username', 'Role', 'Email', 'Active', 'Created')
        tree = ttk.Treeview(users_frame, columns=columns, show='headings', height=12)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Load users
        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, username, role, email, is_active, created_at FROM users ORDER BY username")
            users = cur.fetchall()
            for user in users:
                tree```python
.insert('', 'end', values=user)
        finally:
            cur.close()
            self.db.return_connection(conn)

        tree.pack(fill='both', expand=True)

    def show_audit_log(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        audit_frame = ttk.LabelFrame(self.content_frame, text="Audit Log", padding=10)
        audit_frame.pack(fill='both', expand=True)

        columns = ('ID', 'User', 'Action', 'Details', 'Timestamp')
        tree = ttk.Treeview(audit_frame, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT a.id, u.username, a.action, a.details, a.timestamp
                FROM audit_log a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.timestamp DESC
                LIMIT 100
            """)
            logs = cur.fetchall()
            for log in logs:
                tree.insert('', 'end', values=log)
        finally:
            cur.close()
            self.db.return_connection(conn)

        tree.pack(fill='both', expand=True)

    def logout(self):
        self.db.log_action(self.current_user['id'], "User logged out")
        self.current_user = None
        self.show_login()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = FormApprovalApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Make sure MySQL database is set up and configured properly")