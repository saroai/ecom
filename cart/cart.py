from core.models import Product
from django.core.exceptions import ValidationError

class Cart:
    def __init__(self,request):
        self.session = request.session
        cart = self.session.get("session_key")
        if "session_key" not in request.session:
            cart = self.session["session_key"] = {}
        self.cart = cart

    def add(self, product, qty, color=""):
        product = str(product)
        qty = int(qty)
        color = str(color).strip()
        cart_key = f"{product}_{color}" if color else product

        if type(self.cart.get(list(self.cart.keys())[0])) == int if self.cart else False:
             self.cart.clear()

        if cart_key in self.cart:
            self.cart[cart_key]['qty'] = qty
        else:
            self.cart[cart_key] = {'qty': qty, 'product_id': product, 'color': color}

        self.session.modified = True

    def get_items(self):
        items = []
        valid_keys = []
        for key, data in list(self.cart.items()):
            if not isinstance(data, dict):
                continue
            try:
                product = Product.objects.get(id=data['product_id'])
                items.append({
                    'product': product,
                    'qty': data['qty'],
                    'color': data.get('color', ''),
                    'cart_key': key
                })
                valid_keys.append(key)
            except (Product.DoesNotExist, ValidationError):
                pass
        
        invalid_keys = [k for k in self.cart.keys() if k not in valid_keys]
        for k in invalid_keys:
            self.delete(k)
        return items

    def delete(self, cart_key):
        if cart_key in self.cart:
            del self.cart[cart_key]
            self.session.modified = True

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values() if isinstance(item, dict))

    def total(self):
        total = 0
        for key, data in self.cart.items():
            if not isinstance(data, dict):
                continue
            try:
                product = Product.objects.get(id=data['product_id'])
                if product.is_discount and product.discount_price:
                    product_price = product.discount_price
                else:
                    product_price = product.price or 0
                total += product_price * int(data['qty'])
            except (Product.DoesNotExist, ValidationError):
                pass
        return total
