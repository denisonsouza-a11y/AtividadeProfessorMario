from flask import Flask, flash, redirect, render_template, request, url_for

from repositorio import Repositorio
from servicos import ErroValidacao, ServicoReservas

app = Flask(__name__)
app.secret_key = "chaveficticiadedemonstracao"

servico = ServicoReservas(Repositorio("reservar_sala.db"))


@app.template_filter("data_br")
def data_br(valor):
    """Mostra AAAA-MM-DD como DD/MM/AAAA nas telas."""
    try:
        ano, mes, dia = valor.split("-")
        return f"{dia}/{mes}/{ano}"
    except (AttributeError, ValueError):
        return valor


def nomes_das_salas():
    nomes = {}
    for sala in servico.listar_salas():
        nomes[sala.id] = sala.nome
    return nomes


@app.route("/")
def inicio():
    return render_template("inicio.html")


@app.route("/caex/nova", methods=["GET", "POST"])
def nova_solicitacao():
    if request.method == "POST":
        try:
            servico.criar_solicitacao(
                request.form.get("evento", ""),
                request.form.get("solicitante", ""),
                request.form.get("data", ""),
                request.form.get("hora_inicio", ""),
                request.form.get("hora_fim", ""),
                request.form.get("qtd_pessoas", ""),
            )
        except ErroValidacao as erro:
            flash(str(erro), "erro")
            return render_template("novat.html", form=request.form)

        flash("Solicitação enviada. Acompanhe o status abaixo.", "ok")
        return redirect(url_for("status"))
    return render_template("novat.html", form={})


@app.route("/caex/status")
def status():
    return render_template(
        "StatusCaex.html",
        solicitacoes=servico.listar_todas(),
        nomes_salas=nomes_das_salas(),
    )


@app.route("/admin")
def admin():
    return render_template("adm.html", solicitacoes=servico.listar_pendentes())


@app.route("/admin/solicitacao/<int:id_pedido>")
def detalhe(id_pedido):
    try:
        pedido = servico.obter(id_pedido)
    except ErroValidacao as erro:
        flash(str(erro), "erro")
        return redirect(url_for("admin"))
    return render_template(
        "aprvrecus.html",
        s=pedido,
        salas=servico.salas_disponiveis(pedido),
        nomes_salas=nomes_das_salas(),
    )


@app.route("/admin/solicitacao/<int:id_pedido>/aprovar", methods=["POST"])
def aprovar(id_pedido):
    try:
        servico.aprovar(id_pedido, request.form.get("sala_id", ""))
    except ErroValidacao as erro:
        flash(str(erro), "erro")
        return redirect(url_for("detalhe", id_pedido=id_pedido))
    flash("Solicitação aprovada.", "ok")
    return redirect(url_for("admin"))


@app.route("/admin/solicitacao/<int:id_pedido>/recusar", methods=["POST"])
def recusar(id_pedido):
    try:
        servico.recusar(id_pedido, request.form.get("motivo", ""))
    except ErroValidacao as erro:
        flash(str(erro), "erro")
        return redirect(url_for("detalhe", id_pedido=id_pedido))
    flash("Solicitação recusada.", "ok")
    return redirect(url_for("admin"))


@app.route("/salas", methods=["GET", "POST"])
def salas():
    if request.method == "POST":
        try:
            servico.cadastrar_sala(
                request.form.get("nome", ""), request.form.get("capacidade", "")
            )
        except ErroValidacao as erro:
            flash(str(erro), "erro")
        else:
            flash("Sala cadastrada.", "ok")
        return redirect(url_for("salas"))
    return render_template("salas.html", salas=servico.listar_salas())


if __name__ == "__main__":
    app.run(debug=True, port=5001)
