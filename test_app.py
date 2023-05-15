import os
import pytest
from app import app, db, Post, Comment


@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.create_all()
        post1 = Post(title='Test post 1', body='Test post 1 body')
        post2 = Post(title='Test post 2', body='Test post 2 body')
        db.session.add(post1)
        db.session.add(post2)
        db.session.commit()

    yield client

    with app.app_context():
        db.drop_all()


def test_list_posts(client):
    response = client.get('/posts', headers={
        'Authorization': 'Basic YWRtaW46c2VjcmV0'
    })
    assert response.status_code == 200
    assert len(response.json) == 2


def test_create_post(client):
    response = client.post('/posts', json={
        'title': 'New test post',
        'body': 'New test post body'
    }, headers={
        'Authorization': 'Basic YWRtaW46c2VjcmV0'
    })
    assert response.status_code == 201
    assert response.json['title'] == 'New test post'


def test_delete_post(client):
    posts = Post.query.all()
    post_id = posts[0].id
    response = client.delete(f'/posts/{post_id}', headers={
        'Authorization': 'Basic YWRtaW46c2VjcmV0'
    })
    assert response.status_code == 200
    assert Post.query.get(post_id) is None


def test_list_comments(client):
    posts = Post.query.all()
    post_id = posts[0].id
    comment1 = Comment(name='Test comment 1', body='Test comment 1 body', post_id=post_id)
    comment2 = Comment(name='Test comment 2', body='Test comment 2 body', post_id=post_id)
    db.session.add(comment1)
    db.session.add(comment2)
    db.session.commit()

    response = client.get(f'/posts/{post_id}/comments', headers={
        'Authorization': 'Basic YWRtaW46c2VjcmV0'
    })
    assert response.status_code == 200
    assert len(response.json) == 2


def test_create_comment(client):
    posts = Post.query.all()
    post_id = posts[0].id

    response = client.post(f'/posts/{post_id}/comments', json={
        'name': 'New test comment',
        'body': 'New test comment body'
    }, headers={
        'Authorization': 'Basic YWRtaW46c2VjcmV0'
    })
    assert response.status_code == 201
    assert response.json['name'] == 'New test comment'


# código para medir el coverage con pytest-cov
def test_cov():
    assert True