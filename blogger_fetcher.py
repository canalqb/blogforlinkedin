#!/usr/bin/env python3
"""
Blogger API Fetcher
@CanalQb - Sistema de Automação Blogger → LinkedIn
Busca posts do Blogger via API para postagem automatizada
"""

import requests
import yaml
import logging
from datetime import datetime
from typing import List, Dict, Optional

class BloggerFetcher:
    """Classe para buscar posts do Blogger via API"""
    
    def __init__(self, config_file: str = "config.yml"):
        """Inicializa o fetcher com configuração do YAML"""
        self.config = self._load_config(config_file)
        self.blog_id = self.config['blogger']['blog_id']
        self.api_key = self.config['blogger']['api_key']
        self._setup_logging()
    
    def _load_config(self, config_file: str) -> Dict:
        """Carrega configuração do arquivo YAML"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de configuração {config_file} não encontrado")
        except yaml.YAMLError as e:
            raise ValueError(f"Erro ao ler YAML: {e}")
    
    def _setup_logging(self):
        """Configura logging baseado no config"""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        log_file = self.config.get('logging', {}).get('file', 'automation.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def fetch_posts(self, max_results: int = 10) -> List[Dict]:
        """
        Busca posts do Blogger via API
        
        Args:
            max_results: Número máximo de posts a buscar
            
        Returns:
            Lista de posts do Blogger
        """
        url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts"
        params = {
            'key': self.api_key,
            'maxResults': max_results,
            'orderBy': 'published',  # Ordena por data de publicação
            'status': 'live'  # Apenas posts publicados
        }
        
        try:
            self.logger.info(f"Buscando posts do Blogger (blog_id: {self.blog_id})")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('items', [])
            
            self.logger.info(f"{len(posts)} posts encontrados")
            return posts
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao buscar posts: {e}")
            raise
    
    def get_oldest_unpublished_post(self, published_posts: List[str] = None) -> Optional[Dict]:
        """
        Retorna o post mais antigo não publicado no LinkedIn
        
        Args:
            published_posts: Lista de URLs de posts já publicados
            
        Returns:
            Post mais antigo não publicado ou None
        """
        if published_posts is None:
            published_posts = []
        
        posts = self.fetch_posts(max_results=50)
        
        # Ordena do mais antigo para o mais novo
        posts.sort(key=lambda x: x['published'])
        
        # Busca o primeiro post não publicado
        for post in posts:
            post_url = post.get('url', '')
            if post_url not in published_posts:
                self.logger.info(f"Post mais antigo não encontrado: {post.get('title', 'Sem título')}")
                return post
        
        self.logger.info("Todos os posts já foram publicados")
        return None
    
    def get_post_details(self, post_id: str) -> Dict:
        """
        Busca detalhes de um post específico
        
        Args:
            post_id: ID do post
            
        Returns:
            Detalhes do post
        """
        url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/{post_id}"
        params = {'key': self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao buscar detalhes do post {post_id}: {e}")
            raise
    
    def format_post_for_linkedin(self, post: Dict) -> Dict:
        """
        Formata post do Blogger para postagem no LinkedIn
        
        Args:
            post: Post do Blogger
            
        Returns:
            Dicionário com dados formatados para LinkedIn
        """
        template = self.config.get('post_template', {})
        
        title = post.get('title', 'Sem título')
        url = post.get('url', '')
        content = post.get('content', '')
        
        # Extrai resumo do conteúdo (primeiro parágrafo)
        summary = content.split('\n')[0][:200] if content else ''
        
        # Aplica template
        headline = template.get('headline', '🚀 Novo post no @CanalQb!')
        commentary = template.get('commentary', 'Acabei de publicar um novo conteúdo sobre {title}. Confira agora!')
        commentary = commentary.format(title=title)
        
        hashtags = template.get('hashtags', '#tecnologia #automacao #desenvolvimento #CanalQb')
        
        return {
            'title': title,
            'url': url,
            'summary': summary,
            'headline': headline,
            'commentary': commentary,
            'hashtags': hashtags,
            'visibility': template.get('visibility', 'PUBLIC')
        }


if __name__ == "__main__":
    # Teste do fetcher
    fetcher = BloggerFetcher()
    posts = fetcher.fetch_posts(max_results=5)
    
    print(f"\n=== Posts Encontrados ===")
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post.get('title', 'Sem título')}")
        print(f"   URL: {post.get('url', '')}")
        print(f"   Data: {post.get('published', '')}")
