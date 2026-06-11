#!/usr/bin/env python3
"""
Main Automation Script
@CanalQb - Sistema de Automação Blogger → LinkedIn
Integra o fetcher do Blogger com o poster do LinkedIn
"""

import logging
import json
import os
from blogger_fetcher import BloggerFetcher
from linkedin_poster import LinkedInPoster

class BlogToLinkedInAutomation:
    """Classe principal de automação"""
    
    def __init__(self, config_file: str = "config.yml"):
        """Inicializa a automação"""
        self.fetcher = BloggerFetcher(config_file)
        self.poster = LinkedInPoster(config_file)
        self.logger = logging.getLogger(__name__)
        
        # Arquivo para rastrear posts publicados
        self.published_file = "published_posts.json"
        self.published_posts = self._load_published_posts()
    
    def _load_published_posts(self) -> list:
        """Carrega lista de posts já publicados"""
        if os.path.exists(self.published_file):
            try:
                with open(self.published_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Erro ao carregar posts publicados: {e}")
                return []
        return []
    
    def _save_published_posts(self):
        """Salva lista de posts publicados"""
        try:
            with open(self.published_file, 'w', encoding='utf-8') as f:
                json.dump(self.published_posts, f, indent=2)
            self.logger.info(f"Posts publicados salvos em {self.published_file}")
        except IOError as e:
            self.logger.error(f"Erro ao salvar posts publicados: {e}")
    
    def run(self):
        """Executa a automação completa"""
        try:
            self.logger.info("=== Iniciando automação Blogger → LinkedIn ===")
            
            # Busca o post mais antigo não publicado
            post = self.fetcher.get_oldest_unpublished_post(self.published_posts)
            
            if not post:
                self.logger.info("Nenhum post para publicar. Todos já foram publicados.")
                return
            
            # Formata o post para LinkedIn
            linkedin_post = self.fetcher.format_post_for_linkedin(post)
            
            # Posta no LinkedIn
            post_id = self.poster.post_to_linkedin(linkedin_post)
            
            if post_id:
                # Adiciona à lista de publicados
                self.published_posts.append(post.get('url', ''))
                self._save_published_posts()
                
                self.logger.info(f"✅ Post publicado com sucesso! ID: {post_id}")
                self.logger.info(f"   Título: {post.get('title', 'Sem título')}")
                self.logger.info(f"   URL: {post.get('url', '')}")
            else:
                self.logger.error("❌ Falha ao publicar post")
                
        except Exception as e:
            self.logger.error(f"Erro na automação: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    # Executa a automação
    automation = BlogToLinkedInAutomation()
    automation.run()
