import requests
import re

s = requests.Session()
r1 = s.get('http://127.0.0.1:8000/')
csrftoken = s.cookies.get('csrftoken')

m = re.search(r'data-product-id="([^"]+)"', r1.text)
if m:
    pid = m.group(1)
    print('Found product:', pid)
    r2 = s.post('http://127.0.0.1:8000/cart_add/', data={'action': 'post', 'product_id': pid, 'qty': 1, 'color': ''}, headers={'X-CSRFToken': csrftoken, 'Referer': 'http://127.0.0.1:8000/'})
    print('Add cookies:', r2.cookies.get_dict())
    print('Session cookies before r3:', s.cookies.get_dict())
    r3 = s.get('http://127.0.0.1:8000/cart/')
    print('Cart status:', r3.status_code)
    print('Cart cookies:', r3.cookies.get_dict())
    if 'Your cart is empty' in r3.text:
        print('CART IS EMPTY!')
    else:
        print('CART HAS ITEMS!')
else:
    print('No product found')
