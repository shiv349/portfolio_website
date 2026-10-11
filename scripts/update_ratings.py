#!/usr/bin/env python3
"""Fetch public contest ratings and keep the last successful snapshot on failures."""
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'ratings.json'
USERS={'leetcode':'Shiv_the_ultimate','codeforces':'Shiv_the_ultimate','codechef':'good_magic_02'}
HEADERS={'User-Agent':'portfolio-rating-updater/1.0 (GitHub Actions)','Accept':'application/json, text/plain, */*'}
TIMEOUT=20

def num(value):
    if isinstance(value,bool) or value is None: return None
    try:
        n=float(value)
        return n if 0 <= n < 1e9 else None
    except (TypeError,ValueError): return None

def previous_data():
    try: return json.loads(OUT.read_text()).get('ratings',{})
    except Exception: return {}

def leetcode():
    query="query userContestRankingInfo($username: String!) { userContestRanking(username: $username) { attendedContestsCount rating globalRanking } userContestRankingHistory(username: $username) { attended rating contest { title } } }"
    r=requests.post('https://leetcode.com/graphql',json={'query':query,'variables':{'username':USERS['leetcode']}},headers={**HEADERS,'Referer':'https://leetcode.com/'},timeout=TIMEOUT)
    r.raise_for_status(); body=r.json()
    if body.get('errors'): raise RuntimeError('LeetCode GraphQL returned errors')
    data=body.get('data') or {}; ranking=data.get('userContestRanking')
    if not ranking: raise RuntimeError('LeetCode contest profile not found')
    current=num(ranking.get('rating'))
    history=[num(x.get('rating')) for x in (data.get('userContestRankingHistory') or []) if isinstance(x,dict) and x.get('attended')]
    history=[x for x in history if x is not None]
    highest=max(history) if history else current
    if current is None and highest is None: raise RuntimeError('No LeetCode contest rating available')
    return {'username':USERS['leetcode'],'current':current,'highest':highest,'status':'ok','source':'LeetCode public GraphQL'}

def codeforces():
    handle=USERS['codeforces']; r=requests.get('https://codeforces.com/api/user.info',params={'handles':handle},headers=HEADERS,timeout=TIMEOUT)
    r.raise_for_status(); body=r.json()
    if body.get('status')!='OK' or not body.get('result'): raise RuntimeError(body.get('comment','Codeforces account not found'))
    user=body['result'][0]; current=num(user.get('rating')); highest=num(user.get('maxRating'))
    if current is None and highest is None: raise RuntimeError('No rated Codeforces contest yet')
    return {'username':user.get('handle',handle),'current':current,'highest':highest,'rank':user.get('rank'),'maxRank':user.get('maxRank'),'status':'ok','source':'Official Codeforces API'}

def find_number(obj, names):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k.lower().replace('_','') in names:
                n=num(v)
                if n is not None: return n
        for v in obj.values():
            n=find_number(v,names)
            if n is not None:return n
    elif isinstance(obj,list):
        for v in obj:
            n=find_number(v,names)
            if n is not None:return n
    return None


def codechef():
    handle = USERS['codechef']
    url = f'https://codechef-stats.tashif.codes/rating/{handle}'

    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    body = r.json()

    if not body.get('success') or not isinstance(body.get('data'), dict):
        raise RuntimeError('Invalid CodeChef API response')

    data = body['data']

    # Read the explicit summary fields, not the first
    # rating encountered in the contest history.
    current = num(data.get('current'))
    highest = num(data.get('max'))

    # Use history only as a fallback for the highest rating.
    history = data.get('history', [])
    history_ratings = [
        n for item in history
        if isinstance(item, dict)
        if (n := num(item.get('rating'))) is not None
    ]

    if highest is None and history_ratings:
        highest = max(history_ratings)

    if current is None:
        raise RuntimeError('Current CodeChef rating missing from API')

    if highest is None:
        highest = current

    return {
        'username': handle,
        'current': current,
        'highest': max(highest, current),
        'status': 'ok',
        'source': url
    }

FETCH={'leetcode':leetcode,'codeforces':codeforces,'codechef':codechef}
def main():
    old=previous_data(); ratings={}; failed=[]
    for platform,fn in FETCH.items():
        try:
            ratings[platform]=fn(); print(f"[OK] {platform}: {ratings[platform]['current']} / {ratings[platform]['highest']}")
        except Exception as e:
            print(f'[WARN] {platform}: {e}',file=sys.stderr); failed.append(platform); prior=old.get(platform,{})
            has_old=prior.get('current') is not None or prior.get('highest') is not None
            ratings[platform]={'username':USERS[platform],'current':num(prior.get('current')),'highest':num(prior.get('highest')),'status':'stale' if has_old else 'unavailable','source':prior.get('source','unavailable'),'error':str(e)[:240]}
        time.sleep(1)
    OUT.write_text(json.dumps({'updatedAt':datetime.now(timezone.utc).isoformat(timespec='seconds'),'ratings':ratings},indent=2)+'\n')
    if failed: print('Some sources failed; last successful values were preserved where available.')
if __name__=='__main__': main()
