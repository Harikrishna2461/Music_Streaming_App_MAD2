from flask import Flask, render_template , request, jsonify , current_app , session , make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime , date , timedelta
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource, Api, reqparse, fields, marshal
from flask_security import auth_required, roles_required, current_user
from flask import jsonify
from sqlalchemy import func 
from flask import request
from jinja2 import Template
from celery import Celery, Task , shared_task
import jwt 
import json
import sqlite3
import time
from flask_login import login_required
import flask_excel as excel
from celery.schedules import crontab
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
from datetime import datetime, timedelta

from sqlalchemy import func
from flask import Flask
from flask import Flask, render_template
from flask_caching import Cache

from flask import current_app as app, jsonify, request, render_template, send_file
from flask_security import auth_required, roles_required
from werkzeug.security import check_password_hash
from flask_restful import marshal, fields
import flask_excel as excel
from celery.result import AsyncResult

from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from flask import request

from celery import Celery
from datetime import datetime, timedelta

import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pdfkit

#db = SQLAlchemy()

class Configs(object):
    DEBUG = False
    TESTING = False

class Configurations_Development(Configs):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///music.db'
    SECRET_KEY = "thisissecter"
    SECURITY_PASSWORD_SALT = "thisissaltt"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 3

SMTP_HOST = "localhost"
SMTP_PORT = 1025
broker_url = "redis://localhost:6379/1"
result_backend = "redis://localhost:6379/2"
timezone = "Asia/kolkata"
broker_connection_retry_on_startup=True
SENDER_EMAIL = '21f1002958@ds.study.iitm.ac.in'
SENDER_PASSWORD = ''

def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object("celeryconfig")
    return celery_app

musicapp = Flask(__name__,template_folder='template')

# Configuration settings
musicapp.config['DEBUG'] = True
musicapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
musicapp.config['SECRET_KEY'] = "secret"
musicapp.config['SECURITY_PASSWORD_SALT'] = "salt"
musicapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
musicapp.config['WTF_CSRF_ENABLED'] = False
musicapp.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authentication-Token'
musicapp.config['CACHE_TYPE'] = "RedisCache"
musicapp.config['CACHE_REDIS_HOST'] = "localhost"
musicapp.config['CACHE_REDIS_PORT'] = 6379
musicapp.config['CACHE_REDIS_DB'] = 3
musicapp.config['SMTP_SERVER'] = "localhost"
musicapp.config['SMTP_PORT'] = 1025
musicapp.config['SENDER_EMAIL'] = '21f1002958@ds.study.iitm.ac.in'
musicapp.config['SENDER_PASSWORD'] = ''

# Initialize extensions
db = SQLAlchemy(musicapp)
cache = Cache(musicapp)
api = Api(musicapp)
api = Api(prefix='/api')

# Initialize Celery
celery = Celery('tasks', broker='redis://localhost:6379/0')
celery_app = celery_init_app(musicapp)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'creator', or 'user'
    joining_date = db.Column(db.Date,nullable=False)
    
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.Date, nullable=False, default=date.today())
    creator_id = db.Column(db.Integer)

class Songs(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in seconds
    date_created = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    album = db.relationship('Album', backref=db.backref('songs', lazy=True))
    album_name = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(50), nullable=False )
    average_ratings = db.Column(db.String(10))
    isFlagged = db.Column(db.String(10))
    creator_id = db.Column(db.Integer)
    
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer,nullable=False)
    song_ids = db.Column(db.Text, nullable=False)

class song_statistics(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    play_song_count = db.Column(db.Integer, default=0)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    play_album_count = db.Column(db.Integer, default=0)
    date = db.Column(db.Date)
    listener_id = db.Column(db.Integer)
    # Define a relationship with the Song table
    song = db.relationship('Songs', backref='statistics')

    def __repr__(self):
        return f"<song_statistics(id={self.id}, song_id={self.song_id}, play_song_count={self.play_song_count}, album_id={self.album_id}, play_album_count={self.play_album_count}, date={self.date} )>"

class user_visit(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    visit_time = db.Column(db.DateTime,default=datetime.utcnow())
    
    def __repr__(self):
        return f"<user_visit(id={self.id}, user_id={self.user_id}, visit_time={self.visit_time})>"

class Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    

# Route to serve Vue.js static files
@musicapp.get('/')
def index():
    return render_template('index.html')

#@musicapp.post('/signup')
#@musicapp.route('/signup', methods=['POST'])

# Assuming 'musicapp' is your Flask application instance
# If 'musicapp' is not defined elsewhere, replace it with 'app'
@musicapp.route('/api/', methods=['POST'])
def signup():
    if request.method == 'POST':
        try:
            # Get JSON data from request body
            data = request.json
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role')

            # Hash the password
            hashed_password = generate_password_hash(password, method='sha256')
            
            max_id = db.session.query(func.max(Users.id)).scalar()
            new_id = max_id + 1 if max_id else 1
            
            # Attempt to add the user with retry mechanism
            max_retries = 5
            retry_delay = 0.1  # in seconds
            retry_count = 0
            while retry_count < max_retries:
                try:
                    # Create a new user instance
                    new_user = Users(id=new_id,username=username, email=email, password=hashed_password, role=role, joining_date= date.today())
                    
                    # Add the user to the database session
                    db.session.add(new_user)
                    
                    # Commit the transaction
                    db.session.commit()
                    db.session.close_all()
                    
                    # Return success response
                    return jsonify({'message': 'User signed up successfully'}), 201
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e):
                        print("Database is locked. Retrying...")
                        time.sleep(retry_delay)
                        retry_count += 1
                    else:
                        raise
            # Max retries reached, return an error response
            return jsonify({'error': 'Max retries reached. Failed to sign up user.'}), 500
        except Exception as e:
            # Handle signup error
            return jsonify({'error': str(e)}), 500
    else:
        # Return an error response for other HTTP methods
        return jsonify({'error': 'Method Not Allowed'}), 405


global current_user_id 

logging.basicConfig(level=logging.INFO)
@musicapp.route('/api/login', methods=['POST'])
def login():
    # Get credentials from request
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Query user from database
    user = Users.query.filter_by(email=email).first()

    # Check if user exists and password is correct
    if user and check_password_hash(user.password, password):
        # Store user_id in session or in-memory variable
        #session['user_id'] = user.id
        session['current_user_id'] = user.id
        # Issue JWT token
        token = jwt.encode({'email': user.email, 'role': user.role}, current_app.config['SECRET_KEY'] ,algorithm='HS256')
        #response = make_response(jsonify({'message': 'Login successful', 'role': user['role']}))
        #response.set_cookie('auth_token', token, httponly=True)
        #Adding Entry to user_visit Table
        new_visit = user_visit(user_id=user.id,visit_time=date.today())
        try:
            # Add the new visit entry to the database session
            db.session.add(new_visit)
            db.session.commit()
            # Return success response
            logging.info('Commited Sucessfully.')
            return jsonify({'token': token, 'role': user.role, 'user_id': user.id}), 200
        except Exception as e:
            # If an error occurs, rollback the session and return error response
            db.session.rollback()
            logging.error('Error adding visit to user_visit table: %s', str(e))
            return jsonify({'message': 'Error adding visit to user_visit table', 'error': str(e)}), 500
        #return response, 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

@musicapp.route('/api/admin/home')
def admin_home():
    # Endpoint to fetch admin home page data
    return jsonify({
        'buttons': [
            {'label': 'Admin Dashboard', 'route': '/api/admin-home/dashboard'},
            {'label': 'View Song Statistics', 'route': '/api/admin-home/song-statistics'},
            {'label': 'Manage Songs', 'route': '/api/admin-home/manage-songs'}
        ]
    })

@musicapp.route('/api/dashboard', methods=['GET'])
def admin_dashboard():
    try:
        current_date = date.today()
        # Calculate the date one month ago from today
        one_month_ago = current_date - timedelta(days=30)
        
        # Count the number of users joined in the last month
        num_new_users_last_month = Users.query.filter(Users.role == 'User', Users.joining_date >= one_month_ago).count()
        
        num_users = Users.query.filter_by(role='User').count()
        num_creators = Users.query.filter_by(role='Creator').count()
        num_songs = Songs.query.count()
        num_albums = Album.query.count()
        
        statistics = {
            'num_users': num_users,
            'num_creators': num_creators,
            'num_songs': num_songs,
            'num_albums': num_albums,
            'num_new_users_last_month': num_new_users_last_month
        }
        
        return jsonify(statistics), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@musicapp.route('/api/manage-songs')
def manage_songs():
    return jsonify({
        'buttons': [
            {'label': 'Add Song', 'route': '/admin-add-song'},
            {'label': 'Update Song', 'route': '/admin-update-song'},
            {'label': 'Delete Songs', 'route': '/admin-delete-song'},
            {'label': 'Add Album', 'route': '/admin-add-album'},
            {'label': 'Update Album', 'route': '/admin-update-album'},
            {'label': 'Delete Album', 'route': '/admin-delete-album'}
        ]
    })

@musicapp.route('/api/admin-add-album', methods=['POST'])
def admin_add_album():
    try:
        # Get album data from the request body
        data = request.json
        name = data.get('name')
        artist = data.get('artist')
        creator_id = data.get('creatorId')  # Assuming creatorId is provided by the admin
        
        # Create a new album object
        new_album = Album(name=name, artist=artist, creator_id=creator_id)
        
        # Add the new album to the database
        db.session.add(new_album)
        db.session.commit()
        
        return jsonify({'message': 'Album added successfully'}), 200
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid partial updates
        return jsonify({'message': 'Error: Song with same name already exists.'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/admin-update-album', methods=['POST'])
def admin_update_album():
    try:
        data = request.get_json()
        selected_album = data.get('present_album_name')
        album = Album.query.filter(Album.name == selected_album).first()
        # Configure logging
        logging.basicConfig(level=logging.INFO)

        # Log the value of the `album` variable
        logging.info(album)
        if not album:
            return jsonify({'message': 'Album not found'}), 404
    
        user_id = session.get('current_user_id')
        # Update album attributes as needed
        album.name = data.get('new_album_name', album.name)
        album.artist = data.get('new_artist_name', album.artist)
        album.release_date =  date.today()
        album.creator_id = user_id
        db.session.commit()
        db.session.close_all()
        return jsonify({'message': 'Album updated successfully'}), 200
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid partial updates
        return jsonify({'message': 'Error: Song with same name already exists.'}), 400
    

@musicapp.route('/api/admin-delete-album', methods=['DELETE'])
def admin_delete_album():
    try:
        data = request.get_json()
        album_name = data.get('albumName')
        # Query the album to be deleted
        album = Album.query.filter_by(name=album_name).first()

        if album:
            songs_to_delete = Songs.query.filter_by(album_id=album.id).all()
            for song in songs_to_delete:
                db.session.delete(song)
                
            # Delete the album
            db.session.delete(album)
            db.session.commit()
            return jsonify({'message': 'Album deleted successfully'}), 200
        else:
            return jsonify({'message': 'Album not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/admin-add-song', methods=['POST'])
def admin_add_song():
    try:
        data = request.get_json()
        print("Received data:", data)
        name = data.get('name')
        lyrics = data.get('lyrics')
        genre = data.get('genre')
        duration = data.get('duration')
        album_data = data.get('album')
        print("Received album:", album_data)
        print(type(album_data))
        
        album = Album.query.filter_by(id=album_data['id']).first()
        
        if not album:
            return jsonify({'message': 'Album not found'}), 404

        # Get the current user ID (assuming session handling is correctly implemented)
        creator_id = session.get('current_user_id')

        # Generate a new ID for the song (assuming you want to increment the ID)
        max_id = db.session.query(func.max(Songs.id)).scalar()
        new_id = max_id + 1 if max_id else 1

        # Create a new song instance and add it to the database
        new_song = Songs(id=new_id, name=name, lyrics=lyrics, genre=genre, duration=duration,
                        date_created=datetime.utcnow(),album_id=album.id,album_name=album.name,
                        artist=album.artist,creator_id=creator_id)

        db.session.add(new_song)
        db.session.commit()

        return jsonify({'message': 'Song added successfully'}), 200
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid partial updates
        return jsonify({'message': 'Error: Song with same name already exists.'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/admin-update-song', methods=['POST'])
def admin_update_song():
    try:
        data = request.get_json()
        song_id = data.get('songId')
        
        #selected_song = Album.query.filter_by(id=song['id']).first()
        #song_id = selected_song.id
        
        name = data.get('name')
        lyrics = data.get('lyrics')
        genre = data.get('genre')
        duration = data.get('duration')
        album_name = data.get('album')

        selected_album = Album.query.filter_by(id=album_name['id']).first()
        album_id = selected_album.id
        logging.info(selected_album)
        # Fetch the song object to update
        
        song = Songs.query.get(song_id)
        if not song:
            return jsonify({'message': 'Song not found'}), 404
        
        # Update the song object
        song.name = name
        song.lyrics = lyrics
        song.genre = genre
        song.duration = duration
        song.album_id = album_id
        song.album_name = album_name['name']
        
        # Commit the changes to the database
        db.session.commit()

        return jsonify({'message': 'Song updated successfully'}), 200
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid partial updates
        return jsonify({'message': 'Error: Song with same name already exists.'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/admin-delete-song', methods=['DELETE'])
def admin_delete_song():
    try:
        data = request.get_json()
        song_id = data.get('songId')

        # Fetch the song object to delete
        song = Songs.query.get(song_id)
        if not song:
            return jsonify({'message': 'Song not found'}), 404

        # Delete the song object
        db.session.delete(song)
        db.session.commit()

        return jsonify({'message': 'Song deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/play-song', methods=['POST'])
def play_song():
    try:
        data = request.get_json()
        song_id = data.get('song_id')
        album_id = data.get('album_id')

        # Update the song statistics table
        stats = song_statistics.query.filter_by(song_id=song_id).first()
        if stats:
            # Increment the play count for the song
            stats.play_song_count += 1
            stats.play_album_count += 1
        else:
            # Create a new record in the song statistics table
            stats = song_statistics(song_id=song_id, play_song_count=1,album_id=album_id,play_album_count=1,date=date.today(),listener_id=session.get('current_user_id'))
            db.session.add(stats)

        db.session.commit()

        return jsonify({'message': 'Song played successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def update_song_ratings():
    try:
        # Query all songs from the Songs table
        songs = Songs.query.all()

        for song in songs:
            # Query the sum of ratings and count of unique user_ids for the current song
            rating_sum_count = db.session.query(func.sum(Ratings.rating), func.count(func.distinct(Ratings.user_id))).filter_by(song_id=song.id).first()
            
            if rating_sum_count[1] > 0:
                # Calculate the average rating
                average_rating = rating_sum_count[0] / rating_sum_count[1]
            else:
                average_rating = None
                
            # Update the ratings column in the Songs table with the average rating
            song.average_ratings = average_rating

        # Commit the changes to the database
        db.session.commit()
        db.session.close_all()

        return jsonify({'message': 'Song ratings updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@musicapp.route('/api/song-statistics')
def get_song_statistics():
    try:
        # Get most streamed song
        most_streamed_song = db.session.query(song_statistics.song_id, func.max(song_statistics.play_song_count)).first()
        most_streamed_song_name = db.session.query(Songs.name).filter_by(id=most_streamed_song[0]).first()

        # Get most streamed album
        most_streamed_album = db.session.query(song_statistics.album_id, func.max(song_statistics.play_album_count)).first()
        most_streamed_album_name = db.session.query(Album.name).filter_by(id=most_streamed_album[0]).first()

        # Get most active user
        most_active_user = db.session.query(song_statistics.listener_id, func.count()).group_by(song_statistics.listener_id).order_by(func.count().desc()).first()
        most_active_user_name = db.session.query(Users.username).filter_by(id=most_active_user[0]).first()

        # Get most streamed song in last month
        last_month_start = datetime.now() - timedelta(days=30)
        most_streamed_song_last_month = db.session.query(song_statistics.song_id, func.max(song_statistics.play_song_count)).filter(song_statistics.date >= last_month_start).first()
        most_streamed_song_last_month_name = db.session.query(Songs.name).filter_by(id=most_streamed_song_last_month[0]).first()

        # Get most streamed album in last month
        most_streamed_album_last_month = db.session.query(song_statistics.album_id, func.max(song_statistics.play_album_count)).filter(song_statistics.date >= last_month_start).first()
        most_streamed_album_last_month_name = db.session.query(Album.name).filter_by(id=most_streamed_album_last_month[0]).first()

        # Get most active user in last month
        most_active_user_last_month = db.session.query(song_statistics.listener_id, func.count()).filter(song_statistics.date >= last_month_start).group_by(song_statistics.listener_id).order_by(func.count().desc()).first()
        most_active_user_last_month_name = db.session.query(Users.username).filter_by(id=most_active_user_last_month[0]).first()
        
        # Get highest rated song 
        highest_rating = Songs.query.order_by(Songs.average_ratings.desc()).first().average_ratings
        highest_rated_songs = Songs.query.filter_by(average_ratings=highest_rating).all()
        highest_rated_song_names = [song.name for song in highest_rated_songs]

        return jsonify({
            "mostStreamedSong": most_streamed_song_name[0],
            "mostStreamedAlbum": most_streamed_album_name[0],
            "mostActiveUser": most_active_user_name[0],
            "mostStreamedSongLastMonth": most_streamed_song_last_month_name[0],
            "mostStreamedAlbumLastMonth": most_streamed_album_last_month_name[0],
            "mostActiveUserLastMonth": most_active_user_last_month_name[0],
            'highest_rated_songs': highest_rated_song_names
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@musicapp.route('/api/user-home', methods=['GET'])
def user_home():
    try:
        update_song_ratings()
        
        current_user_id = session.get('current_user_id')
        
        # Query all songs from the database
        songs = Songs.query.all()
        
        # Query current user's ratings for songs
        current_user_ratings = Ratings.query.filter_by(user_id=current_user_id).all()
        user_ratings_dict = {rating.song_id: rating.rating for rating in current_user_ratings}
        
        # Serialize songs data along with current user's ratings
        serialized_songs = [{
            'id': song.id,
            'name': song.name,
            'lyrics': song.lyrics,
            'genre': song.genre,
            'duration': song.duration,
            'date_created': song.date_created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'album_id': song.album_id,
            'album': {
                'id': song.album.id,
                'name': song.album.name
            },
            'artist': song.artist,
            'ratings': user_ratings_dict.get(song.id, None),  # Get user's rating for the song or None if not rated
            'average_ratings': song.average_ratings,
            'flagged': song.isFlagged
        } for song in songs]
        
        return jsonify({'songs': serialized_songs}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

#@login_required
@musicapp.route('/api/creator-home' , methods=['GET'])
def creator_home():
    try:
        update_song_ratings()
        
        current_user_id = session.get('current_user_id')
        # Query all songs from the database
        songs = Songs.query.all()
        
        # Query current user's ratings for songs
        current_user_ratings = Ratings.query.filter_by(user_id=current_user_id).all()
        user_ratings_dict = {rating.song_id: rating.rating for rating in current_user_ratings}
        
        # Serialize songs data
        serialized_songs = [{
            'id': song.id,
            'name': song.name,
            'lyrics' : song.lyrics,
            'genre' : song.genre,
            'duration' : song.duration,
            'date_created' : song.date_created.strftime('%Y-%m-%dT%H:%M:%S.%fZ') ,  # Format as ISO 8601 string
            'album_id' : song.album_id,
            'album' : song.album,
            'artist': song.artist,
            'ratings': user_ratings_dict.get(song.id, None),
            'average_ratings': song.average_ratings,
            'flagged': song.isFlagged, 
            'album': {
                'id': song.album.id,
                'name': song.album.name
            }
        } for song in songs]
        return jsonify({'songs': serialized_songs}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@musicapp.route('/api/workshop', methods=['GET'])
def workshop():
    return jsonify({'message': 'Welcome to the Creators Workshop page!'}), 200

# Defining a helper function to get the current user's ID
def get_current_user_id(token):
    try:
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        email = decoded_token.get('email')
        if email:
            user = Users.query.filter_by(email=email).first()
            if user:
                return user.id
    except Exception as e:
        print("Error decoding token:", e)
        return None

@musicapp.route('/api/create-playlist', methods=['POST'])
def create_playlist():
    # Retrieve user_id from session or in-memory variable
    user_id = user_id = session.get('current_user_id')  # Assuming you have set current_user_id somewhere in your application
    data = request.json
    playlist_name = data.get('name')
    # Use user_id to create playlist
    if user_id:
        #try:
            # Your code to create playlist using user_id
        playlist = Playlist(name=playlist_name, user_id=user_id,song_ids = '[]')  # Adjust playlist creation according to your schema
        db.session.add(playlist)
        db.session.commit()  # Commit changes to the database
        db.session.close_all()
        return jsonify({'message': 'Playlist created successfully'}), 201
        #except Exception as e:
            #db.session.rollback()  # Rollback changes in case of error
            #return jsonify({'message': 'Error creating playlist'}), 500
    else:
        return jsonify({'message': 'User not logged in'}), 401
    
@musicapp.route('/api/playlists', methods=['GET'])
def get_playlists():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        token_parts = token.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            return jsonify({'message': 'Invalid token format'}), 401

        token = token_parts[1]
        
        user_id = get_current_user_id(token)
        if user_id is not None:
            playlists = Playlist.query.filter_by(user_id=user_id).all()
            serialized_playlists = [{'id': playlist.id, 'name': playlist.name} for playlist in playlists]
            return jsonify({'playlists': serialized_playlists}), 200
        else:
            return jsonify({'message': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/playlists-with-songs', methods=['GET'])
def get_playlists_with_songs():
    try:
        user_id = session.get('current_user_id') 
        playlists = Playlist.query.filter_by(user_id=user_id).all()
        playlists_with_songs = []

        for playlist in playlists:
            song_ids = json.loads(playlist.song_ids)
            songs = Songs.query.filter(Songs.id.in_(song_ids)).all()
            serialized_songs = [{
                'id': song.id,
                'name': song.name,
                'lyrics': song.lyrics,
                'genre': song.genre,
                'duration': song.duration,
                'date_created': song.date_created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'album_id': song.album_id,
                'album': {
                    'id': song.album.id,
                    'name': song.album.name
                },
                'artist': song.artist
            } for song in songs]

            playlists_with_songs.append({
                'id': playlist.id,
                'name': playlist.name,
                'songs': serialized_songs
            })

        print('Playlists with songs:', playlists_with_songs) 
        return jsonify({'playlists': playlists_with_songs}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@musicapp.route('/api/add-to-playlist', methods=['POST'])
def add_to_playlist():
    data = request.json
    playlist_id = data.get('playlistId')
    song_id = data.get('songId')

    if not playlist_id or not song_id:
        return jsonify({'message': 'Both playlist ID and song ID are required'}), 400

    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return jsonify({'message': 'Playlist not found'}), 404

    # Remove the trailing ']' from the string
    #song_ids_str = playlist.song_ids[:len()] if playlist.song_ids.endswith(']') else playlist.song_ids

    song_ids_str = playlist.song_ids[:len(playlist.song_ids)-1]
    # Add the new song_id to the string
    if playlist.song_ids == "[]":
        song_ids_str += str(song_id) 
    else:
        song_ids_str += "," + str(song_id) 

    # Add back the ']' at the end
    song_ids_str += ']'
    playlist.song_ids = song_ids_str
    db.session.commit()
    db.session.close_all()

    return jsonify({'message': 'Song added to playlist successfully'}), 201


@musicapp.route('/api/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    try:
        playlist = Playlist.query.get(playlist_id)
        #print(playlist)
        if playlist:
            song_ids = json.loads(playlist.song_ids)
            songs = Songs.query.filter(Songs.id.in_(song_ids)).all()
            serialized_songs = [{
                'id': song.id,
                'name': song.name,
                'lyrics': song.lyrics,
                'genre': song.genre,
                'duration': song.duration,
                'date_created': song.date_created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'album_id': song.album_id,
                'album': {
                    'id': song.album.id,
                    'name': song.album.name
                },
                'artist': song.artist
            } for song in songs]

            serialized_playlist = {
                'id': playlist.id,
                'name': playlist.name,
                'songs': serialized_songs
            }

            return jsonify({'playlist': serialized_playlist}), 200
        else:
            return jsonify({'message': 'Playlist not found'}), 404

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/playlists/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    db.session.close_all()
    return jsonify({ 'message': 'Playlist deleted successfully' }), 200
    
@musicapp.route('/api/rate-song', methods=['POST'])
def rate_song():
    try:
        data = request.json
        song_id = data.get('song_id')
        rating = data.get('rating')

        # Get the current user's ID
        user_id = session.get('current_user_id')

        # Check if the song exists
        song = Songs.query.get(song_id)
        if song:
            # Check if the user has already rated the song
            user_rating = Ratings.query.filter_by(song_id=song_id, user_id=user_id).first()

            if user_rating:
                # Update the existing rating
                user_rating.rating = rating
            else:
                # Create a new rating record
                new_rating = Ratings(song_id=song_id, user_id=user_id, rating=rating)
                db.session.add(new_rating)

            db.session.commit()
            return jsonify({'message': 'Rating submitted successfully'}), 200
        else:
            return jsonify({'message': 'Song not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/set-flag', methods=['POST'])
def set_flag():
    try:
        data = request.json
        song_id = data.get('song_id')
        flag_option = data.get('flag_option')

        song = Songs.query.get(song_id)
        if song:
            # Update the isFlagged column based on the flag_option
            if flag_option == 'flag':
                song.isFlagged = True
            elif flag_option == 'unflag':
                song.isFlagged = False
            
            db.session.commit()
            db.session.close_all()
            return jsonify({'message': 'Flag updated successfully'}), 200
        else:
            return jsonify({'message': 'Song not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
# Assuming you have the necessary imports and configurations already in place

import logging
# Configure logging
logging.basicConfig(filename='musicapp.log', level=logging.DEBUG)

@musicapp.route('/api/add-album', methods=['POST'])
def add_album():
    # Get data from request body
    data = request.json
    name = data.get('name')
    #artist = data.get('artist') # Ensure the key matches the frontend field name
    user = Users.query.filter_by(id=session.get('current_user_id')).first()
    artist = user.username
    max_id = db.session.query(func.max(Album.id)).scalar()
    new_id = max_id + 1 if max_id else 1
    
    # Attempt to add the user with retry mechanism
    max_retries = 100
    retry_delay = 0.1  # in seconds
    retry_count = 0
    while retry_count < max_retries:
        try:
            new_album = Album(id=new_id,name=name, artist=artist, release_date=date.today(),creator_id=session.get('current_user_id'))
                    
            db.session.add(new_album)
            db.session.commit()
            db.session.close_all()
            # Return success response
            return jsonify({'message': 'Album Added Successfully'}), 201
        except IntegrityError as e:
            db.session.rollback()  # Rollback the transaction to avoid partial updates
            return jsonify({'message': 'Error: Song with same name already exists.'}), 400
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print("Database is locked. Retrying...")
                time.sleep(retry_delay)
                retry_count += 1
            else:
                raise
            
# Route for updating an album
@musicapp.route('/api/update-album', methods=['POST'])
def update_album():
    try:
        data = request.get_json()
        selected_album = data.get('present_album_name')
        album = Album.query.filter(Album.name == selected_album).first()
        # Configure logging
        logging.basicConfig(level=logging.INFO)

        # Log the value of the `album` variable
        logging.info(album)
        if not album:
            return jsonify({'message': 'Album not found'}), 404
    
        user_id = session.get('current_user_id')
        if user_id == album.creator_id:
            # Update album attributes as needed
            album.name = data.get('new_album_name', album.name)
            album.artist = data.get('new_artist_name', album.artist)
            album.release_date =  date.today()
            album.creator_id = user_id
            db.session.commit()
            db.session.close_all()
            return jsonify({'message': 'Album updated successfully'}), 200
        else:
            return jsonify({'message': 'You are not authorized to update this album'}), 403
        
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid partial updates
        return jsonify({'message': 'Error: Song with same name already exists.'}), 400
    
        
# Route for deleting an album
@musicapp.route('/api/delete-album', methods=['DELETE'])
def delete_album():
    try:
        data = request.get_json()
        album_name = data.get('albumName')
        # Query the album to be deleted
        album = Album.query.filter_by(name=album_name).first()

        if album:
            user_id = session.get('current_user_id')
            if user_id == album.creator_id:
                songs_to_delete = Songs.query.filter_by(album_id=album.id).all()
                for song in songs_to_delete:
                    db.session.delete(song)
                # Now, delete the album itself
                db.session.delete(album)
                db.session.commit()
                return jsonify({'message': 'Album deleted successfully'}), 200
            else:
                return jsonify({'message': 'You are not authorized to update this album'}), 403
        else:
            return jsonify({'message': 'Album not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Assuming this code is in your Flask application file

@musicapp.route('/api/add-song', methods=['POST'])
def add_song():
    try:
        data = request.get_json()
        print("Received data:", data)
        name = data.get('name')
        lyrics = data.get('lyrics')
        genre = data.get('genre')
        duration = data.get('duration')
        album_data = data.get('album')
        print("Received album:", album_data)
        print(type(album_data))
        
        album = Album.query.filter_by(id=album_data['id']).first()
        
        if not album:
            return jsonify({'message': 'Album not found'}), 404

        # Get the current user ID (assuming session handling is correctly implemented)
        creator_id = session.get('current_user_id')
        if creator_id != album.creator_id:
            return jsonify({'message': 'You are not authorized to add songs to this album.'}), 403

        # Generate a new ID for the song (assuming you want to increment the ID)
        max_id = db.session.query(func.max(Songs.id)).scalar()
        new_id = max_id + 1 if max_id else 1

        # Create a new song instance and add it to the database
        new_song = Songs(id=new_id, name=name, lyrics=lyrics, genre=genre, duration=duration,
                        date_created=datetime.utcnow(),album_id=album.id,album_name=album.name,
                        artist=album.artist,creator_id=creator_id)

        db.session.add(new_song)
        db.session.commit()

        return jsonify({'message': 'Song added successfully'}), 200
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid partial updates
        return jsonify({'message': 'Error: Song with same name already exists.'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Route for updating a song
@musicapp.route('/api/update-song', methods=['POST'])
def update_song():
    try:
        data = request.get_json()
        song_id = data.get('songId')
        
        #selected_song = Album.query.filter_by(id=song['id']).first()
        #song_id = selected_song.id
        
        name = data.get('name')
        lyrics = data.get('lyrics')
        genre = data.get('genre')
        duration = data.get('duration')
        album_name = data.get('album')

        selected_album = Album.query.filter_by(id=album_name['id']).first()
        album_id = selected_album.id
        logging.info(selected_album)
        # Fetch the song object to update
        
        song = Songs.query.get(song_id)
        if not song:
            return jsonify({'message': 'Song not found'}), 404

        # Check if the current user is the creator of the song
        if session.get('current_user_id') != song.creator_id:
            return jsonify({'message': 'You are not authorized to update this song'}), 403
        
        # Update the song object
        song.name = name
        song.lyrics = lyrics
        song.genre = genre
        song.duration = duration
        song.album_id = album_id
        song.album_name = album_name['name']
        
        # Commit the changes to the database
        db.session.commit()

        return jsonify({'message': 'Song updated successfully'}), 200
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid partial updates
        return jsonify({'message': 'Error: Song with same name already exists.'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Route for deleting a song
@musicapp.route('/api/delete-song', methods=['DELETE'])
def delete_song():
    try:
        data = request.get_json()
        song_id = data.get('songId')

        # Fetch the song object to delete
        song = Songs.query.get(song_id)
        if not song:
            return jsonify({'message': 'Song not found'}), 404

        # Check if the current user is the creator of the song
        # You need to implement a method to get the current user ID, such as session or token
        current_user_id = session.get('current_user_id') # Replace this with the actual current user ID
        if current_user_id != song.creator_id:
            return jsonify({'message': 'You are not authorized to delete this song'}), 403
        
        # Delete the song object
        db.session.delete(song)
        db.session.commit()

        return jsonify({'message': 'Song deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/playlists/<int:playlist_id>/<int:song_id>', methods=['POST'])
def delete_song_from_playlist(playlist_id, song_id):
    try:
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'message': 'Playlist not found'}), 404
        
        playlist_songs = playlist.song_ids.replace('[','').replace(']','').split(",")
        if str(song_id) not in playlist_songs:
            return jsonify({'message': 'Song not found in playlist'}), 404
            
        playlist_songs.remove(str(song_id))
        updated_playlist = ','.join(playlist_songs)
        playlist.song_ids = f"[{updated_playlist}]"
        
        db.session.commit()  # Commit the changes to the database
        
        return jsonify({'message': 'Song deleted from playlist successfully'}), 200
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@musicapp.route('/api/albums', methods=['GET'])
def get_albums():
    try:
        albums = Album.query.all()
        serialized_albums = [{
            'id': album.id,
            'name': album.name,
            'artist': album.artist,
            'release_date': album.release_date.strftime('%Y-%m-%d')
        } for album in albums]
        return jsonify({'albums': serialized_albums}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@musicapp.route('/api/songs', methods=['GET'])
def get_songs():
    try:
        # Fetch songs from the database
        songs = Songs.query.all()

        # Serialize songs data to JSON
        serialized_songs = [{'id': song.id, 'name': song.name, 'artist': song.artist, 'creator_id': song.creator_id} for song in songs]

        # Return serialized songs data
        return jsonify({'songs': serialized_songs}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

#Celery Integration
# Import necessary modules

def send_message(to, subject, content_body):
    msg = MIMEMultipart()
    msg["To"] = to
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg.attach(MIMEText(content_body, 'html'))
    client = SMTP(host=SMTP_HOST, port=SMTP_PORT)
    with SMTP(host=SMTP_HOST, port=SMTP_PORT) as client:
        client.send_message(msg=msg)
    #client.send_message(msg=msg)
    #client.quit()

@shared_task(ignore_result=True)
def daily_reminder(to, subject):
    # Query users who are not admins
    users = Users.query.filter(Users.role != 'Admin')

    for user in users:
        # Check if the user has visited the app
        visited = user_visit.query.filter(user_visit.user_id == user.id,func.DATE(user_visit.visit_time) == date.today()).first()
        if not visited:
            # If the user has not visited the app, send them an email
            with open('test.html', 'r') as f:
                template = Template(f.read())
                send_message(user.email, subject,
                            template.render(username=user.username))
                #send_message('recipient@example.com','Test Email','<h1>Hello from HTML</h1>')
    return "OK"

@celery_app.on_after_configure.connect
def send_email(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=18,minute=30),#, day_of_month=14), #day_of_the_week
        daily_reminder.s('harikrishna3579@gmail.com', 'Daily Test'),
    )

def generate_report():
    # 1. Top Songs by Play Count
    top_songs_data = db.session.query(Songs.name, func.sum(song_statistics.play_song_count).label('play_count')) \
    .join(song_statistics, Songs.id == song_statistics.song_id) \
    .group_by(Songs.name).order_by(func.sum(song_statistics.play_song_count).desc()).limit(5).all()    
    
    top_songs_df = pd.DataFrame(top_songs_data, columns=['name', 'play_count'])
    top_songs_plot = top_songs_df.plot(kind='bar', x='name', y='play_count', legend=False)
    plt.title('Top Songs by Play Count')
    plt.xlabel('Song')
    plt.ylabel('Play Count')
    plt.xticks(rotation=45)
    top_songs_buffer = BytesIO()
    top_songs_plot.figure.savefig(top_songs_buffer, format='png')
    top_songs_buffer.seek(0)
    top_songs_plot_data = base64.b64encode(top_songs_buffer.read()).decode('utf-8')
    top_songs_plot_html = f'<img src="data:image/png;base64,{top_songs_plot_data}" alt="Top Songs by Play Count">'

    # 2. Top Albums by Play Count
    top_albums_data = db.session.query(Album.name, func.sum(song_statistics.play_song_count).label('play_count')) \
    .join(song_statistics, Album.id == song_statistics.album_id) \
    .group_by(Album.name).order_by(func.sum(song_statistics.play_song_count).desc()).limit(5).all()
    
    top_albums_df = pd.DataFrame(top_albums_data, columns=['name', 'play_count'])
    top_albums_plot = top_albums_df.plot(kind='bar', x='name', y='play_count', legend=False)
    plt.title('Top Albums by Play Count')
    plt.xlabel('Album')
    plt.ylabel('Play Count')
    plt.xticks(rotation=45)
    top_albums_buffer = BytesIO()
    top_albums_plot.figure.savefig(top_albums_buffer, format='png')
    top_albums_buffer.seek(0)
    top_albums_plot_data = base64.b64encode(top_albums_buffer.read()).decode('utf-8')
    top_albums_plot_html = f'<img src="data:image/png;base64,{top_albums_plot_data}" alt="Top Albums by Play Count">'

    # 3. User Visits Over Time
    visits_data = db.session.query(user_visit.visit_time).all()
    visits_df = pd.DataFrame(visits_data, columns=['visit_time'])
    visits_df['visit_time'] = pd.to_datetime(visits_df['visit_time'])
    visits_over_time = visits_df.resample('D', on='visit_time').size()
    visits_over_time_plot = visits_over_time.plot()
    plt.title('User Visits Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Visits')
    user_visits_buffer = BytesIO()
    visits_over_time_plot.figure.savefig(user_visits_buffer, format='png')
    user_visits_buffer.seek(0)
    user_visits_plot_data = base64.b64encode(user_visits_buffer.read()).decode('utf-8')
    user_visits_plot_html = f'<img src="data:image/png;base64,{user_visits_plot_data}" alt="User Visits Over Time">'

    # 4. Genre Distribution
    genre_distribution_data = db.session.query(Songs.genre, func.count()).group_by(Songs.genre).all()
    genre_distribution_df = pd.DataFrame(genre_distribution_data, columns=['genre', 'count'])
    genre_distribution_plot = genre_distribution_df.plot(kind='pie', y='count', labels=genre_distribution_df['genre'],
                                                        autopct='%1.1f%%', legend=False)
    plt.title('Genre Distribution')
    plt.ylabel('')
    genre_distribution_buffer = BytesIO()
    genre_distribution_plot.figure.savefig(genre_distribution_buffer, format='png')
    genre_distribution_buffer.seek(0)
    genre_distribution_plot_data = base64.b64encode(genre_distribution_buffer.read()).decode('utf-8')
    genre_distribution_plot_html = f'<img src="data:image/png;base64,{genre_distribution_plot_data}" alt="Genre Distribution">'

    # 5. Average Song Duration by Genre
    avg_duration_data = db.session.query(Songs.genre, func.avg(Songs.duration)).group_by(Songs.genre).all()
    avg_duration_df = pd.DataFrame(avg_duration_data, columns=['genre', 'avg_duration'])
    avg_duration_plot = avg_duration_df.plot(kind='bar', x='genre', y='avg_duration', legend=False)
    plt.title('Average Song Duration by Genre')
    plt.xlabel('Genre')
    plt.ylabel('Average Duration (seconds)')
    avg_duration_buffer = BytesIO()
    avg_duration_plot.figure.savefig(avg_duration_buffer, format='png')
    avg_duration_buffer.seek(0)
    avg_duration_plot_data = base64.b64encode(avg_duration_buffer.read()).decode('utf-8')
    avg_duration_plot_html = f'<img src="data:image/png;base64,{avg_duration_plot_data}" alt="Average Song Duration by Genre">'

    # 6. User Ratings Distribution
    user_ratings_data = db.session.query(Songs.average_ratings, func.count()).group_by(Songs.average_ratings).all()
    user_ratings_df = pd.DataFrame(user_ratings_data, columns=['ratings', 'count'])
    user_ratings_plot = user_ratings_df.plot(kind='bar', x='ratings', y='count', legend=False)
    plt.title('User Ratings Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    user_ratings_buffer = BytesIO()
    user_ratings_plot.figure.savefig(user_ratings_buffer, format='png')
    user_ratings_buffer.seek(0)
    user_ratings_plot_data = base64.b64encode(user_ratings_buffer.read()).decode('utf-8')
    user_ratings_plot_html = f'<img src="data:image/png;base64,{user_ratings_plot_data}" alt="User Ratings Distribution">'
    
    # 7. Number of Users Signing Up Over Time
    user_signups_data = db.session.query(Users.joining_date).all()
    user_signups_df = pd.DataFrame(user_signups_data, columns=['joining_date'])
    user_signups_df['joining_date'] = pd.to_datetime(user_signups_df['joining_date'])  # Convert to datetime
    user_signups_over_time = user_signups_df.resample('D', on='joining_date').size()
    user_signups_plot = user_signups_over_time.plot()
    plt.title('Number of Users Signing Up Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Signups')
    user_signups_buffer = BytesIO()
    user_signups_plot.figure.savefig(user_signups_buffer, format='png')
    user_signups_buffer.seek(0)
    user_signups_plot_data = base64.b64encode(user_signups_buffer.read()).decode('utf-8')
    user_signups_plot_html = f'<img src="data:image/png;base64,{user_signups_plot_data}" alt="Number of Users Signing Up Over Time">'
    
    # 8. Number of Creators Signing Up Over Time
    creator_signups_data = db.session.query(Album.release_date).all()
    creator_signups_df = pd.DataFrame(creator_signups_data, columns=['release_date'])
    creator_signups_df['release_date'] = pd.to_datetime(creator_signups_df['release_date'])  # Convert to datetime
    creator_signups_over_time = creator_signups_df.resample('D', on='release_date').size()
    creator_signups_plot = creator_signups_over_time.plot()
    plt.title('Number of Creators Signing Up Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Signups')
    creator_signups_buffer = BytesIO()
    creator_signups_plot.figure.savefig(creator_signups_buffer, format='png')
    creator_signups_buffer.seek(0)
    creator_signups_plot_data = base64.b64encode(creator_signups_buffer.read()).decode('utf-8')
    creator_signups_plot_html = f'<img src="data:image/png;base64,{creator_signups_plot_data}" alt="Number of Creators Signing Up Over Time">'
    
    # Get most streamed song
    most_streamed_song = db.session.query(song_statistics.song_id, func.max(song_statistics.play_song_count)).first()
    most_streamed_song_name = db.session.query(Songs.name).filter_by(id=most_streamed_song[0]).first()

    # Get most streamed album
    most_streamed_album = db.session.query(song_statistics.album_id, func.max(song_statistics.play_album_count)).first()
    most_streamed_album_name = db.session.query(Album.name).filter_by(id=most_streamed_album[0]).first()

    # Get most active user
    most_active_user = db.session.query(song_statistics.listener_id, func.count()).group_by(song_statistics.listener_id).order_by(func.count().desc()).first()
    most_active_user_name = db.session.query(Users.username).filter_by(id=most_active_user[0]).first()

    # Get most streamed song in last month
    last_month_start = datetime.now() - timedelta(days=30)
    most_streamed_song_last_month = db.session.query(song_statistics.song_id, func.max(song_statistics.play_song_count)).filter(song_statistics.date >= last_month_start).first()
    most_streamed_song_last_month_name = db.session.query(Songs.name).filter_by(id=most_streamed_song_last_month[0]).first()

    # Get most streamed album in last month
    most_streamed_album_last_month = db.session.query(song_statistics.album_id, func.max(song_statistics.play_album_count)).filter(song_statistics.date >= last_month_start).first()
    most_streamed_album_last_month_name = db.session.query(Album.name).filter_by(id=most_streamed_album_last_month[0]).first()

    # Get most active user in last month
    most_active_user_last_month = db.session.query(song_statistics.listener_id, func.count()).filter(song_statistics.date >= last_month_start).group_by(song_statistics.listener_id).order_by(func.count().desc()).first()
    most_active_user_last_month_name = db.session.query(Users.username).filter_by(id=most_active_user_last_month[0]).first()
    
    # Get highest rated song
    highest_rating = Songs.query.order_by(Songs.average_ratings.desc()).first().average_ratings
    highest_rated_songs = Songs.query.filter_by(average_ratings=highest_rating).all()
    highest_rated_song_names = [song.name for song in highest_rated_songs]

    # Render the HTML template with the embedded plots
    return render_template('report.html',
                        top_songs_plot_html=top_songs_plot_html,
                        top_albums_plot_html=top_albums_plot_html,
                        user_visits_plot_html=user_visits_plot_html,
                        genre_distribution_plot_html=genre_distribution_plot_html,
                        avg_duration_plot_html=avg_duration_plot_html,
                        user_ratings_plot_html=user_ratings_plot_html,
                        user_signups_plot_html=user_signups_plot_html,
                        creator_signups_plot_html=creator_signups_plot_html,
                        most_streamed_song=most_streamed_song_name,
                        most_streamed_album=most_streamed_album_name,
                        most_active_user=most_active_user_name,
                        most_streamed_song_last_month=most_streamed_song_last_month_name,
                        most_streamed_album_last_month=most_streamed_album_last_month_name,
                        most_active_user_last_month=most_active_user_last_month_name,
                        highest_rating=highest_rating,
                        highest_rated_songs=highest_rated_song_names
                        )

def generate_pdf():
    # Generate the report HTML with embedded plots
    report_html = generate_report()

    # Specify the path to wkhtmltopdf executable
    path_to_wkhtmltopdf = '/usr/local/bin/wkhtmltopdf'  
    
    # Render the HTML to PDF using pdfkit
    options = {
        'quiet': ''
    }
    pdf = pdfkit.from_string(report_html, False, options=options, configuration=pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf))

    return pdf

def send_message_with_attachment(to, subject, content_body, attachment_data, filename):
    msg = MIMEMultipart()
    msg["To"] = to
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    
    # Attach HTML content
    msg.attach(MIMEText(content_body, 'html'))
    
    # Attach PDF file
    attachment = MIMEApplication(attachment_data)
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)
    
    # Send email
    with SMTP(host=SMTP_HOST, port=SMTP_PORT) as client:
        client.send_message(msg=msg)


@shared_task(ignore_result=True)
def send_monthly_report(to, subject):
    # Query users who are not admins
    #user = Users.query.filter(Users.role == 'Admin').all()
    report_pdf = generate_pdf()
    body = "Hello Admin,please find the attached Monthly report under 'MIME' section named 'application/octet-stream' in this email."
    send_message_with_attachment(to,subject,body,report_pdf,'Monthly_Report.pdf')
    
    return "OK"


@celery_app.on_after_configure.connect
def send_report(sender, **kwargs):
    # Schedule the monthly report task
    sender.add_periodic_task(
    crontab(hour=21, minute=33, day_of_month=15),
        send_monthly_report.s('admin@gmail.com',"Monthly Report"),
    )

@musicapp.route('/favicon.ico')
def favicon():
    # Return an empty response to prevent the 404 error
    return '', 204

if __name__ == '__main__':
    musicapp.run(debug=True)

#redis-server
#celery -A main:celery_app worker -l INFO
#celery -A main:celery_app beat -l INFO
#ps aux | grep redis-server
#pkill redis-server
#redis-cli -p <port_number> shutdown
#mailhog
#Go to localhost:8025