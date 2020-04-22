"""
JSON API for the Order app
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework import filters

from django.conf.urls import url

from InvenTree.helpers import str2bool

from part.models import Part
from company.models import SupplierPart

from .models import PurchaseOrder, PurchaseOrderLineItem
from .serializers import POSerializer, POLineItemSerializer

from .models import SalesOrder, SalesOrderLineItem
from .serializers import SalesOrderSerializer, SOLineItemSerializer


class POList(generics.ListCreateAPIView):
    """ API endpoint for accessing a list of PurchaseOrder objects

    - GET: Return list of PO objects (with filters)
    - POST: Create a new PurchaseOrder object
    """

    queryset = PurchaseOrder.objects.all()
    serializer_class = POSerializer

    def get_serializer(self, *args, **kwargs):

        try:
            kwargs['supplier_detail'] = str2bool(self.request.query_params.get('supplier_detail', False))
        except AttributeError:
            pass

        # Ensure the request context is passed through
        kwargs['context'] = self.get_serializer_context()

        return self.serializer_class(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):

        queryset = super().get_queryset(*args, **kwargs)

        queryset = queryset.prefetch_related(
            'supplier',
            'lines',
        )

        queryset = POSerializer.annotate_queryset(queryset)

        return queryset

    def filter_queryset(self, queryset):

        # Perform basic filtering
        queryset = super().filter_queryset(queryset)

        params = self.request.query_params

        # Special filtering for 'status' field
        status = params.get('status', None)

        if status is not None:
            # First attempt to filter by integer value
            queryset = queryset.filter(status=status)

        # Attempt to filter by part
        part = params.get('part', None)

        if part is not None:
            try:
                part = Part.objects.get(pk=part)
                queryset = queryset.filter(id__in=[p.id for p in part.purchase_orders()])
            except (Part.DoesNotExist, ValueError):
                pass

        # Attempt to filter by supplier part
        supplier_part = params.get('supplier_part', None)

        if supplier_part is not None:
            try:
                supplier_part = SupplierPart.objects.get(pk=supplier_part)
                queryset = queryset.filter(id__in=[p.id for p in supplier_part.purchase_orders()])
            except (ValueError, SupplierPart.DoesNotExist):
                pass

        return queryset

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filter_fields = [
        'supplier',
    ]

    ordering_fields = [
        'creation_date',
        'reference',
    ]

    ordering = '-creation_date'


class PODetail(generics.RetrieveUpdateAPIView):
    """ API endpoint for detail view of a PurchaseOrder object """

    queryset = PurchaseOrder.objects.all()
    serializer_class = POSerializer

    def get_serializer(self, *args, **kwargs):

        try:
            kwargs['supplier_detail'] = str2bool(self.request.query_params.get('supplier_detail', False))
        except AttributeError:
            pass

        # Ensure the request context is passed through
        kwargs['context'] = self.get_serializer_context()

        return self.serializer_class(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):

        queryset = super().get_queryset(*args, **kwargs)

        queryset = queryset.prefetch_related(
            'supplier',
            'lines',
        )

        queryset = POSerializer.annotate_queryset(queryset)

        return queryset

    permission_classes = [
        permissions.IsAuthenticated
    ]


class POLineItemList(generics.ListCreateAPIView):
    """ API endpoint for accessing a list of POLineItem objects

    - GET: Return a list of PO Line Item objects
    - POST: Create a new PurchaseOrderLineItem object
    """

    queryset = PurchaseOrderLineItem.objects.all()
    serializer_class = POLineItemSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    filter_backends = [
        DjangoFilterBackend,
    ]

    filter_fields = [
        'order',
        'part'
    ]


class POLineItemDetail(generics.RetrieveUpdateAPIView):
    """ API endpoint for detail view of a PurchaseOrderLineItem object """

    queryset = PurchaseOrderLineItem
    serializer_class = POLineItemSerializer

    permission_classes = [
        permissions.IsAuthenticated,
    ]


class SOList(generics.ListCreateAPIView):
    """
    API endpoint for accessing a list of SalesOrder objects.

    - GET: Return list of SO objects (with filters)
    - POST: Create a new SalesOrder
    """

    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer

    def get_serializer(self, *args, **kwargs):

        try:
            kwargs['customer_detail'] = str2bool(self.request.query_params.get('customer_detail', False))
        except AttributeError:
            pass

        # Ensure the context is passed through to the serializer
        kwargs['context'] = self.get_serializer_context()

        return self.serializer_class(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):

        queryset = super().get_queryset(*args, **kwargs)

        queryset = queryset.prefetch_related(
            'customer',
            'lines'
        )

        queryset = SalesOrderSerializer.annotate_queryset(queryset)

        return queryset

    def filter_queryset(self, queryset):
        """
        Perform custom filtering operations on the SalesOrder queryset.
        """

        queryset = super().filter_queryset(queryset)

        params = self.request.query_params

        status = params.get('status', None)

        if status is not None:
            queryset = queryset.filter(status=status)

        # Filter by "Part"
        # Only return SalesOrder which have LineItem referencing the part
        part = params.get('part', None)

        if part is not None:
            try:
                part = Part.objects.get(pk=part)
                queryset = queryset.filter(id__in=[so.id for so in part.sales_orders()])
            except (Part.DoesNotExist, ValueError):
                pass

        return queryset

    permission_classes = [
        permissions.IsAuthenticated
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filter_fields = [
        'customer',
    ]

    ordering_fields = [
        'creation_date',
        'reference'
    ]

    ordering = '-creation_date'


class SODetail(generics.RetrieveUpdateAPIView):
    """
    API endpoint for detail view of a SalesOrder object.
    """

    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer

    def get_serializer(self, *args, **kwargs):

        try:
            kwargs['customer_detail'] = str2bool(self.request.query_params.get('customer_detail', False))
        except AttributeError:
            pass

        kwargs['context'] = self.get_serializer_context()

        return self.serializer_class(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):

        queryset = super().get_queryset(*args, **kwargs)

        queryset = queryset.prefetch_related('customer', 'lines')

        queryset = SalesOrderSerializer.annotate_queryset(queryset)

        return queryset

    permission_classes = [permissions.IsAuthenticated]


class SOLineItemList(generics.ListCreateAPIView):
    """
    API endpoint for accessing a list of SalesOrderLineItem objects.
    """

    queryset = SalesOrderLineItem.objects.all()
    serializer_class = SOLineItemSerializer

    def get_serializer(self, *args, **kwargs):

        try:
            kwargs['part_detail'] = str2bool(self.request.query_params.get('part_detail', False))
        except AttributeError:
            pass

        try:
            kwargs['order_detail'] = str2bool(self.request.query_params.get('order_detail', False))
        except AttributeError:
            pass

        try:
            kwargs['allocations'] = str2bool(self.request.query_params.get('allocations', False))
        except AttributeError:
            pass

        kwargs['context'] = self.get_serializer_context()

        return self.serializer_class(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):

        queryset = super().get_queryset(*args, **kwargs)

        return queryset.prefetch_related(
            'part',
            'part__stock_items',
            'allocations',
            'allocations__item__location',
            'order',
        )

    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend]

    filter_fields = [
        'order',
        'part',
    ]


class SOLineItemDetail(generics.RetrieveUpdateAPIView):
    """ API endpoint for detail view of a SalesOrderLineItem object """

    queryset = SalesOrderLineItem.objects.all()
    serializer_class = SOLineItemSerializer

    permission_classes = [permissions.IsAuthenticated]


order_api_urls = [
    # API endpoints for purchase orders
    url(r'^po/(?P<pk>\d+)/$', PODetail.as_view(), name='api-po-detail'),
    url(r'^po/$', POList.as_view(), name='api-po-list'),

    # API endpoints for purchase order line items
    url(r'^po-line/(?P<pk>\d+)/$', POLineItemDetail.as_view(), name='api-po-line-detail'),
    url(r'^po-line/$', POLineItemList.as_view(), name='api-po-line-list'),

    # API endpoints for sales ordesr
    url(r'^so/(?P<pk>\d+)/$', SODetail.as_view(), name='api-so-detail'),
    url(r'^so/$', SOList.as_view(), name='api-so-list'),

    # API endpoints for sales order line items
    url(r'^so-line/(?P<pk>\d+)/$', SOLineItemDetail.as_view(), name='api-so-line-detail'),
    url(r'^so-line/$', SOLineItemList.as_view(), name='api-so-line-list'),
]
