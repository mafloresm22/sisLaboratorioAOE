class Laboratorio:
    def __init__(self, idLaboratorios, nombreLaboratorios, pisoLaboratorios, estadoLaboratorios="disponible", instrument_count=0):
        self.idLaboratorios = idLaboratorios
        self.nombreLaboratorios = nombreLaboratorios
        self.pisoLaboratorios = pisoLaboratorios
        self.estadoLaboratorios = estadoLaboratorios
        self.instrument_count = instrument_count

    def to_dict(self):
        return {
            "idLaboratorios": self.idLaboratorios,
            "nombreLaboratorios": self.nombreLaboratorios,
            "pisoLaboratorios": self.pisoLaboratorios,
            "estadoLaboratorios": self.estadoLaboratorios,
            "instrument_count": self.instrument_count
        }