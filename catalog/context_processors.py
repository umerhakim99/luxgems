from cart.models import Cart


def cart_count(request):
    if not request.user.is_authenticated:
        return {"cart_item_count": 0}
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return {"cart_item_count": 0}
    return {"cart_item_count": cart.total_quantity}
