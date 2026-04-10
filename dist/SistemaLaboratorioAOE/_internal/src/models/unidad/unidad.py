class Unidad:
    def __init__(self, idUnidad=None, nombreUnidad=None):
        self.idUnidad = idUnidad
        self.nombreUnidad = nombreUnidad

    def to_dict(self):
        return {
            "idUnidad": self.idUnidad,
            "nombreUnidad": self.nombreUnidad
        }

