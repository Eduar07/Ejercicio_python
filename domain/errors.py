'''
Defines how problems are reported
'''
ERROR_MESSAGES = {
    "ERR001": "The folder does not exist",
    "ERR002": "There are no Excel files to process",
    "ERR004": "Could not open the Excel file",
    "ERR005": "The expected sheet does not exist",
    "ERR006": "Excel file columns do not match the expected structure",
    "ERR010": "Invalid week format",
    "ERR011": "Inconsistent year",
    "ERR012": "Invalid date format",
}


class ATError(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.message = ERROR_MESSAGES.get(code, "Unknown error")
        self.detail = detail

        super().__init__(self.message)


    def __str__(self):
        return f"[{self.code}] {self.message}: {self.detail}"


if __name__ == "__main__":

    error = ATError(
        "ERR001",
        "AT 05.04 - 05.08.xlsx does not exist in Input/"
    )

    print(error)

    print(error.code)

    print(error.detail)


    print("\n--- Non-existent error ---")

    error2 = ATError(
        "ERR999",
        "Code created only for testing"
    )

    print(error2)