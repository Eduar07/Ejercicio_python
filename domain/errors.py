'''
Define como se reportan los problemas
'''
ERROR_MESSAGES = {
    "ERR001": "La carpeta no existe",
    "ERR002": "No existen archivos Excel para procesar",
    "ERR004": "No se pudo abrir el archivo Excel",
    "ERR005": "La hoja esperada no existe",
    "ERR006": "Las columnas del archivo Excel no coinciden con la estructura esperada",
    "ERR010": "Formato de semana inválido",
    "ERR011": "Año inconsistente",
    "ERR012": "Formato de fecha inválido",
}


class ATError(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.mensaje = ERROR_MESSAGES.get(code, "Error desconocido")
        self.detail = detail

        super().__init__(self.mensaje)


    def __str__(self):
        return f"[{self.code}] {self.mensaje}: {self.detail}"


if __name__ == "__main__":

    error = ATError(
        "ERR001",
        "AT 05.04 - 05.08.xlsx no existe en Input/"
    )

    print(error)

    print(error.code)

    print(error.detail)


    print("\n--- Error inexistente ---")

    error2 = ATError(
        "ERR999",
        "Código creado solamente para prueba"
    )

    print(error2)
