"""Fetches football data from football-data.org, api-sports.io, and the-odds-api.com.
Run by GitHub Actions every 3 hours."""
import urllib.request
import json
import os
import time
from datetime import datetime, timedelta

API_KEY = os.environ.get('FOOTBALL_API_KEY', '')
API_FOOTBALL_KEY = os.environ.get('API_FOOTBALL_KEY', '')
ODDS_API_KEY = os.environ.get('ODDS_API_KEY', '')
API_BASE = 'https://api.football-data.org/v4'
ODDS_API_BASE = 'https://api.the-odds-api.com/v4'
LEAGUES = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'DED', 'PPL', 'ELC', 'BSA', 'CL']
DATA_DIR = 'data'

LEAGUE_TO_SPORT = {
    'PL': 'soccer_epl',
    'PD': 'soccer_spain_la_liga',
    'SA': 'soccer_italy_serie_a',
    'BL1': 'soccer_germany_bundesliga',
    'FL1': 'soccer_france_ligue_one',
    'CL': 'soccer_uefa_champs_league',
    'DED': 'soccer_netherlands_eredivisie',
    'PPL': 'soccer_portugal_primeira_liga',
    'ELC': 'soccer_efl_champ',
    'BSA': 'soccer_brazil_campeonato',
}

# Rotation: which leagues to fetch odds for based on hour (cron hits 0/3/6/9/12/15/18/21)
ODDS_ROTATION = {
    0: ['PL', 'PD'],
    6: ['SA', 'BL1'],
    12: ['FL1', 'CL'],
    18: ['DED', 'PPL'],
    21: ['ELC', 'BSA'],
}

def api_get(path):
    url = API_BASE + path
    req = urllib.request.Request(url, headers={
        'X-Auth-Token': API_KEY,
        'User-Agent': 'FootballPredictions/1.0'
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def api_football_get(endpoint):
    """Fetch from API-Football (api-sports.io)."""
    url = 'https://v3.football.api-sports.io' + endpoint
    req = urllib.request.Request(url, headers={
        'x-apisports-key': API_FOOTBALL_KEY,
        'User-Agent': 'FootballPredictions/1.0'
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        return data.get('response', [])

def odds_api_get(endpoint):
    """Fetch from The Odds API."""
    url = ODDS_API_BASE + endpoint
    if '?' in url:
        url += f'&apiKey={ODDS_API_KEY}'
    else:
        url += f'?apiKey={ODDS_API_KEY}'
    req = urllib.request.Request(url, headers={'User-Agent': 'FootballPredictions/1.0'})
    with urllib.request.urlopen(req) as resp:
        remaining = resp.headers.get('x-requests-remaining', '?')
        print(f'  Odds API requests remaining: {remaining}')
        return json.loads(resp.read())

# ==================== ODDS PROCESSING ====================

def normalize_name(name):
    """Normalize team name for matching."""
    n = name.lower().strip()
    for suffix in [' fc', ' cf', ' sc', ' sk', ' fk', ' afc', ' ssc', ' ac']:
        if n.endswith(suffix):
            n = n[:-len(suffix)].strip()
    return n

def match_odds_to_fixtures(odds_events, league_matches):
    """Match odds events to our fixture data by team name + date."""
    for event in odds_events:
        event['matchId'] = None
        oh = normalize_name(event['homeTeam'])
        oa = normalize_name(event['awayTeam'])
        od = datetime.fromisoformat(event['commenceTime'].replace('Z', '+00:00'))

        for m in league_matches:
            mh = normalize_name(m['homeTeam']['name'])
            ma = normalize_name(m['awayTeam']['name'])
            md = datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00'))

            if abs((od - md).total_seconds()) > 86400:
                continue
            if (oh in mh or mh in oh) and (oa in ma or ma in oa):
                event['matchId'] = m['id']
                break

def calc_best_and_arbitrage(bookmakers, market_key):
    """Calculate best odds and arbitrage for a market across bookmakers."""
    if market_key == 'h2h':
        best = {'home': 0, 'draw': 0, 'away': 0}
        best_bk = {'home': '', 'draw': '', 'away': ''}
        for bk in bookmakers:
            for mkt in bk.get('markets', []):
                if mkt['key'] != 'h2h':
                    continue
                for out in mkt['outcomes']:
                    name = out['name']
                    price = out['price']
                    if name == 'Draw':
                        if price > best['draw']:
                            best['draw'] = price
                            best_bk['draw'] = bk['title']
                    elif out.get('_is_home'):
                        if price > best['home']:
                            best['home'] = price
                            best_bk['home'] = bk['title']
                    else:
                        if price > best['away']:
                            best['away'] = price
                            best_bk['away'] = bk['title']
        if best['home'] > 0 and best['draw'] > 0 and best['away'] > 0:
            margin = 1/best['home'] + 1/best['draw'] + 1/best['away'] - 1
            return best, best_bk, margin
        return best, best_bk, None

    elif market_key == 'totals':
        best = {'over': 0, 'under': 0}
        best_bk = {'over': '', 'under': ''}
        point = None
        for bk in bookmakers:
            for mkt in bk.get('markets', []):
                if mkt['key'] != 'totals':
                    continue
                for out in mkt['outcomes']:
                    if point is None and 'point' in out:
                        point = out['point']
                    if out['name'] == 'Over' and out['price'] > best['over']:
                        best['over'] = out['price']
                        best_bk['over'] = bk['title']
                    elif out['name'] == 'Under' and out['price'] > best['under']:
                        best['under'] = out['price']
                        best_bk['under'] = bk['title']
        if best['over'] > 0 and best['under'] > 0:
            margin = 1/best['over'] + 1/best['under'] - 1
            return best, best_bk, margin, point
        return best, best_bk, None, point

    return {}, {}, None

def fetch_odds(leagues_to_fetch):
    """Fetch odds from The Odds API for given leagues."""
    for code in leagues_to_fetch:
        sport_key = LEAGUE_TO_SPORT.get(code)
        if not sport_key:
            continue

        print(f'  Fetching odds for {code} ({sport_key})...')

        # Load existing league data for match linking
        league_file = os.path.join(DATA_DIR, f'{code}.json')
        league_matches = []
        if os.path.exists(league_file):
            with open(league_file, 'r', encoding='utf-8') as f:
                ld = json.load(f)
                league_matches = ld.get('matches', [])

        try:
            raw = odds_api_get(
                f'/sports/{sport_key}/odds?regions=eu,uk&markets=h2h,totals,btts&oddsFormat=decimal'
            )
        except Exception as e:
            print(f'  Error fetching odds for {code}: {e}')
            continue

        if not raw:
            print(f'  No odds data for {code}')
            continue

        events = []
        for ev in raw:
            try:
                home_team = ev.get('home_team', '')
                away_team = ev.get('away_team', '')

                # Tag home/away in h2h outcomes
                for bk in ev.get('bookmakers', []):
                    for mkt in bk.get('markets', []):
                        if mkt.get('key') == 'h2h':
                            for out in mkt.get('outcomes', []):
                                out['_is_home'] = (out.get('name') == home_team)

                # Build bookmaker list for h2h
                h2h_bookmakers = []
                for bk in ev.get('bookmakers', []):
                    for mkt in bk.get('markets', []):
                        if mkt.get('key') == 'h2h':
                            row = {'key': bk.get('key', ''), 'title': bk.get('title', '')}
                            for out in mkt.get('outcomes', []):
                                nm = out.get('name')
                                pr = out.get('price')
                                if nm == home_team:
                                    row['home'] = pr
                                elif nm == 'Draw':
                                    row['draw'] = pr
                                else:
                                    row['away'] = pr
                            if 'home' in row and 'draw' in row and 'away' in row:
                                h2h_bookmakers.append(row)

                # Build bookmaker list for totals
                totals_bookmakers = []
                totals_point = None
                for bk in ev.get('bookmakers', []):
                    for mkt in bk.get('markets', []):
                        if mkt.get('key') == 'totals':
                            row = {'key': bk.get('key', ''), 'title': bk.get('title', '')}
                            for out in mkt.get('outcomes', []):
                                if totals_point is None and 'point' in out:
                                    totals_point = out['point']
                                if out.get('name') == 'Over':
                                    row['over'] = out.get('price')
                                elif out.get('name') == 'Under':
                                    row['under'] = out.get('price')
                            if 'over' in row and 'under' in row:
                                totals_bookmakers.append(row)

                # Build bookmaker list for BTTS (both teams to score)
                btts_bookmakers = []
                btts_best_yes = 0
                btts_best_no = 0
                btts_best_yes_bk = ''
                btts_best_no_bk = ''
                for bk in ev.get('bookmakers', []):
                    for mkt in bk.get('markets', []):
                        if mkt.get('key') == 'btts':
                            row = {'key': bk.get('key', ''), 'title': bk.get('title', '')}
                            for out in mkt.get('outcomes', []):
                                nm = out.get('name', '').lower()
                                pr = out.get('price')
                                if nm == 'yes' and pr:
                                    row['yes'] = pr
                                    if pr > btts_best_yes:
                                        btts_best_yes = pr
                                        btts_best_yes_bk = bk.get('title', '')
                                elif nm == 'no' and pr:
                                    row['no'] = pr
                                    if pr > btts_best_no:
                                        btts_best_no = pr
                                        btts_best_no_bk = bk.get('title', '')
                            if 'yes' in row and 'no' in row:
                                btts_bookmakers.append(row)
                btts_margin = None
                if btts_best_yes > 0 and btts_best_no > 0:
                    btts_margin = 1/btts_best_yes + 1/btts_best_no - 1

                # Best odds & arbitrage for h2h
                h2h_best, h2h_best_bk, h2h_margin = calc_best_and_arbitrage(
                    ev.get('bookmakers', []), 'h2h')

                # Best odds & arbitrage for totals
                t_result = calc_best_and_arbitrage(ev.get('bookmakers', []), 'totals')
                totals_best, totals_best_bk, totals_margin = t_result[0], t_result[1], t_result[2]
                if len(t_result) > 3 and t_result[3]:
                    totals_point = t_result[3]

                event_data = {
                    'oddsId': ev.get('id', ''),
                    'homeTeam': home_team,
                    'awayTeam': away_team,
                    'commenceTime': ev.get('commence_time', ''),
                    'matchId': None,
                    'h2h': {
                        'best': h2h_best,
                        'bestBk': h2h_best_bk,
                        'bookmakers': h2h_bookmakers[:10],
                        'margin': h2h_margin,
                        'arb': h2h_margin is not None and h2h_margin < 0,
                    },
                    'totals': {
                        'point': totals_point or 2.5,
                        'best': totals_best,
                        'bestBk': totals_best_bk,
                        'bookmakers': totals_bookmakers[:10],
                        'margin': totals_margin,
                        'arb': totals_margin is not None and totals_margin < 0,
                    },
                    'btts': {
                        'best': {'yes': btts_best_yes, 'no': btts_best_no},
                        'bestBk': {'yes': btts_best_yes_bk, 'no': btts_best_no_bk},
                        'bookmakers': btts_bookmakers[:10],
                        'margin': btts_margin,
                        'arb': btts_margin is not None and btts_margin < 0,
                    }
                }
                events.append(event_data)
            except Exception as ev_err:
                print(f'  skip event in {code}: {ev_err}')
                continue

        try:
            match_odds_to_fixtures(events, league_matches)
            matched = sum(1 for e in events if e['matchId'])
            print(f'  {len(events)} events, {matched} matched to fixtures')

            arbs = sum(1 for e in events if e['h2h']['arb'] or e['totals']['arb'])
            if arbs:
                print(f'  ARBITRAGE FOUND: {arbs} events!')

            odds_data = {
                'code': code,
                'sportKey': sport_key,
                'updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'events': events
            }
            filepath = os.path.join(DATA_DIR, f'odds_{code}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(odds_data, f, ensure_ascii=False)
            print(f'  Saved to {filepath}')
        except Exception as save_err:
            print(f'  Error saving odds for {code}: {save_err}')

        time.sleep(5)

def get_odds_leagues():
    """Determine which leagues to fetch odds for based on current hour."""
    hour = datetime.utcnow().hour
    for h, leagues in ODDS_ROTATION.items():
        if abs(hour - h) <= 1:
            return leagues
    return list(LEAGUE_TO_SPORT.keys())  # manual trigger: fetch all

# ==================== RPL ====================

RPL_NAMES_RU = {
    'Zenit Saint Petersburg': '\u0417\u0435\u043D\u0438\u0442',
    'Zenit St. Petersburg': '\u0417\u0435\u043D\u0438\u0442',
    'Spartak Moscow': '\u0421\u043F\u0430\u0440\u0442\u0430\u043A \u041C\u043E\u0441\u043A\u0432\u0430',
    'CSKA Moscow': '\u0426\u0421\u041A\u0410 \u041C\u043E\u0441\u043A\u0432\u0430',
    'Lokomotiv Moscow': '\u041B\u043E\u043A\u043E\u043C\u043E\u0442\u0438\u0432 \u041C\u043E\u0441\u043A\u0432\u0430',
    'Dynamo Moscow': '\u0414\u0438\u043D\u0430\u043C\u043E \u041C\u043E\u0441\u043A\u0432\u0430',
    'FC Krasnodar': '\u041A\u0440\u0430\u0441\u043D\u043E\u0434\u0430\u0440',
    'Krasnodar': '\u041A\u0440\u0430\u0441\u043D\u043E\u0434\u0430\u0440',
    'Rostov': '\u0420\u043E\u0441\u0442\u043E\u0432',
    'FK Rostov': '\u0420\u043E\u0441\u0442\u043E\u0432',
    'Rubin Kazan': '\u0420\u0443\u0431\u0438\u043D \u041A\u0430\u0437\u0430\u043D\u044C',
    'Akhmat Grozny': '\u0410\u0445\u043C\u0430\u0442 \u0413\u0440\u043E\u0437\u043D\u044B\u0439',
    'Krylya Sovetov Samara': '\u041A\u0440\u044B\u043B\u044C\u044F \u0421\u043E\u0432\u0435\u0442\u043E\u0432',
    'Krylya Sovetov': '\u041A\u0440\u044B\u043B\u044C\u044F \u0421\u043E\u0432\u0435\u0442\u043E\u0432',
    'FC Ural': '\u0423\u0440\u0430\u043B',
    'Ural': '\u0423\u0440\u0430\u043B',
    'Fakel Voronezh': '\u0424\u0430\u043A\u0435\u043B \u0412\u043E\u0440\u043E\u043D\u0435\u0436',
    'FC Orenburg': '\u041E\u0440\u0435\u043D\u0431\u0443\u0440\u0433',
    'Orenburg': '\u041E\u0440\u0435\u043D\u0431\u0443\u0440\u0433',
    'Nizhny Novgorod': '\u041D\u0438\u0436\u043D\u0438\u0439 \u041D\u043E\u0432\u0433\u043E\u0440\u043E\u0434',
    'PFC Sochi': '\u0421\u043E\u0447\u0438',
    'Sochi': '\u0421\u043E\u0447\u0438',
    'Baltika Kaliningrad': '\u0411\u0430\u043B\u0442\u0438\u043A\u0430',
    'Baltika': '\u0411\u0430\u043B\u0442\u0438\u043A\u0430',
    'Pari Nizhny Novgorod': '\u041F\u0430\u0440\u0438 \u041D\u041D',
    'Torpedo Moscow': '\u0422\u043E\u0440\u043F\u0435\u0434\u043E \u041C\u043E\u0441\u043A\u0432\u0430',
    'Khimki': '\u0425\u0438\u043C\u043A\u0438',
    'Arsenal Tula': '\u0410\u0440\u0441\u0435\u043D\u0430\u043B \u0422\u0443\u043B\u0430',
    'Tambov': '\u0422\u0430\u043C\u0431\u043E\u0432',
    'FC Ufa': '\u0423\u0444\u0430',
    'Ufa': '\u0423\u0444\u0430',
    'Akron Togliatti': '\u0410\u043A\u0440\u043E\u043D \u0422\u043E\u043B\u044C\u044F\u0442\u0442\u0438',
    'Dinamo Makhachkala': '\u0414\u0438\u043D\u0430\u043C\u043E \u041C\u0430\u0445\u0430\u0447\u043A\u0430\u043B\u0430',
}

def rpl_ru_name(name):
    return RPL_NAMES_RU.get(name, name)

def fetch_rpl():
    """Fetch Russian Premier League data from API-Football."""
    today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    league_data = {'code': 'RPL', 'updated': today, 'matches': [], 'standings': [], 'finished': []}

    now = datetime.utcnow()
    season = now.year if now.month >= 7 else now.year - 1

    # 1. Upcoming + Live matches
    try:
        # Fetch scheduled (NS) matches — live отключён
        fixtures = api_football_get(f'/fixtures?league=235&season={season}&status=NS&next=20')
        all_fixtures = list(fixtures[:20])
        for f in all_fixtures:
            status_short = f['fixture'].get('status', {}).get('short', 'NS')
            is_live = status_short in ('1H', 'HT', '2H', 'ET', 'P', 'LIVE')
            match_entry = {
                'id': f['fixture']['id'],
                'utcDate': f['fixture']['date'],
                'status': 'IN_PLAY' if is_live else 'SCHEDULED',
                'matchday': f.get('league', {}).get('round', ''),
                'homeTeam': {
                    'id': f['teams']['home']['id'],
                    'name': rpl_ru_name(f['teams']['home']['name']),
                    'crest': f['teams']['home'].get('logo', '')
                },
                'awayTeam': {
                    'id': f['teams']['away']['id'],
                    'name': rpl_ru_name(f['teams']['away']['name']),
                    'crest': f['teams']['away'].get('logo', '')
                }
            }
            if is_live:
                goals = f.get('goals', {})
                match_entry['score'] = {
                    'fullTime': {
                        'home': goals.get('home', 0),
                        'away': goals.get('away', 0)
                    }
                }
                match_entry['minute'] = f['fixture'].get('status', {}).get('elapsed', '')
            league_data['matches'].append(match_entry)
        live_count = sum(1 for m in league_data['matches'] if m.get('status') == 'IN_PLAY')
        print(f'  RPL: {len(league_data["matches"])} matches ({live_count} live)')
    except Exception as e:
        print(f'  RPL: Error fetching matches: {e}')

    time.sleep(10)

    # 2. Standings
    try:
        standings_resp = api_football_get(f'/standings?league=235&season={season}')
        if standings_resp:
            for s_group in standings_resp:
                for table in s_group.get('league', {}).get('standings', []):
                    for row in table:
                        all_stats = row.get('all', {})
                        goals = all_stats.get('goals', {})
                        league_data['standings'].append({
                            'id': row['team']['id'],
                            'name': rpl_ru_name(row['team']['name']),
                            'crest': row['team'].get('logo', ''),
                            'pos': row['rank'],
                            'played': all_stats.get('played', 0),
                            'won': all_stats.get('win', 0),
                            'draw': all_stats.get('draw', 0),
                            'lost': all_stats.get('lose', 0),
                            'gf': goals.get('for', 0),
                            'ga': goals.get('against', 0),
                            'gd': row.get('goalsDiff', 0),
                            'pts': row.get('points', 0),
                            'form': row.get('form')
                        })
        print(f'  RPL: {len(league_data["standings"])} teams in standings')
    except Exception as e:
        print(f'  RPL: Error fetching standings: {e}')

    time.sleep(10)

    # 3. Recent finished matches
    try:
        date_from = (datetime.utcnow() - timedelta(days=60)).strftime('%Y-%m-%d')
        date_to = datetime.utcnow().strftime('%Y-%m-%d')
        finished = api_football_get(f'/fixtures?league=235&season={season}&status=FT&from={date_from}&to={date_to}')
        for f in finished:
            goals = f.get('goals', {})
            league_data['finished'].append({
                'id': f['fixture']['id'],
                'utcDate': f['fixture']['date'],
                'homeTeam': {'id': f['teams']['home']['id'], 'name': rpl_ru_name(f['teams']['home']['name'])},
                'awayTeam': {'id': f['teams']['away']['id'], 'name': rpl_ru_name(f['teams']['away']['name'])},
                'homeGoals': goals.get('home', 0),
                'awayGoals': goals.get('away', 0)
            })
        print(f'  RPL: {len(league_data["finished"])} recent finished matches')
    except Exception as e:
        print(f'  RPL: Error fetching finished: {e}')

    # Save
    filepath = os.path.join(DATA_DIR, 'RPL.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(league_data, f, ensure_ascii=False)
    print(f'  RPL: Saved to {filepath}')

# ==================== MAIN ====================

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    date_from = (datetime.utcnow() - timedelta(days=60)).strftime('%Y-%m-%d')
    date_to = datetime.utcnow().strftime('%Y-%m-%d')

    for code in LEAGUES:
        print(f'Fetching {code}...')
        api_code = code

        league_data = {'code': code, 'updated': today, 'matches': [], 'standings': [], 'finished': []}
        name_fn = lambda x: x

        # 1. Scheduled + Live matches
        try:
            data = api_get(f'/competitions/{api_code}/matches?status=SCHEDULED')
            matches = data.get('matches', [])
            for m in matches[:20]:
                match_entry = {
                    'id': m['id'],
                    'utcDate': m['utcDate'],
                    'status': m.get('status', 'SCHEDULED'),
                    'matchday': m.get('matchday'),
                    'homeTeam': {
                        'id': m['homeTeam']['id'],
                        'name': name_fn(m['homeTeam'].get('shortName') or m['homeTeam']['name']),
                        'crest': m['homeTeam'].get('crest', '')
                    },
                    'awayTeam': {
                        'id': m['awayTeam']['id'],
                        'name': name_fn(m['awayTeam'].get('shortName') or m['awayTeam']['name']),
                        'crest': m['awayTeam'].get('crest', '')
                    }
                }
                # Add score for live matches
                if m.get('status') in ('IN_PLAY', 'PAUSED'):
                    score = m.get('score', {}).get('fullTime', {})
                    match_entry['score'] = {
                        'fullTime': {
                            'home': score.get('home'),
                            'away': score.get('away')
                        }
                    }
                    match_entry['minute'] = m.get('minute', '')
                league_data['matches'].append(match_entry)
            live_count = sum(1 for m in league_data['matches'] if m.get('status') in ('IN_PLAY', 'PAUSED'))
            print(f'  {len(league_data["matches"])} matches ({live_count} live)')
        except Exception as e:
            print(f'  Error fetching matches: {e}')

        time.sleep(10)

        # 2. Standings
        try:
            data = api_get(f'/competitions/{api_code}/standings')
            for s in data.get('standings', []):
                if s['type'] == 'TOTAL':
                    for row in s.get('table', []):
                        league_data['standings'].append({
                            'id': row['team']['id'],
                            'name': name_fn(row['team'].get('shortName') or row['team']['name']),
                            'crest': row['team'].get('crest', ''),
                            'pos': row['position'],
                            'played': row['playedGames'],
                            'won': row['won'],
                            'draw': row['draw'],
                            'lost': row['lost'],
                            'gf': row['goalsFor'],
                            'ga': row['goalsAgainst'],
                            'gd': row['goalDifference'],
                            'pts': row['points'],
                            'form': row.get('form')
                        })
            print(f'  {len(league_data["standings"])} teams in standings')
        except Exception as e:
            print(f'  Error fetching standings: {e}')

        time.sleep(10)

        # 3. Recent finished matches
        try:
            data = api_get(f'/competitions/{api_code}/matches?status=FINISHED&dateFrom={date_from}&dateTo={date_to}')
            for m in data.get('matches', []):
                league_data['finished'].append({
                    'id': m['id'],
                    'utcDate': m['utcDate'],
                    'homeTeam': {'id': m['homeTeam']['id'], 'name': name_fn(m['homeTeam'].get('shortName') or m['homeTeam']['name'])},
                    'awayTeam': {'id': m['awayTeam']['id'], 'name': name_fn(m['awayTeam'].get('shortName') or m['awayTeam']['name'])},
                    'homeGoals': m['score']['fullTime']['home'],
                    'awayGoals': m['score']['fullTime']['away']
                })
            print(f'  {len(league_data["finished"])} recent finished matches')
        except Exception as e:
            print(f'  Error fetching finished: {e}')

        time.sleep(10)

        # Save
        filepath = os.path.join(DATA_DIR, f'{code}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(league_data, f, ensure_ascii=False)
        print(f'  Saved to {filepath}')

    # Fetch odds from The Odds API
    if ODDS_API_KEY:
        leagues = get_odds_leagues()
        print(f'Fetching odds for: {", ".join(leagues)}')
        fetch_odds(leagues)
    else:
        print('ODDS_API_KEY not set, skipping odds')

    print('Done!')

if __name__ == '__main__':
    main()
