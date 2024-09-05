from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from models import db, User, Post, Comment
import logging
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:master@localhost/Blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '94b8b0c903ae70cb123c69eaad4aa0599216bdef102b4febed5fce28754d170a'  # Your secret key


app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db.init_app(app)
jwt = JWTManager(app)

@app.route('/', methods=['GET'])
def home():
    return 'Hello, World!'

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    role = data.get('role', 'reader')  
    
    hashed_password = generate_password_hash(password, method='sha256')
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400
    
    new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity={'username': username})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    if user.role not in ['author', 'admin']:
        return jsonify({"message": "Permission denied: You must be an author or admin to create a post."}), 403

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"message": "Title and content are required."}), 400

    new_post = Post(title=title, content=content, author_id=user.id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post created successfully."}), 201

@app.route('/api/users', methods=['GET'])
def list_users():
    logging.info("list_users route accessed") 
    users = User.query.all()  
    users_data = []
    
    for user in users:
        user_info = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        users_data.append(user_info)
    
    return jsonify(users=users_data), 200


@app.route('/api/posts', methods=['GET'])
def list_posts():
  
    page = request.args.get('page', 1, type=int) 
    per_page = request.args.get('per_page', 2, type=int) 

    paginated_posts = Post.query.paginate(page=page, per_page=per_page, error_out=False)

   
    posts_data = []
    for post in paginated_posts.items:
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "comments": [
                {
                    "content": comment.content,
                } for comment in post.comments
            ]
        }
        posts_data.append(post_data)
    

    return jsonify({
        "total": paginated_posts.total,
        "page": paginated_posts.page,
        "per_page": paginated_posts.per_page,
        "pages": paginated_posts.pages,
        "posts": posts_data,  
    }), 200



@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({"message": "Content is required."}), 400

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user['username']).first()

    if not user:
        return jsonify({"message": "User not found."}), 404

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"message": "Post not found."}), 404

    new_comment = Comment(content=content, post_id=post_id, user_id=user.id)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "Comment added successfully."}), 201

if __name__ == '__main__':
    app.run(debug=True)
