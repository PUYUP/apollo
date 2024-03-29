# THIRD PARTY
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny


class RootApiView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        return Response({
            'person': {
                'token': reverse('person:token_obtain_pair', request=request,
                                 format=format, current_app='person'),
                'token-refresh': reverse('person:token_refresh', request=request,
                                         format=format, current_app='person'),
                'users': reverse('person:user-list', request=request,
                                 format=format, current_app='person'),
                'otps': reverse('person:otp-list', request=request,
                                format=format, current_app='person'),
            },
        })
