from django.contrib import admin
from .models import CartItem, Category, Invoice, Order, Product, UserProfile


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'low_stock_alert')
    list_editable = ('price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'total_price',
        'status',
        'delivery_partner',
        'created_at',
    )
    list_filter = ('status', 'created_at', 'delivery_partner')
    search_fields = ('id', 'address', 'user__username')
    list_editable = ('status', 'delivery_partner')
    readonly_fields = ('total_price', 'created_at')

    actions = [
        'mark_as_packing',
        'mark_as_out_for_delivery',
        'mark_as_delivered',
    ]

    @admin.action(description='Mark selected orders as Packing')
    def mark_as_packing(self, request, queryset):
        queryset.update(status='Packing')

    @admin.action(description='Mark selected orders as Out for Delivery')
    def mark_as_out_for_delivery(self, request, queryset):
        queryset.update(status='Out for Delivery')

    @admin.action(description='Mark selected orders as Delivered')
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='Delivered')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'order',
        'item_total',
        'delivery_fee',
        'grand_total',
        'created_at',
    )
    search_fields = ('invoice_number', 'order__id')

    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

    actions = ['export_invoices_to_csv']

    @admin.action(description='Export Selected Invoices to CSV')
    def export_invoices_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="invoices_audit.csv"'
        )
        writer = csv.writer(response)

        writer.writerow(
            [
                'Invoice Number',
                'Order ID',
                'Item Total',
                'Delivery Fee',
                'Handling Fee',
                'Grand Total',
                'Created At',
            ]
        )
        for inv in queryset:
            writer.writerow(
                [
                    inv.invoice_number,
                    inv.order.id,
                    inv.item_total,
                    inv.delivery_fee,
                    inv.handling_fee,
                    inv.grand_total,
                    inv.created_at,
                ]
            )
        return response

    readonly_fields = (
        'invoice_number',
        'order',
        'item_total',
        'delivery_fee',
        'handling_fee',
        'grand_total',
        'created_at',
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone', 'is_gold_member', 'created_at')
    search_fields = ('phone', 'name', 'user__username', 'address')
    list_filter = ('is_gold_member', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user_or_session', 'product', 'quantity', 'get_total_price')
    search_fields = ('product__name', 'user__username', 'session_key')
    list_filter = ('quantity',)

    def user_or_session(self, obj):
        return obj.user if obj.user else f'Guest: {obj.session_key[:10]}...'

    user_or_session.short_description = 'User / Session'

    def get_total_price(self, obj):
        return f'₹{obj.total_price()}'

    get_total_price.short_description = 'Total Price'

    actions = ['clear_guest_carts']

    @admin.action(description='Delete All Guest Carts (Cleanup)')
    def clear_guest_carts(self, request, queryset):
        count, _ = queryset.filter(user__isnull=True).delete()
        self.message_user(
            request, f'Successfully cleared {count} guest cart items.'
        )