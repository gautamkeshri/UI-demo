
-- Test data for Form Approval System
-- This file contains sample users and forms for testing the application

-- Clear existing data (optional - uncomment if you want to start fresh)
-- DELETE FROM approvals;
-- DELETE FROM audit_log;
-- DELETE FROM forms;
-- DELETE FROM users WHERE username != 'admin';

-- Insert test users with different roles
INSERT INTO users (username, password_hash, role, email, is_active) VALUES
-- Password for all test users is 'password123'
('john_initiator', '$2b$12$LQv3c1yqBwEHFBTqZfJJRu.kHYI8.6zH8Xg4Gx3qRzZ3J2YnK4uUe', 'Initiator', 'john@company.com', TRUE),
('mary_user', '$2b$12$LQv3c1yqBwEHFBTqZfJJRu.kHYI8.6zH8Xg4Gx3qRzZ3J2YnK4uUe', 'User', 'mary@company.com', TRUE),
('steve_approver', '$2b$12$LQv3c1yqBwEHFBTqZfJJRu.kHYI8.6zH8Xg4Gx3qRzZ3J2YnK4uUe', 'Approver', 'steve@company.com', TRUE),
('lisa_prodhead', '$2b$12$LQv3c1yqBwEHFBTqZfJJRu.kHYI8.6zH8Xg4Gx3qRzZ3J2YnK4uUe', 'Production Head', 'lisa@company.com', TRUE),
('mike_operator', '$2b$12$LQv3c1yqBwEHFBTqZfJJRu.kHYI8.6zH8Xg4Gx3qRzZ3J2YnK4uUe', 'Operator', 'mike@company.com', TRUE),
('sarah_initiator', '$2b$12$LQv3c1yqBwEHFBTqZfJJRu.kHYI8.6zH8Xg4Gx3qRzZ3J2YnK4uUe', 'Initiator', 'sarah@company.com', TRUE);

-- Insert test forms with various statuses
INSERT INTO forms (title, description, form_data, created_by, current_status, current_step, created_at, updated_at) VALUES
(
    'New Marketing Campaign Proposal',
    'Proposal for Q2 2024 marketing campaign targeting young professionals',
    '{"project_name": "Q2 Social Media Campaign", "budget": "50000", "deadline": "2024-06-30", "team_members": "Marketing Team, Creative Agency", "description": "Comprehensive social media campaign across Instagram, LinkedIn, and TikTok targeting 25-35 age demographic"}',
    (SELECT id FROM users WHERE username = 'john_initiator'),
    'pending',
    2,
    '2024-01-15 09:30:00',
    '2024-01-15 09:30:00'
),
(
    'Equipment Purchase Request',
    'Request for new laptops for development team',
    '{"project_name": "Development Team Hardware Upgrade", "budget": "25000", "deadline": "2024-02-28", "team_members": "IT Department, Finance", "description": "Purchase of 10 high-performance laptops for the software development team to improve productivity"}',
    (SELECT id FROM users WHERE username = 'sarah_initiator'),
    'pending',
    3,
    '2024-01-14 14:20:00',
    '2024-01-16 10:15:00'
),
(
    'Office Renovation Project',
    'Complete renovation of the 3rd floor office space',
    '{"project_name": "3rd Floor Office Renovation", "budget": "75000", "deadline": "2024-04-15", "team_members": "Facilities, HR, External Contractors", "description": "Full renovation including new flooring, lighting, workstations, and meeting rooms to accommodate 30 additional employees"}',
    (SELECT id FROM users WHERE username = 'john_initiator'),
    'approved',
    4,
    '2024-01-10 11:00:00',
    '2024-01-18 16:45:00'
),
(
    'Employee Training Program',
    'Quarterly training program for all departments',
    '{"project_name": "Q1 Professional Development Training", "budget": "15000", "deadline": "2024-03-31", "team_members": "HR, Training Vendors", "description": "Comprehensive training program covering leadership skills, technical updates, and compliance requirements for all employees"}',
    (SELECT id FROM users WHERE username = 'sarah_initiator'),
    'rejected',
    2,
    '2024-01-12 08:45:00',
    '2024-01-17 13:20:00'
),
(
    'Mobile App Development',
    'Development of customer-facing mobile application',
    '{"project_name": "Customer Mobile App", "budget": "120000", "deadline": "2024-08-31", "team_members": "Development Team, UX/UI Designers, QA Team", "description": "Native mobile application for iOS and Android platforms with features for account management, product browsing, and customer support"}',
    (SELECT id FROM users WHERE username = 'john_initiator'),
    'pending',
    4,
    '2024-01-08 16:30:00',
    '2024-01-19 09:10:00'
);

-- Insert approval records for completed workflows
INSERT INTO approvals (form_id, user_id, step_number, action, comments, timestamp) VALUES
-- Office Renovation Project approvals (approved through all steps)
(
    (SELECT id FROM forms WHERE title = 'Office Renovation Project'),
    (SELECT id FROM users WHERE username = 'mary_user'),
    2,
    'approved',
    'Project scope looks comprehensive and budget is reasonable.',
    '2024-01-16 10:30:00'
),
(
    (SELECT id FROM forms WHERE title = 'Office Renovation Project'),
    (SELECT id FROM users WHERE username = 'steve_approver'),
    3,
    'approved',
    'All compliance requirements are met. Approved for final review.',
    '2024-01-17 14:15:00'
),
(
    (SELECT id FROM forms WHERE title = 'Office Renovation Project'),
    (SELECT id FROM users WHERE username = 'lisa_prodhead'),
    4,
    'approved',
    'Final approval granted. Project can proceed as planned.',
    '2024-01-18 16:45:00'
),

-- Employee Training Program approvals (rejected at step 2)
(
    (SELECT id FROM forms WHERE title = 'Employee Training Program'),
    (SELECT id FROM users WHERE username = 'mary_user'),
    2,
    'rejected',
    'Budget allocation conflicts with other Q1 priorities. Please revise and resubmit.',
    '2024-01-17 13:20:00'
),

-- Equipment Purchase Request approvals (approved to step 3)
(
    (SELECT id FROM forms WHERE title = 'Equipment Purchase Request'),
    (SELECT id FROM users WHERE username = 'mary_user'),
    2,
    'approved',
    'Hardware upgrade is necessary for team productivity. Budget approved.',
    '2024-01-16 10:15:00'
),

-- Mobile App Development approvals (approved through step 3)
(
    (SELECT id FROM forms WHERE title = 'Mobile App Development'),
    (SELECT id FROM users WHERE username = 'mary_user'),
    2,
    'approved',
    'Strategic initiative aligns with company digital transformation goals.',
    '2024-01-17 11:30:00'
),
(
    (SELECT id FROM forms WHERE title = 'Mobile App Development'),
    (SELECT id FROM users WHERE username = 'steve_approver'),
    3,
    'approved',
    'Technical requirements reviewed and approved. Ready for final budget approval.',
    '2024-01-19 09:10:00'
);

-- Insert audit log entries
INSERT INTO audit_log (user_id, action, details, timestamp) VALUES
((SELECT id FROM users WHERE username = 'john_initiator'), 'User logged in', '', '2024-01-15 09:00:00'),
((SELECT id FROM users WHERE username = 'john_initiator'), 'Created form: New Marketing Campaign Proposal', '', '2024-01-15 09:30:00'),
((SELECT id FROM users WHERE username = 'sarah_initiator'), 'User logged in', '', '2024-01-14 14:00:00'),
((SELECT id FROM users WHERE username = 'sarah_initiator'), 'Created form: Equipment Purchase Request', '', '2024-01-14 14:20:00'),
((SELECT id FROM users WHERE username = 'mary_user'), 'User logged in', '', '2024-01-16 10:00:00'),
((SELECT id FROM users WHERE username = 'mary_user'), 'Form 2 approved with comments: Hardware upgrade is necessary for team productivity. Budget approved.', '', '2024-01-16 10:15:00'),
((SELECT id FROM users WHERE username = 'steve_approver'), 'User logged in', '', '2024-01-17 14:00:00'),
((SELECT id FROM users WHERE username = 'steve_approver'), 'Form 3 approved with comments: All compliance requirements are met. Approved for final review.', '', '2024-01-17 14:15:00'),
((SELECT id FROM users WHERE username = 'lisa_prodhead'), 'User logged in', '', '2024-01-18 16:30:00'),
((SELECT id FROM users WHERE username = 'lisa_prodhead'), 'Form 3 approved with comments: Final approval granted. Project can proceed as planned.', '', '2024-01-18 16:45:00'),
((SELECT id FROM users WHERE username = 'mary_user'), 'Form 4 rejected with comments: Budget allocation conflicts with other Q1 priorities. Please revise and resubmit.', '', '2024-01-17 13:20:00');

-- Display summary of inserted data
SELECT 'Data insertion completed successfully!' as Status;

SELECT 'Users created:' as Info, COUNT(*) as Count FROM users WHERE username != 'admin';
SELECT 'Forms created:' as Info, COUNT(*) as Count FROM forms;
SELECT 'Approvals recorded:' as Info, COUNT(*) as Count FROM approvals;
SELECT 'Audit log entries:' as Info, COUNT(*) as Count FROM audit_log;

-- Show current form statuses for reference
SELECT 
    f.title,
    f.current_status,
    f.current_step,
    u.username as created_by
FROM forms f
JOIN users u ON f.created_by = u.id
ORDER BY f.created_at;
