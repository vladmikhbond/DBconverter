import pyodbc
from src.user_models import Base, User
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import bcrypt

conn_str_ask = 'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=HP2\\SQLEXPRESS; DATABASE=Ask; Trusted_Connection=yes'
path_to_db = "sqlite:///C:/docker_bag/data/user.db"

# Create target DB
engine = create_engine(path_to_db, echo=False)
Base.metadata.create_all(engine)

def read_students():
    with pyodbc.connect(conn_str_ask) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT [UserName] FROM [Ask].[dbo].[AspNetUsers]
            WHERE substring([UserName], 1, 1) in ('1','2','3','4','5','6','7','a','b','c','d','e','f','g')""")
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
            

def add_users_for_testing():
    
    hashed_password = bcrypt.hashpw(b"123456", bcrypt.gensalt())
    users = [ 
        # User(username="student", hashed_password=hp, role="student"), 
        # User(username="tutor", hashed_password=hp, role="tutor"), 
        # User(username="admin", hashed_password=hp, role="admin"), 
        User(username="oop", hashed_password=hashed_password, role="tutor"), 
    ]
    with Session(engine) as session:        
        for user in users:           
            session.add(user)
        session.commit()      



if __name__ == "__main__":
    pass
    rows = read_students()
    # write_students(rows)
    print(f"Конвертовано студентів: {len(rows)}")

    # add_users_for_testing()
    # print(f"Додано тестових юзерів")
    # add_test_problemsets()
    # print(f"Додано тестових задачників")
