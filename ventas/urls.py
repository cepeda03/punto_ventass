from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r"clientes", views.ClienteViewSet)
router.register(r"productos", views.ProductoViewSet)
router.register(r"egresos", views.EgresoViewSet)

urlpatterns = [
    
    path("api/", include(router.urls)),
    path("api/api-auth/", include("rest_framework.urls")),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', views.ventas_view, name='Venta'),
    path('clientes/', views.clientes_view, name='Clientes'),
    path('add_cliente/', views.add_cliente_view, name='AddCliente'),
    path('edit_cliente/', views.edit_cliente_view, name='EditCliente'),
    path('delete_cliente/', views.delete_cliente_view, name='DeleteCliente'),

    path('productos/', views.productos_view, name='Productos'),
    path('add_producto/', views.add_producto_view, name='AddProducto'),
    path('edit_producto/', views.edit_producto_view, name='EditProduct'),
    path('delete_product/', views.delete_producto_view, name='DeleteProduct'),

    path('add_venta/', views.add_ventas.as_view(), name='AddVenta'),
    path('delete_venta/', views.delete_venta_view, name='DeleteVenta'),

    path('export/', views.export_pdf_view, name="ExportPDF"),
    path('export/<id>/<iva>/', views.export_pdf_view, name="ExportPDF"),
]
