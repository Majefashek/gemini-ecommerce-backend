from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework import status
from .models import Product, Order
#from elasticsearch import Elasticsearch
#from google.cloud import aiplatform
import json
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
import google.generativeai as genai
import os
from drf_yasg import openapi
from google.generativeai.types import FunctionDeclaration, Tool
from google.generativeai import GenerativeModel, GenerationConfig
from .serializers import *
from django.shortcuts import get_object_or_404
from .models import *

# ... existing imports ...

    # ... existing code ...

class GeminiChatView(APIView):
    #s = Elasticsearch()
    #aiplatform.init(project='your-project-id')
    


    

        

    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_prompt'],
        properties={
            'user_prompt': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='The prompt provided by the user for processing.'
            ),
        }
    )
)

    def post(self, request):

        def get_product_info(product_id:int)->str:
            '''
            This function returns the product information for a given product id

            Args:
                product_id:int
            Returns:
                str
            '''
            return 'This is the product information for the given product id'
        mytools=[get_product_info]
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash',tools=mytools)
        chat = model.start_chat()
        user_message = request.data.get('user_prompt')
        response = chat.send_message(user_message)
        x = response.candidates[0].content.parts[0].function_call.name
        if response.candidates[0].content.parts[0].function_call.name== 'get_product_info':
            args = response.candidates[0].content.parts[0].function_call.args
            product_id = args['product_id']
            product_info = ProductSerializer(Product.objects.get(id=product_id)).data

            return Response({'response':product_info})
            responses={}
            for part in response.parts:
                if fn := part.function_call:
                    args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                    responses[fn.name]=args
            response_parts = [
                            genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fn, response={"result": val}))
                            for fn, val in responses.items()
                        ]

            response = chat.send_message(response_parts)

            return Response({'response':response})  
            
            url =[x]
        #return Response({'response':url})

        





        