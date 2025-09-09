import pyodbc
from pss_models import Base, Problem, ProblemSet, User
from sqlalchemy import create_engine, String, DateTime
from sqlalchemy.orm import Session
import datetime
import uuid
import bcrypt


conn_str_tss = 'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=HP2\\SQLEXPRESS; DATABASE=TSS; Trusted_Connection=yes'
conn_str_ask = 'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=HP2\\SQLEXPRESS; DATABASE=Ask; Trusted_Connection=yes'
path_to_db = "sqlite:///PSS.db"

engine = create_engine(path_to_db, echo=False)
Base.metadata.create_all(engine)


def read_problems():
    with pyodbc.connect(conn_str_tss) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Title, Attr, Lang, Cond, [View], Hint, Code, Author FROM Tasks")
        rows = cursor.fetchall()
    return rows


def write_problems(rows) -> None:

    with Session(engine) as db:
        db.query(Problem).delete()  # Видалити всі рядки з таблиці Problems
        for r in rows:
            prob = Problem(
                id = str(uuid.uuid4()),  # '550e8400-e29b-41d4-a716-446655440000'
                title = r[1],
                attr = r[2],
                lang = r[3],
                cond = r[4],
                view = r[5],
                hint = r[6],
                code = r[7],
                author = r[8] if r[8] else "noname",
                timestamp = datetime.datetime.now()
            )
            db.add(prob)
        db.commit()      

def read_students():
    with pyodbc.connect(conn_str_ask) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT [UserName] FROM [Ask].[dbo].[AspNetUsers]
            WHERE substring([UserName], 1, 1) in ('1','2','3','4','5','6','7')""")
        rows = cursor.fetchall()
    return rows


def write_students(rows) -> None:
    with Session(engine) as session:
        session.query(User).delete()  # Видалити всі рядки з таблиці Users
        session.commit()
        hp = bcrypt.hashpw(b"123456", bcrypt.gensalt()) 
        for r in rows:
            user = User(
                username = r[0],
                hashed_password = hp,   # bcrypt.hashpw(b"123456", bcrypt.gensalt()),
                role="student"
            )
            session.add(user)
            session.commit()
            print(r[0])
            

def add_test_users():
    
    hp = bcrypt.hashpw(b"123456", bcrypt.gensalt())
    users = [ 
        User(username="student", hashed_password=hp, role="student"), 
        User(username="tutor", hashed_password=hp, role="tutor"), 
        User(username="admin", hashed_password=hp, role="admin"), 
    ]
    with Session(engine) as session:        
        for user in users:           
            session.add(user)
        session.commit()      


def add_test_problemsets():
    probsets = [
        ProblemSet(id="Задачник1", user_id="tutor", open_time=datetime.datetime.now(), open_minutes=0,
                   problem_ids="326f85e2-7013-4ceb-8b33-e755686b8465 ad70aca4-ab88-499c-9a8f-91b4a448f2e6 9b873d4f-2ee2-487e-910e-a22f4cdee43c"),
        ProblemSet(id="Задачник2", user_id="tutor", open_time=datetime.datetime.now(), open_minutes=0,
                   problem_ids="326f85e2-7013-4ceb-8b33-e755686b8465 ad70aca4-ab88-499c-9a8f-91b4a448f2e6 9b873d4f-2ee2-487e-910e-a22f4cdee43c"),
    ]
    with Session(engine) as session:        
        for probset in probsets:           
            session.add(probset)
        session.commit()      


if __name__ == "__main__":
    rows = read_students()
    write_students(rows)
    print(f"Конвертовано студентів: {len(rows)}")


    rows = read_problems()
    write_problems(rows)
    print(f"Конвертовано задач: {len(rows)}")

    add_test_users()
    print(f"Додано тестових юзерів")
    add_test_problemsets()
    print(f"Додано тестових задачників")
