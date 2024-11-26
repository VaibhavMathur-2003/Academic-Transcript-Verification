CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course TEXT NOT NULL,
    course_title TEXT NOT NULL,
    credits INTEGER NOT NULL,
    reg_type TEXT NOT NULL,
    elective_type TEXT NOT NULL,
    branch TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    parent_course_id INTEGER,
    is_current BOOLEAN DEFAULT 1
);
