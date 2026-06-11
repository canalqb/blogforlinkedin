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
        
        # Log das credenciais (sem valores sensíveis)
        self.logger.info(f"Client ID configurado: {'Sim' if self.client_id else 'Não'}")
        self.logger.info(f"Access Token configurado: {'Sim' if self.access_token else 'NÃO - ERRO'}")
        self.logger.info(f"Refresh Token configurado: {'Sim' if self.refresh_token else 'Não'}")
    
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
    
    def _clean_sub(self, sub: str) -> str:
        """
        Remove prefixos inválidos do sub do LinkedIn
        """
        if not sub:
            raise ValueError("sub vazio")
        
        # Remove prefixos que quebram a UGC API
        cleaned = (
            sub.replace("l_", "")
               .replace("urn:li:person:", "")
               .replace("urn:li:member:", "")
        )
        
        # Validação forte
        if len(cleaned) < 5:
            raise ValueError(f"sub inválido após limpeza: {sub} -> {cleaned}")
        
        return cleaned
    
    def get_person_urn(self) -> str:
        """
        Usa OpenID Connect (/v2/userinfo) para obter identidade.
        Compatível com scopes: openid, profile (sem r_liteprofile)
        
        Returns:
            Member URN no formato urn:li:member:{sub}
        """
        url = "https://api.linkedin.com/v2/userinfo"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        self.logger.info("Buscando identidade via userinfo...")
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                self.logger.error(f"userinfo falhou: {response.status_code} {response.text}")
                raise RuntimeError("Não foi possível obter userinfo (token inválido ou scope faltando)")
            
            data = response.json()
            sub = data.get("sub")
            
            if not sub:
                raise RuntimeError("Campo 'sub' não encontrado no userinfo")
            
            # Limpa o sub para remover prefixos inválidos
            cleaned_sub = self._clean_sub(sub)
            
            # URN correto para UGC API usando sub limpo do OpenID
            urn = f"urn:li:member:{cleaned_sub}"
            
            self.logger.info(f"URN gerado: {urn}")
            return urn
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao buscar userinfo: {e}")
            raise
    
    def post_to_linkedin(self, post_data: Dict) -> Optional[str]:
        """
        Posta no LinkedIn usando a API UGC (mais estável)
        
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
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        
        # Formata o texto do post
        commentary = post_data.get('commentary', '')
        hashtags = post_data.get('hashtags', '')
        post_url = post_data.get('url', '')
        title = post_data.get('title', '')
        
        # Texto completo do post
        full_text = f"{commentary}\n\n{post_url}\n\n{hashtags}"
        
        # Payload da requisição (API UGC)
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
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            self.logger.info(f"Postando no LinkedIn: {title}")
            self.logger.debug(f"Payload: {payload}")
            response = requests.post(url, headers=headers, json=payload)
            
            # Log detalhado em caso de erro
            if response.status_code != 201:
                self.logger.error(f"Status Code: {response.status_code}")
                self.logger.error(f"Response Headers: {dict(response.headers)}")
                self.logger.error(f"Response Body: {response.text}")
            
            response.raise_for_status()
            
            # Retorna o ID do post criado
            post_id = response.headers.get('X-RestLi-Id')
            self.logger.info(f"Post criado com sucesso! ID: {post_id}")
            
            return post_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao postar no LinkedIn: {e}")
            
            # Retry seguro apenas se token expirou (401)
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 401:
                    self.logger.warning("Token expirado. Renovando...")
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
