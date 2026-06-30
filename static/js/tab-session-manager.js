/**
 * Tab Session Manager
 * Gerencia sessões isoladas por aba do navegador
 * Permite múltiplos roles/perfis abertos em diferentes abas
 */

class TabSessionManager {
    constructor() {
        this.tabId = this.initializeTabId();
        this.apiBaseUrl = '/users/api/tabs';
        this.refreshInterval = 60000; // 1 minuto
        this.init();
    }

    /**
     * Inicializa o tabId para esta aba
     * Recupera de sessionStorage se existir, caso contrário cria um novo
     */
    initializeTabId() {
        // Tenta recuperar tabId do sessionStorage (específico desta aba)
        let tabId = sessionStorage.getItem('chaplin_tab_id');
        
        if (!tabId) {
            // Se não existe, registra nova aba
            this.registerNewTab();
        }
        
        return tabId;
    }

    /**
     * Registra uma nova aba no servidor
     */
    registerNewTab() {
        // Gera um tabId temporário localmente
        const tempTabId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
        
        sessionStorage.setItem('chaplin_tab_id', tempTabId);
        this.tabId = tempTabId;
        console.log('✓ Nova aba registrada localmente:', this.tabId.substring(0, 8));
        
        // Tenta registrar no servidor (não-crítico)
        fetch(`${this.apiBaseUrl}/register/?tab_id=${tempTabId}`)
            .then(res => res.json())
            .then(data => {
                console.log('✓ Servidor confirmou registro de aba');
            })
            .catch(err => console.warn('⚠ Aviso ao registrar no servidor (não crítico):', err));
    }

    /**
     * Inicializa o Tab Session Manager
     */
    init() {
        if (!this.tabId) {
            console.warn('⚠ Sem tabId ainda, aguardando registro...');
            // Tenta novamente em 500ms
            setTimeout(() => this.init(), 500);
            return;
        }

        // Configura interceptador para enviar tabId em todas as requisições
        this.setupRequestInterceptor();
        
        // Atualiza status periodicamente
        this.startStatusRefresh();
        
        // Limpa sessão ao fechar a aba
        window.addEventListener('beforeunload', () => this.onTabClose());
        
        console.log('✓ Tab Session Manager inicializado para aba:', this.tabId.substring(0, 8));
    }

    /**
     * Configura interceptador de requisições fetch
     * Adiciona tabId em todos os headers
     */
    setupRequestInterceptor() {
        const originalFetch = window.fetch;
        
        window.fetch = function(...args) {
            const [resource, config = {}] = args;
            
            // Não adiciona para requisições da API de tabs (evita loop)
            if (typeof resource === 'string' && !resource.includes('/api/tabs/')) {
                // Adiciona tabId no header
                config.headers = config.headers || {};
                config.headers['X-Tab-Id'] = sessionStorage.getItem('chaplin_tab_id');
            }
            
            return originalFetch.apply(this, [resource, config]);
        };
    }

    /**
     * Faz login nesta aba específica
     */
    login(username, password) {
        return fetch(`${this.apiBaseUrl}/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tab_id: this.tabId,
                username: username,
                password: password
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log('✓ Login bem-sucedido nesta aba como:', data.role);
                // Atualiza UI se necessário
                this.updateUIAfterLogin(data);
            }
            return data;
        });
    }

    /**
     * Faz logout desta aba específica
     */
    logout() {
        return fetch(`${this.apiBaseUrl}/logout/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tab_id: this.tabId
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log('✓ Logout realizado nesta aba');
                sessionStorage.removeItem('chaplin_tab_id');
            }
            return data;
        });
    }

    /**
     * Retorna o status da sessão desta aba
     */
    getStatus() {
        return fetch(`${this.apiBaseUrl}/status/`, {
            headers: {
                'X-Tab-Id': this.tabId
            }
        })
        .then(res => res.json());
    }

    /**
     * Inicia atualização periódica de status
     */
    startStatusRefresh() {
        setInterval(() => {
            this.getStatus()
                .then(data => {
                    if (!data.is_authenticated) {
                        // Se ficou desautenticado, redireciona para login
                        console.log('⚠ Sessão expirou');
                        window.location.href = '/users/login/';
                    }
                })
                .catch(err => console.error('Erro ao atualizar status:', err));
        }, this.refreshInterval);
    }

    /**
     * Chamado quando a aba vai ser fechada
     */
    onTabClose() {
        // Envia logout de forma síncrona
        const tabId = sessionStorage.getItem('chaplin_tab_id');
        if (tabId) {
            navigator.sendBeacon(`${this.apiBaseUrl}/logout/`, JSON.stringify({
                tab_id: tabId
            }));
        }
    }

    /**
     * Atualiza UI após login
     */
    updateUIAfterLogin(data) {
        // Atualiza informações de role exibidas na UI se necessário
        const roleDisplay = document.querySelector('[data-role-display]');
        if (roleDisplay) {
            const roleMap = {
                'admin': 'Administrador',
                'gestor': 'Gestor do Prédio',
                'lider': 'Líder de Equipe',
                'colaborador': 'Colaborador',
            };
            roleDisplay.textContent = roleMap[data.role] || data.role;
        }
    }

    /**
     * Lista todas as abas ativas
     */
    listActiveTabs() {
        return fetch(`${this.apiBaseUrl}/active/`, {
            headers: {
                'X-Tab-Id': this.tabId
            }
        })
        .then(res => res.json());
    }
}

// Inicializa o Tab Session Manager quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.tabSessionManager = new TabSessionManager();
    });
} else {
    window.tabSessionManager = new TabSessionManager();
}
