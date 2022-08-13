#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
from typing import final
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from xmlrpc.client import boolean
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
# configuration variables and instructions,  are stored in the config.py where the connection is implemented .

#----------------------------------------------------------------------------#
# Models.
# Implemented in models.py
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
  else:
    date = value
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data =Venue.query.all()
  
  # Creates a dictionary of venues grouped by their location in state and city

  dict_of_areas ={(area.city,area.state): area.state for  area in data}


  return render_template('pages/venues.html', areas=data,dict_of_areas=dict_of_areas)

@app.route('/venues/search', methods=['GET','POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for cofee should return "Well Performed Arts with Coffee".

  search_term=f"%{request.form.get('search_term', '')}%"
  results = Venue.query.filter(Venue.name.ilike(search_term)).all()
  response={
     "data_results": results,
    "count": len(results)
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    
  # shows the venue page with the given venue_id
    venue=Venue.query.get(venue_id)
    previous_shows = []
    future_shows = []
    
    # Fetches all shows associated with venue id
    shows = Show.query.filter(Show.venue_id == venue_id).\
      join(Artist, Artist.id == Show.artist_id).all()

    
    for show in shows:
      if show.start_time <= datetime.now():
        show_details={
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time    
        }
        previous_shows.append(show_details)
      else:
        show_details={
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time 
        }
        future_shows.append(show_details)
    
    data= {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": previous_shows,
      "upcoming_shows": future_shows,
      "past_shows_count": len(previous_shows),
      "upcoming_shows_count": len(future_shows)
    }
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  # TODO: insert form data as a new Venue record in the db, instead
    error=False
    try:
      name=request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      address = request.form.get('address')
      phone = request.form.get('phone')
      image_link = request.form.get('image_link')
      facebook_link = request.form.get('facebook_link')
      genres = request.form.getlist('genres')
      website_link = request.form.get('website_link')
      talent_needed = request.form.get('seeking_talent',type=boolean)

      description  = request.form.get('seeking_description')
      # TODO: modify data to be the data object returned from db insertion
      venue =Venue(name=name, city=city, state=state, address=address, phone=phone, 
                    genres=genres, image_link=image_link, facebook_link=facebook_link, 
                    website=website_link, seeking_talent=talent_needed, seeking_description=description)
      db.session.add(venue)
      db.session.commit()
    except FileNotFoundError:
        error=True
        db.session.rollback()
    finally:
      db.session.close()
    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    if error:
      flash('An error occurred. Venue ' + name + ' could not be listed.')
    else:
      flash('Venue ' + name + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET','DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue_to_delete=Venue.query.get(venue_id)
  try:
    db.session.delete(venue_to_delete)
    db.session.commit()
    flash('Venue ' + venue_to_delete.name + ' has been deleted.')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue_to_delete.name + ' could not be deleted.')
  finally:
    db.session.close()
  
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    #TODO: replace with real data returned from querying the database
  data= data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=f"%{request.form.get('search_term', '')}%"
  results = Artist.query.filter(Artist.name.ilike(search_term)).all()
  response={
     "data_results": results,
    "count": len(results)
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist=Artist.query.get(artist_id)
    previous_shows = []
    future_shows = []
    
    # Fetches all shows associated with artist id
    shows = Show.query.filter(Show.artist_id == artist_id).\
      join(Venue, Venue.id == Show.venue_id).all()


    for show in shows:
      if show.start_time <= datetime.now():
        show_details={
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time    
        }
        previous_shows.append(show_details)
      else:
        show_details={
         "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time   
        }
        future_shows.append(show_details)
    
    artist_to_display= {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": previous_shows,
      "upcoming_shows": future_shows,
      "past_shows_count": len(previous_shows),
      "upcoming_shows_count": len(future_shows)
    }
    return render_template('pages/show_artist.html', artist=artist_to_display)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.get(artist_id)
  form = ArtistForm(name=artist.name,city=artist.city,state=artist.state,
                    phone=artist.phone, genres=artist.genres,image_link=artist.image_link,
                    facebook_link=artist.facebook_link,website_link=artist.website,
                    seeking_venue=artist.seeking_venue,seeking_description=artist.seeking_description)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error= False
  artist_to_update=Artist.query.get(artist_id)
  # TODO: take values from the form submitted, and update existing
  try:
    name=request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.getlist('genres')
    website_link = request.form.get('website_link')
    venue_needed = request.form.get('seeking_venue',type=boolean)
    description  = request.form.get('seeking_description')

    # artist record with ID <artist_id> using the new attributes
    artist_to_update.name=name
    artist_to_update.city=city
    artist_to_update.state=state
    artist_to_update.phone=phone
    artist_to_update.image_link=image_link
    artist_to_update.facebook_link=facebook_link
    print(artist_to_update.genres)
    artist_to_update.genres=genres
    artist_to_update.website=website_link
    artist_to_update.seeking_venue=venue_needed
    artist_to_update.seeking_description=description
    db.session.commit()
  except:
    db.session.rollback()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue_to_edit=Venue.query.get(venue_id)
    #TODO: populate form with values from venue with ID <venue_id>
    form = VenueForm(name=venue_to_edit.name,city=venue_to_edit.city,state=venue_to_edit.state,phone=venue_to_edit.phone,
     genres=venue_to_edit.genres,image_link=venue_to_edit.image_link,facebook_link=venue_to_edit.facebook_link,
     website_link=venue_to_edit.website,seeking_venue=venue_to_edit.seeking_talent,seeking_description=venue_to_edit.seeking_description,
     address=venue_to_edit.address)
  
    return render_template('forms/edit_venue.html', form=form, venue=venue_to_edit)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  
  error= False
  venue_to_update=Venue.query.get(venue_id)

  try:
    name=request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    address=request.form.get('address')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.getlist('genres')
    website_link = request.form.get('website_link')
    talent_needed = request.form.get('seeking_talent',type=boolean)
    description  = request.form.get('seeking_description')

    # venue record with ID <venue_id> using the new attributes
    venue_to_update.name=name
    venue_to_update.city=city
    venue_to_update.state=state
    venue_to_update.phone=phone
    venue_to_update.address=address
    venue_to_update.image_link=image_link
    venue_to_update.facebook_link=facebook_link
    venue_to_update.genres=genres
    venue_to_update.website=website_link
    venue_to_update.seeking_talent=talent_needed
    venue_to_update.seeking_description=description
    db.session.commit()
  except TypeError:
    db.session.rollbacK()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead

  error=False
  try:
    name=request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    genres = request.form.getlist('genres')
    website_link = request.form.get('website_link')
    venue_needed = request.form.get('seeking_venue',type=boolean)
    description  = request.form.get('seeking_description')

    # TODO: modify data to be the data object returned from db insertion
    artist = Artist(id=(Artist.query.count() +1),name=name, city=city, state=state, phone=phone, 
                  genres=genres, image_link=image_link, facebook_link=facebook_link, 
                  website=website_link, seeking_venue=venue_needed, seeking_description=description)
    db.session.add(artist)
    db.session.commit()
  except TypeError:
      error=True
      db.session.rollback()
  finally:
    db.session.close()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  if error:
      flash('An error occurred. Artist ' + name + ' could not be listed.')
  else:
      flash('Artist ' + name + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]
  all_shows=db.session.query(Show).\
    join(Venue,Venue.id == Show.venue_id).\
      join(Artist, Artist.id == Show.artist_id).all()
  for show in all_shows:
    show_details={
      'venue_id':show.venue_id,
      'venue_name':show.venue.name,
      'artist_id':show.artist_id,
      'artist_name':show.artist.name,
      'artist_image_link':show.artist.image_link,
      'start_time':show.start_time
    }
    data.append(show_details)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error=False
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id=request.form.get("artist_id")
    venue_id=request.form.get('venue_id')
    start_time=request.form.get('start_time')
    new_show=Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  if error:
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success
  else:
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
