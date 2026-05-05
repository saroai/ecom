from core.models import Product

class Cart:

    def __init__(self,request):
        self.session = request.session

        cart = self.session.get("session_key")

        if "session_key" not in request.session:
            cart = self.session["session_key"] = {}


        self.cart = cart

    def add(self,product,qty):
        product = str(product)
        qty = int(qty)

        if product in self.cart:
            self.cart[product] = qty
        else:
            self.cart[product] = qty

        self.session.modified = True


    def products(self):

        all_products = {}
        try:
            for key,val in self.cart.items():
                product = Product.objects.get(id=key)
                all_products[product] = val
        except Exception as e:
            del self.session["session_key"]
            self.session.modified = True
        return all_products

    def delete(self,product_id):

        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True

    def __len__(self):
         return sum(self.cart.values())

    def total(self):
        total = 0
        for pro_id,qty in self.cart.items():
            try:
                product = Product.objects.get(id=pro_id)
                if product.is_discount and product.discount_price:
                    product_price = product.discount_price
                else:
                    product_price = product.price or 0
                total += product_price * int(qty)
            except Product.DoesNotExist:
                pass


        return total











