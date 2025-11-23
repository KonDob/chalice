from chalice import Chalice
import os
from pymongo import MongoClient
import uuid
import random

app = Chalice(app_name='helloworld')


@app.route('/')
def index():
    return {'hello': 'world'}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
@app.route('/hello/{name}')
def hello_name(name):
   # '/hello/james' -> {"hello": "james"}
   return {'hello': name}

@app.route('/users', methods=['POST'])
def create_user():
    # This is the JSON body the user sent in their POST request.
    user_as_json = app.current_request.json_body
    # We'll echo the json body back to the user in a 'user' key.
    return {'user': user_as_json}
#
# See the README documentation for more examples.
#
_mongo_client = None


def _get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        uri = os.environ.get('MONGODB_URI')
        if not uri:
            raise RuntimeError('MONGODB_URI is not set')
        _mongo_client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    return _mongo_client


def _get_db():
    name = os.environ.get('MONGODB_DB', 'test')
    return _get_mongo_client()[name]


@app.route('/db/ping')
def db_ping():
    _get_db().command('ping')
    return {'ok': True}


def _cars_collection():
    return _get_db()['cars']


def _parse_filters(params):
    if not params:
        return {}
    f = {}
    for k, v in params.items():
        if k == 'id':
            f['_id'] = v
        elif k == 'year':
            try:
                f['year'] = int(v)
            except Exception:
                pass
        elif k == 'price':
            try:
                f['price'] = float(v)
            except Exception:
                pass
        elif k in ('make', 'model'):
            f[k] = v
    return f


@app.route('/cars/seed', methods=['POST'])
def seed_cars():
    makes_models = {
        'Toyota': ['Corolla', 'Camry', 'RAV4'],
        'Honda': ['Civic', 'Accord', 'CR-V'],
        'Ford': ['Focus', 'Fusion', 'Escape'],
        'BMW': ['320i', 'X3', 'X5'],
        'Audi': ['A3', 'A4', 'Q5']
    }
    docs = []
    for _ in range(10):
        make = random.choice(list(makes_models.keys()))
        model = random.choice(makes_models[make])
        year = random.randint(2000, 2024)
        price = round(random.uniform(5000, 80000), 2)
        docs.append({
            '_id': str(uuid.uuid4()),
            'make': make,
            'model': model,
            'year': year,
            'price': price
        })
    col = _cars_collection()
    result = col.insert_many(docs)
    return {'inserted': len(result.inserted_ids)}


@app.route('/cars', methods=['GET'])
def list_cars():
    params = app.current_request.query_params
    filt = _parse_filters(params)
    col = _cars_collection()
    items = list(col.find(filt, {'_id': 1, 'make': 1, 'model': 1, 'year': 1, 'price': 1}))
    for it in items:
        it['id'] = it.pop('_id')
    return {'items': items}


@app.route('/cars/avg-price', methods=['GET'])
def avg_price():
    params = app.current_request.query_params
    match = _parse_filters(params)
    pipeline = []
    if match:
        pipeline.append({'$match': match})
    pipeline.append({'$group': {'_id': None, 'avgPrice': {'$avg': '$price'}}})
    col = _cars_collection()
    res = list(col.aggregate(pipeline))
    avg_val = res[0]['avgPrice'] if res else None
    return {'average_price': avg_val}
