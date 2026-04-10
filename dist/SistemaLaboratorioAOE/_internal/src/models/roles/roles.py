class Role:
    def __init__(self, idRol=None, nombreRol=None, users=0):
        self.idRol = idRol
        self.nombreRol = nombreRol
        self.users = users

    def to_dict(self):
        return {
            "idRol": self.idRol,
            "nombreRol": self.nombreRol,
            "users": self.users
        }

