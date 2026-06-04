from django.dispatch import Signal, receiver
order_ready_signal = Signal()
@receiver(order_ready_signal)
def notify_kitchen(sender, order, **kwargs):
    print(f'[CUISINE] Commande #{order.id} - {order.lines.count()} plat(s) - {order.get_order_type_display()}')
