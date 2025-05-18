# 🧾 Sistema de Integração Compras e Transportadora via SOAP

Este projeto demonstra a comunicação entre dois sistemas distintos via SOAP usando Flask e XML puro.  
São duas aplicações Flask independentes:

- **Compras (Cliente SOAP)** – Envia requisições SOAP com informações de pedidos.
- **Transportadora (Servidor SOAP)** – Recebe, processa e responde às requisições SOAP.

---

## 📦 Requisitos

- Python 3.8+
- `venv` (ambiente virtual)

---

## ⚙️ Configuração do Ambiente

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/logisync.git
cd logisync
```

2. Crie o ambiente virtual
### Linux / Mac/OS
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```
3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🔁 Como Funciona a Comunicação SOAP
1. O sistema Compras cria uma requisição SOAP em XML com dados do pedido.
2. Ele envia essa requisição via HTTP POST para o endpoint do servidor da Transportadora.
3. A Transportadora interpreta o XML, executa a lógica de negócios e responde com um XML SOAP.
4. O cliente exibe a resposta, por exemplo, o status da entrega ou confirmação de recebimento.
5. Toda a comunicação ocorre com XML puro sobre HTTP, conforme o padrão SOAP 1.1.
