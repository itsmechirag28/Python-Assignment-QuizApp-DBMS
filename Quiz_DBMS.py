import sqlite3

DB_FILE = "quiz_app.db"

def db_connect():
    return sqlite3.connect(DB_FILE)

# Database Setup
def setup_database():
    with db_connect() as conn:
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                answer TEXT NOT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
            )
        ''')
        conn.commit()

def populate_database():
    with db_connect() as conn:
        cursor = conn.cursor()

        # Seed quizzes
        quizzes = [("Python",), ("DBMS",), ("DSA",)]
        cursor.executemany("INSERT OR IGNORE INTO quizzes (name) VALUES (?)", quizzes)

        # Seed questions
        questions = [
            # Python Quiz
            (1, "Which of the following is the correct way to declare a variable in Python?", "int x = 10,x = 10,variable x = 10 ,declare x = 10", "x = 10"),
            (1, "Which data type is mutable?", "List,Tuple,String,Integer", "List"),
            (1, "What keyword is used to define a function in Python?", "def,func,function,define", "def"),

            # DBMS Quiz
            (2, "What is the purpose of a primary key in a relational database?", "To ensure that all records in a table are unique,To link two tables together,To allow NULL values in the table,To index the data in the table", "To ensure that all records in a table are unique"),
            (2, "Which SQL statement is used to retrieve data?", "INSERT,SELECT,UPDATE,DELETE", "SELECT"),
            (2, "Which of the following is NOT a DDL command?", "CREATE,DROP,SELECT,ALTER", "SELECT"),
            # DSA Quiz
            (3, "What is the time complexity of searching for an element in a balanced binary search tree (BST)?", "O(n),O(logn),O(1),O(nlogn)", "O(nlog n)"),
            (3, "Which data structure is used to implement recursion?", "Queue,Stack,Array,Linked List", "Stack"),
            (3, "Which algorithm is used for finding the shortest path in a weighted graph with non-negative weights?", "Breadth-First Search (BFS),Depth-First Search (DFS),Kruskal's Algorithm,Dijktra's Algorithm", "Dijktra's Algorithm"),
            ]
        cursor.executemany("INSERT OR IGNORE INTO quiz_questions (quiz_id, question, options, answer) VALUES (?, ?, ?, ?)", questions)
        conn.commit()

# User Management
def register():
    username = input("Enter your username: ").strip().lower()
    password = input("Enter your password: ").strip()

    with db_connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            print("Registration successful!")
        except sqlite3.IntegrityError:
            print("username already registered!")

def login():
    username = input("Enter your username: ").strip().lower()
    password = input("Enter your password: ").strip()

    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            print("Login successful!")
            return user[0]  # Return user ID
        else:
            print("Invalid username or password.")
            return None

# Quiz Management
def quiz_option():
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM quizzes")
        return cursor.fetchall()

def quiz(user_id):
    quizzes = quiz_option()

    print("\nAvailable Quizzes:")
    for idx, (quiz_id, name) in enumerate(quizzes, start=1):
        print(f"{idx}. {name}")

    choice = input("Choose a quiz by number: ").strip()
    try:
        quiz_id = quizzes[int(choice) - 1][0]
    except (IndexError, ValueError):
        print("Invalid choice.")
        return

    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT question, options, answer FROM quiz_questions WHERE quiz_id = ?", (quiz_id,))
        questions = cursor.fetchall()

        if not questions:
            print("No questions available for this quiz.")
            return

        score = 0
        for question, options, answer in questions:
            print(f"\n{question}")
            options = options.split(",")  # Assuming options stored as "A,B,C,D"
            for idx, opt in enumerate(options, start=1):
                print(f"{idx}. {opt}")

            user_answer = input("Your answer: ").strip()
            try:
                if options[int(user_answer) - 1] == answer:
                    score += 1
            except (IndexError, ValueError):
                print("Invalid answer.")
        print(f"\nYou scored {score}/{len(questions)}!")
        cursor.execute("INSERT INTO user_scores (user_id, quiz_id, score) VALUES (?, ?, ?)", (user_id, quiz_id, score))
        conn.commit()

# Show Results
def show_results(user_id):
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT quizzes.name, user_scores.score 
            FROM user_scores 
            JOIN quizzes ON user_scores.quiz_id = quizzes.id 
            WHERE user_scores.user_id = ?
        """, (user_id,))
        results = cursor.fetchall()

    if results:
        print("\nYour Quiz Results:")
        for quiz_name, score in results:
            print(f"Quiz: {quiz_name}, Score: {score}")
    else:
        print("No quiz attempts found.")

# Main Menu
def main():
    current_user_id = None

    # Setup and populate database
    setup_database()
    populate_database()

    while True:
        print("\n1. Register\n2. Login\n3. Take Quiz\n4. Show Results\n5. Exit")
        choice = input("Select an option: ").strip()

        if choice == '1':
            register()
        elif choice == '2':
            current_user_id = login()
        elif choice == '3':
            if current_user_id:
                quiz(current_user_id)
            else:
                print("Please log in first!")
        elif choice == '4':
            if current_user_id:
                show_results(current_user_id)
            else:
                print("Please log in first!")
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
