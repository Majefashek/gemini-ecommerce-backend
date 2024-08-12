
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

class GeminiChatService:
    def __init__(self, user):
        self.user = user
        self.recent_chat_history = self.get_chat_history()
        self.model = self._initialize_model()

    

    def _initialize_model(self):
        genai.configure(api_key=os.environ["API_KEY"])

        def get_product_info(product_id:int)->str:
            '''
            This function returns the product information for a given product id

            Args:
                product_id:int
            Returns:
                str
            '''
            return 'This is the product information for the given product id'

        mytools = [get_product_info]
        instruction = self.generate_system_instruction()
        return genai.GenerativeModel('gemini-1.5-flash', tools=mytools, system_instruction=instruction)

    


class GeminiChatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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

        def create_order(product_id:int,quantity:int)->bool:
            '''
            This function creates an order is created or not for a product with a given id:
            Args:
            product_id:int, this is the id of the product that the order is going to be created for
            quantity:int, this is the quantity of the product that is wanted
            Return True if the order is created
            Return False if the product is out of stock
            '''

        def casual_response(query:str)->bool:
            '''
            This determines if the question asked by a user if it is looking for casual response
            or not,not primary functions such as product inquiry, order request or recommending product
            return True if that's the case or returns false if it is not

            Args:
                query: Human question

            Returns True if yes 
            '''
        
        def get_product_info(product_id:int)->dict:
            '''
            This function  takes in the product id
            and gives answer to general inquiry regarding this product 

            Args:
                product_id:int
            Returns: Information regarding the product  it is string format
                dict
            '''
            
        
        mytools=[get_product_info,casual_response,create_order]

        #instruction=self.generate_system_instruction()
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash',tools=mytools)
        chat = model.start_chat()
        user_message = request.data.get('user_prompt')
        prompt=self.generate_system_instruction(user_message)
        response = chat.send_message(prompt)
        
        Function= response.candidates[0].content.parts[0].function_call

        
        if Function.name== 'get_product_info':
            args =Function.args
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
            response_parts = [
                genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fn, response={"result": val}))
                for fn, val in responses.items()
            ]

            response = chat.send_message(response_parts)
            print(response)
            return Response({'response':response.text})
        
        if Function.name=='create_order':
            args =Function.args
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
                "get_product_info":"",
                "casual_response":True
             }
                responses = {
                "create_order":True
                }
                response_parts = [
                    genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fn, response={"result": val}))
                    for fn, val in responses.items()
                ]
                response = chat.send_message(response_parts)
                print(response)
                return Response({'response':"wow order"})
                
            else:
                responses = {
                "create_order":False
                }
                response_parts = [
                    genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fn, response={"result": val}))
                    for fn, val in responses.items()
                ]
                response = chat.send_message(response_parts)
                print(response)

                return Response({'response':"order not created"})
                return False

        
        else:
            responses = {
                "get_product_info":"",
                "casual_response":True
             }
            response_parts = [
                genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fn, response={"result": val}))
                for fn, val in responses.items()
            ]

            response = chat.send_message(response_parts)

                   
            print(response)
            return Response({'response':"wow"})





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





    

    def process_chat(self, user_message):
        chat = self.model.start_chat()
        response = chat.send_message(user_message)
        text = self.keep_normal_text(response.text)
        self.create_chat_history(user_message, text)
        
        # Debugging response content
        print("Response:", response)
        print("Response candidates:", response.candidates)
        
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            print("Function Call:", function_call)
            
            if function_call.name == 'get_product_info':
                args = function_call.args
                print("Function Args:", args)
                product_id = args['product_id']
                product_info = ProductSerializer(Product.objects.get(id=product_id)).data

                return product_info
            else:
                return function_call.name
        else:
            return text

    def create_chat_history(self, chat, response):
        ChatHistory.objects.create(user=self.user, chat_text=chat, response_text=response)

    @staticmethod
    def keep_normal_text(text):
        return re.sub(r'[^\w\s.,!?\'"]+', '', text)

    




    
    def generate_system_instruction(self,user_message):
        chat_history = self.get_chat_history()
        instruction = f"""The following is a structured chat history between you (an ecommerce AI assistant) and the user. 
                        Refer to this history to understand the context before responding to the current query.

                        Chat History (Field Definitions):
                        - `role_user`: Indicates the user's message or statement.
                        - `user_content`: Contains the actual text of the user's message.
                        - `role_assistant`: Indicates your response as the assistant.
                        - `assistant_content`: Contains the actual text of your response.

                        Here is the chat history:
                        chat_history={chat_history}

                    Instructions:
                    1. Product Inquiry:
                        - Definition: A user asking for specific information about a product, typically using a product ID.
                        - Example: "Can you tell me more about product ID 12345?"
                        - Action: Use the product ID to look up and provide detailed information about the product.

                        2. Order Processing:
                        - Definition: A user wanting to place an order for a specific product, usually mentioning a product ID.
                        - Example: "I'd like to order product 67890."
                        - Action: Confirm the product details and guide the user through the ordering process.

                        3. Product Recommendations:
                        - Definition: A user seeking suggestions for products based on their preferences or needs.
                        - Example: "What running shoes do you recommend for long-distance runners?"
                        - Action: Ask for more details if needed, then suggest appropriate products.

                        4. General Query:
                        - Definition: Any question not directly related to specific products, orders, or recommendations.
                        - Example: "What are your store hours?" or "Do you offer gift wrapping?"
                        - Action: Provide a straightforward answer without using specialized tools.

                        Instructions for Handling Queries:

                        1. Identify the type of query based on the definitions above.

                        2. For Product Inquiries:
                        - Look for a product ID in the user's message.
                        - Use appropriate tools to fetch product information.
                        - Provide detailed information about the product (features, price, availability, etc.).

                        3. For Order Processing:
                        - Confirm the product ID the user wants to order.
                        - Guide the user through the ordering steps (quantity, shipping, payment, etc.).
                        - Use order processing tools if available.

                        4. For Product Recommendations:
                        - Understand the user's needs and preferences.
                        - If necessary, ask follow-up questions for clarification.
                        - Provide tailored product suggestions based on the information given.

                        5. For General Queries:
                        - Respond with a straightforward, informative answer.
                        - No need to use specialized ecommerce tools for these queries.

                        6. For all query types:
                        - Always refer to the chat history for context.
                        - Ensure your response is clear, helpful, and relevant to the user's needs.
                        - If any part of the query is unclear, ask for clarification.

                        Here is the current user question:
                        {user_message}

                        Please identify the type of query and respond appropriately based on the instructions above."""
        return instruction



        





    