from io import BytesIO
from django.http import FileResponse
from reportlab.graphics.barcode import code128
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from celery import shared_task
from celery.utils.log import get_task_logger
import re
import math
import time
import uuid
import operator
import datetime
import functools
from io import BytesIO
from xhtml2pdf import pisa
from django.apps import apps
from django.db.models import Q
from django.db.models import Model
from django.db.models import Lookup
from django.http import HttpResponse
from django.template.loader import get_template
from typing import (
    List, 
    Callable,
    Any, 
    Type,
    Dict
)
import io
from reportlab.lib.pagesizes import letter, inch
import treepoem
import os
from django.conf import settings
from PIL import Image
from django.core.files.base import ContentFile



logger = get_task_logger(__name__)

def unique_id_generate(number_of_id):
    unique_id_list = []
    for i in range(number_of_id):
        timespan = format(time.time(), '.14f')
        timespan = timespan.split('.')[1]
        unique_id_list.append(timespan)
        time.sleep(0.2)
    return unique_id_list

def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-", "")
    return random[0:string_length]


def generate_barcode_image(data):
    barcode = treepoem.generate_barcode(
        barcode_type='code128',
        data=data
    )

    # Convert barcode (PIL Image object) directly to BytesIO
    image_io = io.BytesIO()
    
    # Save the image in PNG format
    barcode.save(image_io, format='PNG')
    image_io.seek(0)  # Rewind the file pointer to the start
    
    # Save the image in memory and return a ContentFile with a valid name
    return ContentFile(image_io.read(), name=f'{data}.png')
