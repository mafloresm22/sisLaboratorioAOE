class Role:
    def __init__(self, idRol=None, nombreRol=None):
        self.idRol = idRol
        self.nombreRol = nombreRol

    def to_dict(self):
        return {
            "id": self.idRol,
            "nombre": self.nombreRol
        }

