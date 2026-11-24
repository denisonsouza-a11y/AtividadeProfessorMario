from datetime import datetime

from modelo import Sala, Solicitacao


class ErroValidacao(Exception):
    pass


def _texto(valor):
    """Converte None em texto vazio e tira espaços das pontas."""
    return (valor or "").strip()


class ServicoReservas:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def criar_solicitacao(self, evento, solicitante, data, hora_inicio, hora_fim, qtd_pessoas):
        evento = _texto(evento)
        solicitante = _texto(solicitante)
        if evento == "":
            raise ErroValidacao("Informe o nome do evento.")
        if solicitante == "":
            raise ErroValidacao("Informe quem está solicitando.")
        try:
            dia = datetime.strptime(_texto(data), "%Y-%m-%d").date()
            inicio = datetime.strptime(_texto(hora_inicio), "%H:%M")
            fim = datetime.strptime(_texto(hora_fim), "%H:%M")
        except ValueError:
            raise ErroValidacao("Data ou horário em formato inválido.")
        if dia < datetime.now().date():
            raise ErroValidacao("A data do evento não pode estar no passado.")
        if fim <= inicio:
            raise ErroValidacao("O horário final deve ser depois do inicial.")
        try:
            quantidade = int(_texto(qtd_pessoas))
        except ValueError:
            raise ErroValidacao("A quantidade de pessoas deve ser um número.")
        if quantidade <= 0:
            raise ErroValidacao("A quantidade de pessoas deve ser maior que zero.")

        pedido = Solicitacao(
            None,
            evento,
            solicitante,
            dia.strftime("%Y-%m-%d"),
            inicio.strftime("%H:%M"),
            fim.strftime("%H:%M"),
            quantidade,
        )
        self.repositorio.salvar_solicitacao(pedido)

    def listar_todas(self):
        return self.repositorio.listar_solicitacoes()

    def listar_pendentes(self):
        pendentes = []
        for pedido in self.repositorio.listar_solicitacoes():
            if pedido.status == "pendente":
                pendentes.append(pedido)
        return pendentes

    def obter(self, id_pedido):
        pedido = self.repositorio.buscar_solicitacao(id_pedido)
        if pedido is None:
            raise ErroValidacao("Solicitação não encontrada.")
        return pedido

    def salas_disponiveis(self, pedido):
        ocupadas = self.repositorio.salas_ocupadas(
            pedido.data, pedido.hora_inicio, pedido.hora_fim
        )
        livres = []
        for sala in self.repositorio.listar_salas():
            if sala.capacidade >= pedido.qtd_pessoas and sala.id not in ocupadas:
                livres.append(sala)
        return livres

    def aprovar(self, id_pedido, sala_id):
        pedido = self.obter(id_pedido)
        if pedido.status != "pendente":
            raise ErroValidacao("Essa solicitação já foi analisada.")
        try:
            sala_id = int(_texto(sala_id))
        except ValueError:
            raise ErroValidacao("Escolha uma sala.")
        ids_livres = []
        for sala in self.salas_disponiveis(pedido):
            ids_livres.append(sala.id)
        if sala_id not in ids_livres:
            raise ErroValidacao("Essa sala não está disponível para este evento.")
        self.repositorio.atualizar_decisao(id_pedido, "aprovada", sala_id, None)

    def recusar(self, id_pedido, motivo):
        pedido = self.obter(id_pedido)
        if pedido.status != "pendente":
            raise ErroValidacao("Essa solicitação já foi analisada.")
        motivo = _texto(motivo)
        if motivo == "":
            raise ErroValidacao("Informe o motivo da recusa.")
        self.repositorio.atualizar_decisao(id_pedido, "recusada", None, motivo)

    def cadastrar_sala(self, nome, capacidade):
        nome = _texto(nome)
        if nome == "":
            raise ErroValidacao("Informe o nome da sala.")
        try:
            capacidade = int(_texto(capacidade))
        except ValueError:
            raise ErroValidacao("A capacidade deve ser um número.")
        if capacidade <= 0:
            raise ErroValidacao("A capacidade deve ser maior que zero.")
        self.repositorio.salvar_sala(Sala(None, nome, capacidade))

    def listar_salas(self):
        return self.repositorio.listar_salas()
