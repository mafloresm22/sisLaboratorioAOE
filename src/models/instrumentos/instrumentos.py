class Instrumento:
    def __init__(self, idInstrumento=None, nombreInstrumento=None, 
    descripcionInstrumento=None, cantidadInstrumento=None, 
    marcaInstrumento=None, modeloInstrumento=None, 
    serieInstrumento=None, colorInstrumento=None, 
    tamanoInstrumento=None, pisoInstrumento=None, 
    idEstadoCons=None, usuarioId=None, laboratorioId=None, 
    unidadId=None, imagenInstrumento=None, estado=None):
        self.idInstrumento = idInstrumento
        self.nombreInstrumento = nombreInstrumento
        self.descripcionInstrumento = descripcionInstrumento
        self.cantidadInstrumento = cantidadInstrumento
        self.marcaInstrumento = marcaInstrumento
        self.modeloInstrumento = modeloInstrumento
        self.serieInstrumento = serieInstrumento
        self.colorInstrumento = colorInstrumento
        self.tamanoInstrumento = tamanoInstrumento
        self.pisoInstrumento = pisoInstrumento
        self.idEstadoCons = idEstadoCons
        self.usuarioId = usuarioId
        self.laboratorioId = laboratorioId
        self.unidadId = unidadId
        self.imagenInstrumento = imagenInstrumento
        self.estado = estado

    def to_dict(self):
        return {
            "idInstrumento": self.idInstrumento,
            "nombreInstrumento": self.nombreInstrumento,
            "descripcionInstrumento": self.descripcionInstrumento,
            "cantidadInstrumento": self.cantidadInstrumento,
            "marcaInstrumento": self.marcaInstrumento,
            "modeloInstrumento": self.modeloInstrumento,
            "serieInstrumento": self.serieInstrumento,
            "colorInstrumento": self.colorInstrumento,
            "tamanoInstrumento": self.tamanoInstrumento,
            "pisoInstrumento": self.pisoInstrumento,
            "idEstadoCons": self.idEstadoCons,
            "usuarioId": self.usuarioId,
            "laboratorioId": self.laboratorioId,
            "unidadId": self.unidadId,
            "imagenInstrumento": self.imagenInstrumento,
            "estado": self.estado
        }