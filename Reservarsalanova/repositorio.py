import sqlite3

from modelo import Sala, Solicitacao


class Repositorio:
    def __init__(self, caminho):
        self.caminho = caminho
        self.criar_tabelas()

    def conectar(self):
        return sqlite3.connect(self.caminho)

    def _executar(self, sql, parametros=(), buscar=False):
        """Abre a conexão, executa e fecha sempre, mesmo se der erro."""
        con = self.conectar()
        try:
            cursor = con.execute(sql, parametros)
            linhas = cursor.fetchall() if buscar else None
            con.commit()
            return linhas
        finally:
            con.close()

    def criar_tabelas(self):
        self._executar(
            "CREATE TABLE IF NOT EXISTS salas ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nome TEXT NOT NULL, "
            "capacidade INTEGER NOT NULL)"
        )
        self._executar(
            "CREATE TABLE IF NOT EXISTS solicitacoes ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "evento TEXT NOT NULL, "
            "solicitante TEXT NOT NULL, "
            "data TEXT NOT NULL, "
            "hora_inicio TEXT NOT NULL, "
            "hora_fim TEXT NOT NULL, "
            "qtd_pessoas INTEGER NOT NULL, "
            "status TEXT NOT NULL, "
            "sala_id INTEGER, "
            "motivo_recusa TEXT)"
        )

    def salvar_sala(self, sala):
        self._executar(
            "INSERT INTO salas (nome, capacidade) VALUES (?, ?)",
            (sala.nome, sala.capacidade),
        )

    def listar_salas(self):
        linhas = self._executar(
            "SELECT id, nome, capacidade FROM salas ORDER BY nome", buscar=True
        )
        salas = []
        for linha in linhas:
            salas.append(Sala(linha[0], linha[1], linha[2]))
        return salas

    def salvar_solicitacao(self, pedido):
        self._executar(
            "INSERT INTO solicitacoes "
            "(evento, solicitante, data, hora_inicio, hora_fim, qtd_pessoas, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                pedido.evento,
                pedido.solicitante,
                pedido.data,
                pedido.hora_inicio,
                pedido.hora_fim,
                pedido.qtd_pessoas,
                pedido.status,
            ),
        )

    @staticmethod
    def _montar_solicitacao(linha):
        pedido = Solicitacao(
            linha[0], linha[1], linha[2], linha[3], linha[4], linha[5], linha[6]
        )
        pedido.status = linha[7]
        pedido.sala_id = linha[8]
        pedido.motivo_recusa = linha[9]
        return pedido

    _COLUNAS = (
        "SELECT id, evento, solicitante, data, hora_inicio, hora_fim, "
        "qtd_pessoas, status, sala_id, motivo_recusa FROM solicitacoes"
    )

    def listar_solicitacoes(self):
        linhas = self._executar(
            self._COLUNAS + " ORDER BY data, hora_inicio", buscar=True
        )
        pedidos = []
        for linha in linhas:
            pedidos.append(self._montar_solicitacao(linha))
        return pedidos

    def buscar_solicitacao(self, id_pedido):
        linhas = self._executar(
            self._COLUNAS + " WHERE id = ?", (id_pedido,), buscar=True
        )
        if not linhas:
            return None
        return self._montar_solicitacao(linhas[0])

    def atualizar_decisao(self, id_pedido, status, sala_id, motivo):
        self._executar(
            "UPDATE solicitacoes SET status = ?, sala_id = ?, motivo_recusa = ? "
            "WHERE id = ?",
            (status, sala_id, motivo, id_pedido),
        )

    def salas_ocupadas(self, data, hora_inicio, hora_fim):
        # Dois horários se chocam quando um começa antes do outro terminar.
        linhas = self._executar(
            "SELECT sala_id FROM solicitacoes "
            "WHERE status = 'aprovada' AND data = ? "
            "AND hora_inicio < ? AND hora_fim > ?",
            (data, hora_fim, hora_inicio),
            buscar=True,
        )
        ocupadas = []
        for linha in linhas:
            if linha[0] is not None:
                ocupadas.append(linha[0])
        return ocupadas


if __name__ == "__main__":
    repo = Repositorio("teste.db")

    nome = input("Nome da sala: ")
    capacidade = int(input("Capacidade da sala: "))
    repo.salvar_sala(Sala(None, nome, capacidade))

    evento = input("Nome do evento: ")
    solicitante = input("Quem está solicitando: ")
    data = input("Data (AAAA-MM-DD): ")
    hora_inicio = input("Horário de início (HH:MM): ")
    hora_fim = input("Horário de fim (HH:MM): ")
    qtd_pessoas = int(input("Quantidade de pessoas: "))
    repo.salvar_solicitacao(
        Solicitacao(None, evento, solicitante, data, hora_inicio, hora_fim, qtd_pessoas)
    )

    print("Salas cadastradas:")
    for sala in repo.listar_salas():
        print(sala.id, sala.nome, sala.capacidade)

    print("Solicitações cadastradas:")
    for pedido in repo.listar_solicitacoes():
        print(pedido.id, pedido.evento, pedido.data, pedido.status)
