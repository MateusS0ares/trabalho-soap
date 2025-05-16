from flask import Flask, request, render_template, redirect
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

TRANSPORTADORA_URL = "http://localhost:5001/soap"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        numero = request.form['numero']
        destinatario = request.form['destinatario']
        endereco = request.form['endereco']
        nomes = request.form.getlist('item_nome[]')
        qtds = request.form.getlist('item_qtd[]')

        # Monta itens em XML
        itens_xml = ""
        for nome, qtd in zip(nomes, qtds):
            itens_xml += f"""
            <item>
              <nome>{nome}</nome>
              <quantidade>{qtd}</quantidade>
            </item>
            """

        soap_body = f"""<?xml version="1.0"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <RegistrarPedido xmlns="http://example.com/">
              <numero>{numero}</numero>
              <endereco>{endereco}</endereco>
              <itens>
                {itens_xml}
              </itens>
              <destinatario>{destinatario}</destinatario>
            </RegistrarPedido>
          </soap:Body>
        </soap:Envelope>
        """

        headers = {"Content-Type": "text/xml"}
        try:
            response = requests.post(TRANSPORTADORA_URL, data=soap_body, headers=headers)
            print("Resposta da transportadora:", response.text)
        except Exception as e:
            print("Erro ao enviar pedido:", e)

        return redirect('/')
    return render_template("index.html")

@app.route('/status', methods=['GET', 'POST'])
def status():
    if request.method == 'POST':
        numero = request.form.get("numero")

        soap_body = f"""<?xml version="1.0"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <ConsultarStatus xmlns="http://example.com/">
              <numero>{numero}</numero>
            </ConsultarStatus>
          </soap:Body>
        </soap:Envelope>
        """

        headers = {"Content-Type": "text/xml"}
        try:
            response = requests.post(TRANSPORTADORA_URL, data=soap_body, headers=headers)
            resposta_xml = response.text

            # Parse da resposta SOAP
            root = ET.fromstring(resposta_xml)
            ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/"}
            body = root.find("soap:Body", ns)
            status_element = body.find(".//{http://example.com/}status")
            status = status_element.text if status_element is not None else "Não encontrado"
        except Exception as e:
            print("Erro ao consultar status:", e)
            status = "Erro ao consultar"

        return render_template("status.html", numero=numero, status=status)

    return render_template("status_form.html")

if __name__ == '__main__':
    app.run(port=5000)
