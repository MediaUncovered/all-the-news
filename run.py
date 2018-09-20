import sys
import csv
from dateutil.parser import parse
import all_the_news.model as model

csv.field_size_limit(sys.maxsize)  # some rows can be large


def insert_source(session, name):
    source = model.Source(name=name)
    session.add(source)
    session.commit()
    return source


def loop_through_data(session, reader):
    for row in reader:
        article = model.Article(
            url=row["url"],
            title=row["title"],
            body=row["content"],
            published=parse(row["date"]),
            html=None,
        )


        publication = row["publication"]

        source = session.query(model.Source) \
            .filter(model.Source.name == publication) \
            .one_or_none()

        if source is None:
            source = insert_source(session, publication)

        duplicate = session.query(model.Article) \
            .filter(model.Article.title == article.title and model.Article.url == article.url) \
            .one_or_none()
        if duplicate is None:
            article.source = source
            session.add(article)
            session.commit()

        print("%s: %s" % (row["id"], article.title))


engine = model.engine(database_user="mysecretuser", database_host="localhost", database_port="5432",
                      database_name="media_uncovered", database_password="mysecretpassword")
session = model.session(engine)


file = open("data/articles1.csv", "rU")
reader = csv.DictReader(file, delimiter=',')

loop_through_data(session, reader)

