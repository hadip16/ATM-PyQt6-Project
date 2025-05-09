import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
    QVBoxLayout, QWidget, QMessageBox, QGraphicsPixmapItem, QInputDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class User:
    def __init__(self, card_number, pin, balance):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance

    def check_pin(self, input_pin):
        return self.pin == input_pin

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def deposit(self, amount):
        self.balance += amount

    def transfer(self, target_user, amount):
        if self.withdraw(amount):
            target_user.deposit(amount)
            return True
        return False

    def change_pin(self, new_pin):
        self.pin = new_pin

def load_users():
    try:
        with open("data/users.json", "r") as f:
            data = json.load(f)
            users = {}
            for card, info in data.items():
                users[card] = User(card, info["pin"], info["balance"])
            return users
    except FileNotFoundError:
        return {}

def save_users(users):
    data = {card: {"pin": user.pin, "balance": user.balance} for card, user in users.items()}
    with open("data/users.json", "w") as f:
        json.dump(data, f, indent=4)

class ATMWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATM - PyQt6")
        self.setGeometry(300, 100, 400, 300)
        self.users = load_users()
        self.current_user = None

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()

        self.info_label = QLabel("Enter Card Number:")
        self.info_label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.info_label)

        self.input_line = QLineEdit()
        self.layout.addWidget(self.input_line)
        self.pin_label = QLabel("Enter PIN:")
        self.pin_label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.pin_label)
        self.pin_line = QLineEdit()
        self.pin_line.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.pin_line)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)
        self.main_widget.setLayout(self.layout)

    def login(self):
        card = self.input_line.text()
        pin = self.pin_line.text()
        if card in self.users and self.users[card].check_pin(pin):
            self.current_user = self.users[card]
            self.show_main_menu()
        else:
            QMessageBox.warning(self, "Error", "Invalid card number or PIN")

    def show_main_menu(self):
        self.layout = QVBoxLayout()

        self.balance_button = QPushButton("Show Balance")
        self.balance_button.clicked.connect(self.show_balance)
        self.layout.addWidget(self.balance_button)
        self.withdraw_button = QPushButton("Withdraw")
        self.withdraw_button.clicked.connect(self.withdraw)
        self.layout.addWidget(self.withdraw_button)
        self.transfer_button = QPushButton("Transfer")
        self.transfer_button.clicked.connect(self.transfer)
        self.layout.addWidget(self.transfer_button)
        self.change_pin_button = QPushButton("Change PIN")
        self.change_pin_button.clicked.connect(self.change_pin)
        self.layout.addWidget(self.change_pin_button)
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.layout.addWidget(self.logout_button)

        self.clear_widget()
        self.main_widget.setLayout(self.layout)

    def clear_widget(self):
        for i in reversed(range(self.main_widget.layout().count())):
            widget_to_remove = self.main_widget.layout().itemAt(i).widget()
            self.main_widget.layout().removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

    def show_balance(self):
        QMessageBox.information(self, "Balance", f"Your balance is: {self.current_user.balance}")

    def withdraw(self):
        amount, ok = self.get_amount_input("Withdraw Amount")
        if ok and self.current_user.withdraw(amount):
            QMessageBox.information(self, "Success", "Withdrawal successful")
            save_users(self.users)
        else:
            QMessageBox.warning(self, "Failed", "Insufficient funds or invalid amount")

    def transfer(self):
        target_card, ok1 = self.get_text_input("Enter target card number:")
        if not ok1 or target_card not in self.users:
            QMessageBox.warning(self, "Error", "Target user not found")
            return

        amount, ok2 = self.get_amount_input("Transfer Amount")
        if ok2 and self.current_user.transfer(self.users[target_card], amount):
            QMessageBox.information(self, "Success", "Transfer successful")
            save_users(self.users)
        else:
            QMessageBox.warning(self, "Failed", "Insufficient funds or invalid amount")

    def change_pin(self):
        new_pin, ok = self.get_text_input("Enter new PIN:")
        if ok and new_pin:
            self.current_user.change_pin(new_pin)
            QMessageBox.information(self, "Success", "PIN changed successfully")
            save_users(self.users)

    def logout(self):
        self.current_user = None
        self.clear_widget()
        self.__init__()

    def get_amount_input(self, title):
        text, ok = QInputDialog.getInt(self, title, "Enter amount:")
        return text, ok

    def get_text_input(self, title):
        text, ok = QInputDialog.getText(self, title, "Enter value:")
        return text, ok

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ATMWindow()
    window.show()
    sys.exit(app.exec())
