import pyodbc
from src.pss_models import Base, Problem, ProblemSet, User
from sqlalchemy import create_engine, String, DateTime
from sqlalchemy.orm import Session
import datetime
import uuid

conn_str_tss = 'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=HP2\\SQLEXPRESS; DATABASE=TSS; Trusted_Connection=yes'
path_to_db = "sqlite:///PSS.db"

# Create target DB
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


def add_testing_problemsets():

    probsets = [
        ProblemSet(title="Задачник1", username="tutor", open_time=datetime.datetime.now(), open_minutes=0,
                   problem_ids=""),
        ProblemSet(title="Задачник2", username="tutor", open_time=datetime.datetime.now(), open_minutes=0,
                   problem_ids=""),
    ]
    with Session(engine) as db:        
        for probset in probsets:
            ids = map(lambda p: p.id, db.query(Problem).all()[:3]) 
            probset.problem_ids = ' '.join(ids)                 
            db.add(probset)
        db.commit()      


if __name__ == "__main__":
    pass
    # rows = read_problems()
    # write_problems(rows)
    # print(f"Конвертовано задач: {len(rows)}")

