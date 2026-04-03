class Laboratorio:
    def __init__(self, idLaboratorios, nombreLaboratorios, estadoLaboratorios="disponible", instrument_count=0):
        self.idLaboratorios = idLaboratorios
        self.nombreLaboratorios = nombreLaboratorios
        self.estadoLaboratorios = estadoLaboratorios
        self.instrument_count = instrument_count

    def to_dict(self):
        return {
            "idLaboratorios": self.idLaboratorios,
            "nombreLaboratorios": self.nombreLaboratorios,
            "estadoLaboratorios": self.estadoLaboratorios,
            "instrument_count": self.instrument_count
        }