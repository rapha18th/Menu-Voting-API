

from rest_framework.authentication import  TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status


from django.contrib.auth.models import User
from django.db.models import Case, When
from django.contrib.auth import authenticate
from django.forms.models import model_to_dict


from .models import Restaurant, Menu, Vote
from .serializers import MenuSerializer

import pyrankvote
from pyrankvote import Candidate, Ballot


from datetime import date


@api_view(['POST'])
def register(request):
    try:
        email = request.data['email']
        username = request.data['username']
        password = request.data['password']
        userExists = User.objects.filter(username=username).exists()
        if userExists:
            return Response({'errors': ['User does already exists']})

        user = User.objects.create_user(username, email, password)
        user.save()
        return Response(model_to_dict(user, ['username', 'email']))

    except:
        res = {"msg": "all fields are required", "data": None, "success": False}

        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    try:
        username = request.data['username']
        password = request.data['password']
        userExists = User.objects.filter(username=username).exists()
        if userExists:
            user = authenticate(request, username=username, password=password)
            if not user:
                res = {"msg": "make sure user exists and password is correct",
                       "data": None, "success": False}
                return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

            token = Token.objects.create(user=user)
            return Response({'token': model_to_dict(token, ['key', 'created'])})

        else:
            res = {"msg": "make sure password is correct",
                   "data": None, "success": False}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

        pass
    except:
        res = {"msg": "Enter username and password to login",
               "data": None, "success": False}
        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createRestaurant(request):
    print(request.version)
    data =  request.data
    restaurant = Restaurant()
    restaurant.name = data['name']

    restaurant.save()

    return Response( model_to_dict(restaurant, ['id', 'name']))


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createMenu(request):
    try:
        restaurant = Restaurant.objects.get(pk=request.data['restaurant_id'])

    except:
        res = {"msg": "Restaurant does not exist",
               "data": None, "success": False}
        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

    menu = Menu(restaurant = restaurant, description = request.data['description'] , created_at=date.today())
    menu.save()

    return Response( model_to_dict(menu, ['id', 'created_at']))


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getMenus(request):
    menus = Menu.objects.filter(created_at=date.today())
    return Response(MenuSerializer(menus,many=True).data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def voteForMenu(request):


    if request.version == '1.0':
        try:
            menu = Menu.objects.get(pk=request.data['menu_id'])
            voted = Vote.objects.filter(created_at=date.today(), user=request.user).exists()
            if voted :
                res = {"msg": "You have already voted today",
                       "data": None, "success": False}
                return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

            vote = Vote(menu=menu, user=request.user, created_at=date.today(), rank=1)
            vote.save()


        except:
            res = {"msg": "Menu does not exist",
                   "data": None, "success": False}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

    elif request.version == '2.0':
        menuIds = request.data['menu_ids']
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(menuIds)])
        menus = Menu.objects.filter(pk__in=menuIds).order_by(preserved)

        voted = Vote.objects.filter(created_at=date.today(), user=request.user).exists()
        if voted :
            res = {"msg": "You have already voted today",
                   "data": None, "success": False}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

        counter = 1
        for menu in menus:
            vote = Vote(menu=menu, user=request.user, created_at=date.today(), rank=counter)
            vote.save()
            counter += 1
            pass

        return Response(menuIds)

    return Response()

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getResults(request):
    menus = Menu.objects.filter(created_at=date.today())
    candidates = [Candidate(str(menu.id)) for menu in menus]
    userVotes = {}
    votes = Vote.objects.filter(created_at=date.today())
    for vote in votes:
        if vote.user_id not in userVotes:
            userVotes[vote.user_id] = []
        userVotes[vote.user_id].append(vote.menu_id)



 # Use pyrankvote to get the top menu
    ballots = []
    for userVote in userVotes:
        menuIds = userVotes[userVote]
        rankedMenus = []
        for menuId in menuIds:
            candidate = next((x for x in candidates if x.name == str(menuId)), None)
            rankedMenus.append(candidate)

        ballots.append(Ballot(ranked_candidates=rankedMenus))

    election_result = pyrankvote.instant_runoff_voting(candidates, ballots)

    winners = election_result.get_winners()
    if len(winners) > 0:
        topMenu = Menu.objects.get(pk=int(winners[0].name))
        return Response({'menu' : MenuSerializer(topMenu).data})

    res = {"msg": "No voting happened today",
           "data": None, "success": False}
    return Response(data=res, status=status.HTTP_400_BAD_REQUEST)





