#!/usr/bin/env python3
"""
LinkedIn API Poster
@CanalQb - Sistema de Automação Blogger → LinkedIn
Posta links do Blogger no LinkedIn via API
"""

import requests
import yaml
import logging
from typing import Dict, Optional

class LinkedInPoster:
    """Classe para postar no LinkedIn via API"""
    
    def __init__(self, config_file: str = "config.yml"):
        """Inicializa o poster com configuração do YAML"""
        self.config = self._load_config(config_file)
        self.client_id = self.config['linkedin']['client_id']
        self.client_secret = self.config['linkedin']['client_secret']
        self.redirect_uri = self.config['linkedin']['redirect_uri']
        self.access_token = self.config['linkedin'].get('access_token', '')
        self.refresh_token = self.config['linkedin'].get('refresh_token', '')
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
    
    def refresh_access_token(self) -> str:
        """
        Renova o access token usando o refresh token
        
        Returns:
            Novo access token
        """
        if not self.refresh_token:
            raise ValueError("Refresh token não configurado")
        
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            self.logger.info("Renovando access token...")
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.logger.info("Access token renovado com sucesso")
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao renovar token: {e}")
            raise
    
    def get_person_urn(self) -> str:
        """
        Busca o URN da pessoa autenticada
        
        Returns:
            URN da pessoa (ex: urn:li:person:ABC123)
        """
        url = "https://api.linkedin.com/v2/userinfo"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            user_info = response.json()
            sub = user_info.get('sub', '')
            
            # Formato esperado: l_ABC123 -> urn:li:person:ABC123
            person_urn = f"urn:li:person:{sub.replace('l_', '')}"
            
            self.logger.info(f"Person URN: {person_urn}")
            return person_urn
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao buscar person URN: {e}")
            raise
    
    def post_to_linkedin(self, post_data: Dict) -> Optional[str]:
        """
        Posta no LinkedIn usando a API UGC
        
        Args:
            post_data: Dicionário com dados do post (title, url, commentary, hashtags, visibility)
            
        Returns:
            ID do post criado ou None em caso de erro
        """
        if not self.access_token:
            raise ValueError("Access token não configurado")
        
        # Busca Person URN
        person_urn = self.get_person_urn()
        
        # Constrói o post
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        
        # Formata o texto do post
        commentary = post_data.get('commentary', '')
        hashtags = post_data.get('hashtags', '')
        post_url = post_data.get('url', '')
        title = post_data.get('title', '')
        
        # Texto completo do post
        full_text = f"{commentary}\n\n{post_url}\n\n{hashtags}"
        
        # Payload da requisição
        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": full_text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": post_data.get('visibility', 'PUBLIC')
            }
        }
        
        try:
            self.logger.info(f"Postando no LinkedIn: {title}")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Retorna o ID do post criado
            post_id = response.headers.get('X-RestLi-Id')
            self.logger.info(f"Post criado com sucesso! ID: {post_id}")
            
            return post_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao postar no LinkedIn: {e}")
            if response.status_code == 401:
                self.logger.warning("Token expirado, tentando renovar...")
                self.refresh_access_token()
                # Tenta novamente
                headers['Authorization'] = f'Bearer {self.access_token}'
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                post_id = response.headers.get('X-RestLi-Id')
                self.logger.info(f"Post criado com sucesso após renovação! ID: {post_id}")
                return post_id
            raise


if __name__ == "__main__":
    # Teste do poster
    poster = LinkedInPoster()
    
    # Exemplo de post
    test_post = {
        'title': 'Teste de Postagem Automática',
        'url': 'https://canalqb.com.br/',
        'commentary': 'Testando postagem automática do Blogger para LinkedIn',
        'hashtags': '#tecnologia #automacao #CanalQb',
        'visibility': 'PUBLIC'
    }
    
    try:
        post_id = poster.post_to_linkedin(test_post)
        print(f"\nPost criado com ID: {post_id}")
    except Exception as e:
        print(f"\nErro: {e}")
