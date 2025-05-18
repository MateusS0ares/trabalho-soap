from flask import Flask, request, Response, render_template, redirect, url_for
import xml.etree.ElementTree as ET

app = Flask(__name__)
pedidos = {}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', pedidos=pedidos)

@app.route('/atualizar_status', methods=['POST'])
def atualizar_status():
    numero = request.form.get('numero')
    novo_status = request.form.get('status')
    if numero in pedidos:
        pedidos[numero]['status'] = novo_status
    return redirect(url_for('index'))

@app.route('/soap', methods=['POST'])
def soap_service():
    xml = request.data
    root = ET.fromstring(xml)

    namespaces = {
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'ns': 'http://example.com/'
    }

    body = root.find('soap:Body', namespaces)
    pedido_xml = body.find('ns:RegistrarPedido', namespaces)

    if pedido_xml is not None:
        numero = pedido_xml.find('ns:numero', namespaces).text
        endereco = pedido_xml.find('ns:endereco', namespaces).text
        destinatario = pedido_xml.find('ns:destinatario', namespaces).text

        # Lê múltiplos itens
        itens_xml = pedido_xml.find('ns:itens', namespaces)
        itens = []
        for item in itens_xml.findall('ns:item', namespaces):
            nome = item.find('ns:nome', namespaces).text
            qtd = item.find('ns:quantidade', namespaces).text
            itens.append({'nome': nome, 'quantidade': qtd})

        pedidos[numero] = {
            "destinatario": destinatario,
            "endereco": endereco,
            "itens": itens,
            "status": "Aguardando coleta"
        }

        print(f"Pedido {numero} de {destinatario} com {len(itens)} itens recebido.")

        resposta = f"""<?xml version="1.0"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <RegistrarPedidoResponse xmlns="http://example.com/">
              <status>✅ Pedido registrado com sucesso e enviado para a transportadora!</status>
            </RegistrarPedidoResponse>
          </soap:Body>
        </soap:Envelope>
        """
        return Response(resposta, mimetype='text/xml')

    elif body.find('ns:ConsultarStatus', namespaces) is not None:
        consulta_xml = body.find('ns:ConsultarStatus', namespaces)
        numero = consulta_xml.find('ns:numero', namespaces).text
        status = pedidos.get(numero, {}).get("status", "Pedido não encontrado")

        resposta = f"""<?xml version="1.0"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <ConsultarStatusResponse xmlns="http://example.com/">
              <status>{status}</status>
            </ConsultarStatusResponse>
          </soap:Body>
        </soap:Envelope>
        """
        return Response(resposta, mimetype='text/xml')

    return Response("Operação não reconhecida", status=400)

if __name__ == '__main__':
    app.run(port=5001)
