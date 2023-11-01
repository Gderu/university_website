DROP TABLE IF EXISTS semester;
DROP TABLE IF EXISTS user_data;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS user_course_privileges;
DROP TABLE IF EXISTS exercise_check;

CREATE TABLE semester (
    name TEXT PRIMARY KEY,
    student_pay REAL NOT NULL,
    graduate_pay REAL NOT NULL,
    budget INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_data (
    id INTEGER PRIMARY KEY,
    password BLOB NOT NULL,
    name TEXT NOT NULL,
    mail TEXT UNIQUE,
    role INTEGER NOT NULL,
    is_student INTEGER DEFAULT 0
);

CREATE TABLE course (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    points REAL NOT NULL,
    num_students INTEGER NOT NULL,
    num_exercises INTEGER NOT NULL,
    used_exercises INTEGER NOT NULL,
    semester_name TEXT NOT NULL,
    lecturer_id TEXT NOT NULL,
    FOREIGN KEY(semester_name) REFERENCES semester(name),
    FOREIGN KEY(lecturer_id) REFERENCES user_data(id)
);

CREATE TABLE user_course_privileges (
    user_id INTEGER NOT NULL,
    course_id TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES user_data(id),
    FOREIGN KEY(course_id) REFERENCES course(id),
    UNIQUE (user_id, course_id)
);

CREATE TABLE exercise_check (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,
    checker_id INTEGER NOT NULL,
    request_open_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    request_close_date DATETIME,
    num_exercises INTEGER NOT NULL,
    description TEXT,
    accepted INTEGER,
    FOREIGN KEY(course_id) REFERENCES course(id)
);

INSERT INTO user_data (id, password, name, mail, role, is_student) VALUES
(000000000, "scrypt:32768:8:1$3A8aMadksRoRR3OZ$a130546a94af48a61b2cf1e530fac4370a83d8be58662ee7a69aa70aab9890e46105d26ec1149553de07623c25eda47a81da7a962b6134ad05ee60acd0590258", --321123
 "מנהל", "admin@admin.com", 0, 0);