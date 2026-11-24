class Sala:
    def __init__(self, id, nome, capacidade):
        self.id = id
        self.nome = nome
        self.capacidade = capacidade


class Solicitacao:
    def __init__(self, id, evento, solicitante, data, hora_inicio, hora_fim, qtd_pessoas):
        self.id = id
        self.evento = evento
        self.solicitante = solicitante
        self.data = data
        self.hora_inicio = hora_inicio
        self.hora_fim = hora_fim
        self.qtd_pessoas = qtd_pessoas
        self.status = "pendente"
        self.sala_id = None
        self.motivo_recusa = None