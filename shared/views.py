import mimetypes
import os
from django.http import Http404, FileResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from accounts.permissions import AuthPermission
from shared.models import AudioModel


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    # max_page_size = 100



class ProtectedAudioStreamView(APIView):
    permission_classes = [AuthPermission]

    def get(self, request, id):
        try:
            audio = AudioModel.objects.get(pk=id)
        except AudioModel.DoesNotExist:
            raise Http404

        file_path = audio.file.path

        if not os.path.exists(file_path):
            raise Http404

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        filename = os.path.basename(file_path)
        response = FileResponse(open(file_path, "rb"), content_type=mime_type)
        response["Content-Disposition"] = f'''inline; filename={filename}'''

        return response


class ProtectedAudioDownloadView(APIView):
    permission_classes = [AuthPermission]

    def get(self, request, id):
        try:
            audio = AudioModel.objects.get(pk=id)
        except AudioModel.DoesNotExist:
            raise Http404

        file_path = audio.file.path

        if not os.path.exists(file_path):
            raise Http404

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        filename = os.path.basename(file_path)
        response = FileResponse(open(file_path, "rb"), content_type=mime_type)
        response["Content-Disposition"] = f'''attachment; filename={filename}'''

        return response
