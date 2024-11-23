from rest_framework import generics, permissions
from .models import Livro, Categoria, Autor, Colecao
from .serializers import LivroSerializer, CategoriaSerializer, AutorSerializer, ColecaoSerializer
from .filters import LivroFilter, CategoriaFilter, AutorFilter
from .custom_permissions import IsColecionadorOrReadOnly

class LivroList(generics.ListCreateAPIView):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    filterset_class = LivroFilter
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['titulo', 'autor', 'categoria', 'publicado_em']
    search_fields = ['^titulo', '^autor__nome', '^categoria__nome']

class LivroDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    name = "livro-detail"
    permission_classes = [permissions.IsAuthenticated]

class CategoriaList(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filterset_class = CategoriaFilter
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['nome']
    search_fields = ['^nome']

class CategoriaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    name = "categoria-detail"
    permission_classes = [permissions.IsAuthenticated]

class AutorList(generics.ListCreateAPIView):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    filterset_class = AutorFilter
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['nome']
    search_fields = ['^nome']

class AutorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    name = "autor-detail"
    permission_classes = [permissions.IsAuthenticated]

class ColecaoListCreate(generics.ListCreateAPIView):
    serializer_class = ColecaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['nome', 'descricao', 'colecionador']
    search_fields = ['^nome', '^descricao', 'colecionador__username']

    def get_queryset(self):
        return Colecao.objects.filter(colecionador=self.request.user)

    def perform_create(self, serializer):
        serializer.save(colecionador=self.request.user)


class ColecaoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Colecao.objects.all()
    serializer_class = ColecaoSerializer
    name = "colecao-detail"
    permission_classes = [permissions.IsAuthenticated, IsColecionadorOrReadOnly]

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        return super().delete(request, *args, **kwargs)