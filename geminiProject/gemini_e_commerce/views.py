
import os
import json
import re
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import google.generativeai as genai
from .models import *
from .serializers import ProductSerializer
from haystack.query import SearchQuerySet
from algoliasearch_django import raw_search



class GeminiChatView(APIView):
    

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
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated]

        def build_recommendation_response(recommended_products):
            try:
                response=[]
                recommend_products=recommend_products.hits
                for product in recommended_products:
                    data={}
                    data['id']=product['objectID']
                    data['name']=product['name']
                    data['category']=product['description']
                    data['season']=product['season']
                    response.append(data)

                return response
            except:
                return []


        def build_response_parts(responses):
            response_parts = [
                genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fn, response={"result": val}))
                for fn, val in responses.items()
            ]

            return response_parts
            
        
        def recommend_products(name: str, category: str) -> dict:
            '''
            This function provides product recommendations based on the provided details.
            
            Args:
            name: str - The name of the product or keyword to base the recommendations on.
            category: str - The category of the product, such as "accessory" or "cosmetic".
            
            Returns:
            dict - A dictionary containing details of the best-matched recommended product(s).
            '''
            # response.candidates[0].content.parts[0].function_call implementation goes here
            

        def create_order(product_id: int, quantity: int) -> bool:
            '''
            This function processes an order request for a specific product.
            
            Args:
            product_id: int - The ID of the product to be ordered.
            quantity: int - The quantity of the product to be ordered.
            
            Returns:
            bool - True if the order is successfully created; False if the product is out of stock or cannot be ordered.
            '''
            # Function implementation goes here
            

        def get_product_info(product_id: int) -> dict:
            '''
            This function retrieves detailed information about a specific product based on its ID.
            
            Args:
            product_id: int - The ID of the product for which information is needed.
            
            Returns:
            dict - A dictionary containing detailed information about the product, such as features, price, and availability.
            '''
            # Function implementation goes here
            
            
        
       

    

        try:#instruction=self.generate_system_instruction()
            genai.configure(api_key=os.environ["API_KEY"])
            mytools=[get_product_info,create_order]
            model = genai.GenerativeModel('gemini-1.5-flash',tools=mytools)
            
            print(model._tools.to_proto())
            chat = model.start_chat(enable_automatic_function_calling=True)
            user_message = request.data.get('user_prompt')
            prompt=self.generate_system_instruction(user_message)
            response = chat.send_message(prompt)
            
            Function= response.candidates[0].content.parts[0].function_call
            #print(Function.name)


            if response.candidates[0].content.parts[0].function_call.name=='recommend_products':
                
               
                args =response.candidates[0].content.parts[0].function_call.args
                name= args['name']
                category=args['category']
                query=f"{name} {category}"
                params = { "hitsPerPage": 10 }

                theresponse = raw_search(Product, query,params)
                recommended_products=theresponse

                #data=build_recommendation_response(recommended_products)


                #return Response({'data':recommeded_products})

                responses = {
                    "get_product_info":recommended_products,
                }

                # Build the response parts.
                response_parts =build_response_parts(responses)
                response = chat.send_message(response_parts)
                

                self.create_chat_history(user_message,response.text)
                
                return Response({'success':True,
                                'type':'recommend_products',
                                'data':recommended_products,
                                'response':response.text},status=200)


            
            elif response.candidates[0].content.parts[0].function_call.name== 'get_product_info':
                
                args =response.candidates[0].content.parts[0].function_call.args
                product_id = args['product_id']
                product_info = ProductSerializer(Product.objects.get(id=product_id)).data
                #return product_info
                for part in response.parts:
                    if fn := part.function_call:
                        args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                        print(f"{fn.name}({args})")

                responses = {
                    "get_product_info":product_info,
                }

                # Build the response parts.
                response_parts = build_response_parts(responses)
                response = chat.send_message(response_parts)

                self.create_chat_history(user_message,response.text)


                return Response({'success':True,
                                'type':'get_product_info',
                                'response':response.text}, status=200)
            
            elif response.candidates[0].content.parts[0].function_call.name=='create_order':
                
                args =response.candidates[0].content.parts[0].function_call.args
                product_id = args['product_id']
                quantity=args['quantity']
                product = Product.objects.get(id=product_id)
                if product.stock>=quantity:
                    product.stock-=quantity
                    product.save()
                    Order.objects.create(user=request.user,
                                        product_id=product_id,
                                        quantity=quantity)
                   
                    responses = {
                    "create_order":True
                    }
                    response_parts = build_response_parts(responses)
                    response = chat.send_message(response_parts)

                    self.create_chat_history(user_message,response.text)

                    return Response({'success':True, 
                                    'type':'create_order',
                                    'response':'response.text'},status=200)
                    
                else:
                    responses = {
                    "create_order":False
                    }
                    response_parts =build_response_parts(responses)
                    response = chat.send_message(response_parts)

                    self.create_chat_history(user_message,response.text)

                    return Response({'success':True,
                                    'type':'create_order',
                                    'response':"order not created"},status=200)
                
            else:
                return Response({'message':'Can you re-articulate your question'})

                    
        except Exception as e:
            raise e




    def get_chat_history(self):
        thirty_days_ago = timezone.now() - timedelta(days=2)
        recent_messages = ChatHistory.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[1:]

        if recent_messages:
            return [
                {
                    "role_user": "user",
                    "user_content": message.chat_text,
                    "role_assistant": "assistant",
                    "assistant_content": message.response_text
                } 
                for message in recent_messages
            ]
        return []



    def create_chat_history(self, chat, response):
        response= re.sub(r'[^\w\s.,!?\'"]+', '', response)
        ChatHistory.objects.create(user=self.user, chat_text=chat, response_text=response)


    
    def generate_system_instruction(self,user_message):
        chat_history = self.get_chat_history()
        instruction = f"""
        System: You are an AI assistant for an e-commerce website. Your role is to help customers with product inquiries, recommendations, and order creation. You have access to several tools to assist you in these tasks. Always use the most appropriate tool when responding to user queries.

        Tools:

        1. recommend_products(name: str, category: str) -> dict
        Description: Use this tool to provide product recommendations based on a product name or keyword and category.
        When to use: When a user asks for product suggestions or similar items.

        2. create_order(product_id: int, quantity: int) -> bool
        Description: Use this tool to process an order for a specific product and quantity.
        When to use: When a user expresses a desire to purchase a product.

        3. get_product_info(product_id: int) -> dict
        Description: Use this tool to retrieve detailed information about a specific product.
        When to use: When a user asks for details about a particular product.

        Instructions:
        - Always use the appropriate tool when responding to user queries.
        - If you need more information to use a tool, ask the user for the required details.
        - After using a tool, interpret the results and provide a natural language response to the user.
        - If a tool returns an error or unexpected result, inform the user and offer alternative solutions.

        User: {user_message}"""

        return instruction



        





    