import sqlite3
import json
import tweepy
import config
from dbhelper import DBHelper


def init_api():
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_KEY, config.ACCESS_SECRET)

    api = tweepy.API(auth)
    # import pdb; pdb.set_trace()
    return api

def init_database_helper():
    dbh = DBHelper()
    dbh.init_tables()
    return dbh

def set_user(api, dbh, user):
    user = api.get_user(user)
    dbh.add_profile(user.screen_name, user.id)
    return user

def get_loc(dbh, user):
    tl = user.timeline(count=50)
    db_id = dbh.get_twit_db_id(user.id)[0]
    feat_list = []
    loc_dict = {}
    # import pdb; pdb.set_trace()
    for status in tl:
        if status.place != None:
            # begin count of location
            loc_name = gen_loc_name(status)
            if loc_name not in loc_dict:
                loc_dict[loc_name] = 1
            else:
                loc_dict[loc_name] += 1

            # build geojson feat list
            feat_list.append(
                gen_feat_json(
                    status.place.bounding_box.type,
                    status.place.bounding_box.coordinates
                )
            )
    # create complete geojson
    json_dict = {
        'type': 'FeatureCollection',
        'features': feat_list,
    }
    geo_json = json.dumps(
        json_dict,
        sort_keys=False,
        indent=4,
        separators=(',', ': ')
    )
    with open('geo.json', 'w') as f:
        f.write(geo_json)
    print('[+]Geo Json file created at: ./geo.json')
    print('[-]To use please visit:')
    print('[-]http://geojson.io/')
    print('[-]http://geojsonlint.com/')
    for loc in loc_dict:
        print('[+]{0}: {1}'.format(loc, loc_dict[loc]))
    print('')

def gen_feat_json(poly_type, coord_list):
    """
        only works for 4pt polygons
    """
    coord_list[0].append(coord_list[0][0])
    json_dict = {
        'type': 'Feature',
        'properties': {
            'stroke': '#000000',
            'stroke-width': 2,
            'stroke-opacity': 1,
            'fill': '#ff0606',
            'fill-opacity': 0.1
        },
        'geometry': {
            'type': poly_type,
            'coordinates': coord_list
        }
    }
    return json_dict

def gen_loc_name(status):
    return '{0} | {1}'.format(status.place.full_name, status.place.country)

def get_devices(dbh, user):
    tl = user.timeline(count=50)
    db_id = dbh.get_twit_db_id(user.id)[0]
    dev_dict = {}
    for status in tl:
        try:
            dev = status.source.split(' ')[-1]
            if dev not in dev_dict:
                dev_dict[dev] = 1
            else:
                dev_dict[dev] += 1
        except:
            import pdb; pdb.set_trace()
    for dev in dev_dict:
        print('[+]{0}: {1}'.format(dev, dev_dict[dev]))
    print('')


if __name__ == "__main__":
    cmd = ''
    # init api
    api = init_api()
    # init db and cursor
    dbh = init_database_helper()
    # set user because there's no point otherwise
    user = input('Set User==> ')
    user = set_user(api, dbh, user)
    print('[+]User set\n')
    while cmd.lower() != 'q':
        # display menu
        print('---Menu---')
        print('set | set user')
        print('loc | collect locations of past 50 tweets')
        print('devices | get devices and usage count based on 50 tweets')
        print('q | end game')
        cmd = input('==> ')
        if cmd.lower() == 'set':
            user = input('Set User==> ')
            user = set_user(api, dbh, user)
            print('[+]User set')
        elif cmd.lower() == 'loc':
            get_loc(dbh, user)
        elif cmd.lower() == 'devices':
            get_devices(dbh, user)