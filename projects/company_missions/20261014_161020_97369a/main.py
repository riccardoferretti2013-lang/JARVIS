import ast
import math
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CalculatorEngine:
    """Valuta espressioni aritmetiche senza eseguire codice arbitrario."""

    MAX_EXPRESSION_LENGTH = 256
    MAX_NODES = 128
    MAX_EXPONENT = 100

    def calculate(self, expression: str) -> float:
        if not isinstance(expression, str) or not expression.strip():
            raise ValueError("Inserisci un'espressione.")
        if len(expression) > self.MAX_EXPRESSION_LENGTH:
            raise ValueError("Espressione troppo lunga.")

        normalized = (
            expression.replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
            .replace(",", ".")
        )

        try:
            tree = ast.parse(normalized, mode="eval")
        except (SyntaxError, ValueError, RecursionError) as exc:
            raise ValueError("Espressione non valida.") from exc

        if sum(1 for _ in ast.walk(tree)) > self.MAX_NODES:
            raise ValueError("Espressione troppo complessa.")

        try:
            result = self._evaluate(tree.body)
        except ValueError:
            raise
        except (OverflowError, ZeroDivisionError, TypeError, RecursionError) as exc:
            raise ValueError("Operazione non valida.") from exc

        if isinstance(result, complex) or not math.isfinite(result):
            raise ValueError("Risultato non finito.")
        return float(result)

    def _evaluate(self, node) -> float:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            try:
                value = float(node.value)
            except OverflowError as exc:
                raise ValueError("Numero troppo grande.") from exc
            if not math.isfinite(value):
                raise ValueError("Numero non valido.")
            return value

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = self._evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value

        if isinstance(node, ast.BinOp):
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Add):
                result = left + right
            elif isinstance(node.op, ast.Sub):
                result = left - right
            elif isinstance(node.op, ast.Mult):
                result = left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ValueError("Divisione per zero.")
                result = left / right
            elif isinstance(node.op, ast.FloorDiv):
                if right == 0:
                    raise ValueError("Divisione per zero.")
                result = left // right
            elif isinstance(node.op, ast.Mod):
                if right == 0:
                    raise ValueError("Divisione per zero.")
                result = left % right
            elif isinstance(node.op, ast.Pow):
                if abs(right) > self.MAX_EXPONENT:
                    raise ValueError("Esponente troppo grande.")
                result = left**right
            else:
                raise ValueError("Operatore non supportato.")

            if isinstance(result, complex) or not math.isfinite(result):
                raise ValueError("Risultato non finito.")
            return result

        raise ValueError("Espressione non valida.")


class CalculatorWindow(QWidget):
    def __init__(self, engine: CalculatorEngine):
        super().__init__()
        self.engine = engine
        self.just_calculated = False
        self.last_result = ""

        self.setWindowTitle("Calcolatrice")
        self.setMinimumSize(340, 480)
        self.resize(380, 520)
        self.setStyleSheet(
            """
            QWidget {
                background: #111827;
                color: #f9fafb;
                font-family: "Segoe UI", sans-serif;
            }
            QLineEdit {
                background: #1f2937;
                border: 1px solid #374151;
                border-radius: 12px;
                padding: 14px;
                color: #f9fafb;
                font-size: 26px;
                selection-background-color: #2563eb;
            }
            QLabel#heading {
                color: #9ca3af;
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 2px;
            }
            QLabel#result {
                color: #9ca3af;
                font-size: 17px;
                min-height: 28px;
            }
            QPushButton {
                background: #273449;
                border: none;
                border-radius: 12px;
                min-height: 58px;
                color: #f9fafb;
                font-size: 20px;
            }
            QPushButton:hover {
                background: #37465d;
            }
            QPushButton:pressed {
                background: #475569;
            }
            QPushButton[role="operator"] {
                background: #374151;
                color: #93c5fd;
            }
            QPushButton[role="action"] {
                background: #b45309;
                color: white;
            }
            QPushButton[role="equals"] {
                background: #2563eb;
                color: white;
                font-weight: 700;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(12)

        heading = QLabel("CALCOLATRICE")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setPlaceholderText("0")
        self.display.setClearButtonEnabled(False)
        self.display.setAccessibleName("Espressione")
        self.display.returnPressed.connect(self.calculate)
        self.display.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.display)

        self.result_label = QLabel("")
        self.result_label.setObjectName("result")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.result_label.setAccessibleName("Risultato")
        layout.addWidget(self.result_label)

        grid = QGridLayout()
        grid.setSpacing(9)
        layout.addLayout(grid)

        keys = [
            ("C", "⌫", "(", ")"),
            ("7", "8", "9", "÷"),
            ("4", "5", "6", "×"),
            ("1", "2", "3", "−"),
            ("0", ".", "=", "+"),
        ]

        for row, values in enumerate(keys):
            for column, text in enumerate(values):
                button = QPushButton(text)
                button.setAccessibleName(
                    {
                        "C": "Cancella tutto",
                        "⌫": "Cancella ultimo carattere",
                        "÷": "Dividi",
                        "×": "Moltiplica",
                        "−": "Sottrai",
                        "+": "Somma",
                        "=": "Calcola",
                    }.get(text, text)
                )

                if text == "=":
                    role = "equals"
                    button.clicked.connect(self.calculate)
                elif text in ("C", "⌫"):
                    role = "action"
                    if text == "C":
                        button.clicked.connect(self.clear)
                    else:
                        button.clicked.connect(self.backspace)
                elif text in ("÷", "×", "−", "+", "(", ")"):
                    role = "operator"
                    button.clicked.connect(
                        lambda checked=False, value=text: self.insert_text(value)
                    )
                else:
                    role = ""
                    button.clicked.connect(
                        lambda checked=False, value=text: self.insert_text(value)
                    )

                button.setProperty("role", role)
                grid.addWidget(button, row, column)

    def _on_text_changed(self, _text: str) -> None:
        self.just_calculated = False
        self.last_result = ""
        self.result_label.clear()

    def _set_display(self, text: str) -> None:
        self.display.setText(text)

    def insert_text(self, text: str) -> None:
        if self.just_calculated:
            if text in ("+", "−", "×", "÷"):
                self._set_display(self.last_result + text)
            else:
                self._set_display(text)
            self.just_calculated = False
            self.last_result = ""
            self.result_label.clear()
            self.display.setFocus()
            return

        self.display.insert(text)
        self.display.setFocus()

    def clear(self) -> None:
        self.display.clear()
        self.result_label.clear()
        self.just_calculated = False
        self.last_result = ""
        self.display.setFocus()

    def backspace(self) -> None:
        if self.just_calculated:
            self.just_calculated = False
            self.last_result = ""
            self.result_label.clear()
        self.display.backspace()
        self.display.setFocus()

    def calculate(self) -> None:
        expression = self.display.text().strip()
        try:
            value = self.engine.calculate(expression)
            formatted = format(value, ".15g")
            self.result_label.setText(f"= {formatted}")
            self.just_calculated = True
            self.last_result = formatted
        except ValueError as exc:
            self.result_label.setText(str(exc))
            self.just_calculated = False
            self.last_result = ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalculatorWindow(CalculatorEngine())
    window.show()
    sys.exit(app.exec())
