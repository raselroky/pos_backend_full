from django.shortcuts import render
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView, ListAPIView,
    RetrieveDestroyAPIView,RetrieveAPIView
)
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from .serializers import AdditionalExpenseSerializer,PurchaseSerializer,PurchaseReturnSerializer,PurchaseDetailsSerializer,PurchaseReturnDetailsSerializer,PurchaseHistorySerializer,PurchaseHistoryDetailsSerializer,PurchaseReturnHistorySerializer,PurchaseReturnHistoryDetailsSerializer
from .models import AdditionalExpense,Purchase,PurchaseReturn,PurchaseHistory,PurchaseReturnHistory
from rest_framework.filters import SearchFilter, OrderingFilter
from helpers.invoice import generate_invoice_no,generate_return_no
from helper import MainPagination
from django.db import transaction
from stock.models import Stocks,StockHistory
from products.models import Product,ProductUnit,AttributeVariation,ColorVariation,ProductVariantAttribute,ProductBarcodes
from catalog.models import Brand,Category,SubCategory
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from helpers.barcode import generate_barcode_image
from contacts.models import Contact
from django.db.models import Sum
import uuid


class AdditionalExpenseListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=AdditionalExpense.objects.all()
    serializer_class=AdditionalExpenseSerializer
    
    def create(self, request, *args, **kwargs):
        # Modify request data to include created_by
        data = request.data.copy()  # Create a mutable copy of request.data

        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return AdditionalExpense.objects.all()


class AdditionalExpenseListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=AdditionalExpense.objects.all()
    serializer_class=AdditionalExpenseSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','expense_name','reason']
    pagination_class=MainPagination

    def get_queryset(self):
        return AdditionalExpense.objects.all()


class AdditionalExpenseRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=AdditionalExpense.objects.all()
    serializer_class=AdditionalExpenseSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return AdditionalExpense.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)



####### purchase 

class PurchaseListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None
        # invoice = generate_invoice_no()
        # data['invoice_no'] = invoice

        with transaction.atomic():
            while True:
                inv_pur = generate_invoice_no()
                if not Purchase.objects.filter(invoice_no=inv_pur).exists():
                    break

            data["invoice_no"] = inv_pur


            supplier_id = data.get('supplier')
            if not supplier_id:
                return Response({"error": "Supplier ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                supplier = Contact.objects.get(id=supplier_id)
            except Contact.DoesNotExist:
                return Response({"error": f"Supplier with ID {supplier_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
            purchase_serializer = self.get_serializer(data=data)
            purchase_serializer.is_valid(raise_exception=True)
            purchase = purchase_serializer.save(created_by=request.user,supplier=supplier)

            purchase_history_data = data.get('purchase_history', [])
            for item in purchase_history_data:
                product_variant_id = item.get('product_variant')
                try:
                    product_variant = ProductVariantAttribute.objects.get(id=product_variant_id)
                except ProductVariantAttribute.DoesNotExist:
                    return Response({"error": f"Product Variant with ID {product_variant_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)
                
                
                purchase_quantity = item.get('purchase_quantity', 0)
                good_quantity = item.get('good_quantity', 0)
                demaged_quantity = item.get('demaged_quantity', 0)
                unit_price = item.get('unit_price', 0)
                discount_amount = item.get('discount_amount', 0)
                discount_percent = item.get('discount_percent', 0)
                warranty = item.get('warranty', 0)
                remark = item.get('remark', ""),
                selling_price = item.get('selling_price', 0)
                barcode = item.get('barcode', [])

                if not barcode:
                    barcode = []
                    for _ in range(purchase_quantity):
                        generated_code = f"A-{uuid.uuid4().hex[:5].upper()}"
                        if not ProductBarcodes.objects.filter(barcode=generated_code).exists():
                            barcode.append(generated_code)
                            break
                        
                else:
                    if len(barcode) != purchase_quantity:
                        return Response(
                            {"error": f"Number of barcodes ({len(barcode)}) must match the purchase quantity ({purchase_quantity})."},
                                status=status.HTTP_400_BAD_REQUEST
                                    )
                
                if purchase_quantity!=(good_quantity+demaged_quantity):
                    Response({"error":"purchase qunatity not summation of good quantity and demaged quantity"})

                purchase_history = PurchaseHistory.objects.create(
                    purchase=purchase,
                    product_variant=product_variant,
                    purchase_quantity=purchase_quantity,
                    good_quantity=good_quantity,
                    demaged_quantity=demaged_quantity,
                    unit_price=unit_price,
                    discount_amount=discount_amount,
                    discount_percent=discount_percent,
                    warranty=warranty,
                    remark=remark,
                    
                    created_by=request.user
                )

                stock = Stocks.objects.filter(product_variant=product_variant).first() 

                if stock:
                    stock.total_qty += purchase_quantity
                    stock.available_qty += good_quantity
                    stock.purchase_price = unit_price
                    stock.selling_price = selling_price
                    stock.warranty = warranty
                    stock.discount_percentage = discount_percent
                    stock.remark = remark
                    stock.save()
                else:
                    stock = Stocks.objects.create(
                    product_variant=product_variant,
                    total_qty=purchase_quantity,
                    sold_qty=0,
                    hold_qty=0,
                    available_qty=good_quantity,
                    warranty=warranty,
                    purchase_price=unit_price,
                    selling_price=selling_price,
                    discount_percentage=discount_percent,
                    remark=remark,
                    created_by=request.user 
                    )
                StockHistory.objects.create(
                    stock=stock,
                    quantity=good_quantity,
                    price=unit_price,
                    log_type="Purchase",
                    reference=purchase.id,
                    created_by=request.user
                )
                for barcode_value in barcode:
                    barcode_image = generate_barcode_image(barcode_value)
                    #print(barcode_image,barcode_value)
                    ProductBarcodes.objects.create(
                        inv=inv_pur,
                        product_variant=product_variant,
                        product_status="Purchased",
                        barcode=barcode_value,
                        barcode_image=barcode_image,
                        purchased_at=now(),
                        remarks="Barcode for purchase",
                        created_by=request.user

                    )

            headers = self.get_success_headers(purchase_serializer.data)
            return Response(purchase_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Purchase.objects.all()



class PurchaseListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Purchase.objects.all()
    serializer_class=PurchaseDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','invoice_no','reference']
    pagination_class=MainPagination

    def get_queryset(self):
        return Purchase.objects.all()


class PurchaseRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Purchase.objects.all()
    serializer_class=PurchaseDetailsSerializer
    lookup_field='id'
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        data['updated_by'] = request.user.id

        with transaction.atomic():
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            purchase = serializer.save(updated_by=request.user)

            existing_purchase_history = {ph.product_variant.id: ph for ph in PurchaseHistory.objects.filter(purchase=purchase)}

            purchase_history_data = data.get('purchase_history', [])

            for item in purchase_history_data:
                product_variant_id = item.get('product_variant')
                purchase_quantity = item.get('purchase_quantity', 0)
                good_quantity = item.get('good_quantity', 0)
                demaged_quantity = item.get('demaged_quantity', 0)
                unit_price = item.get('unit_price', 0)
                discount_amount = item.get('discount_amount', 0)
                discount_percent = item.get('discount_percent', 0)
                warranty = item.get('warranty', 0)
                remark = item.get('remark', "")
                selling_price = item.get('selling_price', 0)
                barcode = item.get('barcode', [])

                if len(barcode) != purchase_quantity:
                    return Response(
                        {"error": f"Number of barcodes ({len(barcode)}) must match the good quantity ({purchase_quantity})."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    product_variant = ProductVariantAttribute.objects.get(id=product_variant_id)
                except ProductVariantAttribute.DoesNotExist:
                    return Response({"error": f"Product Variant with ID {product_variant_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

                stock, created = Stocks.objects.get_or_create(product_variant=product_variant, defaults={'total_qty': 0, 'available_qty': 0})

                if product_variant_id in existing_purchase_history:
                    old_purchase_history = existing_purchase_history.pop(product_variant_id)
                    
                    stock.total_qty -= old_purchase_history.purchase_quantity
                    stock.available_qty -= old_purchase_history.good_quantity

                    old_purchase_history.purchase_quantity = purchase_quantity
                    old_purchase_history.good_quantity = good_quantity
                    old_purchase_history.demaged_quantity = demaged_quantity
                    old_purchase_history.unit_price = unit_price
                    old_purchase_history.discount_amount = discount_amount
                    old_purchase_history.discount_percent = discount_percent
                    old_purchase_history.warranty = warranty
                    old_purchase_history.remark = remark
                    old_purchase_history.save()

                else:
                    PurchaseHistory.objects.create(
                        purchase=purchase,
                        product_variant=product_variant,
                        purchase_quantity=purchase_quantity,
                        good_quantity=good_quantity,
                        demaged_quantity=demaged_quantity,
                        unit_price=unit_price,
                        discount_amount=discount_amount,
                        discount_percent=discount_percent,
                        warranty=warranty,
                        remark=remark,
                        created_by=request.user
                    )

                stock.total_qty += purchase_quantity
                stock.available_qty += good_quantity
                stock.purchase_price = unit_price
                stock.selling_price = selling_price
                stock.warranty = warranty
                stock.discount_percentage = discount_percent
                stock.remark = remark
                stock.save()

                StockHistory.objects.create(
                    stock=stock,
                    quantity=good_quantity,
                    price=unit_price,
                    log_type="Purchase Update",
                    reference=purchase.id,
                    created_by=request.user
                )

                existing_barcodes = set(ProductBarcodes.objects.filter(product_variant=product_variant).values_list('barcode', flat=True))
                new_barcodes = set(barcode)

                barcodes_to_delete = existing_barcodes - new_barcodes
                ProductBarcodes.objects.filter(barcode__in=barcodes_to_delete).delete()

                barcodes_to_add = new_barcodes - existing_barcodes
                for barcode_value in barcodes_to_add:
                    barcode_image = generate_barcode_image(barcode_value)
                    ProductBarcodes.objects.create(
                        inv=purchase.invoice_no,
                        product_variant=product_variant,
                        product_status="Purchased",
                        barcode=barcode_value,
                        barcode_image=barcode_image,
                        purchased_at=now(),
                        remarks="Updated barcode for purchase",
                        created_by=request.user
                    )

            for remaining_ph in existing_purchase_history.values():
                stock = Stocks.objects.get(product_variant=remaining_ph.product_variant)
                stock.total_qty -= remaining_ph.purchase_quantity
                stock.available_qty -= remaining_ph.good_quantity
                stock.save()

                remaining_ph.delete()

            return Response(serializer.data, status=status.HTTP_200_OK)


    def get_queryset(self):
        
        return Purchase.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)

class PurchaseRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Purchase.objects.all()
    serializer_class=PurchaseDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return Purchase.objects.all()


####### purchase history 

class PurchaseHistoryListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=PurchaseHistory.objects.all()
    serializer_class=PurchaseHistorySerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy() 

        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None
        invoice=generate_invoice_no()
        data['invoice_no']=invoice

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return PurchaseHistory.objects.all()


class PurchaseHistoryListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseHistory.objects.all()
    serializer_class=PurchaseHistoryDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','product_variant__product__product_name''purchase__id','purchase__invoice_no']
    pagination_class=MainPagination

    def get_queryset(self):
        return PurchaseHistory.objects.all()


class PurchaseHistoryRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseHistory.objects.all()
    serializer_class=PurchaseHistorySerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseHistory.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)

class PurchaseHistoryRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseHistory.objects.all()
    serializer_class=PurchaseHistoryDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseHistory.objects.all()
    



##### purchase return

class PurchaseReturnListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = PurchaseReturn.objects.all()
    serializer_class = PurchaseReturnSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None
        # return_no = generate_return_no()
        # data['return_no'] = return_no
        with transaction.atomic():
            while True:
                return_no = generate_return_no() 
                if not PurchaseReturn.objects.filter(return_no=return_no).exists():
                    break

            data["return_no"] =  return_no

            purchase_return_serializer = self.get_serializer(data=data)
            purchase_return_serializer.is_valid(raise_exception=True)
            purchase_return = purchase_return_serializer.save(created_by=request.user)

            purchase_return_history_data = data.get('purchase_return_history', [])
            total_return_qty = 0
            total_refund_amount = 0

            for item in purchase_return_history_data:
                purchase_history_id = item.get('purchase_history')
                return_qty = item.get('return_qty', 0)
                refund_amount = item.get('refund_amount', 0)
                remark = item.get('remark', "")
                barcode = item.get('barcode', [])
                if len(barcode)>0:
                    if len(barcode) != return_qty:
                        return Response(
                            {"error": f"Number of barcodes ({len(barcode)}) must match return quantity ({return_qty})."},
                            status=status.HTTP_400_BAD_REQUEST
                        )


                try:
                    purchase_history = PurchaseHistory.objects.get(id=purchase_history_id)
                except PurchaseHistory.DoesNotExist:
                    raise ValidationError(f"Purchase history with ID {purchase_history_id} does not exist.")

                purchase_return_historys = PurchaseReturnHistory.objects.create(
                    purchase_return=purchase_return,
                    purchase_history=purchase_history,
                    return_qty=return_qty,
                    refund_amount=refund_amount,
                    remark=remark,
                    created_by=request.user
                )

                total_return_qty += return_qty
                total_refund_amount += refund_amount

                try:
                    stock = Stocks.objects.get(product_variant=purchase_history.product_variant)
                    stock.available_qty -= return_qty
                    
                    stock.save()

                    StockHistory.objects.create(
                        stock=stock,
                        quantity=-return_qty,  
                        price=purchase_history.unit_price,
                        log_type="Return",
                        reference=purchase_return.id,
                        created_by=request.user 
                    )

                except Stocks.DoesNotExist:
                    raise ValidationError(f"Stock for product variant {purchase_history.product_variant.product.product_name} does not exist.")

                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)

                        if barcode_entry.product_variant != purchase_history.product_variant:
                            return Response(
                                {"error": f"Barcode {barcode_value} does not belong to the specified product."},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                        barcode_entry.product_status = "Purchase Return"
                        barcode_entry.purchase_return_at = now()
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        return Response(
                            {"error": f"Barcode {barcode_value} does not exist in records."},
                            status=status.HTTP_400_BAD_REQUEST
                        )


            purchase_return.total_return_qty = total_return_qty
            purchase_return.total_refund_amount = total_refund_amount
            purchase_return.save()

            # purchase_id = purchase_return.purchase.id 
            
            # try:
            #     purchase = Purchase.objects.get(id=purchase_id)
            #     purchase.total_amount -= total_refund_amount
            #     purchase.sub_total -= total_refund_amount
            #     purchase.grand_total-=total_refund_amount
            #     if purchase.paid_amount>0:
            #         purchase.paid_amount-=total_refund_amount
            #     if purchase.due_amount>0:
            #         purchase.due_amount-=total_refund_amount
            #     purchase.save() 

            # except purchase.DoesNotExist:
            #     raise ValidationError(f"Purhcase with ID {purchase_id} does not exist.")
            
            
            # purchase_history.purchase_quantity-=total_return_qty
            # purchase_history.good_quantity-=total_return_qty
            purchase_history.save()
            
            headers = self.get_success_headers(purchase_return_serializer.data)
            return Response(purchase_return_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return PurchaseReturn.objects.all()


class PurchaseReturnListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturn.objects.all()
    serializer_class=PurchaseReturnDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','purchase__supplier__business_name','return_date','total_refund_amount','total_return_qty','purchase__invoice_no','purchase__supplier__mobile','purchase__supplier__email','return_no']
    pagination_class=MainPagination

    def get_queryset(self):
        return PurchaseReturn.objects.all()


class PurchaseReturnRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseReturn.objects.all()
    serializer_class = PurchaseReturnDetailsSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        with transaction.atomic():
            purchase_return_serializer = self.get_serializer(instance, data=data, partial=True)
            purchase_return_serializer.is_valid(raise_exception=True)
            purchase_return = purchase_return_serializer.save(updated_by=request.user)

            purchase_return_history = data.get('purchase_return_history', [])
            total_return_qty = 0
            total_refund_amount = 0

            # Get existing return history items
            existing_return_history_ids = set(instance.purchase_return_history.values_list('id', flat=True))
            new_return_history_ids = set()

            for item in purchase_return_history:
                purchase_history_id = item.get('purchase_history')
                return_qty = item.get('return_qty', 0)
                refund_amount = item.get('refund_amount', 0)
                remark = item.get('remark', "")
                barcode = item.get('barcode', [])

                if len(barcode) != return_qty:
                    return Response(
                        {"error": f"Number of barcodes ({len(barcode)}) must match return quantity ({return_qty})."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    purchase_history = PurchaseHistory.objects.get(id=purchase_history_id)
                except PurchaseHistory.DoesNotExist:
                    return Response(
                        {"error": f"Purchase history with ID {purchase_history_id} does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Check if the return history already exists
                purchase_return_history, created = PurchaseReturnHistory.objects.update_or_create(
                    purchase_return=purchase_return,
                    purchase_history=purchase_history,
                    defaults={
                        "return_qty": return_qty,
                        "refund_amount": refund_amount,
                        "remark": remark,
                        "updated_by": request.user
                    }
                )
                new_return_history_ids.add(purchase_return_history.id)

                total_return_qty += return_qty
                total_refund_amount += refund_amount

                try:
                    stock = Stocks.objects.get(product_variant=purchase_history.product_variant)
                    stock.available_qty -= return_qty
                    stock.sold_qty -= return_qty
                    stock.save()

                    StockHistory.objects.create(
                        stock=stock,
                        quantity=-return_qty,
                        price=purchase_history.unit_price,
                        log_type="Return",
                        reference=purchase_return.id,
                        created_by=request.user
                    )
                except Stocks.DoesNotExist:
                    return Response(
                        {"error": f"Stock for product variant {purchase_history.product_variant.product.product_name} does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)

                        if barcode_entry.product_variant != purchase_history.product_variant:
                            return Response(
                                {"error": f"Barcode {barcode_value} does not belong to the specified product."},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                        barcode_entry.product_status = "Purchase Return"
                        barcode_entry.purchase_return_at = now()
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        return Response(
                            {"error": f"Barcode {barcode_value} does not exist in records."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

            # Remove deleted return history records
            to_delete = existing_return_history_ids - new_return_history_ids
            PurchaseReturnHistory.objects.filter(id__in=to_delete).delete()

            # Update total values in PurchaseReturn
            purchase_return.total_return_qty = total_return_qty
            purchase_return.total_refund_amount = total_refund_amount
            purchase_return.save()

            return Response(purchase_return_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)


class PurchaseReturnRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturn.objects.all()
    serializer_class=PurchaseReturnDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseReturn.objects.all()



###### purchase return history

class PurchaseReturnHistoryListCreateAPIView(ListCreateAPIView):
    permission_classes=(IsAuthenticated,)
    queryset=PurchaseReturnHistory.objects.all()
    serializer_class=PurchaseReturnHistorySerializer
    
    def create(self, request, *args, **kwargs):
        # Modify request data to include created_by
        data = request.data.copy()  # Create a mutable copy of request.data

        data['created_by'] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return PurchaseReturnHistory.objects.all()


class PurchaseReturnHistoryListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturnHistory.objects.all()
    serializer_class=PurchaseReturnHistoryDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','purchase_return__purchase__invoice_no','purchase_return__purchase__supplier__business_name','return_qty','refund_amount','purchase_return__purchase__supplier__email','purchase_return__purchase__supplier__mobile','refund_amount','purchase_history__product__product_name','purchase_history__product__sku','purchase_history__product__country','purchase_history__product__brand__brand_name','purchase_history__product__category__category_name','purchase_history__color__color_name','purchase_history__size__name','purchase_history__size__values','purchase_history__purchase__invoice_no']
    pagination_class=MainPagination
    
    def get_queryset(self):
        return PurchaseReturnHistory.objects.all()


class PurchaseReturnHistoryRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturnHistory.objects.all()
    serializer_class=PurchaseReturnHistorySerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseReturnHistory.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)

class PurchaseReturnHistoryRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=PurchaseReturnHistory.objects.all()
    serializer_class=PurchaseReturnHistoryDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        
        return PurchaseReturnHistory.objects.all()



class PurchaseReturnHistoryList(APIView):
    def post(self,request):
        id=request.data.get('id')

        purchase=Purchase.objects.filter(id=id)
        if purchase:
            purchase_get=Purchase.objects.filter(id=id).first()
            inv=purchase_get.invoice_no
            purchase_history=PurchaseHistory.objects.filter(purchase__invoice_no=inv)
            #print(purchase_history)
            purchase_history_data=PurchaseHistoryDetailsSerializer(purchase_history,many=True)

            return Response(purchase_history_data.data)
        return Response({"message":"data not found!"})