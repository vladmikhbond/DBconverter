import pyodbc
from pss_models import Base, Problem, ProblemSet, User
from sqlalchemy import create_engine, String, DateTime
from sqlalchemy.orm import Session
import datetime
import uuid


conn_str = 'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=HP2\\SQLEXPRESS; DATABASE=TSS; Trusted_Connection=yes'
path_to_db = "sqlite:///PSS.db"

engine = create_engine(path_to_db, echo=False)
Base.metadata.create_all(engine)


def read_problems():
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Title, Attr, Lang, Cond, [View], Hint, Code, Author FROM Tasks")
        rows = cursor.fetchall()
    return rows


def write_problems(rows) -> None:

    with Session(engine) as session:
        session.query(Problem).delete()  # Видалити всі рядки з таблиці Problems
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
            session.add(prob)
        session.commit()      

def add_test_users():
    import bcrypt
    hp1 = bcrypt.hashpw(b"123456", bcrypt.gensalt())
    hp2 = bcrypt.hashpw(b"123456", bcrypt.gensalt())
    hp3 = bcrypt.hashpw(b"123456", bcrypt.gensalt())

    users = [ 
        User(username="student", hashed_password=hp1, role="student"), 
        User(username="tutor", hashed_password=hp2, role="tutor"), 
        User(username="admin", hashed_password=hp3, role="admin"), 
    ]
    with Session(engine) as session:        
        for user in users:           
            session.add(user)
        session.commit()      


def add_test_problemsets():
    probsets = [
        ProblemSet(id="Задачник1", user_id="1Ivanenko", open_time=datetime.datetime.now(), open_minutes=0,
                   problem_ids="326f85e2-7013-4ceb-8b33-e755686b8465 ad70aca4-ab88-499c-9a8f-91b4a448f2e6 9b873d4f-2ee2-487e-910e-a22f4cdee43c"),
        ProblemSet(id="Задачник2", user_id="1Ivanenko", open_time=datetime.datetime.now(), open_minutes=0,
                   problem_ids="326f85e2-7013-4ceb-8b33-e755686b8465 ad70aca4-ab88-499c-9a8f-91b4a448f2e6 9b873d4f-2ee2-487e-910e-a22f4cdee43c"),
    ]
    with Session(engine) as session:        
        for probset in probsets:           
            session.add(probset)
        session.commit()      


if __name__ == "__main__":
    pass
    # rows = read_problems()
    # write_problems(rows)
    # print(f"Конвертовано задач: {len(rows)}")
    add_test_users()
    print(f"Додано тестових юзерів")
    # add_test_problemsets()
    # print(f"Додано тестових задачників")
