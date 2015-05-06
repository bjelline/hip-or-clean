import csv,datetime,decimal,httplib2,io,json,logging,os,psycopg2,psycopg2.extras,random,re,sys,urllib,urllib2
from flask       import Flask, Response, request, session, g, redirect, url_for, abort, render_template, flash
from flask.json  import JSONEncoder
from collections import Counter
from logging     import StreamHandler

app = Flask(__name__)

foursquare_client_id     = os.environ.get('FOURSQUARE_CLIENT_ID')
foursquare_client_secret = os.environ.get('FOURSQUARE_CLIENT_SECRET')
socrata_app_token        = os.environ.get('SOCRATA_APP_TOKEN')
socrata_secret_token     = os.environ.get('SOCRATA_SECRET_TOKEN')
database_url             = os.environ.get('DATABASE_URL')

file_handler = StreamHandler()
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

def json_serial(obj):
  """JSON serializer for objects not serializable by default json code"""
  if isinstance(obj, datetime.datetime):
    serial = obj.isoformat()
    return serial
  if isinstance(obj, datetime.date):
    serial = obj.isoformat()
    return serial
  if isinstance(obj, decimal.Decimal):
    serial = float(obj)
    return serial

def soda_escape(s):
  if s is None:
    return s
  return s.replace("'","''")

def from_db(filter):
  new_venues = []
  try:
    app.logger.error('asking db for q = %s' % filter )
    g.db_cursor.execute("""
        SELECT * from foursquare_cache
        LEFT JOIN inspection_businesses USING(id)
        LEFT JOIN newest_inspection USING(camis) 
        LEFT JOIN inspections USING(camis, inspection_date) 
        WHERE rating > 0.0 AND score is not null
      """, { "q": filter })
    for v in g.db_cursor.fetchall():
      di = dict(v)
      app.logger.error('%s rating is %s' % ( v['name'], v['rating'] ))
      new_venues.append( di )

  except Exception as ex:
    app.logger.error('Error loading data from_db in %s: %s %s' % (sys.exc_traceback.tb_lineno , type(ex), ex))
  return new_venues

def add_inspection_results(given_venues):
  new_venues = given_venues
  try:
    new_venues =[ ]
    for v in given_venues:
      app.logger.error('asking soda for name = %s, phone = %s ' % ( v['name'], v['phone'] ) )
      try:
        if 'phone' in v and 'name' in v:
          url = 'https://data.cityofnewyork.us/resource/xx67-kt59.json?' + urllib.urlencode({
            '$where': "phone='%s' OR dba='%s'" % ( soda_escape(v['phone']), soda_escape(v['name']))
          })
        elif 'phone' in v:
          url = 'https://data.cityofnewyork.us/resource/xx67-kt59.json?' + urllib.urlencode({
            '$where': "phone='%s'" % ( soda_escape(v['phone']) )
          })
        elif 'name' in v:
          url = 'https://data.cityofnewyork.us/resource/xx67-kt59.json?' + urllib.urlencode({
            '$where': "OR dba='%s'" % ( soda_escape(v['name']))
          })
        else:
          app.logger.error("not enough info to call soda")
          continue
        app.logger.error("will call " + url)
        soda_response, soda_json = g.web.request( url, "GET")
        app.logger.error( "got %d chars of json" % len(soda_json) )
        soda_content = json.loads(soda_json)
        inspection_date = datetime.datetime(datetime.MINYEAR,1,1,0,0,0)
        v['inspection_date'] = "01/01/1900"
        v['score'] = 0
        v['grade'] = 0
        v['inspection'] = ""
        for i in soda_content:
          i['id'] = v['id']
          if 'inspection_date' in i:
            # 02/09/2015 2014-07-08T00:00:00
            idate = datetime.datetime.strptime(i['inspection_date'][0:10],  "%Y-%m-%d")
            if idate > inspection_date:
              v['inspection_date'] = i['inspection_date'][0:10]
              if 'violation_description' in i:
                v['inspection'] += i['violation_description']
              if 'score' in i:
                v['score'] = int( i['score'] )
              if not 'grade' in i:
                i['grade'] = None
              v['grade'] = i['grade']
              if not 'grade_date' in i:
                i['grade_date'] = None
              v['grade_date'] = i['grade_date']
              if not 'violation_code' in i:
                i['violation_code'] = None
              v['violation_code'] = i['violation_code']
              if not 'violation_description' in i:
                i['violation_description'] = None
              v['violation_description'] = i['violation_description']
              if not 'score' in i:
                i['score'] = None
              v['score'] = i['score']
          if g.do_db: 
            g.db_cursor.execute("""UPDATE inspection_businesses SET "id" = %(id)s WHERE "camis" = %(camis)s""", i )
            g.db_cursor.execute("""
              INSERT INTO inspection_businesses (
                "camis", "id", "dba", "boro", "building", "street", "zipcode", "phone", "cuisine_description"
              ) SELECT
                %(camis)s, %(id)s, %(dba)s, %(boro)s, %(building)s, %(street)s, %(zipcode)s, %(phone)s, %(cuisine_description)s
                WHERE NOT EXISTS (SELECT 1 FROM inspection_businesses WHERE "camis" = %(camis)s)
              """, i )
            g.db_cursor.execute("""
              INSERT INTO inspections (
                "camis", "inspection_date", "action", "violation_code", "violation_description",
                "critical_flag", "score", "grade", "grade_date", "record_date", "inspection_type"
              ) SELECT
                %(camis)s, %(inspection_date)s, %(action)s, %(violation_code)s, %(violation_description)s,
                %(critical_flag)s, %(score)s, %(grade)s, %(grade_date)s, %(record_date)s, %(inspection_type)s
                WHERE NOT EXISTS (SELECT 1 FROM inspections WHERE "camis" = %(camis)s AND "inspection_date" = %(inspection_date)s)
              """, i)
            app.logger.error("saved %s inspection at %s to database" % (i['dba'], i['inspection_date']))

        v['soda'] = len(soda_content) > 0
        if v["inspection_date"] != "01/01/1900":
          new_venues.append(v)
      except Exception as ex:
        app.logger.error('Error loading data from soda in %s: %s %s' % (sys.exc_traceback.tb_lineno , type(ex), ex))
  except Exception as ex:
    app.logger.error('Error loading data in %s: %s %s' % (sys.exc_traceback.tb_lineno , type(ex), ex))
  return new_venues

def search_foursquare_venues( query ):
  url = 'https://api.foursquare.com/v2/venues/search?' + urllib.urlencode({
        'client_id':     foursquare_client_id,
        'client_secret': foursquare_client_secret,
        'll':            '40.7,-74',
        'v':             '20140806',
        'limit':         100,
        'query':         query
        })
  app.logger.error('search foursquare for %s: %s' % (query, url))
  fsq_response, fsq_content = g.web.request( url, "GET")
  foursquare_response = json.loads(fsq_content)

  if foursquare_response['meta']['code'] != 200:
    raise "error reading foursquare api"

  venues = []
  found_categories = set()
  for venue in foursquare_response['response']['venues']:
    these_categories =  set( [ c['name'] for c in venue['categories'] ] )
    found_categories = found_categories.union( these_categories )
    if query in these_categories:
      venue_response, venue_content = g.web.request('https://api.foursquare.com/v2/venues/' + venue['id'] + '?' + 
        urllib.urlencode({
          'client_id':     foursquare_client_id,
          'client_secret': foursquare_client_secret,
          'v':             '20140806'
        }), "GET"
      )
      venue_response = json.loads(venue_content)
      if 'response' in venue_response and 'venue' in venue_response['response']:
        v = venue_response['response']['venue']
        if 'menu' in v:
          del(v['menu'])
        if 'tips' in v and 'groups' in v['tips']:
          del(v['tips']['groups'])
        v2 = {
            "phone": v['contact']['phone'] if 'contact' in v and 'phone' in  v['contact'] else None,
            "price_tier": v['price']['tier'] if 'price' in v and 'tier' in  v['price'] else None,
            "likes_count": v['likes']['count'], 
            "hereNow_count": v['hereNow']['count'], 
            "canonicalUrl": v['canonicalUrl'],
            "id": v['id'],
            "name": v['name'],
            "address": None,
            "rating": v['rating'] if 'rating' in v else 0,
            "url": v['url'] if 'url' in v else None,
            "bestPhoto": v['bestPhoto']['prefix'] + "300x300" + v['bestPhoto']['suffix'] if 'bestPhoto' in v else '',
            "verified": v['verified']
        }
        if 'address' in v:
          v2['address'] = v['address']
        if 'stats' in v:
          v2.update( v['stats'] )
        if 'location' in v:
          v2.update( v['location'] )
        if 'formattedAddress' in v2:
          del( v2['formattedAddress'] )
        venues.append( v2 )

  app.logger.error('while looking for %s I found %s' % (query, found_categories))
  if g.do_db: 
    for x in venues: 
      app.logger.info( x )
      try:
        g.db_cursor.execute("""DELETE FROM foursquare_cache WHERE id=%(id)s""", x)
        g.db_cursor.execute("""
          INSERT INTO foursquare_cache (
            id, name, phone, verified,
            price_tier, rating,
            address, lat, lng, city, cc, country, state,
            likes_count
          ) VALUES (
            %(id)s, %(name)s, %(phone)s, %(verified)s,
            %(price_tier)s, %(rating)s,
            %(address)s, %(lat)s, %(lng)s, %(city)s, %(cc)s, %(country)s, %(state)s,
            %(likes_count)s
          )""", x )
      except Exception as inst:
        app.logger.error('error %s: could not write %s to db' % (inst, x))

  return venues



# ====================================================================================
@app.before_request
def before_request():
  # try out api
  try:
    do_api                   = os.environ.get('DO_API')
    g.do_api = False
    app.logger.error('do_api=%s' % do_api)
    if do_api == "1" and foursquare_client_id and foursquare_client_secret:
      g.do_api = True
      app.logger.error('have foursquare credentials, will try to use API %s' % do_api)
      g.web = httplib2.Http("tmp/", disable_ssl_certificate_validation=True)
      g.do_api = True
  except Exception as inst:
    app.logger.error('Error trying Foursquare API: %s' % inst)
  # try connecting to database
  try:
    do_db                    = os.environ.get('DO_DB')
    g.do_db = False
    app.logger.error('do_db=%s' % do_db)
    if do_db == "1" and database_url:
      app.logger.error('have database credentials, will try to use database')
      g.db = psycopg2.connect(database_url)
      g.db.autocommit = True
      g.db_cursor = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
      g.do_db = True
  except Exception as inst:
    app.logger.error('Error trying Database: %s' % inst)

# ====================================================================================
@app.route('/map.html')
def map():
  return render_template("map.html", title = "Map")

@app.route('/combined.json')
def combined():
  try:
    q = request.args.get('filter') 
    venues = []
    if q is None:
      q = 'Greek Restaurant'
    if g.do_api:
      venues = search_foursquare_venues( q )
      app.logger.info( "done foursquare query %s, got %d venues" % (q, len(venues)) )
      venues = add_inspection_results( venues )
      app.logger.info( "done inspections, %d venues left" % len(venues) )
    if not g.do_api:
      venues = from_db( q )
      app.logger.info( "done db, %d venues found" % len(venues) )
      if len(venues) > 0:
        app.logger.info( venues[0] )
        app.logger.info( type( venues[0]['rating'] ) )
    app.logger.info("datetime.now() -> %s" %  json.dumps({'now': datetime.datetime.now() }, default=json_serial) )
    resp = Response( json.dumps({
      'status': 200,
      'color': 'purple',
      'message': 'ok',
      'x_label': 'rating',
      'y_label': 'number of checkins',
      'data':  [ [ v['score'], v['rating'], v['name'], v['violation_description'] ] for v in venues ],
      'count':  len(venues),
      'venues':  venues
      }, default=json_serial), status=200, mimetype='application/json')
  except Exception as ex:
    app.logger.error('Error loading data in %s: %s %s' % (sys.exc_traceback.tb_lineno , type(ex), ex))
    resp = Response( json.dumps({ 'status': 404, 'message': 'error loading data'}), status=404, mimetype='application/json')
  return resp

@app.route('/plot.html')
def plot():
  return render_template("plot.html", title = "Plot Overview")

@app.route('/about.html')
def about():
  return render_template("about.html", title = "About this Site")

@app.route('/load')
def load():
  try:
    fp = open("DOHMH_New_York_City_Restaurant_Inspection_Results.csv")
    csvreader = csv.reader(fp)
    # g.db_cursor.execute("")
    for row in csvreader:
      business = row[0:6]
  except Exception as inst:
    app.logger.error('Error: %s' % inst)
    abort(500)
  return render_template("admin.html", title = "Loading Data", output = "done")

# ====================================================================================
@app.route('/data.csv')
def data():
  try:
    q = request.args.get('filter') 
    if q is None:
      q = 'Greek Restaurant'
    app.logger.info( "/data.csv?q=%s, api=%s, db=%s" % (q, g.do_api, g.do_db) )

    venues = []
    if g.do_api:
      app.logger.info( "will search foursquare for fresh results for %s" % q )
      venues = search_foursquare_venues( q )
      app.logger.info( "done foursquare query %s, got %d venues" % (q, len(venues)) )
      venues = add_inspection_results( venues )
      app.logger.info( "done inspections, %d venues left" % len(venues) )

    if not g.do_api and g.do_db:
      app.logger.info( "just loding old results from db" )
      venues = from_db( q )
      app.logger.info( "old results from db, %d venues found" % len(venues) )

    if len(venues) > 0:
      app.logger.info( venues[0] )
      app.logger.info( type( venues[0]['rating'] ) )

    # app.logger.info("datetime.now() -> %s" %  json.dumps({'now': datetime.datetime.now() }, default=json_serial) )

    app.logger.error('all columns in my results: %s' % venues[0].keys())
    
    cols = [ 'score', 'rating', 'name',  'boro', 'street', 'lng', 'lat', 'violation_description' ]
    output = io.BytesIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(cols)
    for v in venues:
      writer.writerow([ v[ c ] for c in cols ])
    resp = Response( output.getvalue(), status=200, mimetype='text/plain')
  except Exception as ex:
    app.logger.error('Error loading data in %s: %s %s' % (sys.exc_traceback.tb_lineno , type(ex), ex))
    resp = Response( "", status=404, mimetype='text/plain')
  return resp

@app.route('/')
def index():
    return render_template("index.html")

# ====================================================================================
if __name__ == '__main__':
  app.run(debug=True)
# ====================================================================================
