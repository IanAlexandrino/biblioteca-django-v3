from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models import Colecao, Livro, Categoria, Autor
from rest_framework.authtoken.models import Token

class ColecaoAPITestCase(APITestCase):
    
    def setUp(self):
        # Criação de usuários
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.token = Token.objects.create(user=self.user1)  # Gerando o token

        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.user2_token = Token.objects.create(user=self.user2)

        # Criação de categorias
        self.categoria1 = Categoria.objects.create(nome="Categoria 1")
        self.categoria2 = Categoria.objects.create(nome="Categoria 2")

        # Criação de autor
        self.autor = Autor.objects.create(nome="Autor 1")
        
        # Criação de livros
        self.livro1 = Livro.objects.create(titulo="Livro 1", autor_id=1, categoria_id=1, publicado_em="2023-01-01")
        self.livro2 = Livro.objects.create(titulo="Livro 2", autor_id=1, categoria_id=1, publicado_em="2023-01-01")
        
        # Criação de coleção para user1
        self.colecao_user1 = Colecao.objects.create(nome="Coleção User 1", descricao="Descrição 1", colecionador=self.user1)
        self.colecao_user1.livros.set([self.livro1, self.livro2])

        # URLs
        self.list_create_url = "/api/core/colecoes/"
        self.detail_url = f"/api/core/colecoes/{self.colecao_user1.id}/"


    
    def test_criar_colecao_usuario_autenticado(self):
        """Testa a criação de uma nova coleção para um usuário autenticado"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            "nome": "Nova Coleção",
            "descricao": "Nova descrição",
            "livros": [self.livro1.id, self.livro2.id]
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Colecao.objects.count(), 2)
        self.assertEqual(Colecao.objects.last().colecionador, self.user1)
    
    def test_criar_colecao_usuario_nao_autenticado(self):
        """Testa que usuários não autenticados não podem criar coleções"""
        data = {
            "nome": "Coleção Inválida",
            "descricao": "Sem permissão",
            "livros": [self.livro1.id]
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_editar_colecao_propria(self):
        """Testa que um usuário pode editar apenas suas próprias coleções"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {"nome": "Coleção Atualizada"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.colecao_user1.refresh_from_db()
        self.assertEqual(self.colecao_user1.nome, "Coleção Atualizada")

    def test_editar_colecao_de_outro_usuario(self):
        """Testa que um usuário não pode editar coleções de outros usuários"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Autentica o usuário 2
        self.client.force_authenticate(user=self.user2)     

        data = {"nome": "Tentativa de Atualização"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_listar_colecoes(self):
        """Testa que usuários autenticados podem listar apenas suas coleções"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Corrigir a iteração para acessar a lista de coleções
        for colecao in response.data['results']:
            self.assertEqual(colecao['colecionador'], self.user1.id)

        # Ajuste para comparar corretamente o número de coleções do usuário autenticado
        self.assertEqual(len(response.data['results']), Colecao.objects.filter(colecionador=self.user1).count())

    def test_deletar_colecao_propria(self):
        """Testa que um usuário pode deletar apenas suas próprias coleções"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Colecao.objects.count(), 0)

    def test_deletar_colecao_de_outro_usuario(self):
        """Testa que um usuário não pode deletar coleções de outros usuários"""
        # Autenticar como user2
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user2_token.key)
        response = self.client.delete(self.detail_url)

        # Verifique se a resposta está correta
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

