from django.shortcuts import render
from .serializers import SaleSerializer,SaleHistorySerializer,SaleReturnSerializer,SaleReturnHistorySerializer,SaleReturnDetailsSerializer,SaleDetailsSerializer,QuotationSerializer,QuotationHistorySerializer,QuotationDetailsSerializer
from .models import Sale,SaleHistory,SaleReturn,SaleReturnHistory,Quotation,QuotationHistory
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.filters import SearchFilter, OrderingFilter
from helpers.invoice import generate_invoice_no,generate_return_no
from helper import MainPagination
from django.db import transaction
from stock.models import Stocks,StockHistory
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from helpers.barcode import generate_barcode_image
from products.models import ProductBarcodes
from django.db.models import Sum
from contacts.models import Contact
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.signals import send_notification
from setting.models import InvoiceSetting



class SaleListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.pop("invoice_no", None)
        data["created_by"] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None
        
        # invoice = generate_invoice_no()
        # data['invoice_no'] = invoice
        with transaction.atomic():
            while True:
                inv_sold = generate_invoice_no()
                if not Sale.objects.filter(invoice_no=inv_sold).exists():
                    break
            
            
            prefixs = InvoiceSetting.objects.filter(assign_branch=data['branch'],is_active=True)
            if prefixs:
                invoicesetting2=InvoiceSetting.objects.filter(assign_branch=data['branch'],is_active=True).first()
                data["invoice_no"] =str(invoicesetting2.prefix)+'-'+inv_sold
            else:
                data["invoice_no"] = inv_sold

            customer_id = data.get("customer")
            customer = None
            if customer_id:
                try:
                    customer = Contact.objects.get(id=customer_id)
                except Contact.DoesNotExist:
                    raise ValidationError(
                        {"error": f"Customer with ID {customer_id} does not exist."})


            sale_history_data = data.get("sale_history", [])
            if not sale_history_data:
                raise ValidationError(
                    {"error": "At least one product must be included in the sale."})
                    

            sale_serializer = self.get_serializer(data=data)
            sale_serializer.is_valid(raise_exception=True)
            sale = sale_serializer.save(created_by=request.user, customer=customer)

            for item in sale_history_data:
                product_id = item.get("product_variant")
                quantity = item.get("quantity", 0)
                discount_amount = item.get("discount_amount", 0)
                discount_percent = item.get("discount_percent", 0)
                discount_type = item.get("discount_type", "Select Type").strip()
                vat_amounts=item.get("vat_amounts",0)
                total_amount_iv=item.get("total_amount_iv",0)
                total_amount_wv=item.get("total_amount_wv",0)
                warranty = item.get("warranty", 0)
                remark = item.get("remark", "")
                barcode = item.get("barcode", [])
                
                if barcode:
                    if len(barcode) != quantity:
                        raise ValidationError(
                            {"error": f"Number of barcodes ({len(barcode)}) must match the quantity ({quantity})."})
                            
                else:
                    barcode_qs = ProductBarcodes.objects.filter(product_variant__id=product_id,product_status='Purchased').values_list('barcode', flat=True)
                    barcode=list(barcode_qs[:quantity])

                    if len(barcode) < quantity:
                        raise ValidationError(
                            {"error": f"Not enough available barcodes for this product (required: {quantity}, found: {len(barcode)})."})
                                

                try:
                    stock = Stocks.objects.get(product_variant__id=product_id)
                except Stocks.DoesNotExist:
                    raise ValidationError(
                        {"error": f"Stock with product variant ID {product_id} does not exist."})
                        

                if stock.available_qty < quantity:
                    raise ValidationError(
                        {"error": f"Not enough stock available for product {stock.product_variant.product.product_name}."})
                        

                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)
                        if barcode_entry.product_variant != stock.product_variant:
                            raise ValidationError(
                                {"error": f"Barcode {barcode_value} does not belong to the specified product."})
                                

                        barcode_entry.inv_sold = data["invoice_no"]
                        barcode_entry.product_status = "Sold"
                        barcode_entry.sold_at = now()
                        barcode_entry.remarks = "Sold via sales transaction"
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        raise ValidationError(
                            {"error": f"Barcode {barcode_value} does not exist in records."})
                            

                SaleHistory.objects.create(
                    sale=sale,
                    product_variant=stock,
                    quantity=quantity,
                    unit_price=stock.purchase_price,
                    selling_price=stock.selling_price,
                    discount_amount=discount_amount,
                    discount_percent=discount_percent,
                    discount_type=discount_type,
                    vat_amounts=vat_amounts,
                    total_amount_iv=total_amount_iv,
                    total_amount_wv=total_amount_wv,
                    warranty=warranty,
                    remark=remark,
                    created_by=request.user
                )

                stock.sold_qty += quantity
                stock.available_qty -= quantity
                stock.save()

               
                StockHistory.objects.create(
                    stock=stock,
                    quantity=-quantity,
                    price=stock.selling_price,
                    log_type="Sale",
                    reference=sale.id,
                    created_by=request.user
                )

        sale.save()
        headers = self.get_success_headers(sale_serializer.data)
        return Response(sale_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SaleListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Sale.objects.all()
    serializer_class=SaleDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','customer__business_name','customer__email','customer__mobile','customer__mobile2','customer__conact_id','customer__owner_name','invoice_no']
    #pagination_class=MainPagination

    def get_queryset(self):
        queryset = Sale.objects.all()
        
        

        return queryset


class SaleRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Sale.objects.all()
    serializer_class = SaleDetailsSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        with transaction.atomic():
            # Update the sale record
            sale_serializer = self.get_serializer(instance, data=data, partial=True)
            sale_serializer.is_valid(raise_exception=True)
            sale = sale_serializer.save(updated_by=request.user)

            sale_history_data = data.get('sale_history', [])
            total_sale_amount = 0
            total_discount_amount = 0

            existing_sale_history_ids = set(instance.sale_history.values_list('id', flat=True))
            new_sale_history_ids = set()

            for item in sale_history_data:
                product_id = item.get('product_variant')
                quantity = item.get('quantity', 0)
                discount_amount = item.get('discount_amount', 0)
                discount_percent = item.get('discount_percent', 0)
                discount_type = item.get("discount_type", "Select Type").strip()
                warranty = item.get('warranty', 0)
                remark = item.get('remark', "")
                barcode = item.get('barcode', [])

                if len(barcode) != quantity:
                    raise ValidationError(
                        {"error": f"Number of barcodes ({len(barcode)}) must match the quantity ({quantity})."})
                        

                try:
                    stock = Stocks.objects.get(product_variant__id=product_id)
                except Stocks.DoesNotExist:
                    raise ValidationError(
                        {"error": f"Stock with product variant ID {product_id} does not exist."})
                        

                # Get previous sale history entry (if exists)
                sale_history, created = SaleHistory.objects.get_or_create(
                    sale=sale,
                    product_variant=stock,
                    defaults={
                        "quantity": quantity,
                        "unit_price": stock.purchase_price,
                        "selling_price": stock.selling_price,
                        "discount_amount": discount_amount,
                        "discount_percent": discount_percent,
                        "discount_type":discount_type,
                        "warranty": warranty,
                        "remark": remark,
                        "updated_by": request.user
                    }
                )

                new_sale_history_ids.add(sale_history.id)

                # Calculate stock adjustments
                previous_quantity = sale_history.quantity
                if previous_quantity != quantity:
                    stock.available_qty += previous_quantity  # Revert old quantity
                    stock.available_qty -= quantity  # Deduct new quantity
                    stock.sold_qty -= previous_quantity
                    stock.sold_qty += quantity
                    stock.save()

                    StockHistory.objects.create(
                        stock=stock,
                        quantity=-quantity,
                        price=stock.selling_price,
                        log_type="Sale Update",
                        reference=sale.id,
                        created_by=request.user
                    )

                # Update sale history record
                sale_history.quantity = quantity
                sale_history.unit_price = stock.purchase_price
                sale_history.selling_price = stock.selling_price
                sale_history.discount_amount = discount_amount
                sale_history.discount_percent = discount_percent
                sale_history.discount_type=discount_type
                sale_history.warranty = warranty
                sale_history.remark = remark
                sale_history.updated_by = request.user
                sale_history.save()

                

                # Handle barcode updates
                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)

                        if barcode_entry.product_variant != stock.product_variant:
                            raise ValidationError(
                                {"error": f"Barcode {barcode_value} does not belong to the specified product."})
                                
                        barcode_entry.inv_sold=sale.invoice_no
                        barcode_entry.product_status = "Sold"
                        barcode_entry.sold_at = now()
                        barcode_entry.remarks = "Updated sale transaction"
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        raise ValidationError(
                            {"error": f"Barcode {barcode_value} does not exist in records."})
                            

            # Remove deleted sale history records
            to_delete = existing_sale_history_ids - new_sale_history_ids
            SaleHistory.objects.filter(id__in=to_delete).delete()

            # Update total values in Sale
            
            sale.save()

            return Response(sale_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)



class SaleRetrieveAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Sale.objects.all()
    serializer_class=SaleDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        #print('views')
        return Sale.objects.all()


### salereturn 



class SaleReturnListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = SaleReturn.objects.all()
    serializer_class = SaleReturnSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy() 
        data['created_by'] = request.user.id 
        data['branch'] = request.user.branch.id if request.user.branch else None
        # return_no = generate_return_no() 
        # data['return_no'] = return_no

        with transaction.atomic():
            
            while True:
                return_no = generate_return_no()+'s'
                if not SaleReturn.objects.filter(return_no=return_no).exists():
                    break

            prefixs = InvoiceSetting.objects.filter(assign_branch=data['branch'],is_active=True)
            if prefixs:
                invoicesetting2=InvoiceSetting.objects.filter(assign_branch=data['branch'],is_active=True).first()
                data["return_no"] =str(invoicesetting2.prefix)+'-'+return_no
                
            else:
                data["return_no"] = return_no


            total_return_qty = 0
            total_refund_amount = 0

            sale_return_history_data = data.get('sale_return_history', [])
            for item in sale_return_history_data:
                sale_history_id = item.get('sale_history')
                return_qty = item.get('return_qty', 0)
                refund_amount = item.get('refund_amount', 0)
                remark = item.get('remark', "")
                barcode = item.get('barcode', [])
                if len(barcode) != return_qty:
                    return Response({"error": f"Number of barcodes ({len(barcode)}) must match the good quantity ({return_qty})."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    sale_history = SaleHistory.objects.get(id=sale_history_id)
                except SaleHistory.DoesNotExist:
                    raise ValidationError(f"Sale history with ID {sale_history_id} does not exist.")
                
                if return_qty > sale_history.quantity:
                    return Response(
                        {"error": f"Cannot return more than the sold quantity for sale history ID {sale_history_id}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)

                        if barcode_entry.product_variant!= sale_history.product_variant.product_variant:
                            return Response(
                                {"error": f"Barcode {barcode_value} does not belong to the returned product."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        
                        barcode_entry.inv_return_no=data["return_no"]
                        barcode_entry.product_status = "Sales Return"
                        barcode_entry.sold_at = None  
                        barcode_entry.sales_return_at = now() 
                        barcode_entry.remarks = "Returned via sales return"
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        return Response(
                            {"error": f"Barcode {barcode_value} does not exist in records."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                sale_return_serializer = self.get_serializer(data=data)
                sale_return_serializer.is_valid(raise_exception=True)
                sale_return = sale_return_serializer.save(created_by=request.user)

                SaleReturnHistory.objects.create(
                    sale_return=sale_return,
                    sale_history=sale_history,
                    return_qty=return_qty,
                    refund_amount=refund_amount,
                    remark=remark,
                    created_by=request.user
                )
                total_return_qty += return_qty
                total_refund_amount += refund_amount

                try:
                    stock = Stocks.objects.get(id=sale_history.product_variant.id)
                    stock.sold_qty -= return_qty
                    stock.available_qty += return_qty
                    stock.save()

                    StockHistory.objects.create(
                        stock=stock,
                        quantity=return_qty, 
                        price=sale_history.selling_price, 
                        log_type="Return",  
                        reference=sale_return.id, 
                        created_by=request.user 
                    )

                except Stocks.DoesNotExist:
                    raise ValidationError(f"Stock for product {sale_history.product_variant} does not exist.")
                
                
            sale_return.total_return_qty = total_return_qty
            sale_return.total_refund_amount = total_refund_amount
            sale_return.save()
            
            sale_id = sale_return.sale.id 

            try:
                sale = Sale.objects.get(id=sale_id)
                sale.total_amount -= total_refund_amount
                sale.sub_total -= total_refund_amount
                if sale.paid_amount>0:
                    sale.paid_amount-=total_refund_amount
                sale.save() 

            except Sale.DoesNotExist:
                raise ValidationError(f"Sale with ID {sale_id} does not exist.")


            headers = self.get_success_headers(sale_return_serializer.data)
            return Response(sale_return_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_success_headers(self, data):
        return {'Location': f"/sale_returns/{data.get('id')}/"}


class SaleReturnListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=SaleReturn.objects.all()
    serializer_class=SaleReturnDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields =  ['id','sale__customer__business_name','sale__customer__email','sale__customer__mobile','sale__customer__mobile2','sale__customer__conact_id','sale__customer__owner_name','sale__invoice_no','return_no','return_date']
    pagination_class=MainPagination

    def get_queryset(self):
        return SaleReturn.objects.all()


class SaleReturnRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=SaleReturn.objects.all()
    serializer_class=SaleReturnDetailsSerializer
    lookup_field='id'
    #parser_classes = (MultiPartParser, FormParser)

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        sale_return = self.get_object()  # Get the existing SaleReturn instance

        # Set the return number
        return_no = sale_return.return_no

        with transaction.atomic():
            # Update the sale return serializer
            sale_return_serializer = self.get_serializer(sale_return, data=data, partial=True)
            sale_return_serializer.is_valid(raise_exception=True)
            sale_return = sale_return_serializer.save(updated_by=request.user)

            total_return_qty = 0
            total_refund_amount = 0

            sale_return_history_data = data.get('sale_return_history', [])
            for item in sale_return_history_data:
                sale_history_id = item.get('sale_history')
                return_qty = item.get('return_qty', 0)
                refund_amount = item.get('refund_amount', 0)
                remark = item.get('remark', "")
                barcode = item.get('barcode', [])

                if len(barcode) != return_qty:
                    return Response({"error": f"Number of barcodes ({len(barcode)}) must match the good quantity ({return_qty})."}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    sale_history = SaleHistory.objects.get(id=sale_history_id)
                except SaleHistory.DoesNotExist:
                    raise ValidationError(f"Sale history with ID {sale_history_id} does not exist.")
                
                if return_qty > sale_history.quantity:
                    return Response(
                        {"error": f"Cannot return more than the sold quantity for sale history ID {sale_history_id}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Handle barcodes
                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)

                        if barcode_entry.product_variant != sale_history.product_variant.product_variant:
                            return Response(
                                {"error": f"Barcode {barcode_value} does not belong to the returned product."},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                        barcode_entry.product_status = "Sales Return"
                        barcode_entry.sold_at = None  # Reset sold timestamp
                        barcode_entry.sales_return_at = now()  # Set return timestamp
                        barcode_entry.remarks = "Returned via sales return"
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        return Response(
                            {"error": f"Barcode {barcode_value} does not exist in records."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Create SaleReturnHistory for this update
                SaleReturnHistory.objects.create(
                    sale_return=sale_return,
                    sale_history=sale_history,
                    return_qty=return_qty,
                    refund_amount=refund_amount,
                    remark=remark,
                    created_by=request.user
                )
                total_return_qty += return_qty
                total_refund_amount += refund_amount

                # Update stock quantities based on the returned items
                try:
                    stock = Stocks.objects.get(id=sale_history.product_variant.id)
                    stock.sold_qty -= return_qty
                    stock.available_qty += return_qty
                    stock.save()

                    # Log the stock update in the stock history
                    StockHistory.objects.create(
                        stock=stock,
                        quantity=return_qty,
                        price=sale_history.selling_price,
                        log_type="Return",
                        reference=sale_return.id,
                        created_by=request.user
                    )

                except Stocks.DoesNotExist:
                    raise ValidationError(f"Stock for product {sale_history.product_variant} does not exist.")
                
            sale_return.save()  # Save the SaleReturn instance after all updates

            # Return the updated sale return data
            headers = self.get_success_headers(sale_return_serializer.data)
            return Response(sale_return_serializer.data, status=status.HTTP_200_OK, headers=headers)

    def get_success_headers(self, data):
        return {'Location': f"/sale_returns/{data.get('id')}/"}
    
    def get_queryset(self):
        
        return SaleReturn.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)




class SaleReturnRetrieveListAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=SaleReturn.objects.all()
    serializer_class=SaleReturnDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        return SaleReturn.objects.all()







### quotation ###


class QuotationListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.pop("invoice_no", None)
        data["created_by"] = request.user.id
        data['branch'] = request.user.branch.id if request.user.branch else None

        # invoice = generate_invoice_no()
        # data['invoice_no'] = invoice
        with transaction.atomic():
            while True:
                inv_quotation = generate_invoice_no()
                if not Quotation.objects.filter(invoice_no=inv_quotation).exists():
                    break

            prefixs = InvoiceSetting.objects.filter(assign_branch=data['branch'],is_active=True)
            if prefixs:
                invoicesetting2=InvoiceSetting.objects.filter(assign_branch=data['branch'],is_active=True).first()
                data["invoice_no"] =str(invoicesetting2.prefix)+'-'+inv_quotation
                
            else:
                data["invoice_no"] = inv_quotation

            print(data["invoice_no"])
            customer_id = data.get("customer")
            customer = None
            if customer_id:
                try:
                    customer = Contact.objects.get(id=customer_id)
                except Contact.DoesNotExist:
                    return Response(
                        {"error": f"Customer with ID {customer_id} does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            quotation_history_data = data.get("quotation_history", [])
            if not quotation_history_data:
                return Response(
                    {"error": "At least one product must be included in the quotation."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            

            for item in quotation_history_data:
                product_id = item.get("product_variant")
                quantity = item.get("quantity", 0)
                discount_amount = item.get("discount_amount", 0)
                discount_percent = item.get("discount_percent", 0)
                discount_type = item.get("discount_type", "Select Type").strip()
                vat_amounts=item.get("vat_amounts",0)
                total_amount_iv=item.get("total_amount_iv",0)
                total_amount_wv=item.get("total_amount_wv",0)
                warranty = item.get("warranty", 0)
                remark = item.get("remark", "")
                barcode = item.get("barcode", [])
                
                if barcode:
                    if len(barcode) != quantity:
                        print(f"Number of barcodes ({len(barcode)}) must match the quantity ({quantity}).")
                        
                        return Response(
                            {"error": f"Number of barcodes ({len(barcode)}) must match the quantity ({quantity})."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    barcode_qs = ProductBarcodes.objects.filter(product_variant__id=product_id,product_status='Purchased').values_list('barcode', flat=True)
                    barcode=list(barcode_qs[:quantity])

                    if len(barcode) != quantity:
                        print(f"Not enough available barcodes for this product (required: {quantity}, found: {len(barcode)}).")
                        
                        return Response(
                            {"error": f"Not enough available barcodes for this product (required: {quantity}, found: {len(barcode)})."},
                                status=status.HTTP_400_BAD_REQUEST)
                

                try:
                    stock = Stocks.objects.get(product_variant__id=product_id)
                except Stocks.DoesNotExist:
                    print(f"Stock with product variant ID {product_id} does not exist.")
                    
                    return Response(
                        {"error": f"Stock with product variant ID {product_id} does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if stock.available_qty < quantity:
                    print(f"Not enough stock available for product {stock.product_variant.product.product_name}.")
                    
                    # return Response(
                    #     {"error": f"Not enough stock available for product {stock.product_variant.product.product_name}."},
                    #     status=status.HTTP_400_BAD_REQUEST
                    # )

                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)
                        if barcode_entry.product_variant != stock.product_variant:
                            return Response(
                                {"error": f"Barcode {barcode_value} does not belong to the specified product."},
                                status=status.HTTP_400_BAD_REQUEST
                            )

                        barcode_entry.inv_quotation = data["invoice_no"]
                        barcode_entry.product_status = "Quotation"
                        barcode_entry.quotation_at= now()
                        barcode_entry.remarks = "quotation via sales transaction"
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        print(f"Barcode {barcode_value} does not exist in records.")
                        return Response(
                            {"error": f"Barcode {barcode_value} does not exist in records."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                quotation_serializer = self.get_serializer(data=data)
                quotation_serializer.is_valid(raise_exception=True)
                quotation = quotation_serializer.save(created_by=request.user, customer=customer)
                print("Creating quotation history for", stock.product_variant.product.product_name)

                QuotationHistory.objects.create(
                    quotation=quotation,
                    product_variant=stock,
                    quantity=quantity,
                    unit_price=stock.purchase_price,
                    selling_price=stock.selling_price,
                    discount_amount=discount_amount,
                    discount_percent=discount_percent,
                    discount_type=discount_type,
                    vat_amounts=vat_amounts,
                    total_amount_iv=total_amount_iv,
                    total_amount_wv=total_amount_wv,
                    warranty=warranty,
                    remark=remark,
                    created_by=request.user
                    #branch=request.user.branch.id if request.user.branch else None
                )

                # stock.sold_qty += quantity
                # stock.available_qty -= quantity
                # stock.save()

               
                # StockHistory.objects.create(
                #     stock=stock,
                #     quantity=-quantity,
                #     price=stock.selling_price,
                #     log_type="Sale",
                #     reference=sale.id,
                #     created_by=request.user
                # )

        quotation.save()
        headers = self.get_success_headers(quotation_serializer.data)
        return Response(quotation_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class QuotationListAPIView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Quotation.objects.all()
    serializer_class=QuotationDetailsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id','customer__business_name','customer__email','customer__mobile','customer__mobile2','customer__conact_id','customer__owner_name','invoice_no']
    pagination_class=MainPagination

    def get_queryset(self):
        return Quotation.objects.all()


class QuotationRetrieveUpdateDestroyListAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Quotation.objects.all()
    serializer_class = QuotationDetailsSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        with transaction.atomic():
            # Update the sale record
            quotation_serializer = self.get_serializer(instance, data=data, partial=True)
            quotation_serializer.is_valid(raise_exception=True)
            quotation = quotation_serializer.save(updated_by=request.user)

            quotation_history_data = data.get('quotation_history', [])
            total_sale_amount = 0
            total_discount_amount = 0

            existing_quotation_history_ids = set(instance.quotation_history.values_list('id', flat=True))
            new_quotation_history_ids = set()

            for item in quotation_history_data:
                product_id = item.get('product_variant')
                quantity = item.get('quantity', 0)
                discount_amount = item.get('discount_amount', 0)
                discount_percent = item.get('discount_percent', 0)
                warranty = item.get('warranty', 0)
                remark = item.get('remark', "")
                barcode = item.get('barcode', [])

                if len(barcode) != quantity:
                    print(f"Number of barcodes ({len(barcode)}) must match the quantity ({quantity}).")
                    # return Response(
                    #     {"error": f"Number of barcodes ({len(barcode)}) must match the quantity ({quantity})."},
                    #     status=status.HTTP_400_BAD_REQUEST
                    # )

                try:
                    stock = Stocks.objects.get(product_variant__id=product_id)
                except Stocks.DoesNotExist:
                    print(f"Stock with product variant ID {product_id} does not exist.")
                    # return Response(
                    #     {"error": f"Stock with product variant ID {product_id} does not exist."},
                    #     status=status.HTTP_400_BAD_REQUEST
                    # )

                # Get previous sale history entry (if exists)
                quotation_history, created = QuotationHistory.objects.get_or_create(
                    quotation=quotation,
                    product_variant=stock,
                    defaults={
                        "quantity": quantity,
                        "unit_price": stock.purchase_price,
                        "selling_price": stock.selling_price,
                        "discount_amount": discount_amount,
                        "discount_percent": discount_percent,
                        "warranty": warranty,
                        "remark": remark,
                        "updated_by": request.user
                    }
                )

                new_quotation_history_ids.add(quotation_history.id)

                # Calculate stock adjustments
                previous_quantity = quotation_history.quantity
                # if previous_quantity != quantity:
                #     stock.available_qty += previous_quantity  # Revert old quantity
                #     stock.available_qty -= quantity  # Deduct new quantity
                #     stock.sold_qty -= previous_quantity
                #     stock.sold_qty += quantity
                #     stock.save()

                #     StockHistory.objects.create(
                #         stock=stock,
                #         quantity=-quantity,
                #         price=stock.selling_price,
                #         log_type="Sale Update",
                #         reference=sale.id,
                #         created_by=request.user
                #     )

                quotation_history.quantity = quantity
                quotation_history.unit_price = stock.purchase_price
                quotation_history.selling_price = stock.selling_price
                quotation_history.discount_amount = discount_amount
                quotation_history.discount_percent = discount_percent
                quotation_history.warranty = warranty
                quotation_history.remark = remark
                quotation_history.updated_by = request.user
                quotation_history.save()

                for barcode_value in barcode:
                    try:
                        barcode_entry = ProductBarcodes.objects.get(barcode=barcode_value)

                        if barcode_entry.product_variant != stock.product_variant:
                            return Response(
                                {"error": f"Barcode {barcode_value} does not belong to the specified product."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        barcode_entry.inv_quotation=quotation.invoice_no
                        barcode_entry.product_status = "Quotation"
                        barcode_entry.quotation_at = now()
                        barcode_entry.remarks = "Updated quotation transaction"
                        barcode_entry.save()

                    except ProductBarcodes.DoesNotExist:
                        return Response(
                            {"error": f"Barcode {barcode_value} does not exist in records."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

            to_delete = existing_quotation_history_ids - new_quotation_history_ids
            QuotationHistory.objects.filter(id__in=to_delete).delete()

            
            quotation.save()

            return Response(quotation_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
    
        self.perform_destroy(instance)
        return Response({"success": True, "message": "Deleted successfully"}, status=status.HTTP_200_OK)
    


class QuotationRetrieveAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=Quotation.objects.all()
    serializer_class=QuotationDetailsSerializer
    lookup_field='id'

    def get_queryset(self):
        #print('views')
        return Quotation.objects.all()