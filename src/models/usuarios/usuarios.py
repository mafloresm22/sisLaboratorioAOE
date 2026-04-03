class Usuario:
    def __init__(self, idUsuarios=None, nombreUsuarios=None, rolId=None, nombreRol=None):
        self.idUsuarios = idUsuarios
        self.nombreUsuarios = nombreUsuarios
        self.rolId = rolId
        self.nombreRol = nombreRol

    def to_dict(self):
        return {
            "idUsuarios": self.idUsuarios,
            "nombreUsuarios": self.nombreUsuarios,
            "rolId": self.rolId,
            "nombreRol": self.nombreRol
        }
