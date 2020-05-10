from django.contrib.auth.models import User, Group
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string

from rest_framework import viewsets, permissions, status
from rest_framework.parsers import JSONParser

from dlap_ludo.game.serializers import CreateRoomSerializer, JoinRoomSerializer, UserSerializer, GroupSerializer
from dlap_ludo.game.models import Room, Player

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render  # only form base view

PAWN_NOT_ON_THE_BOARD_STATUS = -1
PAWN_AT_THE_FINISH_LINE_STATUS = -2
PAWN_INDEX_TO_COLOR = ['blue', 'yellow', 'red', 'green', 'watcher']
PAWN_COLOR_TO_INDEX = {'blue': 0, 'yellow': 1, 'red': 2, 'green': 3, 'watcher': 4}
BOARD_FIELDS_DESC = { # according to board prepared by Domi
    'blue': {
        'start_field': 3,
        'stop_field': 2,
    },
    'yellow': {
        'start_field': 13,
        'stop_field': 12,
    },
    'red': {
        'start_field': 23,
        'stop_field': 22,
    },
    'green': {
        'start_field': 33,
        'stop_field': 32,
    },
}

# EMPTY_BOARD = {
#     'game_started': False,
#     'pawns': {
#         'blue': [PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD],
#         'yellow': [PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD],
#         'red': [PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD],
#         'green': [PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD, PAWN_NOT_ON_THE_BOARD]
#     },
#     'user_playing_color': None,
# }

@csrf_exempt
def base_view(request):
    return render(request, 'base.html')

@csrf_exempt
def create_room(request):
    """
    The create_room view takes JSON message in format (to see requirements see serializers.py):
    {
        "is_private_room": true,
        "room_name": "name_of_room",
        "admin_player_username": "username_of_room's_admin_plyer"
    }

    Response format will be:
    {
        'token': 'token_generated_by_app_and_required_for_every_request',
        'is_player': true/false, // did plyer get to the room as plyer or there was no place and is watcher
        'color': 'blue'
    }

    In case of error response status is different then 200:
    - 400 Bad request - response looks like:
        {"admin_player_username": ["This field may not be blank."]}
    or
        {"admin_player_username": ["Ensure this field has at least 8 characters."]}
    -
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CreateRoomSerializer(data=data)
        if serializer.is_valid():

            is_private_room = serializer.data['is_private_room']
            room_name = serializer.data['room_name']
            admin_player_username = serializer.data['admin_player_username']

            room = Room(name=room_name, is_private=is_private_room)
            try:
                room.save()
            except IntegrityError as e:
                return JsonResponse({'room_name': 'room_name already taken'}, status=400)

            color = PAWN_INDEX_TO_COLOR[0]

            token = get_random_string(length=64)
            player = Player(name=admin_player_username, is_admin=True, room=room, token=token, color=color)
            player.save()

            board = {
                
            }

            response = {
                "token": token,
                "is_player": True,
                "color": color
            }

            return JsonResponse(response, status=201)

        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def join_room(request):
    """
    The join_room view takes JSON message in format (to see requirements see serializers.py):
    {
        "room_name": "name_of_room",
        "player_username": "username_of_player"
    }

    Response format will be:
    {
        'token': 'token_generated_by_app_and_required_for_every_request',
        'is_player': true/false, // did player get to the room as player or there was no place and is watcher
        'color': 'red'
    }

    In case of error response status is different then 200:
    - 400 Bad request - response looks like:
        {"player_username": ["This field may not be blank."]}
    or
        {"player_username": ["Ensure this field has at least 8 characters."]}
    -
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = JoinRoomSerializer(data=data)
        if serializer.is_valid():

            room_name = serializer.data['room_name']
            player_username = serializer.data['player_username']

            try:
                room = Room.objects.get(name=room_name)
            except ObjectDoesNotExist:
                return JsonResponse({'room_name': 'room doesn\'t exist'}, status=400)

            players_in_room = Player.objects.filter(room_id=room.id)

            for player_in_room in players_in_room:
                if player_in_room.name == player_username:
                    return JsonResponse({'player_username': 'player_username already exist in this room'}, status=400)

            color = PAWN_INDEX_TO_COLOR[4]
            is_player = len(players_in_room) < 4
            if is_player:
                color = PAWN_INDEX_TO_COLOR[len(players_in_room)]

            token = get_random_string(length=64)
            player = Player(name=player_username, room=room, token=token, color=color)
            player.save()

            response = {
                "token": token,
                "is_player": is_player,
                "color": color
            }

            return JsonResponse(response, status=201)

        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def get_board(request):
    pass


@csrf_exempt
def roll_cube(request):
    pass


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]