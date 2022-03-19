import os
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets, views, parsers
from django_filters.rest_framework import DjangoFilterBackend

from ..base.services import delete_old_file

from . import models, serializer
from ..base.permissions import IsAuthor
from ..base.classes import MixedSerializer, Pagination


class GenreView(generics.ListAPIView):
    """ Список жанров """

    queryset = models.Genre.objects.all()
    serializer_class = serializer.GenreSerializer


class LicenseView(viewsets.ModelViewSet):
    """ CRUD лицензий автора """

    serializer_class = serializer.LicenseSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.License.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AlbumView(viewsets.ModelViewSet):
    """ CRUD альбомов автора """

    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializer.AlbumSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.Album.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()


class PublicAlbumView(generics.ListAPIView):
    """ Список публичных альбомов автора """

    serializer_class = serializer.AlbumSerializer

    def get_queryset(self):
        return models.Album.objects.filter(user__id=self.kwargs.get('pk'), private=False)


class TrackView(MixedSerializer, viewsets.ModelViewSet):
    """ CRUD треков """

    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [IsAuthor]
    serializer_class = serializer.CreateAuthorTracksSerializer
    serializer_classes_by_action = {
        'list': serializer.AuthorTrackSerializer
    }

    def get_queryset(self):
        return models.Track.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_old_file(instance.file.path)
        delete_old_file(instance.cover.path)
        instance.delete()


class PlayListView(MixedSerializer, viewsets.ModelViewSet):
    """ CRUD плейлистов пользователя """

    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [IsAuthor]
    serializer_class = serializer.CreatePlayListSerializer
    serializer_classes_by_action = {
        'list': serializer.PlayListSerializer
    }

    def get_queryset(self):
        return models.Playlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()


class TracksListView(generics.ListAPIView):
    """ Список всех треков """

    queryset = models.Track.objects.filter(album__private=False, private=False)
    serializer_class = serializer.AuthorTrackSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'user__displat_name',
                        'album__name', 'genre__name']


class AuthorTracksListView(generics.ListAPIView):
    """ Список всех треков автора """

    serializer_class = serializer.AuthorTrackSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'album__name', 'genre__name']

    def get_queryset(self):
        return models.Track.objects.filter(
            user__id=self.kwargs.get('pk'),
            album__private=False, private=False
        )


class CommentAuthorView(viewsets.ModelViewSet):
    """ CRUD коментариев автора """

    serializer_class = serializer.CommentAuthorSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.Comment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentView(viewsets.ModelViewSet):
    """ Коментарии к треку """
    
    serializer_class = serializer.CommentSerializer

    def get_queryset(self):
        return models.Comment.objects.filter(track_id=self.kwargs.get('pk'))


class StreamingFileView(views.APIView):
    """ Прослушивание трека """

    def set_play(self, track):
        track.plays_count += 1
        track.save()

    def get(self, request, pk):
        track = get_object_or_404(models.Track, id=pk)
        if os.path.exists(track.file.path):
            self.set_play(track)
            return FileResponse(open(track.file.path, 'rb'), filename=track.file.name)
        else:
            return Http404


class DownloadTrackView(views.APIView):
    """ Скачивание трека """

    def set_download(self):
        self.track.download += 1
        self.track.save()

    def get(self, request, pk):
        self.track = get_object_or_404(models.Track, id=pk)
        if os.path.exists(self.track.file.path):
            self.set_download()
            return FileResponse(
                open(self.track.file.path, 'rb'),
                filename=self.track.file.name,
                as_attachment=True
            )
        else:
            return Http404
