from csv import DictReader

from django.core.management import BaseCommand

from api_yamdb import settings
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

CSV_PATH = f"{settings.BASE_DIR}/static/data/"

CSV_TABLES = {
    "User": DictReader(open(f"{CSV_PATH}users.csv", encoding="utf-8")),
    "Category": DictReader(open(f"{CSV_PATH}category.csv", encoding="utf-8")),
    "Genre": DictReader(open(f"{CSV_PATH}genre.csv", encoding="utf-8")),
    "Title": DictReader(open(f"{CSV_PATH}titles.csv", encoding="utf-8")),
    "GenreTitle": DictReader(
        open(f"{CSV_PATH}genre_title.csv", encoding="utf-8")
    ),
    "Review": DictReader(open(f"{CSV_PATH}review.csv", encoding="utf-8")),
    "Comment": DictReader(open(f"{CSV_PATH}comments.csv", encoding="utf-8")),
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        for value in CSV_TABLES["User"]:
            User.objects.get_or_create(
                pk=value["id"],
                username=value["username"],
                email=value["email"],
                role=value["role"],
                bio=value["bio"],
                first_name=value["first_name"],
                last_name=value["last_name"],
            )
        for value in CSV_TABLES["Category"]:
            Category.objects.get_or_create(
                pk=value["id"], name=value["name"], slug=value["slug"]
            )
        for value in CSV_TABLES["Genre"]:
            Genre.objects.get_or_create(
                pk=value["id"], name=value["name"], slug=value["slug"]
            )
        for value in CSV_TABLES["Title"]:
            category = Category.objects.get(pk=value["category"])
            Title.objects.get_or_create(
                pk=value["id"],
                name=value["name"],
                year=value["year"],
                category=category,
            )
        for value in CSV_TABLES["GenreTitle"]:
            title = Title.objects.get(pk=value["title_id"])
            genre = Genre.objects.get(pk=value["genre_id"])
            Title.genre.through.objects.get_or_create(
                pk=value["id"], title=title, genre=genre
            )
        for value in CSV_TABLES["Review"]:
            title = Title.objects.get(pk=value["title_id"])
            author = User.objects.get(pk=value["author"])
            Review.objects.get_or_create(
                pk=value["id"],
                title=title,
                text=value["text"],
                author=author,
                score=value["score"],
                pub_date=value["pub_date"],
            )
        for value in CSV_TABLES["Comment"]:
            review = Review.objects.get(pk=value["review_id"])
            author = User.objects.get(pk=value["author"])
            Comment.objects.get_or_create(
                pk=value["id"],
                review=review,
                text=value["text"],
                author=author,
                pub_date=value["pub_date"],
            )
