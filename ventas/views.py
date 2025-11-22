from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.conf import settings
import os
import json

from .models import Cliente, Egreso, Producto, ProductosEgreso
from .forms import (
    AddClienteForm, EditarClienteForm,
    AddProductoForm, EditarProductoForm
)


from rest_framework import viewsets, permissions
from .serializers import ClienteSerializer, ProductoSerializer, EgresoSerializer



class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by("id")
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by("id")
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]


class EgresoViewSet(viewsets.ModelViewSet):
    queryset = Egreso.objects.all().order_by("id")
    serializer_class = EgresoSerializer
    permission_classes = [permissions.IsAuthenticated]



def ventas_view(request):
    ventas = Egreso.objects.all()
    num_ventas = ventas.count()
    context = {
        "ventas": ventas,
        "num_ventas": num_ventas
    }
    return render(request, "ventas.html", context)


def clientes_view(request):
    clientes = Cliente.objects.all()
    form_personal = AddClienteForm()
    form_editar = EditarClienteForm()
    context = {
        "clientes": clientes,
        "form_personal": form_personal,
        "form_editar": form_editar,
    }
    return render(request, "clientes.html", context)


def add_cliente_view(request):
    if request.method == "POST":
        form = AddClienteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
            except Exception:
                messages.error(request, "Error al guardar el cliente")
        else:
            messages.error(request, "Formulario inválido")
    return redirect("Clientes")


def edit_cliente_view(request):
    if request.method == "POST":
        cliente = Cliente.objects.get(pk=request.POST.get("id_personal_editar"))
        form = EditarClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, "Formulario inválido")
    return redirect("Clientes")


def delete_cliente_view(request):
    if request.method == "POST":
        cliente = Cliente.objects.get(pk=request.POST.get("id_personal_eliminar"))
        cliente.delete()
    return redirect("Clientes")


def productos_view(request):
    productos = Producto.objects.all()
    form_add = AddProductoForm()
    form_editar = EditarProductoForm()
    context = {
        "productos": productos,
        "form_add": form_add,
        "form_editar": form_editar
    }
    return render(request, "productos.html", context)


def add_producto_view(request):
    if request.method == "POST":
        form = AddProductoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
            except Exception:
                messages.error(request, "Error al guardar el producto")
        else:
            messages.error(request, "Formulario inválido")
    return redirect("Productos")


def edit_producto_view(request):
    if request.method == "POST":
        producto = Producto.objects.get(pk=request.POST.get("id_producto_editar"))
        form = EditarProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, "Formulario inválido")
    return redirect("Productos")


def delete_producto_view(request):
    if request.method == "POST":
        producto = Producto.objects.get(pk=request.POST.get("id_producto_eliminar"))
        producto.delete()
    return redirect("Productos")


def delete_venta_view(request):
    if request.method == "POST":
        venta = Egreso.objects.get(pk=request.POST.get("id_producto_eliminar"))
        venta.delete()
    return redirect("Venta")


class add_ventas(ListView):
    template_name = "add_ventas.html"
    model = Egreso

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST.get("action")

            if action == "autocomplete":
                data = []
                term = request.POST.get("term", "")
                for i in Producto.objects.filter(descripcion__icontains=term)[0:10]:
                    item = i.toJSON()
                    item["value"] = i.descripcion
                    data.append(item)

            elif action == "save":
                total_pagado = (
                    float(request.POST.get("efectivo", 0)) +
                    float(request.POST.get("tarjeta", 0)) +
                    float(request.POST.get("transferencia", 0)) +
                    float(request.POST.get("vales", 0)) +
                    float(request.POST.get("otro", 0))
                )

                fecha = request.POST.get("fecha")
                id_cliente = request.POST.get("id_cliente")
                cliente_obj = Cliente.objects.get(pk=int(id_cliente))

                datos = json.loads(request.POST.get("verts", "{}"))
                total_venta = float(datos.get("total", 0))
                productos = datos.get("productos", [])

                ticket = int(request.POST.get("ticket", 0)) == 1
                desglosar_iva = int(request.POST.get("desglosar", 0)) == 1
                comentarios = request.POST.get("comentarios", "")

                nueva_venta = Egreso.objects.create(
                    fecha_pedido=fecha,
                    cliente=cliente_obj,
                    total=total_venta,
                    pagado=total_pagado,
                    comentarios=comentarios,
                    ticket=ticket,
                    desglosar=desglosar_iva,
                )

                for p in productos:
                    prod = Producto.objects.get(pk=int(p["id"]))
                    ProductosEgreso.objects.create(
                        egreso=nueva_venta,
                        producto=prod,
                        cantidad=float(p.get("cantidad", 1)),
                        precio=float(p.get("precio", prod.precio)),
                        subtotal=float(p.get("subtotal", 0)),
                        iva=float(p.get("iva", 0)),
                    )

                data["ok"] = True
                data["id_venta"] = nueva_venta.id

            else:
                data["error"] = "Acción no válida"

        except Exception as e:
            data["error"] = str(e)

        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos_lista"] = Producto.objects.all()
        context["clientes_lista"] = Cliente.objects.all()
        return context


def export_pdf_view(request, id=None, iva=None):
    if id is None or iva is None:
        return redirect("Venta")

    template = get_template("ticket.html")
    subtotal = 0
    iva_suma = 0

    venta = Egreso.objects.get(pk=float(id))
    datos = ProductosEgreso.objects.filter(egreso=venta)

    for i in datos:
        subtotal += float(i.subtotal)
        iva_suma += float(i.iva)

    empresa = "Mi empresa S.A. De C.V"
    context = {
        "num_ticket": id,
        "iva": iva,
        "fecha": venta.fecha_pedido,
        "cliente": venta.cliente.nombre,
        "items": datos,
        "total": venta.total,
        "empresa": empresa,
        "comentarios": venta.comentarios,
        "subtotal": subtotal,
        "iva_suma": iva_suma,
    }

    html_template = template.render(context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; ticket.pdf"

    
    response.write(html_template)
    return response
