from pyexpat.errors import messages
from django.shortcuts import render, redirect
from .models import Cliente, Egreso, Producto, Egreso, ProductosEgreso
from .forms import AddClienteForm , EditarClienteForm, AddProductoForm, EditarProductoForm
from django.contrib import messages
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse
#from weasyprint.text.fonts import FontConfiguration
from django.template.loader import get_template
#from weasyprint import HTML, CSS
from django.conf import settings
import os
import json



# Create your views here.

def ventas_view(request):
    ventas = Egreso.objects.all()
    num_ventas = len(ventas)
    context = {
        'ventas': ventas, 
        'num_ventas': num_ventas
    }
    return render(request, 'ventas.html', context)

def clientes_view(request):
    clientes = Cliente.objects.all()
    form_personal = AddClienteForm()
    form_editar = EditarClienteForm()

    context = {
        'clientes': clientes,
        'form_personal': form_personal, 
        'form_editar': form_editar,
       
    }
    return render(request, 'clientes.html', context)


def add_cliente_view(request):
    #print("Guardar cliente")
    if request.POST:
        form = AddClienteForm(request.POST, request.FILES)
        if form.is_valid:
            try: 
                form.save()
            except:
                messages(request, "Error al guardar el cliente")
                return redirect('Clientes')
    return redirect('Clientes')

def edit_cliente_view(request):
    if request.POST:
        cliente = Cliente.objects.get(pk=request.POST.get('id_personal_editar'))
        form = EditarClienteForm(
            request.POST, request.FILES, instance= cliente)
        if form.is_valid():
            form.save()
    return redirect('Clientes')

def delete_cliente_view(request):
    if request.POST:
        cliente = Cliente.objects.get(pk=request.POST.get('id_personal_eliminar'))
        cliente.delete()

    return redirect('Clientes')

def delete_venta_view(request):
    if request.POST:
        cliente = Egreso.objects.get(pk=request.POST.get('id_producto_eliminar'))
        cliente.delete()

    return redirect('Venta')

def productos_view(request):
    """
    clientes = Cliente.objects.all()
    form_editar = EditarClienteForm()
    """
    productos = Producto.objects.all()
    form_add = AddProductoForm()
    form_editar = EditarProductoForm()

    context = {
       'productos': productos, 
       'form_add': form_add, 
       'form_editar': form_editar

    }
    return render(request, 'productos.html', context)

def add_producto_view(request):
    #print("Guardar cliente")
    if request.POST:
        form = AddProductoForm(request.POST, request.FILES)
        if form.is_valid():
            try: 
                form.save()
            except:
                messages(request, "Error al guardar el productos")
                return redirect('Productos')

    return redirect('Productos')


def edit_producto_view(request):
    print("Hola")
    if request.POST:
        producto = Producto.objects.get(pk=request.POST.get('id_producto_editar'))
        form = EditarProductoForm(
            request.POST, request.FILES, instance= producto)
        if form.is_valid():
            form.save()
    return redirect('Productos')

def delete_producto_view(request):
    if request.POST:
        product = Producto.objects.get(pk=request.POST.get('id_producto_eliminar'))
        product.delete()

    return redirect('Productos')


class add_ventas(ListView):
    template_name = 'add_ventas.html'
    model = Egreso

    def dispatch(self,request,*args,**kwargs):
        return super().dispatch(request, *args, **kwargs)
    """
    def get_queryset(self):
        return ProductosPreventivo.objects.filter(
            preventivo=self.kwargs['id']
        )
    """
    def post(self, request,*ars, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'autocomplete':
                data = []
                for i in Producto.objects.filter(descripcion__icontains=request.POST["term"])[0:10]:
                    item = i.toJSON()
                    item['value'] = i.descripcion
                    data.append(item)
            elif action == 'save': 
                #Validamos y recuperamos
                #print("Hello worl estamos en save") 
                total_pagado = float(request.POST["efectivo"]) + float(request.POST["tarjeta"]) + float(request.POST["transferencia"]) + float(request.POST["vales"]) + float(request.POST["otro"])
                #print(total_pagado)
                fecha = request.POST["fecha"]
                #print(fecha)
                id_cliente = request.POST["id_cliente"]
                #print(id_cliente)
                cliente_obj = Cliente.objects.get(pk=int(id_cliente))
                #print(cliente_obj)
                datos = json.loads(request.POST["verts"])
                total_venta = float(datos["total"])
                ticket_num = int(request.POST["ticket"])
                if ticket_num == 1:
                    ticket = True
                else:
                    ticket = False
                desglosar_iva_num =int(request.POST["desglosar"])
                if desglosar_iva_num ==  0:
                    desglosar_iva = False
                elif desglosar_iva_num == 1: 
                    desglosar_iva =True
                
                comentarios = request.POST["comentarios"]
                # Guardar y venta y productos
                nueva_venta = Egreso(fecha_pedido = fecha, cliente=cliente_obj, total= total_venta, pagado = total_pagado,comentarios=comentarios, ticket=ticket, desglosar=desglosar_iva)
                nueva_venta.save()

                #Agregar productos
               

            else:
                data['error'] = "Ha ocurrido un error"
        except Exception as e:
            data['error'] = str(e)
        
        

        return JsonResponse(data,safe=False)
    
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        context["productos_lista"] = Producto.objects.all()
        context["clientes_lista"] = Cliente.objects.all()

        return context


def export_pdf_view(request, id, iva):
    #print(id)
    template = get_template("ticket.html")
    #print(id)
    subtotal = 0 
    iva_suma = 0 

    venta = Egreso.objects.get(pk=float(id))
    datos = ProductosEgreso.objects.filter(egreso=venta)
    for i in datos:
        subtotal = subtotal + float(i.subtotal)
        iva_suma = iva_suma + float(i.iva)

    empresa = "Mi empresa S.A. De C.V"
    context ={
        'num_ticket': id,
        'iva': iva,
        'fecha': venta.fecha_pedido,
        'cliente': venta.cliente.nombre,
        'items': datos, 
        'total': venta.total, 
        'empresa': empresa,
        'comentarios': venta.comentarios,
        'subtotal': subtotal,
        'iva_suma': iva_suma,
    }
    html_template = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; ticket.pdf"
    css_url = os.path.join(settings.BASE_DIR,'index\static\index\css/bootstrap.min.css')

   
