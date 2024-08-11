
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
from .models import ChatHistory, Product
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
        user_message = request.data.get('user_prompt')
        if not user_message:
            return Response({'error': 'user_prompt is required'}, status=400)

        chat_service = GeminiChatService(request.user)
        response_text = chat_service.process_chat(user_message)
        return Response({'response': response_text})
    





    def get_chat_history(self):
        thirty_days_ago = timezone.now() - timedelta(days=2)
        recent_messages = ChatHistory.objects.filter(
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')[:30]

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

    




    
    def generate_system_instruction(self):
        chat_history = self.get_chat_history()
        instruction = f"""
            The following is a structured chat history between you (the Assistant) and the user. 
            Refer to this history to understand the context before responding to the current query.

            Chat History (Field Definitions):
            - `role_user`: Indicates the user's message or statement.
            - `user_content`: Contains the actual text of the user's message.
            - `role_assistant`: Indicates the assistant's response.
            - `assistant_content`: Contains the actual text of the assistant's response.

            Here is the chat history:
            chat_history={chat_history}

            Instructions:
            1. Review the chat history to gather context and understand the flow of the conversation.
            2. The `role_user` fields represent the user's questions or statements. The `role_assistant` fields are your responses.
            3. Use the context from the chat history to inform your response to the current message.
            4. Ensure that your response considers the previous interactions and provides a coherent answer to the user's current query.
            5. If necessary, clarify any ambiguities or correct any misunderstandings from previous responses.
            6. Provide a response that builds upon the context provided and helps advance the conversation.

            Also note: Whenever you are asked about our conversation history, please refer to the chat history above
            and give a more context-based answer.
            ALWAYS REFER TO THE chat_history before giving a response.
            ALSO NOTE KEY WORDS SUCH AS REMEMBER; whenever those key words are invoked, please refer to them before
            giving a response.
            NOTE:Avoid answers like "I am unable to remember past conversations. I have no memory of past interactions. Each time we interact, it's like starting a new conversation."
            """
        return instruction



        





        