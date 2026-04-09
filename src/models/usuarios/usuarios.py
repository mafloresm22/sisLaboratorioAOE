class Usuario:
    def __init__(self, idUsuarios=None, nombreUsuarios=None, rolId=None, nombreRol=None, nombresCompletosUsuarios=None, apellidosCompletosUsuarios=None):
        self.idUsuarios = idUsuarios
        self.nombreUsuarios = nombreUsuarios
        self.nombresCompletosUsuarios = nombresCompletosUsuarios
        self.apellidosCompletosUsuarios = apellidosCompletosUsuarios
        self.rolId = rolId
        self.nombreRol = nombreRol

    def to_dict(self):
        return {
            "idUsuarios": self.idUsuarios,
            "nombreUsuarios": self.nombreUsuarios,
            "nombresCompletosUsuarios": self.nombresCompletosUsuarios,
            "apellidosCompletosUsuarios": self.apellidosCompletosUsuarios,
            "rolId": self.rolId,
            "nombreRol": self.nombreRol
        }
