from flask import Flask, request, render_template, redirect, url_for
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)
TRANSPORTADORA_URL = "http://localhost:5001/soap"

@app.route('/')
def root():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template("login.html")

@app.route('/dashboard', methods=['GET'])
def dashboard():
    mensagem = request.args.get('mensagem')
    return render_template("dashboard.html", toast=mensagem)

@app.route('/enviar', methods=['POST'])
def enviar():
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
          <itens>{itens_xml}</itens>
          <destinatario>{destinatario}</destinatario>
        </RegistrarPedido>
      </soap:Body>
    </soap:Envelope>
    """

    headers = {"Content-Type": "text/xml"}
    mensagem_transportadora = "Pedido enviado."

    try:
        response = requests.post(TRANSPORTADORA_URL, data=soap_body, headers=headers)
        resposta_xml = response.text

        # Extraindo a mensagem real da resposta
        root = ET.fromstring(resposta_xml)
        ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/"}
        body = root.find("soap:Body", ns)
        status_element = body.find(".//{http://example.com/}status")
        mensagem_transportadora = status_element.text if status_element is not None else "Resposta indefinida da transportadora."
    except Exception as e:
        mensagem_transportadora = f"Erro ao enviar o pedido!"

    return redirect(url_for('dashboard', mensagem=mensagem_transportadora))

@app.route('/status', methods=['POST'])
def status():
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

    return render_template("dashboard.html", resultado_status=status, numero_consultado=numero)

if __name__ == '__main__':
    app.run(port=5000)
