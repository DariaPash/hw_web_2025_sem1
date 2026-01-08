# Generated migration for fulltext search indexes

from django.db import migrations
from django.contrib.postgres.operations import BtreeGinExtension


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_answer_dislikes_cnt_answer_likes_cnt_and_more'),
    ]

    operations = [
        BtreeGinExtension(),
        migrations.RunSQL(
            # Создаем GIN индекс для полнотекстового поиска
            sql="""
            CREATE INDEX IF NOT EXISTS app_question_title_text_gin_idx 
            ON app_question 
            USING gin(to_tsvector('russian', coalesce(title, '') || ' ' || coalesce(text, '')));
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS app_question_title_text_gin_idx;
            """
        ),
    ]
