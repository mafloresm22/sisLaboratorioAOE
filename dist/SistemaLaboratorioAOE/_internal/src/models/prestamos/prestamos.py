class Prestamo:
    def __init__(self, idPrestamo=None, usuarioId=None, fechaSolicitud=None, 
                 fechaLimitePrestamo=None, motivoPrestamo=None, estadoPrestamo=None):
        self.idPrestamo = idPrestamo
        self.usuarioId = usuarioId
        self.fechaSolicitud = fechaSolicitud
        self.fechaLimitePrestamo = fechaLimitePrestamo
        self.motivoPrestamo = motivoPrestamo
        self.estadoPrestamo = estadoPrestamo

    def to_dict(self):
        return {
            "idPrestamo": self.idPrestamo,
            "usuarioId": self.usuarioId,
            "fechaSolicitud": self.fechaSolicitud,
            "fechaLimitePrestamo": self.fechaLimitePrestamo,
            "motivoPrestamo": self.motivoPrestamo,
            "estadoPrestamo": self.estadoPrestamo
        }

class DetallePrestamo:
    def __init__(self, idDetalle=None, prestamoId=None, instrumentoId=None, 
                 cantidadSolicitada=None, fechaDevolucion=None, 
                 estadoEntrega=None, estadoDevolucion=None):
        self.idDetalle = idDetalle
        self.prestamoId = prestamoId
        self.instrumentoId = instrumentoId
        self.cantidadSolicitada = cantidadSolicitada
        self.fechaDevolucion = fechaDevolucion
        self.estadoEntrega = estadoEntrega
        self.estadoDevolucion = estadoDevolucion

    def to_dict(self):
        return {
            "idDetalle": self.idDetalle,
            "prestamoId": self.prestamoId,
            "instrumentoId": self.instrumentoId,
            "cantidadSolicitada": self.cantidadSolicitada,
            "fechaDevolucion": self.fechaDevolucion,
            "estadoEntrega": self.estadoEntrega,
            "estadoDevolucion": self.estadoDevolucion
        }
