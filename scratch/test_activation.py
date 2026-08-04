import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

with app.test_client() as client:
    resp = client.get('/activate')
    html = resp.get_data(as_text=True)
    
    # Extract token
    token = html.split('name="csrf_token" value="')[1].split('"')[0]
    print(f"Extracted CSRF Token: {token[:15]}...")
    
    post_resp = client.post('/activate', data={
        'license_key': 'DCMS-A1Y-20270804-HWIDDED882105E9D-7E8A86E962',
        'csrf_token': token
    })
    print(f"POST Status Code: {post_resp.status_code}")
    print(f"Redirect Location: {post_resp.location}")
