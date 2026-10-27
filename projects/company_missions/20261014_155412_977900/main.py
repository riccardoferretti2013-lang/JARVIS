import ast
import sys
from decimal import Decimal, DecimalException, localcontext

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CalculatorError(ValueError):
    """Espressione non valida o operazione matematica non eseguibile."""


class CalculatorEngine:
    """Valuta espressioni aritmetiche senza usare eval()."""

    _BINARY_OPERATORS = {
        ast.Add: lambda left, right: left + right,
        ast.Sub: lambda left, right: left - right,
        ast.Mult: lambda left, right: left * right,
        ast.Div: lambda left, right: left / right,
        ast.Pow: lambda left, right: left ** int(right),
    }
    _UNARY_OPERATORS = {
        ast.UAdd: lambda value: value,
        ast.USub: lambda value: -value,
    }

    def evaluate(self, expression: str) -> Decimal:
        if not isinstance(expression, str) or not expression.strip():
            raise CalculatorError("Inserisci un'espressione.")
        if len(expression) > 256:
            raise CalculatorError("L'espressione è troppo lunga.")

        source = expression.replace("×", "*").replace("÷", "/").replace("^", "**")

        try:
            tree = ast.parse(source, mode="eval")
            if sum(1 for _ in ast.walk(tree)) > 64:
                raise CalculatorError("L'espressione è troppo complessa.")

            with localcontext() as context:
                context.prec = 28
                result = self._visit(tree.body, source)

            self._check_result(result)
            return result
        except CalculatorError:
            raise
        except (SyntaxError, DecimalException, ValueError, OverflowError, TypeError) as exc:
            raise CalculatorError("Espressione non valida.") from exc

    def _visit(self, node: ast.AST, source: str) -> Decimal:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            literal = ast.get_source_segment(source, node)
            if literal is None:
                raise CalculatorError("Numero non valido.")

            try:
                value = Decimal(literal.replace("_", ""))
            except DecimalException as exc:
                raise CalculatorError("Numero non valido.") from exc

            if not value.is_finite() or len(value.as_tuple().digits) > 256:
                raise CalculatorError("Numero fuori dai limiti supportati.")
            if not value.is_zero() and abs(value.adjusted()) > 1000:
                raise CalculatorError("Numero fuori dai limiti supportati.")
            if abs(value.as_tuple().exponent) > 1000:
                raise CalculatorError("Numero fuori dai limiti supportati.")
            return value

        if isinstance(node, ast.BinOp):
            operation = self._BINARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise CalculatorError("Operatore non supportato.")

            left = self._visit(node.left, source)
            right = self._visit(node.right, source)

            if isinstance(node.op, ast.Pow):
                if right != right.to_integral_value() or abs(right) > 1000:
                    raise CalculatorError("L'esponente deve essere un intero tra -1000 e 1000.")

            result = operation(left, right)
            self._check_result(result)
            return result

        if isinstance(node, ast.UnaryOp):
            operation = self._UNARY_OPERATORS.get(type(node.op))
            if operation is None:
                raise CalculatorError("Operatore non supportato.")
            result = operation(self._visit(node.operand, source))
            self._check_result(result)
            return result

        raise CalculatorError("Espressione non valida.")

    @staticmethod
    def _check_result(value: Decimal) -> None:
        if not value.is_finite():
            raise CalculatorError("Risultato non finito.")
        if not value.is_zero() and abs(value.adjusted()) > 1000:
            raise CalculatorError("Risultato fuori dai limiti supportati.")
        if abs(value.as_tuple().exponent) > 1000:
            raise CalculatorError("Risultato fuori dai limiti supportati.")


class MainWindow(QMainWindow):
    def __init__(self, engine: CalculatorEngine):
        super().__init__()
        self.engine = engine
        self._just_evaluated = False

        self.setWindowTitle("Calcolatrice")
        self.setMinimumSize(340, 480)
        self.resize(380, 540)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        title = QLabel("CALCOLATRICE")
        title.setObjectName("title")
        layout.addWidget(title)

        self.expression = QLineEdit()
        self.expression.setObjectName("expression")
        self.expression.setPlaceholderText("Inserisci un'espressione")
        self.expression.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.expression.setClearButtonEnabled(True)
        self.expression.setMaxLength(256)
        self.expression.returnPressed.connect(self._calculate)
        self.expression.textChanged.connect(self._on_expression_changed)
        layout.addWidget(self.expression)

        self.result = QLabel(" ")
        self.result.setObjectName("result")
        self.result.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.result.setMinimumHeight(34)
        layout.addWidget(self.result)

        grid = QGridLayout()
        grid.setSpacing(9)
        layout.addLayout(grid)

        button_rows = [
            [("AC", "clear"), ("(", "insert"), (")", "insert"), ("⌫", "back")],
            [("7", "insert"), ("8", "insert"), ("9", "insert"), ("÷", "insert")],
            [("4", "insert"), ("5", "insert"), ("6", "insert"), ("×", "insert")],
            [("1", "insert"), ("2", "insert"), ("3", "insert"), ("−", "insert")],
        ]

        for row_index, row in enumerate(button_rows):
            for column_index, (text, action) in enumerate(row):
                button = self._make_button(text, action)
                grid.addWidget(button, row_index, column_index)

        zero_button = self._make_button("0", "insert")
        grid.addWidget(zero_button, 4, 0, 1, 2)
        grid.addWidget(self._make_button(".", "insert"), 4, 2)
        grid.addWidget(self._make_button("^", "insert"), 4, 3)
        grid.addWidget(self._make_button("+", "insert"), 5, 3)

        equals_button = self._make_button("=", "calculate")
        equals_button.setObjectName("equalsButton")
        grid.addWidget(equals_button, 5, 0, 1, 3)

        self.setStyleSheet(
            """
            QWidget#root {
                background-color: #111827;
                color: #f9fafb;
            }
            QLabel#title {
                color: #9ca3af;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 2px;
            }
            QLineEdit#expression {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 12px;
                color: #f9fafb;
                font-size: 24px;
                padding: 14px;
                selection-background-color: #2563eb;
            }
            QLabel#result {
                color: #60a5fa;
                font-size: 21px;
                font-weight: 600;
                padding-right: 4px;
            }
            QPushButton {
                background-color: #273449;
                border: none;
                border-radius: 12px;
                color: #f9fafb;
                font-size: 20px;
                min-height: 54px;
            }
            QPushButton:hover {
                background-color: #37465d;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton#equalsButton {
                background-color: #2563eb;
                color: white;
                font-size: 23px;
                font-weight: 700;
            }
            QPushButton#equalsButton:hover {
                background-color: #1d4ed8;
            }
            """
        )

    def _make_button(self, text: str, action: str) -> QPushButton:
        button = QPushButton(text)
        button.setSizePolicy(
            button.sizePolicy().Policy.Expanding,
            button.sizePolicy().Policy.Expanding,
        )
        button.setFont(QFont("Arial", 17))

        if action == "insert":
            value = {"−": "-", "×": "*", "÷": "/"}.get(text, text)
            button.clicked.connect(lambda checked=False, v=value: self._insert(v))
        elif action == "clear":
            button.clicked.connect(self._clear)
        elif action == "back":
            button.clicked.connect(self._backspace)
        elif action == "calculate":
            button.clicked.connect(self._calculate)

        return button

    def _insert(self, value: str) -> None:
        if self._just_evaluated:
            if value in "+-*/^":
                self._just_evaluated = False
            else:
                self.expression.clear()
                self._just_evaluated = False

        self.expression.insert(value)
        self.expression.setFocus()

    def _clear(self) -> None:
        self.expression.clear()
        self.result.setText(" ")
        self._just_evaluated = False
        self.expression.setFocus()

    def _backspace(self) -> None:
        if self._just_evaluated:
            self.expression.clear()
            self._just_evaluated = False
        else:
            self.expression.backspace()
        self.expression.setFocus()

    def _on_expression_changed(self, _text: str) -> None:
        if not self._just_evaluated:
            self.result.setText(" ")

    def _calculate(self) -> None:
        try:
            value = self.engine.evaluate(self.expression.text())
            formatted = format(value, "f")
            if "." in formatted:
                formatted = formatted.rstrip("0").rstrip(".")
            if formatted in ("", "-0"):
                formatted = "0"

            self.result.setText(formatted)
            self.expression.setText(formatted)
            self.expression.setCursorPosition(len(formatted))
            self._just_evaluated = True
        except CalculatorError as exc:
            self.result.setText(str(exc))
            self._just_evaluated = False


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Calcolatrice")
    window = MainWindow(CalculatorEngine())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
