#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate

from models import db, Article, User, ArticleSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

with app.app_context():
    db.create_all()

    if Article.query.count() == 0:
        default_user = User(name='Test User')
        db.session.add(default_user)

        for i in range(1, 5):
            article = Article(
                author=f'Author {i}',
                title=f'Test Article {i}',
                content=f'This is test content for article {i}.',
                preview=f'This is test content for article {i}.',
                minutes_to_read=1,
                user=default_user,
            )
            db.session.add(article)

        db.session.commit()

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles')
def index_articles():
    articles = [ArticleSchema().dump(a) for a in Article.query.all()]
    return jsonify(articles), 200

@app.route('/articles/<int:id>')
def show_article(id):
    # Initialize the page view count for a new session
    session['page_views'] = session.get('page_views', 0) + 1

    # Enforce a maximum of three article views per session
    if session['page_views'] > 3:
        return jsonify({'message': 'Maximum pageview limit reached'}), 401

    article = Article.query.get_or_404(id)
    article_data = ArticleSchema().dump(article)
    return jsonify(article_data), 200


if __name__ == '__main__':
    app.run(port=5555)