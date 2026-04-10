"""Fetches football data from football-data.org and saves as JSON files.
Run by GitHub Actions every 6 hours."""
import urllib.request
import json
import os
import time
from datetime import datetime, timedelta

API_KEY = os.environ.get('FOOTBALL_API_KEY', '')
API_BASE = 'https://api.football-data.org/v4'
LEAGUES = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']
DATA_DIR = 'data'

def api_get(path):
    url = API_BASE + path
    req = urllib.request.Request(url, headers={
        'X-Auth-Token': API_KEY,
        'User-Agent': 'FootballPredictions/1.0'
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    date_from = (datetime.utcnow() - timedelta(days=60)).strftime('%Y-%m-%d')
    date_to = datetime.utcnow().strftime('%Y-%m-%d')

    for code in LEAGUES:
        print(f'Fetching {code}...')
        league_data = {'code': code, 'updated': today, 'matches': [], 'standings': [], 'finished': []}

        # 1. Scheduled matches
        try:
            data = api_get(f'/competitions/{code}/matches?status=SCHEDULED')
            matches = data.get('matches', [])
            # Keep only next 20 matches, strip unnecessary fields
            for m in matches[:20]:
                league_data['matches'].append({
                    'id': m['id'],
                    'utcDate': m['utcDate'],
                    'matchday': m.get('matchday'),
                    'homeTeam': {
                        'id': m['homeTeam']['id'],
                        'name': m['homeTeam'].get('shortName') or m['homeTeam']['name'],
                        'crest': m['homeTeam'].get('crest', '')
                    },
                    'awayTeam': {
                        'id': m['awayTeam']['id'],
                        'name': m['awayTeam'].get('shortName') or m['awayTeam']['name'],
                        'crest': m['awayTeam'].get('crest', '')
                    }
                })
            print(f'  {len(league_data["matches"])} scheduled matches')
        except Exception as e:
            print(f'  Error fetching matches: {e}')

        time.sleep(7)  # Rate limit: 10 req/min

        # 2. Standings
        try:
            data = api_get(f'/competitions/{code}/standings')
            for s in data.get('standings', []):
                if s['type'] == 'TOTAL':
                    for row in s.get('table', []):
                        league_data['standings'].append({
                            'id': row['team']['id'],
                            'name': row['team'].get('shortName') or row['team']['name'],
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

        time.sleep(7)

        # 3. Recent finished matches (for form calculation)
        try:
            data = api_get(f'/competitions/{code}/matches?status=FINISHED&dateFrom={date_from}&dateTo={date_to}')
            for m in data.get('matches', []):
                league_data['finished'].append({
                    'id': m['id'],
                    'utcDate': m['utcDate'],
                    'homeTeam': {'id': m['homeTeam']['id'], 'name': m['homeTeam'].get('shortName') or m['homeTeam']['name']},
                    'awayTeam': {'id': m['awayTeam']['id'], 'name': m['awayTeam'].get('shortName') or m['awayTeam']['name']},
                    'homeGoals': m['score']['fullTime']['home'],
                    'awayGoals': m['score']['fullTime']['away']
                })
            print(f'  {len(league_data["finished"])} recent finished matches')
        except Exception as e:
            print(f'  Error fetching finished: {e}')

        time.sleep(7)

        # Save
        filepath = os.path.join(DATA_DIR, f'{code}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(league_data, f, ensure_ascii=False)
        print(f'  Saved to {filepath}')

    print('Done!')

if __name__ == '__main__':
    main()
