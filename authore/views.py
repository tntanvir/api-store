from django.shortcuts import render
from .models import MoreInfo
from django.contrib.auth.models import User
from .serializer import Registerseializer,loginSerializer,MoreInfoSerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.contrib.auth import login,logout,authenticate
# Create your views here.

class RegisterView(APIView):
    serializer_class = Registerseializer
    
    def post(self, request):
        serializer= self.serializer_class(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            token=default_token_generator.make_token(user)
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link=f'https://api-clothify.onrender.com/authore/active/{uid}/{token}/'

            email_subject ='Confirm Your Account'
            email_body=render_to_string('confirm_email.html',{'confirm_link':confirm_link})
            email=EmailMultiAlternatives(email_subject,'',to=[user.email])
            email.attach_alternative(email_body,'text/html')

            email.send()
            return Response({'message':'Account Created Successfully. Please verify your email.'}, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
def activate(request,uid64,token):
    try:
        uid=urlsafe_base64_decode(uid64).decode()
        user=User._default_manager.get(pk=uid)
    except(User.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        return redirect('login')
    else:
        return redirect('login')
    
class UserLoginView(APIView):
    def post(self, request):
        serializer =loginSerializer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                token,_=Token.objects.get_or_create(user=user)
                login(request, user)
                return Response({'token': token.key,'id':user.id,'username':user.username,'message':'Login complete'}, status=status.HTTP_200_OK)
            else:
                return Response({'error':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors)



class UserLogoutView(APIView):
        print('inside logout')
        def get(self, request):
            request.user.auth_token.delete()
            logout(request)
            print('logged out')
            return Response({'message':'Logged Out'}, status=status.HTTP_200_OK)






class MoreInfoDetailUpdateView(APIView):

    def get(self, request, username):
        more_info = get_object_or_404(MoreInfo, user__username=username)
        serializer = MoreInfoSerializer(more_info)
        return Response(serializer.data)

    def put(self, request, username):
        more_info = get_object_or_404(MoreInfo, user__username=username)
        serializer = MoreInfoSerializer(more_info, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):

    def delete(self, request, username):
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)