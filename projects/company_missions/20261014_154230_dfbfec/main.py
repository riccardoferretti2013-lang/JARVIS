import ast
import re
import sys
from decimal import Decimal, DecimalException, localcontext

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CalculatorError(ValueError):
    """Errore di input o di calcolo da mostrare nell'interfaccia."""


class CalculatorEngine:
    MAX_EXPRESSION_LENGTH = 256
    MAX_EXPONENT = 100
    MAX_RESULT_ADJUSTED_EXPONENT = 1000
    MAX_TREE_DEPTH = 64

    def evaluate(self, expression: str) -> Decimal:
        """Valuta un'espressione aritmetica senza eseguire codice Python."""
        expression = (
            expression.strip()
            .replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
            .replace("^", "**")
        )
        if not expression or len(expression) > self.MAX_EXPRESSION_LENGTH:
            raise CalculatorError("Inserisci un'espressione valida.")

        try:
            tree = ast.parse(expression, mode="eval")
            with localcontext() as context:
                context.prec = 28
                result = self._visit(tree.body, expression, 0)
        except CalculatorError:
            raise
        except (
            SyntaxError,
            ValueError,
            DecimalException,
            ArithmeticError,
            OverflowError,
            RecursionError,
        ):
            raise CalculatorError(
                "Espressione non valida o operazione impossibile."
            ) from None

        if not result.is_finite():
            raise CalculatorError("Il risultato non è finito.")
        if result and abs(result.adjusted()) > self.MAX_RESULT_ADJUSTED_EXPONENT:
            raise CalculatorError("Il risultato è troppo grande.")
        return result

    @staticmethod
    def format_result(value: Decimal) -> str:
        """Restituisce un formato decimale compatto, senza zeri superflui."""
        if value.is_zero():
            return "0"
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text

    def _visit(self, node: ast.AST, source: str, depth: int) -> Decimal:
        if depth > self.MAX_TREE_DEPTH:
            raise CalculatorError("Espressione troppo complessa.")

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            literal = ast.get_source_segment(source, node)
            if literal is None:
                raise CalculatorError("Numero non valido.")
            try:
                return Decimal(literal.replace("_", ""))
            except DecimalException:
                raise CalculatorError("Numero non valido.") from None

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = self._visit(node.operand, source, depth + 1)
            return value if isinstance(node.op, ast.UAdd) else -value

        if isinstance(node, ast.BinOp):
            left = self._visit(node.left, source, depth + 1)
            right = self._visit(node.right, source, depth + 1)

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                if right != right.to_integral_value():
                    raise CalculatorError("L'esponente deve essere un numero intero.")
                exponent = int(right)
                if abs(exponent) > self.MAX_EXPONENT:
                    raise CalculatorError("Esponente troppo grande.")
                return left**exponent

        raise CalculatorError("Espressione non valida.")


class CalculatorWindow(QWidget):
    def __init__(self, engine: CalculatorEngine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Calcolatrice")
        self.setMinimumSize(340, 440)
        self.resize(380, 500)
        self.setStyleSheet(
            """
            QWidget {
                background: #151923;
                color: #edf0f7;
            }
            QLineEdit {
                background: #202634;
                border: 0;
                border-radius: 10px;
                padding: 14px;
                color: white;
                selection-background-color: #526dfe;
            }
            QPushButton {
                background: #262d3c;
                border: 0;
                border-radius: 10px;
                min-height: 54px;
                color: #edf0f7;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #343e52;
            }
            QPushButton:pressed {
                background: #414d64;
            }
            QPushButton[accent="true"] {
                background: #526dfe;
            }
            QPushButton[accent="true"]:hover {
                background: #6980ff;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        self.expression = QLineEdit()
        self.expression.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.expression.setFont(QFont("Arial", 22))
        self.expression.setPlaceholderText("Inserisci un'espressione")
        self.expression.setMaxLength(self.engine.MAX_EXPRESSION_LENGTH)
        self.expression.returnPressed.connect(self.calculate)
        self.expression.textChanged.connect(self._on_expression_changed)
        root.addWidget(self.expression)

        self.result = QLabel(" ")
        self.result.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.result.setWordWrap(True)
        self._set_result_style(error=False)
        root.addWidget(self.result)

        grid = QGridLayout()
        grid.setSpacing(8)
        root.addLayout(grid)

        keys = [
            ("C", "⌫", "(", ")"),
            ("7", "8", "9", "÷"),
            ("4", "5", "6", "×"),
            ("1", "2", "3", "−"),
            ("%", "0", ".", "+"),
            ("xʸ", "=", "", ""),
        ]

        for row, items in enumerate(keys):
            for column, key in enumerate(items):
                if not key:
                    continue
                button = QPushButton(key)
                if key == "=":
                    button.setProperty("accent", True)
                    grid.addWidget(button, row, column, 1, 2)
                else:
                    grid.addWidget(button, row, column)
                button.clicked.connect(
                    lambda checked=False, selected=key: self.press(selected)
                )

        for column in range(4):
            grid.setColumnStretch(column, 1)

    def press(self, key: str) -> None:
        if key == "C":
            self.expression.clear()
            self.result.setText(" ")
            return

        if key == "⌫":
            self.expression.backspace()
            return

        if key == "=":
            self.calculate()
            return

        if key == "%":
            self._insert_percent()
            return

        replacements = {"÷": "/", "×": "*", "−": "-", "xʸ": "**"}
        self.expression.insert(replacements.get(key, key))

    def _insert_percent(self) -> None:
        """Interpreta il tasto percentuale come divisione per cento."""
        text_before_cursor = self.expression.text()[: self.expression.cursorPosition()]
        if re.search(r"(?:\d|\))\s*$", text_before_cursor):
            self.expression.insert("/100")

    def calculate(self) -> None:
        try:
            value = self.engine.evaluate(self.expression.text())
            self.result.setText(self.engine.format_result(value))
            self._set_result_style(error=False)
        except CalculatorError as error:
            self.result.setText(str(error))
            self._set_result_style(error=True)

    def _on_expression_changed(self, _text: str) -> None:
        self.result.setText(" ")
        self._set_result_style(error=False)

    def _set_result_style(self, error: bool) -> None:
        color = "#ff8585" if error else "#aab4c8"
        self.result.setStyleSheet(
            f"color: {color}; font-size: 18px; padding: 4px;"
        )


def main() -> int:
    app = QApplication(sys.argv)
    window = CalculatorWindow(CalculatorEngine())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
