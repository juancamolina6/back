from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from os import getenv
from models import Post, Comment
from auth import requires_auth
import psycopg2


app = Flask(__name__)
CORS(app)

# configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# definir las rutas aquí
@app.route('/posts', methods=['GET'])
@requires_auth
def list_posts():
    posts = Post.query.all()
    return jsonify([post.to_dict() for post in posts]), 200

@app.route('/posts', methods=['POST'])
@requires_auth
def create_post():
    data = request.json
    post = Post(title=data['title'], body=data['body'])
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201

@app.route('/posts/<int:id>', methods=['DELETE'])
@requires_auth
def delete_post(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'}), 200

@app.route('/posts/<int:post_id>/comments', methods=['GET'])
@requires_auth
def list_comments(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404

    comments = Comment.query.filter_by(post_id=post_id).all()
    return jsonify([comment.to_dict() for comment in comments]), 200

@app.route('/posts/<int:post_id>/comments', methods=['POST'])
@requires_auth
def create_comment(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.json
    comment = Comment(body=data['body'], post=post)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201

if __name__ == '__main__':
    db.create_all() # Crear las tablas en la base de datos
    app.run()
