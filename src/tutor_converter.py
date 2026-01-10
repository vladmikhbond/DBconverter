import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import datetime as dt

from src.tutor_models import Disc, Lecture, Picture

conn_str_ask = 'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=HP2\\SQLEXPRESS; DATABASE=Ask; Trusted_Connection=yes'
path_to_db = "sqlite:///C:/docker_bag/data/Tutor.db"

# Create target DB
engine = create_engine(path_to_db, echo=False)
# Base.metadata.create_all(engine)


def convert_disc(disc_title: str, username: str, lang: str):
    disc = None
    with Session(engine) as db:
        same_titlt_discs = db.query(Disc).filter(Disc.title == disc_title).all()
        if len(same_titlt_discs) > 0:
            print ("same_titlt_discs")
            return
        disc = Disc(username=username,
                    title=disc_title,
                    lang=lang,
                    theme="black")
        db.add(disc)
        db.commit()
        db.refresh(disc)

    rows = read_lectures(disc)
    write_lectures(disc, rows)

    rows = read_pictures(disc)
    write_pictures(disc, rows)

def read_lectures(disc: Disc):
    with pyodbc.connect(conn_str_ask) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT Title, Content FROM Lecture WHERE TutorName='{disc.title}'")
        rows = cursor.fetchall()
    return rows

def write_lectures(disc: Disc, rows) -> None:
    with Session(engine) as db:
        for r in rows:
            content = r[1].replace("@1", '🔴1').replace("@2", '🔴2').replace("@3", '📔3') \
                          .replace("@4", '❗4').replace("@5", '📘5');  
            lecture = Lecture(
                disc_id=disc.id,
                content=content,
                is_public=False,
                modified=dt.datetime.now()
            )
            db.add(lecture)

        db.commit()      

def read_pictures(disc: Disc):
    with pyodbc.connect(conn_str_ask) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT TutorName, PictureName, Content FROM Picture WHERE TutorName='{disc.title}'")
        rows = cursor.fetchall()
    return rows

def write_pictures(disc: Disc, rows) -> None:
    with Session(engine) as db:
        for r in rows:
            picture = Picture(
                title=r[1],
                disc_id=disc.id,
                image=r[2]
            )
            db.add(picture)
        db.commit()      


def beauty():
    with Session(engine) as db:
        lectures = db.query(Lecture).all()
        for lec in lectures:
            ss = lec.content.splitlines()
            for i, s in enumerate(ss):
                if   s.startswith('🔴1'): ss[i] = '🔴' + s[2:]
                elif s.startswith('🔴2'): ss[i] = '🟥' + s[2:]
                elif s.startswith('📔3'): ss[i] = '🟦' + s[2:]
                elif s.startswith('❗4'): ss[i] = '🟨' + s[2:]
                elif s.startswith('📗5'): ss[i] = '🟩' + s[2:]
                elif s.startswith('📘6'): ss[i] = '⬛' + s[2:]
            lec.content = '\n'.join(ss)
        db.commit()
    return len(lectures)        




if __name__ == "__main__":
    beauty()
    # convert_disc(disc_title="vba", username="tutor", lang="js")

